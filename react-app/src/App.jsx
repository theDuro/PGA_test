import { BrowserRouter, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import SecondPage from "./pages/SecondPage";
import ErrorsPage from "./pages/ErrorsPage";
import "./App.css";
import StatusPage from "./pages/StatusPage";

const App = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/SecondPage" element={<SecondPage />} />
        <Route path="/errors" element={<ErrorsPage />} />  {/* ← DODAJ TO */}
        <Route path="/status" element={<StatusPage />} />  {/* ← DODAJ TO */}        
      </Routes>
    </BrowserRouter>
  );
};

export default App;