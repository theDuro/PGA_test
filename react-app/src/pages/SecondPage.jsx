import { useState } from "react";
import { useNavigate } from "react-router-dom";

const initialFields = [
  { key: "sheet_width", label: "Sheet width (mm)", value: "" },
  { key: "sheet_thickness", label: "Sheet thickness (mm)", value: "" },
  { key: "rolling_force", label: "Rolling force (kN)", value: "" },
  { key: "motor_power", label: "Motor power (kW)", value: "" },
  { key: "line_speed", label: "Line speed (m/min)", value: "" },
  { key: "process_time", label: "Process time (s)", value: "" },
];

const SecondPage = () => {
  const navigate = useNavigate();
  const [fields, setFields] = useState(initialFields);

  const goBack = () => navigate("/");

  const handleChange = (index, newValue) => {
    setFields((prev) =>
      prev.map((field, i) =>
        i === index ? { ...field, value: newValue === "" ? "" : Number(newValue) } : field
      )
    );
  };

  const sendData = async () => {
    const payload = {};
    fields.forEach((f) => {
      payload[f.key] = f.value;
    });

    console.log("Sending payload to backend:", payload);

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

      const resp = await response.json();
      console.log("Backend response:", resp);
      alert("Data sent to backend and RabbitMQ");
    } catch (err) {
      console.error("Error sending data:", err);
      alert("Error sending data");
    }
  };

  return (
    <div className="page">
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
        <button onClick={sendData}>Send</button>
        <button onClick={goBack}>Back</button>
      </div>
    </div>
  );
};

export default SecondPage;