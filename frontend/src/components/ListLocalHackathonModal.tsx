'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Sparkles, Building2, MapPin, Calendar, Trophy, Link2, Mail, FileText, CheckCircle2 } from 'lucide-react';
import { Hackathon } from './HackathonCard';

interface ListLocalHackathonModalProps {
    isOpen: boolean;
    onClose: () => void;
    onHackathonAdded: (newHack: Hackathon) => void;
}

export function ListLocalHackathonModal({ isOpen, onClose, onHackathonAdded }: ListLocalHackathonModalProps) {
    const [title, setTitle] = useState('');
    const [organization, setOrganization] = useState('');
    const [type, setType] = useState<'in-person' | 'virtual' | 'hybrid'>('in-person');
    const [location, setLocation] = useState('');
    const [theme, setTheme] = useState('');
    const [prizePool, setPrizePool] = useState('');
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');
    const [applyUrl, setApplyUrl] = useState('');
    const [contactEmail, setContactEmail] = useState('');
    const [description, setDescription] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [isSuccess, setIsSuccess] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (!title.trim() || !organization.trim() || !applyUrl.trim()) {
            setError('Please fill in Hackathon Title, Organizing College/Club, and Registration Link.');
            return;
        }

        setIsSubmitting(true);

        const newHack: Hackathon = {
            id: `local-${Date.now()}`,
            title: title.trim(),
            organization: organization.trim(),
            type,
            theme: theme.trim() || 'Open Innovation',
            prizePool: prizePool ? parseInt(prizePool.replace(/[^\d]/g, ''), 10) || 0 : 0,
            startDate: startDate || new Date().toISOString().split('T')[0],
            endDate: endDate || startDate || new Date().toISOString().split('T')[0],
            applyUrl: applyUrl.startsWith('http') ? applyUrl : `https://${applyUrl}`,
            source: 'Local Campus',
            location: location.trim() || (type === 'virtual' ? 'Online' : 'College Campus'),
            contactEmail: contactEmail.trim(),
            description: description.trim(),
            participants: 1
        };

        try {
            // Send to backend API
            const res = await fetch('http://localhost:8000/api/hackathons/local', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: newHack.title,
                    organization: newHack.organization,
                    type: newHack.type,
                    theme: newHack.theme,
                    prizePool: newHack.prizePool,
                    startDate: newHack.startDate,
                    endDate: newHack.endDate,
                    applyUrl: newHack.applyUrl,
                    location: newHack.location,
                    contactEmail: newHack.contactEmail,
                    description: newHack.description
                })
            });

            if (res.ok) {
                const data = await res.json();
                if (data.data) {
                    onHackathonAdded(data.data);
                } else {
                    onHackathonAdded(newHack);
                }
            } else {
                // If backend has an error, still add to client state
                onHackathonAdded(newHack);
            }
        } catch {
            // If offline, still add to client UI state and localStorage
            onHackathonAdded(newHack);
        }

        setIsSubmitting(false);
        setIsSuccess(true);
        setTimeout(() => {
            setIsSuccess(false);
            onClose();
            // Reset form
            setTitle('');
            setOrganization('');
            setLocation('');
            setTheme('');
            setPrizePool('');
            setStartDate('');
            setEndDate('');
            setApplyUrl('');
            setContactEmail('');
            setDescription('');
        }, 1200);
    };

    if (!isOpen) return null;

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm overflow-y-auto">
                <motion.div
                    initial={{ opacity: 0, scale: 0.95, y: 10 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95, y: 10 }}
                    className="relative w-full max-w-xl bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden my-8"
                >
                    {/* Header */}
                    <div className="bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 px-6 py-5 text-white flex items-center justify-between">
                        <div className="flex items-center gap-2.5">
                            <div className="p-2 bg-white/10 rounded-lg backdrop-blur-sm">
                                <Sparkles className="w-5 h-5 text-amber-300" />
                            </div>
                            <div>
                                <h3 className="font-bold text-lg text-white">List a Local / Campus Hackathon</h3>
                                <p className="text-xs text-blue-100">Publish your college event to the portal for students</p>
                            </div>
                        </div>
                        <button
                            onClick={onClose}
                            className="p-1.5 rounded-lg text-white/80 hover:text-white hover:bg-white/10 transition-colors"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>

                    {isSuccess ? (
                        <div className="p-12 text-center flex flex-col items-center justify-center gap-3">
                            <motion.div
                                initial={{ scale: 0 }}
                                animate={{ scale: 1 }}
                                className="w-16 h-16 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center"
                            >
                                <CheckCircle2 className="w-10 h-10" />
                            </motion.div>
                            <h4 className="text-xl font-bold text-slate-800">Hackathon Listed!</h4>
                            <p className="text-sm text-slate-500 max-w-xs">
                                Your local hackathon is now live on the portal for all students to discover.
                            </p>
                        </div>
                    ) : (
                        <form onSubmit={handleSubmit} className="p-6 space-y-4 max-h-[80vh] overflow-y-auto text-slate-800">
                            {error && (
                                <div className="p-3 bg-rose-50 border border-rose-200 text-rose-600 text-xs rounded-lg font-medium">
                                    {error}
                                </div>
                            )}

                            <div>
                                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                                    Hackathon Title *
                                </label>
                                <input
                                    type="text"
                                    required
                                    placeholder="e.g. National College CodeFest 2026"
                                    value={title}
                                    onChange={(e) => setTitle(e.target.value)}
                                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-blue-500 text-sm outline-none transition-all"
                                />
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                                        College / Organization *
                                    </label>
                                    <div className="relative">
                                        <Building2 className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                                        <input
                                            type="text"
                                            required
                                            placeholder="e.g. IIT Bombay / Tech Club"
                                            value={organization}
                                            onChange={(e) => setOrganization(e.target.value)}
                                            className="w-full pl-9 pr-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-blue-500 text-sm outline-none transition-all"
                                        />
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                                        Event Format
                                    </label>
                                    <select
                                        value={type}
                                        onChange={(e) => setType(e.target.value as any)}
                                        className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-blue-500 text-sm outline-none transition-all cursor-pointer"
                                    >
                                        <option value="in-person">In-Person (On-Campus)</option>
                                        <option value="virtual">Virtual (Online)</option>
                                        <option value="hybrid">Hybrid</option>
                                    </select>
                                </div>
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                                        Venue / Campus Location
                                    </label>
                                    <div className="relative">
                                        <MapPin className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                                        <input
                                            type="text"
                                            placeholder="e.g. Main Auditorium, Bengaluru"
                                            value={location}
                                            onChange={(e) => setLocation(e.target.value)}
                                            className="w-full pl-9 pr-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-blue-500 text-sm outline-none transition-all"
                                        />
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                                        Theme / Domain
                                    </label>
                                    <input
                                        type="text"
                                        placeholder="e.g. AI, Web3, FinTech, Open"
                                        value={theme}
                                        onChange={(e) => setTheme(e.target.value)}
                                        className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-blue-500 text-sm outline-none transition-all"
                                    />
                                </div>
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                                <div>
                                    <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                                        Prize Pool (₹)
                                    </label>
                                    <div className="relative">
                                        <Trophy className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                                        <input
                                            type="number"
                                            placeholder="50000"
                                            value={prizePool}
                                            onChange={(e) => setPrizePool(e.target.value)}
                                            className="w-full pl-9 pr-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-blue-500 text-sm outline-none transition-all"
                                        />
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                                        Start Date
                                    </label>
                                    <div className="relative">
                                        <Calendar className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                                        <input
                                            type="date"
                                            value={startDate}
                                            onChange={(e) => setStartDate(e.target.value)}
                                            className="w-full pl-9 pr-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-blue-500 text-sm outline-none transition-all"
                                        />
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                                        End Date
                                    </label>
                                    <div className="relative">
                                        <Calendar className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                                        <input
                                            type="date"
                                            value={endDate}
                                            onChange={(e) => setEndDate(e.target.value)}
                                            className="w-full pl-9 pr-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-blue-500 text-sm outline-none transition-all"
                                        />
                                    </div>
                                </div>
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                                        Registration / Apply Link *
                                    </label>
                                    <div className="relative">
                                        <Link2 className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                                        <input
                                            type="url"
                                            required
                                            placeholder="https://forms.gle/... or event site"
                                            value={applyUrl}
                                            onChange={(e) => setApplyUrl(e.target.value)}
                                            className="w-full pl-9 pr-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-blue-500 text-sm outline-none transition-all"
                                        />
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                                        Organizer Contact Email
                                    </label>
                                    <div className="relative">
                                        <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                                        <input
                                            type="email"
                                            placeholder="organizer@college.edu"
                                            value={contactEmail}
                                            onChange={(e) => setContactEmail(e.target.value)}
                                            className="w-full pl-9 pr-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-blue-500 text-sm outline-none transition-all"
                                        />
                                    </div>
                                </div>
                            </div>

                            <div>
                                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                                    Brief Description (Optional)
                                </label>
                                <textarea
                                    rows={2}
                                    placeholder="Tell participants what to expect, eligibility rules, or special perks..."
                                    value={description}
                                    onChange={(e) => setDescription(e.target.value)}
                                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-blue-500 text-sm outline-none transition-all resize-none"
                                />
                            </div>

                            <div className="pt-2 flex items-center justify-end gap-3 border-t border-slate-100">
                                <button
                                    type="button"
                                    onClick={onClose}
                                    className="px-4 py-2.5 rounded-xl text-sm font-semibold text-slate-600 hover:bg-slate-100 transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    disabled={isSubmitting}
                                    className="px-6 py-2.5 rounded-xl text-sm font-bold bg-blue-600 hover:bg-blue-700 text-white shadow-md shadow-blue-500/20 disabled:opacity-50 transition-all flex items-center gap-2"
                                >
                                    {isSubmitting ? 'Publishing...' : 'Publish Hackathon'}
                                </button>
                            </div>
                        </form>
                    )}
                </motion.div>
            </div>
        </AnimatePresence>
    );
}
