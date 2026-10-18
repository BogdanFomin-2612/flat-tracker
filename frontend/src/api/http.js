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
        // На самом входе 401 означает неверный пароль, а не протухший токен: редирект стёр бы сообщение об ошибке
        const isLoginRequest = error.config?.url?.includes('/users/login')
        if (error.response?.status === 401 && !isLoginRequest) {
            localStorage.removeItem('token')
            window.location.href = '/login' // Жесткий редирект при протухшем токене
        }
        return Promise.reject(error)
    }
)