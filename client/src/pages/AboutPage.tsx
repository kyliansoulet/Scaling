export default function AboutPage() {
  return (
    <div className="card">
      <h1>À propos</h1>
      <p>Client React + TypeScript (Vite) servi par Scalingo, API FastAPI et base PostgreSQL managée.</p>
      <p className="muted">API : {import.meta.env.VITE_API_URL}</p>
    </div>
  );
}
