import { BrowserRouter, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import SecondPage from "./pages/SecondPage";
import ErrorsPage from "./pages/ErrorsPage";
import StatusPage from "./pages/StatusPage";
import { SSEProvider } from "./SSEContext";
import "./App.css";

const App = () => {
  return (
    <SSEProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/SecondPage" element={<SecondPage />} />
          <Route path="/errors" element={<ErrorsPage />} />
          <Route path="/status" element={<StatusPage />} />
        </Routes>
      </BrowserRouter>
    </SSEProvider>
  );
};

export default App;