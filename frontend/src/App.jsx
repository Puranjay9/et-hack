import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Layout from './components/Layout'
import LoginPage from './pages/LoginPage'
import SignupPage from './pages/SignupPage'
import DashboardPage from './pages/DashboardPage'
import CampaignsPage from './pages/CampaignsPage'
import CampaignNewPage from './pages/CampaignNewPage'
import CampaignDetailPage from './pages/CampaignDetailPage'
import AnalyticsPage from './pages/AnalyticsPage'
import SponsorsPage from './pages/SponsorsPage'
import SettingsPage from './pages/SettingsPage'

function ProtectedRoute({ children }) {
    const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
    if (!isAuthenticated) return <Navigate to="/login" replace />
    return children
}

function App() {
    return (
        <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />
            <Route
                path="/"
                element={
                    <ProtectedRoute>
                        <Layout />
                    </ProtectedRoute>
                }
            >
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="dashboard" element={<DashboardPage />} />
                <Route path="campaigns" element={<CampaignsPage />} />
                <Route path="campaigns/new" element={<CampaignNewPage />} />
                <Route path="campaigns/:id" element={<CampaignDetailPage />} />
                <Route path="analytics" element={<AnalyticsPage />} />
                <Route path="sponsors" element={<SponsorsPage />} />
                <Route path="settings" element={<SettingsPage />} />
            </Route>
        </Routes>
    )
}

export default App
