import { useQuery } from '@tanstack/react-query'
import { sponsorAPI } from '../api/client'
import { Building2, Globe, Mail, ExternalLink } from 'lucide-react'
import { useState } from 'react'

export default function SponsorsPage() {
    const [industry, setIndustry] = useState('')

    const { data: sponsors, isLoading } = useQuery({
        queryKey: ['sponsors', industry],
        queryFn: () => sponsorAPI.list({ industry: industry || undefined }).then((r) => r.data),
    })

    return (
        <div className="space-y-6 animate-fade-in">
            <div>
                <h1 className="page-header">Partners Database</h1>
                <p className="text-gray-400 mt-1">A living BD database of every company discovered or contacted</p>
            </div>

            {/* Filter */}
            <div className="flex gap-4">
                <input
                    type="text"
                    placeholder="Filter by industry..."
                    value={industry}
                    onChange={(e) => setIndustry(e.target.value)}
                    className="input-field max-w-xs"
                />
            </div>

            {/* Sponsor Grid */}
            {isLoading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {[1, 2, 3, 4, 5, 6].map((i) => (
                        <div key={i} className="glass-card p-6 h-40 animate-shimmer" />
                    ))}
                </div>
            ) : sponsors?.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {sponsors.map((sponsor) => (
                        <div key={sponsor.id} className="glass-card-hover p-6 space-y-4">
                            <div className="flex items-start gap-4">
                                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500/20 to-indigo-500/20 flex items-center justify-center shrink-0">
                                    <Building2 className="w-6 h-6 text-primary-400" />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <h3 className="font-semibold text-white truncate">{sponsor.name}</h3>
                                    {sponsor.industry && (
                                        <span className="badge-info mt-1">{sponsor.industry}</span>
                                    )}
                                </div>
                            </div>

                            <div className="space-y-2">
                                {sponsor.website && (
                                    <a href={sponsor.website} target="_blank" rel="noopener noreferrer"
                                        className="flex items-center gap-2 text-sm text-gray-400 hover:text-primary-400 transition-colors">
                                        <Globe className="w-4 h-4" />
                                        <span className="truncate">{sponsor.website}</span>
                                        <ExternalLink className="w-3 h-3 shrink-0" />
                                    </a>
                                )}
                                {sponsor.contact_email && (
                                    <div className="flex items-center gap-2 text-sm text-gray-400">
                                        <Mail className="w-4 h-4" />
                                        <span className="truncate">{sponsor.contact_email}</span>
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="glass-card p-16 text-center">
                    <Building2 className="w-16 h-16 mx-auto mb-4 text-gray-600" />
                    <h3 className="text-xl font-semibold text-gray-300 mb-2">No partners yet</h3>
                    <p className="text-gray-500">Run a campaign to discover partners</p>
                </div>
            )}
        </div>
    )
}
