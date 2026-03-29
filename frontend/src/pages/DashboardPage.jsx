import { useQuery } from '@tanstack/react-query'
import { campaignAPI, analyticsAPI } from '../api/client'
import { Link } from 'react-router-dom'
import {
    Megaphone,
    Users,
    Mail,
    TrendingUp,
    ArrowRight,
    Sparkles,
} from 'lucide-react'

export default function DashboardPage() {
    const { data: campaigns } = useQuery({
        queryKey: ['campaigns'],
        queryFn: () => campaignAPI.list().then((r) => r.data),
    })

    const { data: sponsorStats } = useQuery({
        queryKey: ['analytics', 'sponsors'],
        queryFn: () => analyticsAPI.sponsors().then((r) => r.data),
    })

    const { data: campaignStats } = useQuery({
        queryKey: ['analytics', 'campaigns'],
        queryFn: () => analyticsAPI.campaigns().then((r) => r.data),
    })

    const totalCampaigns = campaigns?.length || 0
    const totalSponsors = sponsorStats?.total_sponsors || 0
    const totalSent = campaignStats?.reduce((acc, c) => acc + (c.sent || 0), 0) || 0
    const totalReplied = campaignStats?.reduce((acc, c) => acc + (c.replied || 0), 0) || 0
    const responseRate = totalSent > 0 ? ((totalReplied / totalSent) * 100).toFixed(1) : '0.0'

    const stats = [
        {
            label: 'Active Campaigns',
            value: totalCampaigns,
            icon: Megaphone,
            gradient: 'from-blue-500 to-cyan-500',
            glow: 'shadow-blue-500/20',
        },
        {
            label: 'Sponsors Found',
            value: totalSponsors,
            icon: Users,
            gradient: 'from-emerald-500 to-teal-500',
            glow: 'shadow-emerald-500/20',
        },
        {
            label: 'Emails Sent',
            value: totalSent,
            icon: Mail,
            gradient: 'from-purple-500 to-pink-500',
            glow: 'shadow-purple-500/20',
        },
        {
            label: 'Response Rate',
            value: `${responseRate}%`,
            icon: TrendingUp,
            gradient: 'from-amber-500 to-orange-500',
            glow: 'shadow-amber-500/20',
        },
    ]

    return (
        <div className="space-y-8 animate-fade-in">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="page-header">Mission Control</h1>
                    <p className="text-gray-400 mt-1">From Noise to Signal: The New Standard for B2B & Student Outreach</p>
                </div>
                <Link to="/campaigns/new" className="btn-primary flex items-center gap-2">
                    <Sparkles className="w-4 h-4" />
                    New Campaign
                </Link>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {stats.map(({ label, value, icon: Icon, gradient, glow }) => (
                    <div key={label} className={`glass-card-hover p-6 ${glow} shadow-lg`}>
                        <div className="flex items-start justify-between">
                            <div>
                                <p className="text-sm text-gray-400 font-medium">{label}</p>
                                <p className="text-3xl font-bold mt-2 text-white">{value}</p>
                            </div>
                            <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${gradient} flex items-center justify-center shadow-lg`}>
                                <Icon className="w-6 h-6 text-white" />
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Recent Campaigns */}
            <div className="glass-card">
                <div className="p-6 border-b border-white/5 flex items-center justify-between">
                    <h2 className="text-lg font-semibold text-white">Recent Activity Feed</h2>
                    <Link to="/campaigns" className="btn-ghost text-sm flex items-center gap-1">
                        View All <ArrowRight className="w-4 h-4" />
                    </Link>
                </div>
                <div className="divide-y divide-white/5">
                    {campaigns?.slice(0, 5).map((campaign) => (
                        <Link
                            key={campaign.id}
                            to={`/campaigns/${campaign.id}`}
                            className="flex items-center justify-between p-6 hover:bg-white/5 transition-colors"
                        >
                            <div>
                                <p className="font-medium text-white">{campaign.goal || 'Untitled Campaign'}</p>
                                <p className="text-sm text-gray-400 mt-1">
                                    {campaign.type || 'General'} · Created {new Date(campaign.created_at).toLocaleDateString()}
                                </p>
                            </div>
                            <span
                                className={`badge ${campaign.status === 'active'
                                    ? 'badge-success'
                                    : campaign.status === 'processing'
                                        ? 'badge-warning'
                                        : campaign.status === 'completed'
                                            ? 'badge-info'
                                            : 'bg-white/10 text-gray-400 border border-white/10'
                                    }`}
                            >
                                {campaign.status}
                            </span>
                        </Link>
                    )) || (
                            <div className="p-12 text-center text-gray-500">
                                <Megaphone className="w-12 h-12 mx-auto mb-4 opacity-30" />
                                <p>No campaigns yet</p>
                                <Link to="/campaigns/new" className="text-primary-400 text-sm mt-2 inline-block hover:underline">
                                    Create your first campaign
                                </Link>
                            </div>
                        )}
                </div>
            </div>
        </div>
    )
}
