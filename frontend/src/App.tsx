import { BrowserRouter, Routes, Route } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import CallPage from "./pages/CallPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/call/:roomName" element={<CallPage />} />
      </Routes>
    </BrowserRouter>
  );
}