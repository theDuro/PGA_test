import { createContext, useContext, useEffect, useRef, useState } from "react";

const SSEContext = createContext(null);

export const SSEProvider = ({ children }) => {
  console.log("SSEProvider mounted");
  const [lastResult, setLastResult] = useState(null);
  const eventSourceRef = useRef(null);

  useEffect(() => {
    console.log("SSE useEffect running");
    const connect = () => {
      console.log("SSE connecting...");
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }

      const es = new EventSource("http://localhost:8000/stream");
      eventSourceRef.current = es;

      console.log("SSE EventSource created:", es);

      es.onopen = () => {
        console.log("SSE połączone!");
      };

      es.onmessage = (event) => {
        console.log("SSE RAW:", event.data);
        try {
          const data = JSON.parse(event.data);
          console.log("SSE PARSED:", data);
          if (data.output && Array.isArray(data.output)) {
            setLastResult(data);
          }
        } catch (e) {
          console.error("Błąd parsowania SSE:", e);
        }
      };

      es.onerror = (err) => {
        console.warn("SSE rozłączone, restartuję za 3s...", err);
        es.close();
        setTimeout(connect, 3000);
      };
    };

    connect();

    return () => {
      console.log("SSE cleanup");
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  return (
    <SSEContext.Provider value={{ lastResult }}>
      {children}
    </SSEContext.Provider>
  );
};

export const useSSE = () => useContext(SSEContext);