'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { HackathonCard, Hackathon } from '../../components/HackathonCard';
import { ListLocalHackathonModal } from '../../components/ListLocalHackathonModal';
import { TeamUpModal } from '../../components/TeamUpModal';
import { motion, AnimatePresence } from 'framer-motion';
import { 
    Search, 
    Filter, 
    Sparkles, 
    PlusCircle, 
    RefreshCw, 
    Bookmark, 
    Trophy, 
    CheckCircle2,
    Wifi,
    WifiOff
} from 'lucide-react';
import initialHackathonsData from '../../data/initialHackathons.json';

export default function HackathonsPage() {
    const [hackathons, setHackathons] = useState<Hackathon[]>(initialHackathonsData as Hackathon[]);
    const [isLoading, setIsLoading] = useState(false);
    const [isSyncing, setIsSyncing] = useState(false);
    const [isBackendConnected, setIsBackendConnected] = useState<boolean | null>(null);
    const [search, setSearch] = useState('');
    const [filterSource, setFilterSource] = useState('all');
    const [filterType, setFilterType] = useState('all');
    const [sortBy, setSortBy] = useState<'default' | 'prize' | 'participants' | 'match'>('default');
    const [onlyBookmarked, setOnlyBookmarked] = useState(false);
    const [bookmarkedIds, setBookmarkedIds] = useState<string[]>([]);
    const [resumeProfile, setResumeProfile] = useState<{
        overallScore: number;
        recommendedRole: string;
        extractedSkills: string[];
    } | null>(null);
    const [mounted, setMounted] = useState(false);
    
    // Modal states
    const [isAddModalOpen, setIsAddModalOpen] = useState(false);
    const [selectedHackForTeam, setSelectedHackForTeam] = useState<Hackathon | null>(null);
    const [statusToast, setStatusToast] = useState<{ message: string; type: 'success' | 'info' | 'error' } | null>(null);
    
    const [currentPage, setCurrentPage] = useState(1);
    const ITEMS_PER_PAGE = 12;

    // Load saved bookmarks, local stored events, and AI resume profile from localStorage on mount
    useEffect(() => {
        setMounted(true);
        try {
            const savedBookmarks = localStorage.getItem('bookmarked_hackathons');
            if (savedBookmarks) {
                setBookmarkedIds(JSON.parse(savedBookmarks));
            }

            const savedLocalHacks = localStorage.getItem('local_added_hackathons');
            if (savedLocalHacks) {
                const parsedLocal: Hackathon[] = JSON.parse(savedLocalHacks);
                if (Array.isArray(parsedLocal) && parsedLocal.length > 0) {
                    setHackathons(prev => {
                        const existingIds = new Set(prev.map(h => h.id));
                        const uniqueLocal = parsedLocal.filter(h => !existingIds.has(h.id));
                        return [...uniqueLocal, ...prev];
                    });
                }
            }

            const savedResumeData = localStorage.getItem('resume_match_data');
            if (savedResumeData) {
                const parsedResume = JSON.parse(savedResumeData);
                setResumeProfile({
                    overallScore: parsedResume.overallScore,
                    recommendedRole: parsedResume.recommendedRole,
                    extractedSkills: parsedResume.extractedSkills || []
                });
                if (Array.isArray(parsedResume.matchedScores) && parsedResume.matchedScores.length > 0) {
                    const scoreMap = new Map(parsedResume.matchedScores.map((s: any) => [s.id, s]));
                    setHackathons(prev => prev.map(h => {
                        const scoreInfo: any = scoreMap.get(h.id);
                        if (scoreInfo) {
                            return {
                                ...h,
                                matchScore: scoreInfo.matchScore,
                                matchExplanation: scoreInfo.matchReason
                            };
                        }
                        return h;
                    }));
                    setSortBy('match');
                }
            }
        } catch {
            // ignore localStorage error
        }
    }, []);

    const toggleBookmark = (id: string) => {
        setBookmarkedIds(prev => {
            const updated = prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id];
            try {
                localStorage.setItem('bookmarked_hackathons', JSON.stringify(updated));
            } catch {
                // ignore
            }
            return updated;
        });
    };

    // Fetch live data from backend aggregator endpoint
    const fetchLiveHackathons = async (isRefresh = false) => {
        if (isRefresh) {
            setIsSyncing(true);
        }

        try {
            // Try relative API route first (via Next.js rewrite) or direct fallback
            const endpoints = [
                `/api/hackathons/scrape/all${isRefresh ? '?refresh=true' : ''}`,
                `http://127.0.0.1:8000/api/hackathons/scrape/all${isRefresh ? '?refresh=true' : ''}`,
                `http://localhost:8000/api/hackathons/scrape/all${isRefresh ? '?refresh=true' : ''}`
            ];

            let successData = null;

            for (const endpoint of endpoints) {
                try {
                    const res = await fetch(endpoint, { cache: 'no-store' });
                    if (res.ok) {
                        const json = await res.json();
                        if (json.data && Array.isArray(json.data) && json.data.length > 0) {
                            successData = json;
                            break;
                        }
                    }
                } catch {
                    // Try next endpoint
                }
            }

            if (successData) {
                setIsBackendConnected(true);
                setHackathons(prev => {
                    // Merge local user-added hackathons if any
                    let localSaved: Hackathon[] = [];
                    try {
                        const raw = localStorage.getItem('local_added_hackathons');
                        if (raw) localSaved = JSON.parse(raw);
                    } catch {}
                    const existingIds = new Set(successData.data.map((h: Hackathon) => h.id));
                    const uniqueLocal = localSaved.filter(h => !existingIds.has(h.id));
                    return [...uniqueLocal, ...successData.data];
                });

                if (isRefresh) {
                    setStatusToast({
                        message: `Successfully synced ${successData.totalCount || successData.data.length} live hackathons!`,
                        type: 'success'
                    });
                    setTimeout(() => setStatusToast(null), 3500);
                }
            } else {
                setIsBackendConnected(false);
                if (isRefresh) {
                    setStatusToast({
                        message: 'Backend server not responding. Operating with pre-cached snapshot (52 events).',
                        type: 'info'
                    });
                    setTimeout(() => setStatusToast(null), 4000);
                }
            }
        } catch {
            setIsBackendConnected(false);
        } finally {
            setIsLoading(false);
            setIsSyncing(false);
        }
    };

    useEffect(() => {
        fetchLiveHackathons(false);
    }, []);

    const handleHackathonAdded = (newHack: Hackathon) => {
        setHackathons(prev => [newHack, ...prev]);
        try {
            const raw = localStorage.getItem('local_added_hackathons');
            const localSaved: Hackathon[] = raw ? JSON.parse(raw) : [];
            localStorage.setItem('local_added_hackathons', JSON.stringify([newHack, ...localSaved]));
        } catch {}
        setStatusToast({
            message: `"${newHack.title}" has been published to the portal!`,
            type: 'success'
        });
    };

    const clearResumeProfile = () => {
        try {
            localStorage.removeItem('resume_match_data');
        } catch {}
        setResumeProfile(null);
        setSortBy('default');
        setHackathons(prev => prev.map(h => ({ ...h, matchScore: undefined, matchExplanation: undefined })));
        setStatusToast({
            message: 'Cleared AI Resume match profile. Restored default listing.',
            type: 'info'
        });
        setTimeout(() => setStatusToast(null), 3000);
    };

    // Filter & Sort Logic
    const filteredHackathons = useMemo(() => {
        return hackathons.filter(hack => {
            // Bookmarks filter
            if (onlyBookmarked && !bookmarkedIds.includes(hack.id)) {
                return false;
            }

            // Source filter
            if (filterSource !== 'all') {
                const s = (hack.source || '').toLowerCase();
                if (filterSource === 'local' && !(s.includes('local') || s.includes('campus'))) return false;
                if (filterSource === 'devfolio' && !s.includes('devfolio')) return false;
                if (filterSource === 'devnovate' && !s.includes('devnovate')) return false;
                if (filterSource === 'unstop' && !s.includes('unstop')) return false;
            }

            // Type filter
            if (filterType !== 'all' && hack.type !== filterType) {
                return false;
            }

            // Search query filter
            if (search.trim()) {
                const q = search.toLowerCase();
                const titleMatch = hack.title?.toLowerCase().includes(q);
                const themeMatch = hack.theme?.toLowerCase().includes(q);
                const orgMatch = hack.organization?.toLowerCase().includes(q);
                const locMatch = hack.location?.toLowerCase().includes(q);
                if (!titleMatch && !themeMatch && !orgMatch && !locMatch) {
                    return false;
                }
            }

            return true;
        }).sort((a, b) => {
            if (sortBy === 'match') {
                const sA = a.matchScore || 0;
                const sB = b.matchScore || 0;
                return sB - sA;
            }
            if (sortBy === 'prize') {
                const prizeA = typeof a.prizePool === 'number' ? a.prizePool : 0;
                const prizeB = typeof b.prizePool === 'number' ? b.prizePool : 0;
                return prizeB - prizeA;
            }
            if (sortBy === 'participants') {
                const pA = a.participants || 0;
                const pB = b.participants || 0;
                return pB - pA;
            }
            return 0;
        });
    }, [hackathons, search, filterSource, filterType, sortBy, onlyBookmarked, bookmarkedIds]);

    const paginatedHackathons = filteredHackathons.slice(0, currentPage * ITEMS_PER_PAGE);
    const hasMore = paginatedHackathons.length < filteredHackathons.length;

    // Aggregated stats
    const stats = useMemo(() => {
        let devfolioCount = 0;
        let devnovateCount = 0;
        let unstopCount = 0;
        let localCount = 0;

        hackathons.forEach(h => {
            const s = (h.source || '').toLowerCase();
            if (s.includes('devfolio')) devfolioCount++;
            else if (s.includes('devnovate')) devnovateCount++;
            else if (s.includes('unstop')) unstopCount++;
            else if (s.includes('local') || s.includes('campus')) localCount++;
        });

        return {
            total: hackathons.length,
            devfolioCount,
            devnovateCount,
            unstopCount,
            localCount
        };
    }, [hackathons]);

    return (
        <div className="min-h-screen bg-slate-50 text-slate-900 pb-20 font-sans selection:bg-blue-500 selection:text-white relative">
            {/* Ambient Background Glows */}
            <div className="absolute top-0 right-0 w-[550px] h-[550px] bg-gradient-to-br from-blue-200/40 to-indigo-200/30 rounded-full blur-[140px] pointer-events-none" />
            <div className="absolute top-48 left-0 w-[450px] h-[450px] bg-gradient-to-tr from-purple-200/30 to-pink-200/20 rounded-full blur-[140px] pointer-events-none" />

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 sm:pt-12 relative z-10 flex flex-col gap-8">
                
                {/* Hero & Action Bar */}
                <header className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-2 border-b border-slate-200">
                    <div className="max-w-2xl">
                        <div className="flex items-center gap-2 mb-3 flex-wrap">
                            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-100/80 border border-blue-200 text-blue-700 text-xs font-bold shadow-xs">
                                <Sparkles className="w-3.5 h-3.5" />
                                <span>Devfolio • Devnovate • Unstop • Campus</span>
                            </span>

                            {isBackendConnected === true && (
                                <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-0.5 rounded-full">
                                    <Wifi className="w-3 h-3 text-emerald-600" />
                                    Live Sync Connected
                                </span>
                            )}
                            {isBackendConnected === false && (
                                <span className="inline-flex items-center gap-1 text-[11px] font-bold text-amber-700 bg-amber-50 border border-amber-200 px-2.5 py-0.5 rounded-full" title="Backend not detected; running in cached snapshot mode">
                                    <WifiOff className="w-3 h-3 text-amber-600" />
                                    Snapshot Mode (52 Events)
                                </span>
                            )}
                        </div>

                        <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-slate-900 leading-tight">
                            Live <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">Hackathon Hub</span>
                        </h1>
                        <p className="mt-2 text-sm sm:text-base text-slate-600 font-medium">
                            All national and campus hackathons in one unified dashboard. Find teammates, compete for bounties, and submit your local college events.
                        </p>
                    </div>

                    <div className="flex flex-wrap items-center gap-3">
                        <button
                            onClick={() => fetchLiveHackathons(true)}
                            disabled={isSyncing}
                            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs sm:text-sm font-semibold transition-all shadow-xs hover:border-slate-300 disabled:opacity-50 cursor-pointer"
                            title="Fetch fresh live data from websites"
                        >
                            <RefreshCw className={`w-4 h-4 text-slate-500 ${isSyncing ? 'animate-spin text-blue-600' : ''}`} />
                            {isSyncing ? 'Scraping Sites...' : 'Sync Live Data'}
                        </button>

                        <button
                            onClick={() => setIsAddModalOpen(true)}
                            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white text-xs sm:text-sm font-bold transition-all shadow-md shadow-blue-500/20 cursor-pointer"
                        >
                            <PlusCircle className="w-4 h-4" />
                            List Campus Hackathon
                        </button>
                    </div>
                </header>

                {/* Status Toast Banner */}
                {statusToast && (
                    <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0 }}
                        className={`p-3.5 rounded-xl border text-xs sm:text-sm font-medium flex items-center gap-2.5 shadow-xs ${
                            statusToast.type === 'success'
                                ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
                                : 'bg-blue-50 border-blue-200 text-blue-800'
                        }`}
                    >
                        <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                        <span>{statusToast.message}</span>
                    </motion.div>
                )}

                {/* Live Stats Cards Bar */}
                <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-5 gap-3 sm:gap-4">
                    <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
                        <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Live Events</span>
                        <div className="flex items-baseline gap-1.5 mt-1">
                            <span className="text-2xl font-extrabold text-slate-900">{stats.total}</span>
                            <span className="text-xs font-semibold text-emerald-600">Active</span>
                        </div>
                    </div>

                    <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
                        <span className="text-[11px] font-bold text-purple-600 uppercase tracking-wider block">Devfolio</span>
                        <div className="flex items-baseline gap-1.5 mt-1">
                            <span className="text-2xl font-extrabold text-slate-900">{stats.devfolioCount}</span>
                            <span className="text-xs text-slate-400">Listed</span>
                        </div>
                    </div>

                    <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
                        <span className="text-[11px] font-bold text-emerald-600 uppercase tracking-wider block">Devnovate</span>
                        <div className="flex items-baseline gap-1.5 mt-1">
                            <span className="text-2xl font-extrabold text-slate-900">{stats.devnovateCount}</span>
                            <span className="text-xs text-slate-400">Listed</span>
                        </div>
                    </div>

                    <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
                        <span className="text-[11px] font-bold text-sky-600 uppercase tracking-wider block">Unstop</span>
                        <div className="flex items-baseline gap-1.5 mt-1">
                            <span className="text-2xl font-extrabold text-slate-900">{stats.unstopCount}</span>
                            <span className="text-xs text-slate-400">Listed</span>
                        </div>
                    </div>

                    <div className="bg-white p-4 rounded-2xl border border-amber-300 ring-1 ring-amber-100 shadow-xs col-span-2 sm:col-span-4 lg:col-span-1">
                        <span className="text-[11px] font-bold text-amber-700 uppercase tracking-wider block">Campus / Local</span>
                        <div className="flex items-baseline gap-1.5 mt-1">
                            <span className="text-2xl font-extrabold text-slate-900">{stats.localCount}</span>
                            <span className="text-xs text-amber-600 font-medium">Student Events</span>
                        </div>
                    </div>
                </div>

                {/* AI Resume Profile Active Banner */}
                {resumeProfile && (
                    <div className="p-4 rounded-2xl bg-gradient-to-r from-blue-500/10 via-indigo-500/10 to-purple-500/10 border border-blue-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-xs">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-blue-600 text-white flex items-center justify-center font-black text-sm shrink-0 shadow-xs">
                                {resumeProfile.overallScore}%
                            </div>
                            <div>
                                <div className="flex items-center gap-2 flex-wrap">
                                    <span className="text-xs font-bold text-blue-700 uppercase tracking-wider">
                                        ⚡ AI Resume Match Active
                                    </span>
                                    <span className="text-xs bg-white text-slate-700 font-semibold px-2 py-0.5 rounded-md border border-slate-200">
                                        {resumeProfile.recommendedRole}
                                    </span>
                                </div>
                                <p className="text-xs text-slate-600 mt-0.5">
                                    Hackathons are ranked by skill alignment with your profile ({resumeProfile.extractedSkills.slice(0, 4).join(', ')}).
                                </p>
                            </div>
                        </div>

                        <button
                            onClick={clearResumeProfile}
                            className="text-xs font-bold text-slate-600 hover:text-rose-600 px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-rose-50 transition-colors shrink-0 cursor-pointer"
                        >
                            Reset AI Ranking
                        </button>
                    </div>
                )}

                {/* Filters, Search & Sorting Controls */}
                <div className="bg-white p-4 sm:p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col gap-4">
                    {/* Top Row: Search and Quick Toggles */}
                    <div className="flex flex-col md:flex-row items-center gap-3">
                        <div className="w-full relative flex-1">
                            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                            <input
                                type="text"
                                placeholder="Search by title, theme, college, or city (e.g. AI, Bengaluru, Innohacks)..."
                                className="w-full bg-slate-50 border border-slate-200 pl-10 pr-4 py-2.5 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white text-sm font-medium transition-all"
                                value={search}
                                onChange={(e) => {
                                    setSearch(e.target.value);
                                    setCurrentPage(1);
                                }}
                            />
                        </div>

                        <div className="flex items-center gap-2 w-full md:w-auto">
                            {mounted && (
                                <button
                                    onClick={() => {
                                        setOnlyBookmarked(!onlyBookmarked);
                                        setCurrentPage(1);
                                    }}
                                    className={`px-3.5 py-2.5 rounded-xl border text-xs sm:text-sm font-bold flex items-center gap-2 transition-all cursor-pointer ${
                                        onlyBookmarked
                                            ? 'bg-blue-600 text-white border-blue-600 shadow-xs'
                                            : 'bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100'
                                    }`}
                                >
                                    <Bookmark className={`w-4 h-4 ${onlyBookmarked ? 'fill-white' : ''}`} />
                                    Saved ({bookmarkedIds.length})
                                </button>
                            )}

                            <select
                                value={sortBy}
                                onChange={(e) => setSortBy(e.target.value as any)}
                                className="px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-700 text-xs sm:text-sm font-semibold outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
                            >
                                {resumeProfile && <option value="match">Sort: Best AI Match (Highest %)</option>}
                                <option value="default">Sort: Default</option>
                                <option value="prize">Sort: Prize Pool (High to Low)</option>
                                <option value="participants">Sort: Most Popular</option>
                            </select>
                        </div>
                    </div>

                    {/* Bottom Row: Source & Mode Filter Chips */}
                    <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-slate-100">
                        {/* Source Filter Tabs */}
                        <div className="flex flex-wrap items-center gap-1.5">
                            <span className="text-xs font-bold text-slate-400 mr-1 uppercase">Source:</span>
                            {[
                                { id: 'all', label: 'All Platforms' },
                                { id: 'devfolio', label: 'Devfolio' },
                                { id: 'devnovate', label: 'Devnovate' },
                                { id: 'unstop', label: 'Unstop' },
                                { id: 'local', label: '🏫 Campus / Local' }
                            ].map((tab) => (
                                <button
                                    key={tab.id}
                                    onClick={() => {
                                        setFilterSource(tab.id);
                                        setCurrentPage(1);
                                    }}
                                    className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                                        filterSource === tab.id
                                            ? 'bg-slate-900 text-white shadow-xs'
                                            : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                                    }`}
                                >
                                    {tab.label}
                                </button>
                            ))}
                        </div>

                        {/* Format Filter */}
                        <div className="flex items-center gap-1.5">
                            <span className="text-xs font-bold text-slate-400 mr-1 uppercase">Format:</span>
                            {[
                                { id: 'all', label: 'All' },
                                { id: 'in-person', label: 'In-Person' },
                                { id: 'virtual', label: 'Virtual' },
                                { id: 'hybrid', label: 'Hybrid' }
                            ].map((tab) => (
                                <button
                                    key={tab.id}
                                    onClick={() => {
                                        setFilterType(tab.id);
                                        setCurrentPage(1);
                                    }}
                                    className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                                        filterType === tab.id
                                            ? 'bg-blue-600 text-white font-bold shadow-xs'
                                            : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                                    }`}
                                >
                                    {tab.label}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Results Counter & Active Filter Indicators */}
                <div className="flex items-center justify-between text-xs sm:text-sm font-semibold text-slate-500">
                    <div>
                        Showing <strong className="text-slate-900">{filteredHackathons.length}</strong> hackathons
                        {filterSource !== 'all' && <span> from <strong className="text-blue-600 capitalize">{filterSource}</strong></span>}
                        {filterType !== 'all' && <span> ({filterType})</span>}
                        {search && <span> matching &quot;{search}&quot;</span>}
                    </div>

                    {(filterSource !== 'all' || filterType !== 'all' || search || onlyBookmarked) && (
                        <button
                            onClick={() => {
                                setFilterSource('all');
                                setFilterType('all');
                                setSearch('');
                                setOnlyBookmarked(false);
                            }}
                            className="text-blue-600 hover:text-blue-800 text-xs font-bold underline cursor-pointer"
                        >
                            Reset All Filters
                        </button>
                    )}
                </div>

                {/* Grid of Hackathon Cards */}
                <div className="flex flex-col gap-8">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 sm:gap-6">
                        <AnimatePresence>
                            {paginatedHackathons.map((hack) => (
                                <HackathonCard
                                    key={hack.id}
                                    hackathon={hack}
                                    onTeamUp={(h) => setSelectedHackForTeam(h)}
                                    isBookmarked={bookmarkedIds.includes(hack.id)}
                                    onToggleBookmark={toggleBookmark}
                                />
                            ))}
                        </AnimatePresence>
                    </div>

                    {filteredHackathons.length === 0 && (
                        <div className="py-24 flex flex-col items-center justify-center text-center bg-white rounded-2xl border border-slate-200 p-8 shadow-xs">
                            <div className="w-14 h-14 rounded-full bg-slate-100 flex items-center justify-center mb-3">
                                <Filter className="w-6 h-6 text-slate-400" />
                            </div>
                            <h3 className="text-base font-bold text-slate-800">No hackathons match your filters</h3>
                            <p className="text-xs sm:text-sm text-slate-500 max-w-sm mt-1 mb-4">
                                Try clearing your search terms or changing the platform filter to explore more events.
                            </p>
                            <button
                                onClick={() => {
                                    setFilterSource('all');
                                    setFilterType('all');
                                    setSearch('');
                                    setOnlyBookmarked(false);
                                }}
                                className="px-4 py-2 bg-blue-600 text-white rounded-xl text-xs font-bold hover:bg-blue-700 transition-colors cursor-pointer"
                            >
                                Reset Filters
                            </button>
                        </div>
                    )}

                    {hasMore && (
                        <div className="flex justify-center mt-4">
                            <button
                                onClick={() => setCurrentPage(p => p + 1)}
                                className="px-8 py-3 font-bold text-blue-600 bg-white border border-blue-200 rounded-xl hover:bg-blue-50 transition-all shadow-xs cursor-pointer"
                            >
                                Load More Hackathons ({filteredHackathons.length - paginatedHackathons.length} remaining)
                            </button>
                        </div>
                    )}
                </div>
            </div>

            {/* Modals */}
            <ListLocalHackathonModal
                isOpen={isAddModalOpen}
                onClose={() => setIsAddModalOpen(false)}
                onHackathonAdded={handleHackathonAdded}
            />

            <TeamUpModal
                isOpen={!!selectedHackForTeam}
                onClose={() => setSelectedHackForTeam(null)}
                hackathon={selectedHackForTeam}
            />
        </div>
    );
}
