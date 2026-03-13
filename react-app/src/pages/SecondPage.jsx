import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useSSE } from "../SSEContext";
import "./SecondPage.css";

const initialFields = [
  { key: "sheet_width", label: "Sheet width (mm)", value: "" },
  { key: "sheet_thickness", label: "Sheet thickness (mm)", value: "" },
  { key: "process_time", label: "Process time (s)", value: "" },
];

const RESULT_LABELS = ["var: 1", "var: 2", "var: 3", "var: 4", "var: 5"];

const SecondPage = () => {
  const navigate = useNavigate();
  const [fields, setFields] = useState(initialFields);
  const [results, setResults] = useState(null);
  const [waiting, setWaiting] = useState(false);
  const { lastResult } = useSSE();

  useEffect(() => {
    if (lastResult) {
      setResults(lastResult.output);
      setWaiting(false);
    }
  }, [lastResult]);

  const goBack = () => navigate("/");

  const handleChange = (index, newValue) => {
    setFields((prev) =>
      prev.map((field, i) =>
        i === index
          ? { ...field, value: newValue === "" ? "" : Number(newValue) }
          : field
      )
    );
  };

  const sendData = async () => {
    const payload = {};
    fields.forEach((f) => {
      payload[f.key] = f.value;
    });

    setResults(null);
    setWaiting(true);

    try {
      const response = await fetch("http://localhost:8000/data", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const text = await response.text();
        throw new Error(text);
      }
    } catch (err) {
      console.error("Error sending data:", err);
      alert("Error sending data");
      setWaiting(false);
    }
  };

  return (
    <div className="page">
      {/* Lewa połowa — formularz */}
      <div className="left-panel">
        <h1>Production Parameters</h1>
        <div className="grid">
          {fields.map((field, index) => (
            <div className="field" key={field.key}>
              <label htmlFor={"input" + index}>{field.label}</label>
              <input
                type="number"
                id={"input" + index}
                value={field.value}
                onChange={(e) => handleChange(index, e.target.value)}
              />
            </div>
          ))}
        </div>
        <div className="buttons">
          <button onClick={sendData} disabled={waiting}>
            {waiting ? "Czekam na wyniki..." : "Send"}
          </button>
          <button onClick={goBack}>Back</button>
        </div>
      </div>

      {/* Prawa połowa — wyniki */}
      <div className="right-panel">
        <h2>Wyniki AI</h2>

        {!results && !waiting && (
          <div className="results-empty">
            <p>Wyślij dane aby zobaczyć wyniki</p>
          </div>
        )}

        {waiting && !results && (
          <div className="results-waiting">
            <p>⏳ Oczekiwanie na odpowiedź z AI...</p>
          </div>
        )}

        {results && (
          <table className="results-table">
            <thead>
              <tr>
                <th>Zmienna</th>
                <th>Wartość</th>
              </tr>
            </thead>
            <tbody>
              {results.map((val, i) => (
                <tr key={i}>
                  <td>{RESULT_LABELS[i]}</td>
                  <td className="result-value">{val}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default SecondPage;