import { Navigate, Outlet, Route, Routes } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { RequireAuth, RequireRole, roleHome } from '../auth/guards'
import { AppLayout } from '../components/layout'
import { FeaturePlaceholder } from '../pages/common/FeaturePlaceholder'
import { NotFound } from '../pages/common/NotFound'
import { Login } from '../pages/auth/Login'
import { Register } from '../pages/auth/Register'
import { ForgotPassword } from '../pages/auth/ForgotPassword'
import { ResetPassword } from '../pages/auth/ResetPassword'
import { VerifyEmail } from '../pages/auth/VerifyEmail'
import {
  adminRoutes,
  professorRoutes,
  studentRoutes,
  type RouteMeta,
} from './routes'

/** Renders the real page when implemented, otherwise its phase placeholder. */
function roleRoutes(metas: RouteMeta[]) {
  return metas.map((meta) => {
    const Page = meta.page
    return (
      <Route
        key={meta.path}
        path={meta.path}
        element={Page ? <Page /> : <FeaturePlaceholder meta={meta} />}
      />
    )
  })
}

export function AppRouter() {
  const { user, loading } = useAuth()

  // Root: go to the authenticated user's dashboard, or the login page.
  const rootRedirect = () => {
    if (loading) return null
    if (!user) return <Navigate to="/auth/login" replace />
    return <Navigate to={roleHome[user.role]} replace />
  }

  return (
    <Routes>
      {/* Public */}
      <Route path="/auth/login" element={<Login />} />
      <Route path="/auth/register" element={<Register />} />
      <Route path="/auth/forgot-password" element={<ForgotPassword />} />
      <Route path="/auth/reset-password" element={<ResetPassword />} />
      <Route path="/auth/verify-email" element={<VerifyEmail />} />

      {/* Authenticated shell, role-scoped inside */}
      <Route
        element={
          <RequireAuth>
            <AppLayout />
          </RequireAuth>
        }
      >
        <Route element={<RequireRole role="STUDENT" ><Outlet /></RequireRole>}>
          {roleRoutes(studentRoutes)}
        </Route>
        <Route element={<RequireRole role="PROFESSOR"><Outlet /></RequireRole>}>
          {roleRoutes(professorRoutes)}
        </Route>
        <Route element={<RequireRole role="ADMIN"><Outlet /></RequireRole>}>
          {roleRoutes(adminRoutes)}
        </Route>
      </Route>

      <Route path="/" element={rootRedirect()} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}
