import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import {
    LayoutDashboard,
    Megaphone,
    BarChart3,
    Users,
    Settings,
    LogOut,
    Sparkles,
} from 'lucide-react'

const navItems = [
    { to: '/dashboard', icon: LayoutDashboard, label: 'Mission Control' },
    { to: '/campaigns', icon: Megaphone, label: 'Campaigns' },
    { to: '/analytics', icon: BarChart3, label: 'Analytics' },
    { to: '/sponsors', icon: Users, label: 'Partners/Sponsors' },
    { to: '/settings', icon: Settings, label: 'Settings' },
]

export default function Layout() {
    const navigate = useNavigate()
    const logout = useAuthStore((s) => s.logout)

    const handleLogout = () => {
        logout()
        navigate('/login')
    }

    return (
        <div className="flex h-screen overflow-hidden">
            {/* Sidebar */}
            <aside className="w-64 bg-surface-800/50 backdrop-blur-xl border-r border-white/5 flex flex-col">
                {/* Logo */}
                <div className="p-6 border-b border-white/5">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center">
                            <Sparkles className="w-5 h-5 text-white" />
                        </div>
                        <div>
                            <h1 className="font-bold text-lg text-white">Altior IQ</h1>
                            <p className="text-xs text-gray-500">Intelligent Outreach Engine</p>
                        </div>
                    </div>
                </div>

                {/* Nav */}
                <nav className="flex-1 p-4 space-y-1">
                    {navItems.map(({ to, icon: Icon, label }) => (
                        <NavLink
                            key={to}
                            to={to}
                            className={({ isActive }) =>
                                `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${isActive
                                    ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
                                    : 'text-gray-400 hover:text-white hover:bg-white/5'
                                }`
                            }
                        >
                            <Icon className="w-5 h-5" />
                            {label}
                        </NavLink>
                    ))}
                </nav>

                {/* Logout */}
                <div className="p-4 border-t border-white/5">
                    <button onClick={handleLogout} className="btn-ghost w-full flex items-center gap-3 justify-start">
                        <LogOut className="w-5 h-5" />
                        Logout
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-y-auto">
                <div className="p-8 max-w-7xl mx-auto">
                    <Outlet />
                </div>
            </main>
        </div>
    )
}
