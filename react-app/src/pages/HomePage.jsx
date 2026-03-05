import { useNavigate } from "react-router-dom";
import Button from "../components/Button";
import "./HomePage.css";

const HomePage = () => {
  const navigate = useNavigate();

  const goToNext = () => navigate("/SecondPage");
  const goToErrors = () => navigate("/errors");
  const goToStatus = () => navigate("/status"); 

  return (
    <div className="home">
      <h1>Menu główne</h1>

      <div className="buttons">
        <Button onClick={goToErrors}>Lista błędów</Button>
        <Button onClick={goToStatus}>Stan</Button>
        <Button onClick={goToNext}>predykcja</Button>
      </div>
    </div>
  );
};

export default HomePage;