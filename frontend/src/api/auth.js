const baseURL = "http://127.0.0.1:8000" // 你的后端地址

// 1. 注册用户
export async function register(username, password) {
  const res = await fetch(`${baseURL}/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ username, password })
  })
  return res.json()
}

// 2. 登录获取 Token
export async function login(username, password) {
  const res = await fetch(`${baseURL}/token`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ username, password })
  })
  return res.json()
}

export async function getProfile() {
  const token = localStorage.getItem("token")
  const res = await fetch(`${baseURL}/profile`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`
    }
  })
  return res.json()
}

// 3. 获取当前用户的对话列表
export async function getConversations(token) {
  const res = await fetch(`${baseURL}/conversations`, {
    method: "GET",
    headers: {
      "Authorization": `Bearer ${token}`
    }
  })
  return res.json()
}

// 4. 创建新对话
export async function createConversation(token, title) {
  const res = await fetch(`${baseURL}/conversations`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({ title })
  })
  return res.json()
}