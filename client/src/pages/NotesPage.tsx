import { FormEvent, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, getToken, Note } from "../api";

export default function NotesPage() {
  const navigate = useNavigate();
  const [notes, setNotes] = useState<Note[]>([]);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function load() {
    try {
      setNotes(await api<Note[]>("/notes"));
    } catch (err) {
      if (!getToken()) navigate("/login");
      else setError((err as Error).message);
    }
  }

  useEffect(() => { load(); }, []);

  async function add(e: FormEvent) {
    e.preventDefault();
    await api<Note>("/notes", { method: "POST", body: JSON.stringify({ title, content }) });
    setTitle(""); setContent("");
    load();
  }

  async function remove(id: number) {
    await api<void>(`/notes/${id}`, { method: "DELETE" });
    load();
  }

  return (
    <>
      <form className="card" onSubmit={add}>
        <h1>Mes notes</h1>
        <input placeholder="Titre" value={title} onChange={(e) => setTitle(e.target.value)} required maxLength={200} />
        <textarea placeholder="Contenu" value={content} onChange={(e) => setContent(e.target.value)} rows={3} />
        <button type="submit">Ajouter</button>
      </form>
      {error && <p className="error">{error}</p>}
      <ul className="notes">
        {notes.map((n) => (
          <li key={n.id} className="card">
            <div><strong>{n.title}</strong><p>{n.content}</p></div>
            <button className="danger" onClick={() => remove(n.id)}>Supprimer</button>
          </li>
        ))}
        {notes.length === 0 && <p className="muted">Aucune note pour l'instant.</p>}
      </ul>
    </>
  );
}
