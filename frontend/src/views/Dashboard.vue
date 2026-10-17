<template>
  <div class="min-h-screen bg-slate-50 font-sans pb-20">
    <!-- Верхняя панель навигации -->
    <nav class="bg-white shadow-sm px-6 py-4 flex justify-between items-center mb-8">
      <h1 class="text-xl font-extrabold text-slate-900 tracking-tight">Sniper Tracker</h1>
      <div class="flex items-center gap-4">
        <div class="px-4 py-1.5 rounded-full text-sm font-bold flex items-center gap-2"
             :class="isPro ? 'bg-blue-100 text-blue-700' : 'bg-slate-100 text-slate-600'">
          <span v-if="isPro" class="text-blue-500">★</span>
          Тариф: {{ isPro ? 'PRO' : 'Free' }}
        </div>
        <button @click="logout" class="text-slate-500 hover:text-slate-800 font-medium transition-colors">
          Выйти
        </button>
      </div>
    </nav>

    <div class="max-w-6xl mx-auto px-6 grid md:grid-cols-3 gap-8">
      <!-- Основная колонка: Задачи -->
      <div class="md:col-span-2 space-y-8">
        
        <!-- Форма создания задачи -->
        <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
          <h2 class="text-lg font-bold text-slate-800 mb-4">Новая задача для парсера</h2>
          
          <div v-if="errorMessage" class="mb-4 p-4 bg-red-50 text-red-700 rounded-xl text-sm font-medium border border-red-100">
            {{ errorMessage }}
          </div>

          <form @submit.prevent="createTask" class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <input v-model="form.title" type="text" placeholder="Название (напр. 1-к на Подоле)" required class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all">
              <input v-model="form.url" type="url" placeholder="Вставь ссылку на поиск с OLX" required class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all">
            </div>
            
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 bg-slate-50 p-4 rounded-xl">
              <div>
                <label class="block text-xs font-semibold text-slate-500 uppercase mb-1">Мин. цена</label>
                <input v-model.number="form.min_price" type="number" placeholder="От" class="w-full px-3 py-2 rounded-lg border border-slate-200 outline-none">
              </div>
              <div>
                <label class="block text-xs font-semibold text-slate-500 uppercase mb-1">Макс. цена</label>
                <input v-model.number="form.max_price" type="number" placeholder="До" class="w-full px-3 py-2 rounded-lg border border-slate-200 outline-none">
              </div>
              <div>
                <label class="block text-xs font-semibold text-slate-500 uppercase mb-1">Комнат</label>
                <input v-model.number="form.rooms" type="number" placeholder="Точно" class="w-full px-3 py-2 rounded-lg border border-slate-200 outline-none">
              </div>
              <div class="flex items-center justify-center pt-5">
                <label class="flex items-center gap-2 cursor-pointer">
                  <input v-model="form.owner_only" type="checkbox" class="w-5 h-5 rounded border-slate-300 text-blue-600 focus:ring-blue-500 cursor-pointer">
                  <span class="text-sm font-medium text-slate-700">Без риелторов</span>
                </label>
              </div>
            </div>

            <button type="submit" :disabled="isLoading" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3.5 rounded-xl transition-all shadow-md disabled:opacity-50">
              {{ isLoading ? 'Создание...' : 'Начать мониторинг' }}
            </button>
          </form>
        </div>

        <!-- Список активных задач -->
        <div>
          <h2 class="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
            Активные задачи 
            <span class="bg-slate-200 text-slate-600 px-2 py-0.5 rounded-full text-xs">{{ tasks.length }} / {{ isPro ? 10 : 1 }}</span>
          </h2>
          
          <div v-if="tasks.length === 0" class="text-center py-10 bg-white rounded-2xl border border-slate-100 border-dashed">
            <p class="text-slate-400 font-medium">Нет активных задач. Создайте первую выше!</p>
          </div>

          <div class="space-y-3">
            <div v-for="task in tasks" :key="task.id" class="bg-white p-5 rounded-xl border border-slate-200 flex justify-between items-center hover:shadow-md transition-shadow">
              <div>
                <h3 class="font-bold text-slate-900 text-lg">{{ task.title }}</h3>
                <div class="flex gap-3 mt-2 text-sm text-slate-500 font-medium">
                  <span v-if="task.min_price || task.max_price" class="bg-slate-100 px-2 py-1 rounded-md">
                    ₴ {{ task.min_price || 0 }} - {{ task.max_price || '∞' }}
                  </span>
                  <span v-if="task.rooms" class="bg-slate-100 px-2 py-1 rounded-md">Комнат: {{ task.rooms }}</span>
                </div>
              </div>
              <button @click="deleteTask(task.id)" class="text-red-400 hover:text-red-600 p-2 transition-colors" title="Удалить">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Боковая колонка: Управление подпиской -->
      <div>
        <div class="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-6 text-white shadow-xl relative overflow-hidden">
          <div class="absolute top-0 right-0 -mr-8 -mt-8 w-32 h-32 rounded-full bg-white opacity-5 blur-2xl"></div>
          
          <h2 class="text-xl font-bold mb-2">Статус аккаунта</h2>
          <p class="text-slate-300 text-sm mb-6">Расширь возможности парсера и обходи конкурентов.</p>
          
          <div class="space-y-4 mb-6">
            <div class="flex justify-between items-center border-b border-slate-700 pb-3">
              <span class="text-slate-400 text-sm">Текущий тариф</span>
              <span class="font-bold">{{ isPro ? 'PRO (Оплачен)' : 'Free (Базовый)' }}</span>
            </div>
            <div class="flex justify-between items-center border-b border-slate-700 pb-3">
              <span class="text-slate-400 text-sm">Лимит задач</span>
              <span class="font-bold">{{ tasks.length }} / {{ isPro ? 10 : 1 }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-slate-400 text-sm">Частота проверок</span>
              <span class="font-bold text-blue-400">{{ isPro ? 'Каждые 5 мин' : '1 раз в час' }}</span>
            </div>
          </div>

          <button v-if="!isPro" @click="showPaymentModal = true" class="w-full bg-blue-500 hover:bg-blue-400 text-white font-bold py-3 rounded-xl transition-colors shadow-lg">
            Перейти на PRO (299 ₴)
          </button>
          <div v-else class="text-center p-3 bg-white/10 rounded-xl font-medium text-blue-200">
            Подписка активна
          </div>

          <!-- НОВЫЙ БЛОК: Интеграция Telegram -->
          <div class="mt-6 border-t border-slate-700 pt-6">
            <h3 class="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4">Уведомления</h3>
            
            <div v-if="isTelegramConnected" class="flex items-center justify-center gap-2 text-green-400 bg-green-400/10 py-3 rounded-xl font-medium border border-green-400/20">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
              Telegram подключен
            </div>
            
            <button v-else @click="connectTelegram" :disabled="isConnectingTelegram" class="w-full bg-[#0088cc] hover:bg-[#0077b5] text-white font-bold py-3 rounded-xl transition-all shadow-lg flex items-center justify-center gap-2 disabled:opacity-50">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/></svg>
              {{ isConnectingTelegram ? 'Получение ссылки...' : 'Подключить Telegram' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно оплаты (Заглушка) -->
    <div v-if="showPaymentModal" class="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-3xl p-8 max-w-md w-full shadow-2xl">
        <h3 class="text-2xl font-bold text-slate-900 mb-2">Оформление PRO</h3>
        <p class="text-slate-500 mb-6">К оплате: <span class="font-bold text-slate-800">299 ₴ / месяц</span></p>
        
        <div class="bg-slate-50 border border-slate-200 rounded-xl p-4 mb-6 text-center text-sm text-slate-600 font-medium">
          Здесь будет интегрирован виджет оплаты Monobank или WayForPay.
        </div>

        <div class="flex gap-3">
          <button @click="showPaymentModal = false" class="flex-1 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold py-3 rounded-xl transition-colors">
            Отмена
          </button>
          <button @click="simulatePayment" class="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-xl transition-colors shadow-lg">
            Оплатить тестово
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const tasks = ref([])
const errorMessage = ref('')
const isLoading = ref(false)
const showPaymentModal = ref(false)
const isPro = ref(false) 
const isConnectingTelegram = ref(false)
const isTelegramConnected = ref(false)

const form = ref({
  title: '',
  url: '',
  min_price: null,
  max_price: null,
  rooms: null,
  owner_only: false
})

const fetchUser = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await fetch('http://localhost:8000/users/me', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (response.ok) {
      const userData = await response.json()
      // Если plan_id > 1 (это наш тариф Pro), включаем премиум интерфейс
      isPro.value = userData.plan_id > 1
      // Проверяем наличие telegram_chat_id в профиле пользователя
      isTelegramConnected.value = !!userData.telegram_chat_id
    }
  } catch (error) {
    console.error('Ошибка загрузки профиля', error)
  }
}

const fetchTasks = async () => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      router.push('/login')
      return
    }
    const response = await fetch('http://localhost:8000/tasks/', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (response.ok) {
      tasks.value = await response.json()
    }
  } catch (error) {
    console.error('Ошибка загрузки задач', error)
  }
}

const createTask = async () => {
  errorMessage.value = ''
  isLoading.value = true
  
  try {
    const token = localStorage.getItem('token')
    const response = await fetch('http://localhost:8000/tasks/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(form.value)
    })
    
    if (response.ok) {
      form.value = { title: '', url: '', min_price: null, max_price: null, rooms: null, owner_only: false }
      await fetchTasks()
    } else if (response.status === 403) {
      const errorData = await response.json()
      errorMessage.value = errorData.detail || 'Достигнут лимит задач. Перейдите на PRO.'
    } else {
      errorMessage.value = 'Ошибка при создании задачи. Проверьте данные.'
    }
  } catch (error) {
    errorMessage.value = 'Ошибка соединения с сервером.'
  } finally {
    isLoading.value = false
  }
}

const deleteTask = async (id) => {
  try {
    const token = localStorage.getItem('token')
    await fetch(`http://localhost:8000/tasks/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    })
    await fetchTasks()
  } catch (error) {
    console.error('Ошибка удаления', error)
  }
}

const simulatePayment = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await fetch('http://localhost:8000/users/upgrade', {
      method: 'POST',
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (response.ok) {
      isPro.value = true
      showPaymentModal.value = false
      await fetchTasks()
    } else {
      alert('Ошибка при обновлении тарифа на сервере.')
    }
  } catch (error) {
    console.error('Ошибка оплаты:', error)
  }
}

const connectTelegram = async () => {
  isConnectingTelegram.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await fetch('http://localhost:8000/users/me/telegram-link', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    if (response.ok) {
      const data = await response.json()
      // Открываем Deep Link в новой вкладке — браузер сам предложит открыть приложение Telegram
      window.open(data.link, '_blank')
    } else {
      alert('Ошибка соединения. Попробуйте еще раз.')
    }
  } catch (error) {
    console.error('Сбой при получении ссылки Telegram:', error)
  } finally {
    isConnectingTelegram.value = false
  }
}

const logout = () => {
  localStorage.removeItem('token')
  router.push('/')
}

onMounted(() => {
  fetchUser()
  fetchTasks()
})
</script>