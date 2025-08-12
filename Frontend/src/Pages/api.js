// src/api.js
const BASE_URL = "http://localhost:8000";

async function postJSON(path, payload) {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.erro || `Falha em ${path}`);
  }
  return data;
}

export const registarAluno   = (p) => postJSON("/registar_aluno", p);
export const registarDocente = (p) => postJSON("/registar_docente", p);
