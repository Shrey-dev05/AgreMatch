'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Users, Sparkles, CheckCircle2, MessageSquare, Send } from 'lucide-react';
import { Hackathon } from './HackathonCard';

interface TeamUpModalProps {
    isOpen: boolean;
    onClose: () => void;
    hackathon: Hackathon | null;
}

export function TeamUpModal({ isOpen, onClose, hackathon }: TeamUpModalProps) {
    const [role, setRole] = useState('Frontend Developer');
    const [skills, setSkills] = useState('');
    const [contact, setContact] = useState('');
    const [message, setMessage] = useState('');
    const [isSubmitted, setIsSubmitted] = useState(false);

    if (!isOpen || !hackathon) return null;

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitted(true);
        setTimeout(() => {
            setIsSubmitted(false);
            onClose();
        }, 2200);
    };

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    className="relative w-full max-w-lg bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden text-slate-800"
                >
                    <div className="bg-gradient-to-r from-indigo-600 to-blue-600 px-6 py-5 text-white flex items-center justify-between">
                        <div className="flex items-center gap-2.5">
                            <div className="p-2 bg-white/10 rounded-lg">
                                <Users className="w-5 h-5 text-white" />
                            </div>
                            <div>
                                <h3 className="font-bold text-lg text-white">Find a Teammate</h3>
                                <p className="text-xs text-indigo-100 truncate max-w-xs">{hackathon.title}</p>
                            </div>
                        </div>
                        <button onClick={onClose} className="p-1.5 rounded-lg text-white/80 hover:text-white hover:bg-white/10">
                            <X className="w-5 h-5" />
                        </button>
                    </div>

                    {isSubmitted ? (
                        <div className="p-8 text-center flex flex-col items-center justify-center gap-3">
                            <div className="w-14 h-14 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center">
                                <CheckCircle2 className="w-8 h-8" />
                            </div>
                            <h4 className="text-lg font-bold text-slate-800">Match Request Broadcasted!</h4>
                            <p className="text-sm text-slate-500 max-w-sm">
                                Your profile has been added to the matchmaking pool for <strong>{hackathon.title}</strong>. Compatible builders will be notified!
                            </p>
                        </div>
                    ) : (
                        <form onSubmit={handleSubmit} className="p-6 space-y-4">
                            <div>
                                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                                    Your Primary Role
                                </label>
                                <select
                                    value={role}
                                    onChange={(e) => setRole(e.target.value)}
                                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-blue-500 text-sm outline-none cursor-pointer"
                                >
                                    <option value="Frontend Developer">Frontend Developer (React, Next.js, Tailwind)</option>
                                    <option value="Backend Developer">Backend Developer (Python, Node.js, Go, DB)</option>
                                    <option value="AI / ML Engineer">AI / ML Engineer (PyTorch, LLMs, LangChain)</option>
                                    <option value="Full Stack Developer">Full Stack Generalist</option>
                                    <option value="UI/UX Designer">UI/UX Designer (Figma, Prototyping)</option>
                                    <option value="Pitch & Product Manager">Pitch Lead & Product Manager</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                                    Your Key Skills & Tech Stack
                                </label>
                                <input
                                    type="text"
                                    required
                                    placeholder="e.g. Next.js, Python, PostgreSQL, Gemini API"
                                    value={skills}
                                    onChange={(e) => setSkills(e.target.value)}
                                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-blue-500 text-sm outline-none"
                                />
                            </div>

                            <div>
                                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                                    Discord / Telegram / Email to Connect
                                </label>
                                <input
                                    type="text"
                                    required
                                    placeholder="e.g. @shrey_dev or student@college.edu"
                                    value={contact}
                                    onChange={(e) => setContact(e.target.value)}
                                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-blue-500 text-sm outline-none"
                                />
                            </div>

                            <div>
                                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                                    What are you looking for in a partner?
                                </label>
                                <textarea
                                    rows={2}
                                    placeholder="e.g. Looking for a backend coder or an AI dev to build an agentic project together!"
                                    value={message}
                                    onChange={(e) => setMessage(e.target.value)}
                                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-blue-500 text-sm outline-none resize-none"
                                />
                            </div>

                            <div className="pt-2 flex items-center justify-end gap-3 border-t border-slate-100">
                                <button
                                    type="button"
                                    onClick={onClose}
                                    className="px-4 py-2 rounded-xl text-sm font-semibold text-slate-600 hover:bg-slate-100"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="px-5 py-2.5 rounded-xl text-sm font-bold bg-indigo-600 hover:bg-indigo-700 text-white shadow-md shadow-indigo-500/20 flex items-center gap-2"
                                >
                                    <Send className="w-4 h-4" />
                                    Post Match Request
                                </button>
                            </div>
                        </form>
                    )}
                </motion.div>
            </div>
        </AnimatePresence>
    );
}
