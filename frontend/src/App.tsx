import { Navigate, Route, Routes } from 'react-router-dom'
import { AdminLayout } from './admin/AdminLayout'
import { AdminRoute } from './admin/AdminRoute'
import { ProtectedRoute } from './auth/ProtectedRoute'
import { AppLayout } from './layout/AppLayout'
import { AccountPage } from './pages/AccountPage'
import { AdminCategoriesPage } from './pages/admin/AdminCategoriesPage'
import { AdminEventPage } from './pages/admin/AdminEventPage'
import { AdminModerationPage } from './pages/admin/AdminModerationPage'
import { AdminOverviewPage } from './pages/admin/AdminOverviewPage'
import { AdminParticipantsPage } from './pages/admin/AdminParticipantsPage'
import { HomePage } from './pages/HomePage'
import { LoginPage } from './pages/LoginPage'
import { MyMemoriesPage } from './pages/MyMemoriesPage'
import { MyResultsPage } from './pages/MyResultsPage'
import { PeopleListPage } from './pages/PeopleListPage'
import { RatingPage } from './pages/RatingPage'

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<AdminRoute />}>
          <Route element={<AdminLayout />}>
            <Route path="/admin" element={<Navigate to="/admin/overview" replace />} />
            <Route path="/admin/overview" element={<AdminOverviewPage />} />
            <Route path="/admin/participants" element={<AdminParticipantsPage />} />
            <Route path="/admin/categories" element={<AdminCategoriesPage />} />
            <Route path="/admin/event" element={<AdminEventPage />} />
            <Route path="/admin/moderation" element={<AdminModerationPage />} />
          </Route>
        </Route>
        <Route path="/rate/:targetId" element={<RatingPage />} />
        <Route element={<AppLayout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/people" element={<PeopleListPage />} />
          <Route path="/results" element={<MyResultsPage />} />
          <Route path="/memories" element={<MyMemoriesPage />} />
          <Route path="/account" element={<AccountPage />} />
        </Route>
      </Route>
    </Routes>
  )
}

export default App
