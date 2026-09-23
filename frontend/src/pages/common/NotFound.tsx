import { Link } from 'react-router-dom'
import { Button, Card } from '../../components/ui'
import { useAuth } from '../../auth/AuthContext'
import { roleHome } from '../../auth/guards'

export function NotFound() {
  const { user } = useAuth()
  const home = user ? roleHome[user.role] : '/auth/login'

  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <Card className="max-w-md text-center">
        <p className="text-5xl font-bold text-brand-700">404</p>
        <h1 className="mt-3 text-lg font-semibold text-slate-900">Page not found</h1>
        <p className="mt-2 text-sm text-slate-500">
          The page you are looking for doesn't exist or has moved.
        </p>
        <Link to={home} className="mt-5 inline-block">
          <Button>Back to dashboard</Button>
        </Link>
      </Card>
    </div>
  )
}
