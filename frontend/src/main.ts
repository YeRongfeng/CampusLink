import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import { router } from './router'
import './styles.css'
import { useAuthStore } from './stores/auth'
import { configureAuthRequest } from './api/request'

const app = createApp(App)
app.use(createPinia())
const auth = useAuthStore()
configureAuthRequest({
  getToken: () => auth.token,
  onUnauthorized: (requestToken) => {
    if (auth.token !== requestToken) return
    auth.logout()
    const route = router.currentRoute.value
    if (route.meta.requiresAuth) {
      void router.replace({ path: '/login', query: { redirect: route.fullPath, reason: 'expired' } })
    }
  },
})
app.use(router).mount('#app')
