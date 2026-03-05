import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Button from "../components/Button";
import "./ErrorsPage.css";

const ErrorsPage = () => {
  const [errors, setErrors] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const eventSource = new EventSource("http://localhost:8000/events");

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        // zakładamy że backend wysyła:
        // { id, code, context, part_id, occurred_at }

        setErrors((prev) => [data, ...prev]);
      } catch (err) {
        console.error("Błąd parsowania JSON:", err);
      }
    };

    eventSource.onerror = () => {
      console.error("Błąd połączenia SSE");
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, []);

  return (
    <div className="errors">
      <h1>Lista błędów</h1>

      <div className="errors-list">
        {errors.length === 0 ? (
          <p>Brak błędów</p>
        ) : (
          errors.map((error, index) => (
            <div key={index} className="error-card">
              <p><strong>Kod:</strong> {error.code}</p>
              <p><strong>Kontekst:</strong> {error.context}</p>
              <p><strong>ID części:</strong> {error.part_id}</p>
              <p><strong>Data:</strong> {error.occurred_at}</p>
            </div>
          ))
        )}
      </div>

      <Button onClick={() => navigate("/")}>
        Powrót do menu
      </Button>
    </div>
  );
};

export default ErrorsPage;