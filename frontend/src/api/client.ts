import axios, {
  type AxiosRequestConfig,
  type InternalAxiosRequestConfig,
} from 'axios'

/**
 * Central HTTP client. Base URL comes from VITE_API_BASE_URL (see
 * frontend/.env.example); the request interceptor attaches the JWT and the
 * response interceptor silently refreshes the access token on 401.
 */

export const ACCESS_TOKEN_KEY = 'skillmap.access'
export const REFRESH_TOKEN_KEY = 'skillmap.refresh'

export const API_BASE_URL: string =
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem(ACCESS_TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

type RetriableConfig = InternalAxiosRequestConfig & { _retry?: boolean }

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original: RetriableConfig | undefined = error.config
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)

    if (error.response?.status === 401 && original && !original._retry && refreshToken) {
      original._retry = true
      try {
        const { data } = await axios.post<{ access: string }>(`${API_BASE_URL}/auth/refresh`, {
          refresh: refreshToken,
        })
        localStorage.setItem(ACCESS_TOKEN_KEY, data.access)
        original.headers.Authorization = `Bearer ${data.access}`
        return api(original)
      } catch {
        clearTokens()
      }
    }
    return Promise.reject(error)
  },
)

export function clearTokens(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
}

export function storeTokens(access: string, refresh: string): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, access)
  localStorage.setItem(REFRESH_TOKEN_KEY, refresh)
}

/** Thin helpers so endpoint modules stay declarative. */
export function get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
  return api.get(url, config).then((r) => r.data as T)
}

export function post<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
  return api.post(url, data, config).then((r) => r.data as T)
}

export function patch<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
  return api.patch(url, data, config).then((r) => r.data as T)
}

export function remove<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
  return api.delete(url, config).then((r) => r.data as T)
}