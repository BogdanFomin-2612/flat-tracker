import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'

const routes = [
    {
        path: '/',
        name: 'Landing',
        component: () => import('../views/Landing.vue')
    },
    {
        path: '/login',
        name: 'Login',
        component: Login
    },
    {
        path: '/dashboard',
        name: 'Dashboard',
        component: Dashboard
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router