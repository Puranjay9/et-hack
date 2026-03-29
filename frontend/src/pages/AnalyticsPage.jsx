import { useQuery } from '@tanstack/react-query'
import { analyticsAPI } from '../api/client'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts'
import { BarChart3, TrendingUp, Mail, Users } from 'lucide-react'

const COLORS = ['#818cf8', '#34d399', '#fbbf24', '#f87171', '#60a5fa', '#a78bfa']

export default function AnalyticsPage() {
    const { data: campaignStats } = useQuery({
        queryKey: ['analytics', 'campaigns'],
        queryFn: () => analyticsAPI.campaigns().then((r) => r.data),
    })

    const { data: sponsorStats } = useQuery({
        queryKey: ['analytics', 'sponsors'],
        queryFn: () => analyticsAPI.sponsors().then((r) => r.data),
    })

    const chartData = campaignStats?.map((c, i) => ({
        name: c.campaign_goal?.slice(0, 20) || `Campaign ${i + 1}`,
        sent: c.sent || 0,
        opened: c.opened || 0,
        replied: c.replied || 0,
        openRate: c.open_rate || 0,
        evalScore: c.avg_eval_score || 0,
    })) || []

    const industryData = Object.entries(sponsorStats?.by_industry || {}).map(([name, value]) => ({
        name, value,
    }))

    const totalSent = campaignStats?.reduce((a, c) => a + (c.sent || 0), 0) || 0
    const totalOpened = campaignStats?.reduce((a, c) => a + (c.opened || 0), 0) || 0
    const totalReplied = campaignStats?.reduce((a, c) => a + (c.replied || 0), 0) || 0

    return (
        <div className="space-y-8 animate-fade-in">
            <div>
                <h1 className="page-header">Analytics</h1>
                <p className="text-gray-400 mt-1">Track your outreach performance</p>
            </div>

            {/* Summary Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                {[
                    { label: 'Campaigns', value: campaignStats?.length || 0, icon: BarChart3, gradient: 'from-primary-500 to-primary-600' },
                    { label: 'Total Sent', value: totalSent, icon: Mail, gradient: 'from-blue-500 to-cyan-500' },
                    { label: 'Total Opened', value: totalOpened, icon: TrendingUp, gradient: 'from-emerald-500 to-teal-500' },
                    { label: 'Total Replies', value: totalReplied, icon: Users, gradient: 'from-amber-500 to-orange-500' },
                ].map(({ label, value, icon: Icon, gradient }) => (
                    <div key={label} className="glass-card-hover p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-400">{label}</p>
                                <p className="text-3xl font-bold text-white mt-1">{value}</p>
                            </div>
                            <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${gradient} flex items-center justify-center`}>
                                <Icon className="w-6 h-6 text-white" />
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Outreach Performance */}
                <div className="glass-card p-6">
                    <h3 className="font-semibold text-white mb-6">Outreach Performance</h3>
                    {chartData.length > 0 ? (
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={chartData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                                <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} />
                                <YAxis stroke="#94a3b8" fontSize={12} />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: '#1e293b',
                                        border: '1px solid rgba(255,255,255,0.1)',
                                        borderRadius: '12px',
                                        color: '#fff',
                                    }}
                                />
                                <Bar dataKey="sent" fill="#818cf8" radius={[4, 4, 0, 0]} />
                                <Bar dataKey="opened" fill="#34d399" radius={[4, 4, 0, 0]} />
                                <Bar dataKey="replied" fill="#fbbf24" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    ) : (
                        <div className="h-[300px] flex items-center justify-center text-gray-500">No data yet</div>
                    )}
                </div>

                {/* Industry Distribution */}
                <div className="glass-card p-6">
                    <h3 className="font-semibold text-white mb-6">Sponsor Industries</h3>
                    {industryData.length > 0 ? (
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie data={industryData} cx="50%" cy="50%" outerRadius={100} dataKey="value" label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}>
                                    {industryData.map((_, index) => (
                                        <Cell key={index} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: '#fff' }}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                    ) : (
                        <div className="h-[300px] flex items-center justify-center text-gray-500">No data yet</div>
                    )}
                </div>

                {/* Eval Scores Over Time */}
                <div className="glass-card p-6 lg:col-span-2">
                    <h3 className="font-semibold text-white mb-6">AI Email Quality Scores</h3>
                    {chartData.length > 0 ? (
                        <ResponsiveContainer width="100%" height={250}>
                            <LineChart data={chartData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                                <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} />
                                <YAxis stroke="#94a3b8" fontSize={12} domain={[0, 10]} />
                                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: '#fff' }} />
                                <Line type="monotone" dataKey="evalScore" stroke="#818cf8" strokeWidth={3} dot={{ fill: '#818cf8', r: 5 }} />
                            </LineChart>
                        </ResponsiveContainer>
                    ) : (
                        <div className="h-[250px] flex items-center justify-center text-gray-500">No data yet</div>
                    )}
                </div>
            </div>
        </div>
    )
}
