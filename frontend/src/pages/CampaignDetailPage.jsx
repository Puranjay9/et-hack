import { useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { campaignAPI, emailAPI } from '../api/client'
import { useState, useEffect } from 'react'
import toast from 'react-hot-toast'
import {
    Sparkles,
    Mail,
    Send,
    Eye,
    RefreshCw,
    Users,
    BarChart3,
    Loader2,
    CheckCircle2,
    XCircle,
    Clock,
    X,
} from 'lucide-react'

export default function CampaignDetailPage() {
    const { id } = useParams()
    const queryClient = useQueryClient()
    const [activeTab, setActiveTab] = useState('overview')
    const [selectedEmail, setSelectedEmail] = useState(null)
    const [isSendModalOpen, setIsSendModalOpen] = useState(false)
    const [testEmail, setTestEmail] = useState('')

    const { data: campaign, isLoading: campaignLoading } = useQuery({
        queryKey: ['campaign', id],
        queryFn: () => campaignAPI.get(id).then((r) => r.data),
        refetchInterval: (data) => data?.status === 'processing' ? 3000 : false,
    })

    const { data: emails } = useQuery({
        queryKey: ['campaign-emails', id],
        queryFn: () => emailAPI.listByCampaign(id).then((r) => r.data),
        enabled: activeTab === 'emails',
    })

    const generateMutation = useMutation({
        mutationFn: () => campaignAPI.generateOutreach(id),
        onSuccess: () => {
            toast.success('AI agent pipeline started!')
            queryClient.invalidateQueries(['campaign', id])
        },
        onError: (err) => toast.error(err.response?.data?.detail || 'Failed to start generation'),
    })

    const sendMutation = useMutation({
        mutationFn: () => emailAPI.send(id, {}),
        onSuccess: (res) => {
            toast.success(`${res.data.queued} emails queued for sending!`)
            queryClient.invalidateQueries(['campaign-emails', id])
        },
    })

    const sendTestMutation = useMutation({
        mutationFn: () => campaignAPI.sendTest(id, testEmail),
        onSuccess: () => {
            toast.success('Test email queued!')
            setTestEmail('')
        },
        onError: (err) => toast.error(err.response?.data?.detail || 'Failed to send test email')
    })

    const uploadCSVMutation = useMutation({
        mutationFn: (file) => campaignAPI.uploadCSV(id, file),
        onSuccess: (res) => {
            toast.success(`Successfully imported ${res.data.imported} emails!`)
            setIsSendModalOpen(false)
        },
        onError: (err) => toast.error(err.response?.data?.detail || 'Failed to upload CSV')
    })

    if (campaignLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 animate-spin text-primary-400" />
            </div>
        )
    }

    const tabs = [
        { id: 'overview', label: 'Overview', icon: BarChart3 },
        { id: 'emails', label: 'Conversations', icon: Mail },
        { id: 'sponsors', label: 'Partners Database', icon: Users },
    ]

    const statusConfig = {
        draft: { color: 'bg-gray-500/20 text-gray-400', icon: Clock },
        processing: { color: 'bg-amber-500/20 text-amber-400', icon: Loader2, animate: true },
        active: { color: 'bg-emerald-500/20 text-emerald-400', icon: CheckCircle2 },
        completed: { color: 'bg-blue-500/20 text-blue-400', icon: CheckCircle2 },
        failed: { color: 'bg-red-500/20 text-red-400', icon: XCircle },
    }

    const status = statusConfig[campaign?.status] || statusConfig.draft

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div className="flex items-start justify-between">
                <div>
                    <h1 className="page-header">{campaign?.goal || 'Untitled Campaign'}</h1>
                    <div className="flex items-center gap-3 mt-2">
                        <span className={`badge ${status.color}`}>
                            <status.icon className={`w-3 h-3 mr-1 ${status.animate ? 'animate-spin' : ''}`} />
                            {campaign?.status}
                        </span>
                        <span className="text-sm text-gray-400">{campaign?.type || 'General'}</span>
                    </div>
                </div>
                <div className="flex gap-3">
                    {campaign?.status === 'draft' && (
                        <button
                            onClick={() => generateMutation.mutate()}
                            disabled={generateMutation.isPending}
                            className="btn-primary flex items-center gap-2"
                        >
                            <Sparkles className="w-4 h-4" />
                            {generateMutation.isPending ? 'Starting...' : 'Generate Intelligence'}
                        </button>
                    )}
                    {campaign?.status === 'active' && (
                        <>
                            <button
                                onClick={() => setIsSendModalOpen(true)}
                                className="btn-primary flex items-center gap-2"
                            >
                                <Send className="w-4 h-4" />
                                Send Outreach
                            </button>
                            <button onClick={() => generateMutation.mutate()} className="btn-secondary flex items-center gap-2">
                                <RefreshCw className="w-4 h-4" />
                                Regenerate
                            </button>
                        </>
                    )}
                </div>
            </div>

            {/* Agent Progress Tracker */}
            {campaign?.status === 'processing' && (
                <div className="glass-card p-6 border-l-4 border-primary-500">
                    <div className="flex items-center gap-3 mb-4">
                        <Loader2 className="w-5 h-5 animate-spin text-primary-400" />
                        <span className="font-semibold text-white">AI Agents Working...</span>
                    </div>
                    <div className="flex gap-4">
                        {['Strategy', 'Discovery', 'Memory', 'Email Gen', 'Evaluator'].map((agent, i) => (
                            <div key={agent} className="flex items-center gap-2">
                                <div className={`w-3 h-3 rounded-full ${i <= 2 ? 'bg-emerald-400' : i === 3 ? 'bg-amber-400 animate-pulse' : 'bg-gray-600'}`} />
                                <span className="text-sm text-gray-400">{agent}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Tabs */}
            <div className="flex gap-2 border-b border-white/5 pb-0">
                {tabs.map(({ id: tabId, label, icon: Icon }) => (
                    <button
                        key={tabId}
                        onClick={() => setActiveTab(tabId)}
                        className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-all duration-200 -mb-px ${activeTab === tabId
                            ? 'text-primary-400 border-primary-400'
                            : 'text-gray-400 border-transparent hover:text-white'
                            }`}
                    >
                        <Icon className="w-4 h-4" />
                        {label}
                    </button>
                ))}
            </div>

            {/* Tab Content */}
            {activeTab === 'overview' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-slide-up">
                    <div className="glass-card p-6 space-y-4">
                        <h3 className="font-semibold text-white">Campaign Details</h3>
                        <div className="space-y-3">
                            {[
                                { label: 'Target Audience', value: campaign?.target_audience },
                                { label: 'Budget', value: campaign?.budget ? `$${Number(campaign.budget).toLocaleString()}` : 'Not set' },
                                { label: 'Partnership Type', value: campaign?.partnership_type },
                                { label: 'Created', value: new Date(campaign?.created_at).toLocaleString() },
                            ].map(({ label, value }) => (
                                <div key={label} className="flex justify-between">
                                    <span className="text-sm text-gray-400">{label}</span>
                                    <span className="text-sm text-white">{value || 'N/A'}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="glass-card p-6 space-y-4">
                        <h3 className="font-semibold text-white">Outreach Metrics</h3>
                        <div className="grid grid-cols-2 gap-4">
                            {[
                                { label: 'Total', value: campaign?.outreach_count || 0, color: 'text-white' },
                                { label: 'Sent', value: campaign?.sent_count || 0, color: 'text-blue-400' },
                                { label: 'Opened', value: campaign?.opened_count || 0, color: 'text-emerald-400' },
                                { label: 'Replied', value: campaign?.replied_count || 0, color: 'text-amber-400' },
                            ].map(({ label, value, color }) => (
                                <div key={label} className="bg-white/5 rounded-xl p-4">
                                    <p className="text-xs text-gray-400">{label}</p>
                                    <p className={`text-2xl font-bold ${color}`}>{value}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {activeTab === 'emails' && (
                <div className="space-y-4 animate-slide-up">
                    {emails?.length > 0 ? (
                        emails.map((email) => (
                            <div
                                key={email.id}
                                className="glass-card-hover p-6 cursor-pointer"
                                onClick={() => setSelectedEmail(email)}
                            >
                                <div className="flex items-start justify-between">
                                    <div className="flex-1">
                                        <h3 className="font-semibold text-white">{email.subject || 'No subject'}</h3>
                                        <p className="text-sm text-gray-400 mt-1 line-clamp-2">{email.body?.replace(/<[^>]*>/g, '').slice(0, 150)}</p>
                                    </div>
                                    <div className="flex items-center gap-3 ml-4">
                                        {email.eval_score && (
                                            <div className={`px-3 py-1 rounded-lg text-sm font-semibold ${email.eval_score >= 7 ? 'bg-emerald-500/20 text-emerald-400'
                                                : email.eval_score >= 5 ? 'bg-amber-500/20 text-amber-400'
                                                    : 'bg-red-500/20 text-red-400'
                                                }`}>
                                                {email.eval_score.toFixed(1)}
                                            </div>
                                        )}
                                        <span className={`badge ${email.status === 'sent' ? 'badge-success'
                                            : email.status === 'opened' ? 'badge-info'
                                                : email.status === 'replied' ? 'badge-warning'
                                                    : 'bg-white/10 text-gray-400 border border-white/10'
                                            }`}>
                                            {email.status}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        ))
                    ) : (
                        <div className="glass-card p-12 text-center">
                            <Mail className="w-12 h-12 mx-auto mb-4 text-gray-600" />
                            <p className="text-gray-400">No conversations generated yet</p>
                        </div>
                    )}
                </div>
            )}

            {activeTab === 'sponsors' && (
                <div className="glass-card p-12 text-center animate-slide-up">
                    <Users className="w-12 h-12 mx-auto mb-4 text-gray-600" />
                    <p className="text-gray-400">Partners will appear here after generation</p>
                </div>
            )}

            {/* Email Preview Modal */}
            {selectedEmail && (
                <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <div className="glass-card max-w-2xl w-full max-h-[80vh] overflow-y-auto">
                        <div className="p-6 border-b border-white/5 flex items-center justify-between">
                            <h3 className="font-semibold text-white">Conversation Preview</h3>
                            <button onClick={() => setSelectedEmail(null)} className="text-gray-400 hover:text-white">
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                        <div className="p-6 space-y-4">
                            <div>
                                <label className="text-xs text-gray-400 uppercase tracking-wider">Subject</label>
                                <p className="text-white font-medium mt-1">{selectedEmail.subject}</p>
                            </div>
                            <div>
                                <label className="text-xs text-gray-400 uppercase tracking-wider">Body</label>
                                <div className="mt-2 bg-white/5 rounded-xl p-4 text-gray-300 text-sm leading-relaxed"
                                    dangerouslySetInnerHTML={{ __html: selectedEmail.body }} />
                            </div>
                            {selectedEmail.eval_details && Object.keys(selectedEmail.eval_details).length > 0 && (
                                <div>
                                    <label className="text-xs text-gray-400 uppercase tracking-wider">Eval Scores</label>
                                    <div className="grid grid-cols-2 gap-2 mt-2">
                                        {Object.entries(selectedEmail.eval_details).map(([key, val]) => (
                                            <div key={key} className="flex justify-between bg-white/5 rounded-lg px-3 py-2">
                                                <span className="text-xs text-gray-400 capitalize">{key.replace('_', ' ')}</span>
                                                <span className="text-xs font-semibold text-white">{val}/10</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
            {/* Send Options Modal */}
            {isSendModalOpen && (
                <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <div className="glass-card max-w-md w-full">
                        <div className="p-6 border-b border-white/5 flex items-center justify-between">
                            <h3 className="font-semibold text-white flex items-center gap-2">
                                <Send className="w-4 h-4 text-primary-400" />
                                Dispatch Outreach
                            </h3>
                            <button onClick={() => setIsSendModalOpen(false)} className="text-gray-400 hover:text-white">
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                        <div className="p-6 space-y-4">
                            <button
                                onClick={() => {
                                    sendMutation.mutate();
                                    setIsSendModalOpen(false);
                                }}
                                disabled={sendMutation.isPending}
                                className="w-full flex items-center gap-4 p-4 rounded-xl bg-white/5 hover:bg-white/10 transition-colors border border-white/5 text-left"
                            >
                                <div className="w-10 h-10 rounded-lg bg-primary-500/20 flex items-center justify-center shrink-0">
                                    <Sparkles className="w-5 h-5 text-primary-400" />
                                </div>
                                <div>
                                    <p className="font-medium text-white">Send to AI-Discovered Partners</p>
                                    <p className="text-xs text-gray-400 mt-1">Dispatch emails to {campaign?.outreach_count || 0} sponsors found by the AI agent.</p>
                                </div>
                            </button>

                            <button className="w-full flex items-center gap-4 p-4 rounded-xl bg-white/5 hover:bg-white/10 transition-colors border border-white/5 text-left cursor-pointer relative overflow-hidden group">
                                <input
                                    type="file"
                                    className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
                                    accept=".csv"
                                    onChange={(e) => {
                                        const file = e.target.files?.[0];
                                        if (file) uploadCSVMutation.mutate(file);
                                    }}
                                />
                                <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center shrink-0">
                                    {uploadCSVMutation.isPending ? <Loader2 className="w-5 h-5 text-emerald-400 animate-spin" /> : <Users className="w-5 h-5 text-emerald-400" />}
                                </div>
                                <div>
                                    <p className="font-medium text-white group-hover:text-emerald-400 transition-colors">
                                        {uploadCSVMutation.isPending ? 'Uploading...' : 'Upload Custom CSV List'}
                                    </p>
                                    <p className="text-xs text-gray-400 mt-1">Upload a CSV containing explicit names and emails.</p>
                                </div>
                            </button>

                            <div className="border border-white/5 rounded-xl p-4 bg-white/5">
                                <div className="flex items-center gap-2 mb-3">
                                    <Mail className="w-4 h-4 text-blue-400" />
                                    <p className="font-medium text-white text-sm">Send Test Email (Manual)</p>
                                </div>
                                <div className="flex gap-2">
                                    <input
                                        type="email"
                                        value={testEmail}
                                        onChange={(e) => setTestEmail(e.target.value)}
                                        placeholder="name@company.com"
                                        className="input-field text-sm"
                                    />
                                    <button
                                        onClick={() => sendTestMutation.mutate()}
                                        disabled={sendTestMutation.isPending || !testEmail}
                                        className="btn-secondary px-4 text-sm shrink-0 flex items-center gap-2"
                                    >
                                        {sendTestMutation.isPending ? <Loader2 className="w-3 h-3 animate-spin" /> : null}
                                        Blast
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
