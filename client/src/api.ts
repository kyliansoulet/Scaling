const RAW_API_URL: string | undefined = import.meta.env.VITE_API_URL;

export function buildUrl(base: string | undefined, path: string): string {
  if (!base) throw new Error("VITE_API_URL n'est pas définie au moment du build");
  return base.replace(/\/+$/, "") + "/" + path.replace(/^\/+/, "");
}

export type Note = { id: number; title: string; content: string; created_at: string };

const TOKEN_KEY = "coco-notes-token";
export const getToken = () => localStorage.getItem(TOKEN_KEY);
export const setToken = (t: string | null) =>
  t ? localStorage.setItem(TOKEN_KEY, t) : localStorage.removeItem(TOKEN_KEY);

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const res = await fetch(buildUrl(RAW_API_URL, path), { ...init, headers });
  if (res.status === 401) setToken(null);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const detail = typeof body.detail === "string" ? body.detail : `Erreur ${res.status}`;
    throw new Error(detail);
  }
  return (res.status === 204 ? undefined : await res.json()) as T;
}
