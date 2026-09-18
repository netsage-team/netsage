async function parseResponse(response) {
  const text = await response.text()
  const contentType = response.headers.get('content-type') || ''

  let data = {}

  if (text && contentType.includes('application/json')) {
    try {
      data = JSON.parse(text)
    } catch {
      data = {}
    }
  }

  if (!response.ok) {
    throw new Error(
      data.detail ||
      data.non_field_errors?.[0] ||
      `NetSage API request failed (${response.status}). Please retry.`
    )
  }

  return data
}

async function apiRequest(path, options = {}) {
  const response = await fetch(path, {
    credentials: 'same-origin',
    ...options,
    headers: {
      Accept: 'application/json',
      ...(options.headers || {}),
    },
  })

  return parseResponse(response)
}

export async function getCsrfToken() {
  const data = await apiRequest('/api/auth/csrf/')
  return data.csrfToken
}

export async function getCurrentUser() {
  return apiRequest('/api/auth/me/')
}

export async function signIn(username, password) {
  const csrfToken = await getCsrfToken()

  return apiRequest('/api/auth/login/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
    },
    body: JSON.stringify({
      username,
      password,
    }),
  })
}

export async function signOut() {
  const csrfToken = await getCsrfToken()

  return apiRequest('/api/auth/logout/', {
    method: 'POST',
    headers: {
      'X-CSRFToken': csrfToken,
    },
  })
}

export async function getJson(path) {
  return apiRequest(path)
}

export function resultsOf(data) {
  if (Array.isArray(data)) return data
  return data?.results || []
}
