import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Link from 'next/link';
import { Layers, Sparkles, PlusCircle } from 'lucide-react';

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Hackathon Aggregator | Devfolio, Devnovate, Unstop & Campus",
  description: "One-stop portal for all live hackathons across Devfolio, Devnovate, Unstop, and local campus listings. Find teammates and apply seamlessly.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-slate-50 text-slate-900 min-h-screen flex flex-col`}
        suppressHydrationWarning
      >
        <nav className="sticky top-0 z-40 w-full bg-white/90 backdrop-blur-md border-b border-slate-200 px-4 sm:px-8 py-3.5 flex items-center justify-between shadow-xs">
          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="bg-gradient-to-tr from-blue-600 to-indigo-600 p-2 rounded-xl text-white shadow-sm group-hover:scale-105 transition-transform">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <span className="font-extrabold text-lg sm:text-xl tracking-tight text-slate-900 group-hover:text-blue-600 transition-colors">
                Agreggator<span className="text-blue-600">.</span>
              </span>
              <span className="hidden sm:inline-block text-[10px] text-slate-400 font-bold ml-2 uppercase tracking-wider">
                Hackathon Hub
              </span>
            </div>
          </Link>

          <div className="flex gap-2 sm:gap-4 items-center">
            <Link 
              href="/hackathons" 
              className="text-xs sm:text-sm font-bold text-slate-700 hover:text-blue-600 transition-colors px-3 py-1.5 rounded-lg hover:bg-slate-100 flex items-center gap-1.5"
            >
              <Sparkles className="w-3.5 h-3.5 text-blue-600" />
              Explore Hackathons
            </Link>
            <Link 
              href="/hackathons" 
              className="inline-flex items-center gap-1.5 text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 px-3.5 py-2 rounded-xl transition-all shadow-xs cursor-pointer"
            >
              <PlusCircle className="w-3.5 h-3.5" />
              List Event
            </Link>
          </div>
        </nav>

        <main className="flex-1">
          {children}
        </main>

        <footer className="border-t border-slate-200 bg-white py-8 px-4 text-center text-xs text-slate-500">
          <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="font-medium">
              Agreggator — Aggregating Devfolio, Devnovate, Unstop & Local Campus Competitions.
            </p>
            <div className="flex items-center gap-4 text-slate-400 font-semibold">
              <Link href="/hackathons" className="hover:text-blue-600 transition-colors">All Hackathons</Link>
              <span>•</span>
              <a href="https://devfolio.co/hackathons" target="_blank" rel="noreferrer" className="hover:text-purple-600 transition-colors">Devfolio</a>
              <span>•</span>
              <a href="https://devnovate.co/events" target="_blank" rel="noreferrer" className="hover:text-emerald-600 transition-colors">Devnovate</a>
              <span>•</span>
              <a href="https://unstop.com" target="_blank" rel="noreferrer" className="hover:text-sky-600 transition-colors">Unstop</a>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
