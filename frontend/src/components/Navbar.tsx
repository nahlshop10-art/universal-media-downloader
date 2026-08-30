'use client';

import React from 'react';
import { DownloadCloud, Sparkles, ShieldCheck } from 'lucide-react';

export default function Navbar() {
  return (
    <header className="border-b border-gray-800/80 bg-gray-950/60 backdrop-blur-xl sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center shadow-lg shadow-indigo-500/25">
            <DownloadCloud className="w-5 h-5 text-white" />
          </div>
          <div>
            <span className="font-bold text-lg text-white tracking-tight flex items-center gap-1.5">
              MediaRip <span className="text-xs bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 px-2 py-0.5 rounded-full font-medium">Pro</span>
            </span>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <div className="hidden sm:flex items-center gap-2 text-xs text-gray-400 bg-gray-900/80 border border-gray-800 px-3 py-1.5 rounded-lg">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>1000+ Platforms Supported</span>
          </div>
          <a
            href="#supported-platforms"
            className="text-xs text-gray-300 hover:text-white transition font-medium"
          >
            Platforms
          </a>
        </div>
      </div>
    </header>
  );
}
