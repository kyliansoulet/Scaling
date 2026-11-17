import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, setToken } from "../api";

export default function AuthPage({ mode }: { mode: "login" | "register" }) {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const isLogin = mode === "login";

  async function submit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      const { access_token } = await api<{ access_token: string }>(
        isLogin ? "/auth/login" : "/auth/register",
        { method: "POST", body: JSON.stringify({ email, password }) },
      );
      setToken(access_token);
      navigate("/");
    } catch (err) {
      setError((err as Error).message);
    }
  }

  return (
    <form className="card" onSubmit={submit}>
      <h1>{isLogin ? "Connexion" : "Créer un compte"}</h1>
      <label>Email<input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required /></label>
      <label>Mot de passe<input type="password" minLength={6} value={password} onChange={(e) => setPassword(e.target.value)} required /></label>
      {error && <p className="error">{error}</p>}
      <button type="submit">{isLogin ? "Se connecter" : "S'inscrire"}</button>
      <p>
        {isLogin ? <>Pas de compte ? <Link to="/register">Inscription</Link></> : <>Déjà inscrit ? <Link to="/login">Connexion</Link></>}
      </p>
    </form>
  );
}
