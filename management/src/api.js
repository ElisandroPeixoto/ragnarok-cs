// Thin wrapper over the backend's management API (backend/api/v1/endpoints/admin.py).
const BASE = "/api/v1/admin";

async function request(method, path, body) {
  const response = await fetch(`${BASE}${path}`, {
    method,
    headers: body === undefined ? undefined : { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const text = await response.text();
  const data = text ? JSON.parse(text) : null;
  if (!response.ok) {
    throw new Error(errorMessage(data) || `${response.status} ${response.statusText}`);
  }
  return data;
}

// FastAPI answers {"detail": "..."} or, for validation errors, {"detail": [{loc, msg}, ...]}
function errorMessage(data) {
  const detail = data?.detail;
  if (!detail) return null;
  if (typeof detail === "string") return detail;
  return detail.map((entry) => `${entry.loc?.slice(1).join(".")}: ${entry.msg}`).join("; ");
}

export const api = {
  options: () => request("GET", "/options"),
  characters: () => request("GET", "/characters"),
  updateCharacter: (id, values) => request("PATCH", `/characters/${id}`, values),
  monsters: () => request("GET", "/monsters"),
  updateMonster: (id, values) => request("PATCH", `/monsters/${id}`, values),
  jobs: () => request("GET", "/jobs"),
  updateJob: (name, values) => request("PATCH", `/jobs/${encodeURIComponent(name)}`, values),
  items: () => request("GET", "/items"),
  updateItem: (id, values) => request("PATCH", `/items/${id}`, values),
  sprites: () => request("GET", "/sprites"),
  uploadSprite: (group, name, pngBase64, json) =>
    request("POST", `/sprites/${group}/${name}`, { sheet_png_base64: pngBase64, sheet_json: json }),
};

// Whole zeny with a dot as the thousands separator, like the game: 1234567 -> "1.234.567z"
export const formatZeny = (zeny) => `${String(Math.trunc(Number(zeny) || 0)).replace(/\B(?=(\d{3})+(?!\d))/g, ".")}z`;

// Paths stored in the database are relative to the game's assets/ folder
export const assetUrl = (path) => (path ? `/assets/${path}` : null);
