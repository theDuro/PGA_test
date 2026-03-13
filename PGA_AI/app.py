import json
import numpy as np
import pika
import time
import os
import random
import logging

# -----------------------------
# Logger
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

# -----------------------------
# Konfiguracja RabbitMQ
# -----------------------------
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "admin")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "admin123")

QUEUE_INPUT  = os.getenv("QUEUE_INPUT",  "ml_input")
QUEUE_OUTPUT = os.getenv("QUEUE_OUTPUT", "output")


# -----------------------------
# Ekstrakcja danych wejściowych
# Obsługuje dowolny format JSON:
#   • {"input": [1, 2, 3]}
#   • {"input": {"a": 1, "b": 2}}
#   • {"sheet_width": 1, "sheet_thickness": 3, ...}  ← płaski dict
#   • [1, 2, 3]                                       ← lista na górnym poziomie
#   • 42                                              ← prymityw
# -----------------------------
def extract_features(data: dict | list) -> list:
    """
    Zwraca listę wartości liczbowych z danych wejściowych,
    niezależnie od struktury JSON.
    """
    # Jeśli JSON to lista — zwróć ją bezpośrednio
    if isinstance(data, list):
        return _flatten(data)

    # Jeśli JSON to dict
    if isinstance(data, dict):
        # Priorytet: klucz "input" jeśli istnieje
        if "input" in data:
            return _flatten(data["input"])

        # Priorytet: klucz "features" jeśli istnieje
        if "features" in data:
            return _flatten(data["features"])

        # W przeciwnym razie: wyciągamy wszystkie wartości z dict
        # Pomijamy pola meta (timestamp, id, itp.)
        META_KEYS = {"timestamp", "id", "source", "version", "type"}
        values = [
            v for k, v in data.items()
            if k not in META_KEYS
        ]
        return _flatten(values)

    # Prymityw (int, float, str)
    return _flatten([data])


def _flatten(obj) -> list:
    """
    Rekurencyjnie spłaszcza zagnieżdżone listy/dict do listy liczb.
    Wartości nie-numeryczne są pomijane z ostrzeżeniem.
    """
    result = []
    if isinstance(obj, (int, float)):
        result.append(float(obj))
    elif isinstance(obj, str):
        try:
            result.append(float(obj))
        except ValueError:
            log.warning(f"⚠️  Pomijam wartość tekstową: '{obj}'")
    elif isinstance(obj, list):
        for item in obj:
            result.extend(_flatten(item))
    elif isinstance(obj, dict):
        for v in obj.values():
            result.extend(_flatten(v))
    else:
        log.warning(f"⚠️  Nieznany typ: {type(obj)} — pomijam")
    return result


# -----------------------------
# Symulacja modelu ML
# (zastąp model.predict gdy będziesz mieć model)
# -----------------------------
def run_model(features: list) -> list:
    """
    Tymczasowo: losowe wyniki zamiast modelu ML.
    Docelowo:
        x = np.array(features, dtype=np.float32).reshape(1, -1)
        return model.predict(x)[0].tolist()
    """
    return [round(random.uniform(0, 100), 2) for _ in range(5)]


# -----------------------------
# Callback — obsługa wiadomości
# -----------------------------
def make_callback(channel):
    def callback(ch, method, properties, body):
        try:
            raw = body.decode("utf-8")
            data = json.loads(raw)
            log.info(f"📥 Odebrano: {data}")

            # Elastyczne wyciąganie cech
            features = extract_features(data)
            log.info(f"🔢 Cechy wejściowe: {features}")

            if not features:
                log.warning("⚠️  Brak cech numerycznych w danych — pomijam wiadomość")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                return

            # Predykcja
            predictions = run_model(features)

            # Budowanie odpowiedzi
            result = {
                "input":     features,
                "output":    predictions,
                "timestamp": data.get("timestamp", "") if isinstance(data, dict) else "",
                "meta": {
                    "feature_count": len(features),
                    "raw_keys": list(data.keys()) if isinstance(data, dict) else None,
                }
            }

            channel.basic_publish(
                exchange="",
                routing_key=QUEUE_OUTPUT,
                body=json.dumps(result),
                properties=pika.BasicProperties(delivery_mode=2)
            )

            log.info(f"✅ Wyniki: {predictions}")
            log.info(f"📤 Wysłano do kolejki '{QUEUE_OUTPUT}'")
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except json.JSONDecodeError as e:
            log.error(f"❌ Błąd parsowania JSON: {e} | body: {body}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        except Exception as e:
            log.error(f"❌ Nieoczekiwany błąd: {e}", exc_info=True)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    return callback


# -----------------------------
# Połączenie z RabbitMQ z retry
# -----------------------------
def connect_rabbitmq(max_retries=10) -> pika.BlockingConnection:
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    for attempt in range(1, max_retries + 1):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    port=RABBITMQ_PORT,
                    credentials=credentials,
                    heartbeat=600,
                    blocked_connection_timeout=300,
                )
            )
            log.info(f"✅ Połączono z RabbitMQ (próba {attempt})")
            return connection
        except Exception as e:
            log.warning(f"❌ Próba {attempt}/{max_retries} — błąd: {e}")
            time.sleep(5)
    raise RuntimeError("Nie udało się połączyć z RabbitMQ po wielu próbach")


# -----------------------------
# Główna pętla z auto-reconnect
# -----------------------------
def main():
    log.info("🚀 AI Service startuje...")

    while True:
        connection = None
        try:
            connection = connect_rabbitmq()
            channel = connection.channel()

            channel.queue_declare(queue=QUEUE_INPUT,  durable=True)
            channel.queue_declare(queue=QUEUE_OUTPUT, durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(
                queue=QUEUE_INPUT,
                on_message_callback=make_callback(channel)
            )

            log.info(f"🔄 Czekam na dane w kolejce '{QUEUE_INPUT}'...")
            channel.start_consuming()

        except pika.exceptions.AMQPConnectionError as e:
            log.error(f"🔌 Utracono połączenie z RabbitMQ: {e} — restartuję za 5s...")
            time.sleep(5)

        except KeyboardInterrupt:
            log.info("🛑 Zatrzymano przez użytkownika")
            break

        except Exception as e:
            log.error(f"💥 Krytyczny błąd: {e}", exc_info=True)
            time.sleep(5)

        finally:
            if connection and not connection.is_closed:
                try:
                    connection.close()
                except Exception:
                    pass


if __name__ == "__main__":
    main()