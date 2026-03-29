import { useAuthStore } from '../store/authStore'
import { useQuery } from '@tanstack/react-query'
import { authAPI } from '../api/client'
import { User, Mail, Shield, Calendar } from 'lucide-react'

export default function SettingsPage() {
    const user = useAuthStore((s) => s.user)

    const { data: profile } = useQuery({
        queryKey: ['auth', 'me'],
        queryFn: () => authAPI.me().then((r) => r.data),
    })

    const displayUser = profile || user

    return (
        <div className="max-w-2xl mx-auto space-y-8 animate-fade-in">
            <div>
                <h1 className="page-header">Settings</h1>
                <p className="text-gray-400 mt-1">Manage your account</p>
            </div>

            {/* Profile Info */}
            <div className="glass-card p-6 space-y-6">
                <h2 className="text-lg font-semibold text-white">Profile</h2>

                <div className="space-y-4">
                    <div className="flex items-center gap-4 p-4 bg-white/5 rounded-xl">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center">
                            <User className="w-6 h-6 text-white" />
                        </div>
                        <div>
                            <p className="text-sm text-gray-400">Name</p>
                            <p className="text-white font-medium">{displayUser?.name || 'Unknown'}</p>
                        </div>
                    </div>

                    <div className="flex items-center gap-4 p-4 bg-white/5 rounded-xl">
                        <div className="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center">
                            <Mail className="w-6 h-6 text-gray-400" />
                        </div>
                        <div>
                            <p className="text-sm text-gray-400">Email</p>
                            <p className="text-white font-medium">{displayUser?.email || 'Unknown'}</p>
                        </div>
                    </div>

                    <div className="flex items-center gap-4 p-4 bg-white/5 rounded-xl">
                        <div className="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center">
                            <Shield className="w-6 h-6 text-gray-400" />
                        </div>
                        <div>
                            <p className="text-sm text-gray-400">Role</p>
                            <p className="text-white font-medium capitalize">{displayUser?.role || 'user'}</p>
                        </div>
                    </div>

                    <div className="flex items-center gap-4 p-4 bg-white/5 rounded-xl">
                        <div className="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center">
                            <Calendar className="w-6 h-6 text-gray-400" />
                        </div>
                        <div>
                            <p className="text-sm text-gray-400">Member Since</p>
                            <p className="text-white font-medium">
                                {displayUser?.created_at ? new Date(displayUser.created_at).toLocaleDateString() : 'Unknown'}
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* API Keys (placeholder) */}
            <div className="glass-card p-6 space-y-4">
                <h2 className="text-lg font-semibold text-white">Configuration</h2>
                <p className="text-sm text-gray-400">
                    API keys and SMTP settings are configured via environment variables in the backend.
                </p>
                <div className="bg-white/5 rounded-xl p-4 text-sm text-gray-400 font-mono">
                    OPENAI_API_KEY=sk-•••••••••••<br />
                    SENDGRID_API_KEY=SG.•••••••••••<br />
                    SEARCH_API_KEY=•••••••••••
                </div>
            </div>
        </div>
    )
}
