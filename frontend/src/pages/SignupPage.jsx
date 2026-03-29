import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { authAPI } from '../api/client'
import toast from 'react-hot-toast'
import { Sparkles, Mail, Lock, User } from 'lucide-react'

export default function SignupPage() {
    const [name, setName] = useState('')
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [loading, setLoading] = useState(false)
    const navigate = useNavigate()

    const handleSignup = async (e) => {
        e.preventDefault()
        setLoading(true)
        try {
            await authAPI.signup({ name, email, password })
            toast.success('Account created! Please sign in.')
            navigate('/login')
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Signup failed')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
            <div className="absolute inset-0">
                <div className="absolute top-1/3 right-1/3 w-96 h-96 bg-primary-600/20 rounded-full blur-3xl animate-pulse-slow" />
                <div className="absolute bottom-1/3 left-1/3 w-96 h-96 bg-emerald-600/15 rounded-full blur-3xl animate-pulse-slow" />
            </div>

            <div className="relative z-10 w-full max-w-md mx-4">
                <div className="text-center mb-8 animate-fade-in">
                    <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center mx-auto mb-4 shadow-lg shadow-primary-500/25">
                        <Sparkles className="w-8 h-8 text-white" />
                    </div>
                    <h1 className="text-3xl font-bold text-white">Create Account</h1>
                    <p className="text-gray-400 mt-2">Start your Intelligent Outreach Engine</p>
                </div>

                <form onSubmit={handleSignup} className="glass-card p-8 space-y-6 animate-slide-up">
                    <div>
                        <label className="block text-sm font-medium text-gray-400 mb-2">Name</label>
                        <div className="relative">
                            <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                            <input
                                id="signup-name"
                                type="text"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                className="input-field pl-12"
                                placeholder="Your name"
                                required
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-400 mb-2">Email</label>
                        <div className="relative">
                            <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                            <input
                                id="signup-email"
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="input-field pl-12"
                                placeholder="you@example.com"
                                required
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-400 mb-2">Password</label>
                        <div className="relative">
                            <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                            <input
                                id="signup-password"
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="input-field pl-12"
                                placeholder="Min. 6 characters"
                                minLength={6}
                                required
                            />
                        </div>
                    </div>

                    <button id="signup-submit" type="submit" disabled={loading} className="btn-primary w-full">
                        {loading ? (
                            <span className="flex items-center justify-center gap-2">
                                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                Creating...
                            </span>
                        ) : (
                            'Create Account'
                        )}
                    </button>

                    <p className="text-center text-gray-500 text-sm">
                        Already have an account?{' '}
                        <Link to="/login" className="text-primary-400 hover:text-primary-300 font-medium">
                            Sign in
                        </Link>
                    </p>
                </form>
            </div>
        </div>
    )
}
