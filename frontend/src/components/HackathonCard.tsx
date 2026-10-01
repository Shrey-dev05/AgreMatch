'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ExternalLink, Calendar, MapPin, Trophy, Users, Bookmark, Sparkles, Building2 } from 'lucide-react';

export type Hackathon = {
    id: string;
    title: string;
    organization: string;
    type: 'virtual' | 'in-person' | 'hybrid';
    theme: string;
    prizePool: number | string;
    startDate: string;
    endDate: string;
    applyUrl: string;
    source: string;
    location?: string;
    participants?: number;
    contactEmail?: string;
    description?: string;
    matchScore?: number;
    matchExplanation?: string;
};

interface HackathonCardProps {
    hackathon: Hackathon;
    onTeamUp?: (hackathon: Hackathon) => void;
    isBookmarked?: boolean;
    onToggleBookmark?: (id: string) => void;
}

const MONTH_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

const formatStableDate = (dateStr: string) => {
    if (!dateStr) return 'Dates Announced Soon';
    try {
        if (/^\d{2}-\d{2}-\d{4}$/.test(dateStr)) {
            const parts = dateStr.split('-');
            const m = parseInt(parts[1], 10) - 1;
            return `${MONTH_NAMES[m] || parts[1]} ${parts[0]}, ${parts[2]}`;
        }
        const d = new Date(dateStr);
        if (isNaN(d.valueOf())) return dateStr;
        return `${MONTH_NAMES[d.getUTCMonth()]} ${d.getUTCDate()}, ${d.getUTCFullYear()}`;
    } catch {
        return dateStr;
    }
};

const formatPrize = (pool: number | string | undefined) => {
    if (!pool || pool === 0 || pool === '0') return 'Bounties & Swag';
    if (typeof pool === 'number') {
        return `₹${pool.toLocaleString('en-US')}`;
    }
    return String(pool);
};

export function HackathonCard({ hackathon, onTeamUp, isBookmarked = false, onToggleBookmark }: HackathonCardProps) {
    const [mounted, setMounted] = useState(false);
    useEffect(() => {
        setMounted(true);
    }, []);

    const isLocal = (hackathon.source || '').toLowerCase().includes('local') || (hackathon.source || '').toLowerCase().includes('campus');

    const getSourceStyle = (source: string) => {
        const s = (source || '').toLowerCase();
        if (s.includes('devfolio')) {
            return 'bg-purple-50 text-purple-700 border-purple-200/80';
        }
        if (s.includes('devnovate')) {
            return 'bg-emerald-50 text-emerald-700 border-emerald-200/80';
        }
        if (s.includes('unstop')) {
            return 'bg-sky-50 text-sky-700 border-sky-200/80';
        }
        if (s.includes('local') || s.includes('campus')) {
            return 'bg-amber-50 text-amber-800 border-amber-300 font-bold';
        }
        return 'bg-slate-50 text-slate-700 border-slate-200';
    };

    const getTypeBadge = (type: string) => {
        switch (type) {
            case 'virtual':
                return <span className="bg-blue-50 text-blue-700 border border-blue-200 text-[11px] font-semibold px-2.5 py-0.5 rounded-full">Virtual</span>;
            case 'in-person':
                return <span className="bg-rose-50 text-rose-700 border border-rose-200 text-[11px] font-semibold px-2.5 py-0.5 rounded-full">In-Person</span>;
            case 'hybrid':
                return <span className="bg-teal-50 text-teal-700 border border-teal-200 text-[11px] font-semibold px-2.5 py-0.5 rounded-full">Hybrid</span>;
            default:
                return null;
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            whileHover={{ y: -4 }}
            className={`flex flex-col bg-white rounded-2xl border transition-all duration-300 p-5 sm:p-6 shadow-sm hover:shadow-xl relative group ${
                isLocal 
                    ? 'border-amber-300 ring-1 ring-amber-100 hover:shadow-amber-500/10' 
                    : 'border-slate-200 hover:border-blue-300 hover:shadow-blue-500/5'
            }`}
        >
            {/* Top Bar Badges */}
            <div className="flex items-center justify-between gap-2 mb-3">
                <div className="flex items-center gap-2 flex-wrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${getSourceStyle(hackathon.source)}`}>
                        {isLocal ? '🏫 ' : ''}{hackathon.source}
                    </span>
                    {getTypeBadge(hackathon.type)}
                    {hackathon.matchScore && (
                        <span className="bg-emerald-500 text-white text-[11px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1 shadow-xs">
                            <Sparkles className="w-3 h-3" /> {hackathon.matchScore}% Match
                        </span>
                    )}
                </div>

                {onToggleBookmark && mounted && (
                    <button
                        onClick={() => onToggleBookmark(hackathon.id)}
                        className={`p-2 rounded-xl transition-all cursor-pointer ${
                            isBookmarked
                                ? 'bg-blue-50 text-blue-600'
                                : 'text-slate-400 hover:text-slate-600 hover:bg-slate-100'
                        }`}
                        title={isBookmarked ? 'Remove Bookmark' : 'Save Hackathon'}
                    >
                        <Bookmark className={`w-4 h-4 ${isBookmarked ? 'fill-blue-600' : ''}`} />
                    </button>
                )}
            </div>

            {/* Title & Organization */}
            <div className="mb-4">
                <h3 className="text-lg sm:text-xl font-bold text-slate-900 leading-snug tracking-tight group-hover:text-blue-600 transition-colors line-clamp-2">
                    {hackathon.title}
                </h3>
                <div className="flex items-center gap-1.5 mt-1.5 text-xs font-medium text-slate-500">
                    <Building2 className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                    <span className="truncate">{hackathon.organization || 'Organizer'}</span>
                    {hackathon.location && hackathon.location !== 'Online' && (
                        <>
                            <span>•</span>
                            <MapPin className="w-3 h-3 text-slate-400 shrink-0" />
                            <span className="truncate text-slate-600">{hackathon.location}</span>
                        </>
                    )}
                </div>
            </div>

            {/* Details Chips */}
            <div className="grid grid-cols-2 gap-2 mb-4 text-xs">
                <div className="flex items-center gap-2 p-2.5 rounded-xl bg-slate-50 border border-slate-100">
                    <Trophy className="w-4 h-4 text-amber-500 shrink-0" />
                    <div className="truncate">
                        <span className="block text-[10px] text-slate-400 uppercase font-bold">Prize Pool</span>
                        <span className="font-bold text-slate-800">{formatPrize(hackathon.prizePool)}</span>
                    </div>
                </div>

                <div className="flex items-center gap-2 p-2.5 rounded-xl bg-slate-50 border border-slate-100">
                    <Calendar className="w-4 h-4 text-blue-500 shrink-0" />
                    <div className="truncate">
                        <span className="block text-[10px] text-slate-400 uppercase font-bold">Timeline</span>
                        <span className="font-semibold text-slate-700 truncate block">
                            {formatStableDate(hackathon.startDate)}
                        </span>
                    </div>
                </div>
            </div>

            {/* Theme & Extras */}
            <div className="flex items-center justify-between text-xs mb-5 pt-1">
                <div className="flex items-center gap-1.5 text-slate-600 bg-slate-100/70 px-2.5 py-1 rounded-lg max-w-[70%]">
                    <span className="text-[10px] uppercase font-bold text-slate-400">Theme:</span>
                    <span className="truncate font-medium">{hackathon.theme || 'Open Innovation'}</span>
                </div>
                {hackathon.participants ? (
                    <span className="flex items-center gap-1 text-[11px] font-semibold text-slate-500">
                        <Users className="w-3.5 h-3.5 text-slate-400" />
                        {hackathon.participants.toLocaleString()} joined
                    </span>
                ) : null}
            </div>

            {/* Actions Footer */}
            <div className="mt-auto pt-3 border-t border-slate-100 flex items-center gap-2.5">
                <a
                    href={hackathon.applyUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 py-2.5 px-3.5 rounded-xl text-xs sm:text-sm font-bold bg-blue-600 hover:bg-blue-700 text-white transition-all shadow-sm hover:shadow-blue-500/20 flex items-center justify-center gap-1.5"
                >
                    Apply Now
                    <ExternalLink className="w-3.5 h-3.5" />
                </a>

                <button
                    onClick={() => onTeamUp && onTeamUp(hackathon)}
                    className="flex-1 py-2.5 px-3.5 rounded-xl text-xs sm:text-sm font-bold bg-slate-50 hover:bg-indigo-50 text-slate-700 hover:text-indigo-600 border border-slate-200 hover:border-indigo-200 transition-all flex items-center justify-center gap-1.5 cursor-pointer"
                >
                    <Users className="w-3.5 h-3.5" />
                    Find Teammates
                </button>
            </div>
        </motion.div>
    );
}
