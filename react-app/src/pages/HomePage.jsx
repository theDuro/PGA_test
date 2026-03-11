import { useNavigate } from "react-router-dom";
import Button from "../components/Button";
import "./HomePage.css";

const HomePage = () => {
  const navigate = useNavigate();

  const goToNext = () => navigate("/SecondPage");
  const goToErrors = () => navigate("/errors");
  const goToStatus = () => navigate("/status");


  const partsPositions = [
    { partId: 1, x: 55, y: -18, name: "Transporter Łańcuchowy" },
    { partId: 2, x: 20, y: -10, name: "Transporter Łańcuchowy" },
    { partId: 3, x: 50, y: 3, name: "Robot" },
    { partId: 4, x: 75, y: 50, name: "Miejsce odłożenia " },
    { partId: 6, x: 50, y: 20, name: "Pozycjoner koszy" },
  ];

  const handlePartClick = (part) => {
    alert(`Kliknięto ${part.name}`);
  };

  return (
    <div className="home">
      <h1>Menu główne</h1>

      <div className="buttons">
        <Button onClick={goToErrors}>Lista błędów</Button>
        <Button onClick={goToStatus}>Stan</Button>
        <Button onClick={goToNext}>predykcja</Button>
      </div>

      <div
        style={{
          position: "relative",
          width: "100%",
          height: "600px",
          marginTop: "40px",
          background: "url(/machine.png) center/contain no-repeat",
        }}
      >
        {partsPositions.map((p) => (
          <button
            key={p.partId}
            onClick={() => handlePartClick(p)}
            style={{
              position: "absolute",
              left: `${p.x}%`,
              top: `${p.y}%`,
              transform: "translate(-50%, -50%)",
              padding: "10px 14px",
              borderRadius: "6px",
              border: "2px solid transparent",
              background: "transparent",
              color: "transparent",
              fontWeight: "bold",
              cursor: "pointer",
              transition: "background 0.2s, color 0.2s, border-color 0.2s",
            }}
            onMouseEnter={e => {
              e.currentTarget.style.background = "rgba(255, 165, 0, 0.2)";
              e.currentTarget.style.color = "orange";
              e.currentTarget.style.borderColor = "rgba(255, 165, 0, 0.8)";
            }}
            onMouseLeave={e => {
              e.currentTarget.style.background = "transparent";
              e.currentTarget.style.color = "transparent";
              e.currentTarget.style.borderColor = "transparent";
            }}
          >
            {p.name}
          </button>
        ))}
      </div>
    </div>
  );
};

export default HomePage;