import { API_ORIGIN } from '../config/api'

const baseURL = API_ORIGIN

function parseErrorDetail(data) {
  if (!data?.detail) return "请求失败";
  if (typeof data.detail === "string") return data.detail;
  if (Array.isArray(data.detail)) {
    return data.detail.map((e) => e.msg).join("; ");
  }
  return "请求失败";
}

export async function register(username, email, password) {
  const params = new URLSearchParams({ username, email, password });
  const res = await fetch(`${baseURL}/register?${params}`, { method: "POST" });
  const data = await res.json();
  if (!res.ok) {
    return { error: parseErrorDetail(data), ...data };
  }
  return data;
}

export async function login(username, password) {
  const formData = new FormData();
  formData.append("username", username);
  formData.append("password", password);

  const res = await fetch(`${baseURL}/token`, {
    method: "POST",
    body: formData,
  });
  const data = await res.json();
  if (!res.ok) {
    return { error: parseErrorDetail(data), ...data };
  }
  return data;
}

export async function getConversations(token) {
  const res = await fetch(`${baseURL}/conversations`, {
    method: "GET",
    headers: { Authorization: `Bearer ${token}` },
  });
  const data = await res.json();
  if (!res.ok) {
    return { error: parseErrorDetail(data), ...data };
  }
  return data;
}

export async function createConversation(token, title) {
  const params = new URLSearchParams({ title });
  const res = await fetch(`${baseURL}/conversations?${params}`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
  const data = await res.json();
  if (!res.ok) {
    return { error: parseErrorDetail(data), ...data };
  }
  return data;
}
