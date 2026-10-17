<template>
  <div class="min-h-screen bg-white font-sans text-slate-900 pb-24">
    <!-- Верхняя панель навигации -->
    <nav class="max-w-7xl mx-auto px-6 py-6 flex justify-between items-center w-full">
      <div class="text-2xl font-extrabold tracking-tight">Sniper Tracker</div>
      <div class="flex items-center gap-3">
        <button @click="router.push('/login')" class="text-slate-600 hover:text-slate-900 font-semibold px-4 py-2 transition-colors">
          Войти
        </button>
        <button @click="router.push('/login')" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2.5 px-6 rounded-xl transition-all shadow-md shadow-blue-600/20">
          Регистрация
        </button>
      </div>
    </nav>

    <!-- Главный экран (Hero) -->
    <main class="text-center pt-16 md:pt-24 px-6 max-w-5xl mx-auto">
      <h1 class="text-5xl md:text-7xl font-extrabold tracking-tight mb-8">
        Твой персональный <br class="hidden md:block" />
        <span class="text-blue-600">снайпер</span> недвижимости
      </h1>
      <p class="text-lg md:text-xl text-slate-500 mb-10 max-w-2xl mx-auto leading-relaxed">
        Получай мгновенные уведомления о новых квартирах на OLX раньше риелторов. Автоматический обход блокировок и мониторинг 24/7 прямо в Telegram.
      </p>
      
      <div class="flex flex-col sm:flex-row items-center justify-center gap-4 mb-32">
        <button @click="router.push('/login')" class="w-full sm:w-auto bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 px-8 rounded-xl transition-all shadow-lg shadow-blue-600/30 text-lg">
          Попробовать бесплатно
        </button>
        <a href="#pricing" class="w-full sm:w-auto bg-white border border-slate-200 hover:border-slate-300 text-slate-700 font-bold py-4 px-8 rounded-xl transition-all text-lg shadow-sm flex items-center justify-center">
          Смотреть тарифы
        </a>
      </div>

      <!-- Секция тарифов -->
      <div id="pricing" class="max-w-4xl mx-auto text-left">
        <h2 class="text-3xl md:text-4xl font-extrabold text-center mb-12">Выбери свой тариф</h2>
        
        <div class="grid md:grid-cols-2 gap-8">
          <!-- Тариф Free -->
          <div class="bg-white rounded-3xl border border-slate-200 p-8 shadow-sm hover:shadow-md transition-shadow flex flex-col">
            <h3 class="text-2xl font-bold mb-2">Free</h3>
            <p class="text-slate-500 mb-6">Для базового поиска жилья</p>
            <div class="text-4xl font-extrabold mb-8">0 ₴<span class="text-lg text-slate-400 font-medium">/мес</span></div>
            
            <ul class="space-y-4 mb-8 flex-1">
              <li class="flex items-center gap-3 text-slate-600">
                <svg class="w-5 h-5 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                1 активная задача
              </li>
              <li class="flex items-center gap-3 text-slate-600">
                <svg class="w-5 h-5 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                Проверка раз в час
              </li>
              <li class="flex items-center gap-3 text-slate-600">
                <svg class="w-5 h-5 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                Уведомления в Telegram
              </li>
            </ul>
            
            <button @click="router.push('/login')" class="w-full bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold py-3 rounded-xl transition-colors">
              Начать бесплатно
            </button>
          </div>

          <!-- Тариф PRO -->
          <div class="bg-white rounded-3xl border-2 border-blue-500 p-8 shadow-xl relative flex flex-col">
            <div class="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-blue-500 text-white font-bold px-4 py-1 rounded-full text-sm tracking-wide">
              ХИТ ПРОДАЖ
            </div>
            <h3 class="text-2xl font-bold mb-2">Pro</h3>
            <p class="text-slate-500 mb-6">Для профессионального перехвата</p>
            <div class="text-4xl font-extrabold mb-8">299 ₴<span class="text-lg text-slate-400 font-medium">/мес</span></div>
            
            <ul class="space-y-4 mb-8 flex-1">
              <li class="flex items-center gap-3 text-slate-600">
                <svg class="w-5 h-5 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                До 10 активных задач
              </li>
              <li class="flex items-center gap-3 text-slate-600">
                <svg class="w-5 h-5 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                Мгновенная проверка (каждые 5 мин)
              </li>
              <li class="flex items-center gap-3 text-slate-600">
                <svg class="w-5 h-5 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                Фильтр "Только от собственников"
              </li>
            </ul>
            
            <button @click="router.push('/login')" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-xl transition-all shadow-lg shadow-blue-600/30">
              Оформить PRO
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
</script>