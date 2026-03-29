import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { useMutation } from '@tanstack/react-query'
import { campaignAPI } from '../api/client'
import toast from 'react-hot-toast'
import { ChevronRight, ChevronLeft, Check, Sparkles } from 'lucide-react'

const steps = [
    { id: 1, title: 'DNA Basics', desc: 'Campaign details' },
    { id: 2, title: 'Target Audience', desc: 'Target demographics' },
    { id: 3, title: 'Value Exchange', desc: 'What you offer sponsors' },
    { id: 4, title: 'Campaign Intent', desc: 'Campaign objectives' },
    { id: 5, title: 'Review', desc: 'Confirm & launch' },
]

export default function CampaignNewPage() {
    const [step, setStep] = useState(1)
    const navigate = useNavigate()
    const { register, handleSubmit, watch, getValues } = useForm({
        defaultValues: {
            type: '',
            goal: '',
            target_audience: '',
            budget: '',
            partnership_type: 'sponsorship',
            target_sponsor_profile: {},
            offerings: {},
            offerings_text: '',
            sponsor_industries: '',
        },
    })

    const createMutation = useMutation({
        mutationFn: (data) => campaignAPI.create(data),
        onSuccess: (res) => {
            toast.success('Campaign created!')
            navigate(`/campaigns/${res.data.id}`)
        },
        onError: (err) => {
            toast.error(err.response?.data?.detail || 'Failed to create campaign')
        },
    })

    const onSubmit = (data) => {
        createMutation.mutate({
            type: data.type,
            goal: data.goal,
            target_audience: data.target_audience,
            budget: data.budget ? parseFloat(data.budget) : null,
            partnership_type: data.partnership_type,
            target_sponsor_profile: {
                industries: data.sponsor_industries?.split(',').map((s) => s.trim()).filter(Boolean),
            },
            offerings: {
                description: data.offerings_text,
            },
        })
    }

    const values = watch()

    return (
        <div className="max-w-3xl mx-auto space-y-8 animate-fade-in">
            <div>
                <h1 className="page-header">Create Campaign</h1>
                <p className="text-gray-400 mt-1">Build the "AI Brain" of your organization</p>
            </div>

            {/* Step indicator */}
            <div className="flex items-center gap-2">
                {steps.map(({ id, title }) => (
                    <div key={id} className="flex items-center gap-2">
                        <button
                            onClick={() => id < step && setStep(id)}
                            className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all duration-300 ${id === step
                                ? 'bg-primary-500 text-white shadow-lg shadow-primary-500/25'
                                : id < step
                                    ? 'bg-emerald-500/20 text-emerald-400'
                                    : 'bg-white/5 text-gray-500'
                                }`}
                        >
                            {id < step ? <Check className="w-4 h-4" /> : id}
                        </button>
                        <span className={`text-sm hidden sm:inline ${id === step ? 'text-white' : 'text-gray-500'}`}>
                            {title}
                        </span>
                        {id < steps.length && <ChevronRight className="w-4 h-4 text-gray-600" />}
                    </div>
                ))}
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="glass-card p-8">
                {/* Step 1: Basic Info */}
                {step === 1 && (
                    <div className="space-y-6 animate-slide-up">
                        <h2 className="text-xl font-semibold text-white">Company & Profile DNA</h2>
                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-2">Event/Campaign Type</label>
                            <select {...register('type')} className="input-field">
                                <option value="">Select type...</option>
                                <option value="hackathon">Hackathon</option>
                                <option value="tech-fest">Tech Fest</option>
                                <option value="cultural-fest">Cultural Fest</option>
                                <option value="sports-event">Sports Event</option>
                                <option value="workshop">Workshop Series</option>
                                <option value="conference">Conference</option>
                                <option value="other">Other</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-2">Budget Goal ($)</label>
                            <input {...register('budget')} type="number" className="input-field" placeholder="25000" />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-2">Partnership Type</label>
                            <select {...register('partnership_type')} className="input-field">
                                <option value="sponsorship">Cash Sponsorship</option>
                                <option value="in-kind">In-Kind Sponsorship</option>
                                <option value="media">Media Partnership</option>
                                <option value="mixed">Mixed</option>
                            </select>
                        </div>
                    </div>
                )}

                {/* Step 2: Audience */}
                {step === 2 && (
                    <div className="space-y-6 animate-slide-up">
                        <h2 className="text-xl font-semibold text-white">Target Audience</h2>
                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-2">Describe your audience</label>
                            <textarea
                                {...register('target_audience')}
                                className="input-field h-32 resize-none"
                                placeholder="e.g., 5000+ engineering students from top universities, primarily interested in AI/ML and web development..."
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-2">Target sponsor industries</label>
                            <input
                                {...register('sponsor_industries')}
                                className="input-field"
                                placeholder="technology, finance, education (comma-separated)"
                            />
                        </div>
                    </div>
                )}

                {/* Step 3: Offerings */}
                {step === 3 && (
                    <div className="space-y-6 animate-slide-up">
                        <h2 className="text-xl font-semibold text-white">Value Exchange</h2>
                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-2">
                                What do you offer the recipient? (Visibility, User Access, Data Insights...)
                            </label>
                            <textarea
                                {...register('offerings_text')}
                                className="input-field h-48 resize-none"
                                placeholder="e.g., Logo placement on all materials, booth space at venue, speaking slot, social media promotion with 50K+ reach..."
                            />
                        </div>
                    </div>
                )}

                {/* Step 4: Goals */}
                {step === 4 && (
                    <div className="space-y-6 animate-slide-up">
                        <h2 className="text-xl font-semibold text-white">Campaign Intent</h2>
                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-2">Campaign name/goal</label>
                            <textarea
                                {...register('goal')}
                                className="input-field h-32 resize-none"
                                placeholder="e.g., Secure 10 sponsors for TechFest 2026 — aiming for $50K total sponsorship with a mix of platinum and gold tiers..."
                            />
                        </div>
                    </div>
                )}

                {/* Step 5: Review */}
                {step === 5 && (
                    <div className="space-y-6 animate-slide-up">
                        <h2 className="text-xl font-semibold text-white">Review & Create</h2>
                        <div className="space-y-4">
                            {[
                                { label: 'Type', value: values.type || 'Not set' },
                                { label: 'Budget', value: values.budget ? `$${Number(values.budget).toLocaleString()}` : 'Not set' },
                                { label: 'Partnership', value: values.partnership_type },
                                { label: 'Audience', value: values.target_audience || 'Not set' },
                                { label: 'Goal', value: values.goal || 'Not set' },
                            ].map(({ label, value }) => (
                                <div key={label} className="flex gap-4 p-4 bg-white/5 rounded-xl">
                                    <span className="text-gray-400 text-sm w-24 shrink-0">{label}</span>
                                    <span className="text-white text-sm">{value}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Navigation */}
                <div className="flex items-center justify-between mt-8 pt-6 border-t border-white/5">
                    <button
                        type="button"
                        onClick={() => setStep(Math.max(1, step - 1))}
                        className={`btn-secondary flex items-center gap-2 ${step === 1 ? 'invisible' : ''}`}
                    >
                        <ChevronLeft className="w-4 h-4" />
                        Back
                    </button>

                    {step < 5 ? (
                        <button type="button" onClick={() => setStep(step + 1)} className="btn-primary flex items-center gap-2">
                            Next
                            <ChevronRight className="w-4 h-4" />
                        </button>
                    ) : (
                        <button type="submit" disabled={createMutation.isPending} className="btn-primary flex items-center gap-2">
                            <Sparkles className="w-4 h-4" />
                            {createMutation.isPending ? 'Creating...' : 'Create Campaign'}
                        </button>
                    )}
                </div>
            </form>
        </div>
    )
}
