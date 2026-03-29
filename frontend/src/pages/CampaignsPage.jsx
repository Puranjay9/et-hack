import { useQuery } from '@tanstack/react-query'
import { campaignAPI } from '../api/client'
import { Link } from 'react-router-dom'
import { Plus, Megaphone, Filter } from 'lucide-react'
import { useState } from 'react'

export default function CampaignsPage() {
    const [statusFilter, setStatusFilter] = useState('')

    const { data: campaigns, isLoading } = useQuery({
        queryKey: ['campaigns', statusFilter],
        queryFn: () =>
            campaignAPI.list({ status_filter: statusFilter || undefined }).then((r) => r.data),
    })

    const statuses = ['', 'draft', 'active', 'processing', 'completed', 'failed']

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="page-header">Campaigns</h1>
                    <p className="text-gray-400 mt-1">Manage your intelligent outreach campaigns</p>
                </div>
                <Link to="/campaigns/new" className="btn-primary flex items-center gap-2">
                    <Plus className="w-4 h-4" />
                    New Campaign
                </Link>
            </div>

            {/* Filters */}
            <div className="flex gap-2">
                {statuses.map((s) => (
                    <button
                        key={s}
                        onClick={() => setStatusFilter(s)}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${statusFilter === s
                            ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
                            : 'text-gray-400 hover:text-white hover:bg-white/5 border border-transparent'
                            }`}
                    >
                        {s === '' ? 'All' : s.charAt(0).toUpperCase() + s.slice(1)}
                    </button>
                ))}
            </div>

            {/* Campaign Grid */}
            {isLoading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {[1, 2, 3].map((i) => (
                        <div key={i} className="glass-card p-6 animate-shimmer h-48" />
                    ))}
                </div>
            ) : campaigns?.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {campaigns.map((campaign) => (
                        <Link
                            key={campaign.id}
                            to={`/campaigns/${campaign.id}`}
                            className="glass-card-hover p-6 space-y-4"
                        >
                            <div className="flex items-start justify-between">
                                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500/20 to-purple-500/20 flex items-center justify-center">
                                    <Megaphone className="w-5 h-5 text-primary-400" />
                                </div>
                                <span
                                    className={`badge ${campaign.status === 'active'
                                        ? 'badge-success'
                                        : campaign.status === 'processing'
                                            ? 'badge-warning'
                                            : campaign.status === 'completed'
                                                ? 'badge-info'
                                                : campaign.status === 'failed'
                                                    ? 'badge-danger'
                                                    : 'bg-white/10 text-gray-400 border border-white/10'
                                        }`}
                                >
                                    {campaign.status}
                                </span>
                            </div>

                            <div>
                                <h3 className="font-semibold text-white text-lg">
                                    {campaign.goal || 'Untitled Campaign'}
                                </h3>
                                <p className="text-sm text-gray-400 mt-1 line-clamp-2">
                                    {campaign.type || 'General'} · {campaign.target_audience || 'No audience set'}
                                </p>
                            </div>

                            <div className="flex items-center justify-between text-xs text-gray-500 pt-2 border-t border-white/5">
                                <span>{new Date(campaign.created_at).toLocaleDateString()}</span>
                                {campaign.budget && <span>${Number(campaign.budget).toLocaleString()}</span>}
                            </div>
                        </Link>
                    ))}
                </div>
            ) : (
                <div className="glass-card p-16 text-center">
                    <Megaphone className="w-16 h-16 mx-auto mb-4 text-gray-600" />
                    <h3 className="text-xl font-semibold text-gray-300 mb-2">No campaigns yet</h3>
                    <p className="text-gray-500 mb-6">Create your first intelligent outreach campaign</p>
                    <Link to="/campaigns/new" className="btn-primary">
                        <Plus className="w-4 h-4 inline mr-2" />
                        Create Campaign
                    </Link>
                </div>
            )}
        </div>
    )
}
