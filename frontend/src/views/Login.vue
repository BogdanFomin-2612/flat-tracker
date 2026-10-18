<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { http } from '../api/http' // Импортируем наш настроенный клиент

const email = ref('')
const password = ref('')
const error = ref('')
const router = useRouter()

const handleLogin = async () => {
  error.value = ''
  try {
    const formData = new URLSearchParams()
    formData.append('username', email.value)
    formData.append('password', password.value)

    // Теперь используем короткий путь, baseURL подтянется из .env
    const response = await http.post('/users/login', formData)
    
    localStorage.setItem('token', response.data.access_token)
    router.push('/dashboard')
  } catch (err) {
    // 429 — сервер временно блокирует вход после серии неудачных попыток (защита от перебора)
    error.value = err.response?.status === 429
      ? 'Слишком много попыток входа. Подождите минуту.'
      : 'Неверный email или пароль'
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100">
    <div class="bg-white p-8 rounded-lg shadow-md w-96">
      <h1 class="text-2xl font-bold mb-6 text-center text-gray-800">Sniper Tracker</h1>
      <div v-if="error" class="mb-4 text-red-600 text-sm text-center bg-red-50 py-2 rounded">
      {{ error }}
    </div>
      
      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input 
            v-model="email" 
            type="email" 
            required
            class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="admin@example.com"
          >
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Пароль</label>
          <input 
            v-model="password" 
            type="password" 
            required
            class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="••••••••"
          >
        </div>
        
        <button 
          type="submit" 
          class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition duration-200 font-medium mt-2"
        >
          Войти
        </button>
      </form>
    </div>
  </div>
</template>