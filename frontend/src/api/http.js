import axios from 'axios'

export const http = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
})

// Автоматическое добавление JWT токена
http.interceptors.request.use((config) => {
    const token = localStorage.getItem('token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

// Глобальная обработка ошибок авторизации
http.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token')
            window.location.href = '/login' // Жесткий редирект при протухшем токене
        }
        return Promise.reject(error)
    }
)