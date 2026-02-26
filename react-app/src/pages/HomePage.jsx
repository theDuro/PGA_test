import { useNavigate } from "react-router-dom";
import Button from "../components/Button";
import "./HomePage.css"; // import CSS

const HomePage = () => {
  const navigate = useNavigate();

  const goToNext = () => navigate("/SecondPage");
  const test1 = () => alert("Opcja 1");
  const test2 = () => alert("Opcja 2");

  return (
    <div className="home">
      <h1>Menu główne</h1>

      {/* Kontener przycisków wyrównany do lewej */}
      <div className="buttons">
        <Button onClick={test1}>Opcja 1</Button>
        <Button onClick={test2}>Opcja 2</Button>
        <Button onClick={goToNext}>Przejdź do drugiego okna</Button>
      </div>
    </div>
  );
};

export default HomePage;