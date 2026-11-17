import { Link, Navigate, Route, Routes, useNavigate } from "react-router-dom";
import { getToken, setToken } from "./api";
import AuthPage from "./pages/AuthPage";
import NotesPage from "./pages/NotesPage";
import AboutPage from "./pages/AboutPage";

function RequireAuth({ children }: { children: JSX.Element }) {
  return getToken() ? children : <Navigate to="/login" replace />;
}

export default function App() {
  const navigate = useNavigate();
  const logged = !!getToken();
  return (
    <div className="container">
      <header>
        <Link to="/" className="brand">Coco Notes</Link>
        <nav>
          <Link to="/about">À propos</Link>
          {logged && (
            <button className="link" onClick={() => { setToken(null); navigate("/login"); }}>
              Déconnexion
            </button>
          )}
        </nav>
      </header>
      <Routes>
        <Route path="/" element={<RequireAuth><NotesPage /></RequireAuth>} />
        <Route path="/login" element={<AuthPage mode="login" />} />
        <Route path="/register" element={<AuthPage mode="register" />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
}
