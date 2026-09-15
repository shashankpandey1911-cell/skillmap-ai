import { AuthProvider } from './auth/AuthContext'
import { AppRouter } from './router/AppRouter'
import { ToastProvider } from './components/ui'

export default function App() {
  return (
    <ToastProvider>
      <AuthProvider>
        <AppRouter />
      </AuthProvider>
    </ToastProvider>
  )
}