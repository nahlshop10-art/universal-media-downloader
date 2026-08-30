'use client';

import React, { useState } from 'react';
import { Search, Loader2, Clipboard, ArrowRight, Youtube, Instagram, Facebook, Twitter, Film, Music, Check } from 'lucide-react';

interface UrlInputProps {
  onSearch: (url: string) => void;
  isLoading: boolean;
}

export default function UrlInput({ onSearch, isLoading }: UrlInputProps) {
  const [url, setUrl] = useState('');
  const [copied, setCopied] = useState(false);

  const getPlatformIcon = (urlStr: string) => {
    const u = urlStr.toLowerCase();
    if (u.includes('youtube.com') || u.includes('youtu.be')) {
      return { name: 'YouTube', icon: Youtube, color: 'text-red-500 bg-red-500/10 border-red-500/30' };
    }
    if (u.includes('instagram.com')) {
      return { name: 'Instagram', icon: Instagram, color: 'text-pink-500 bg-pink-500/10 border-pink-500/30' };
    }
    if (u.includes('twitter.com') || u.includes('x.com')) {
      return { name: 'Twitter / X', icon: Twitter, color: 'text-sky-400 bg-sky-400/10 border-sky-400/30' };
    }
    if (u.includes('facebook.com') || u.includes('fb.watch')) {
      return { name: 'Facebook', icon: Facebook, color: 'text-blue-500 bg-blue-500/10 border-blue-500/30' };
    }
    if (u.includes('tiktok.com')) {
      return { name: 'TikTok', icon: Film, color: 'text-cyan-400 bg-cyan-400/10 border-cyan-400/30' };
    }
    if (u.includes('soundcloud.com')) {
      return { name: 'SoundCloud', icon: Music, color: 'text-orange-500 bg-orange-500/10 border-orange-500/30' };
    }
    return null;
  };

  const detectedPlatform = getPlatformIcon(url);

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) {
        setUrl(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }
    } catch {
      // Fallback
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (url.trim() && !isLoading) {
      onSearch(url.trim());
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto">
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative flex items-center bg-gray-900/90 border-2 border-indigo-500/40 focus-within:border-indigo-500 rounded-2xl p-2 shadow-2xl shadow-indigo-950/50 backdrop-blur-xl transition duration-200">
          <div className="pl-3 pr-2 text-gray-400">
            <Search className="w-6 h-6" />
          </div>

          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Paste YouTube, Instagram, Facebook, Twitter, TikTok video or audio link..."
            className="w-full bg-transparent text-white placeholder-gray-500 text-sm sm:text-base focus:outline-none pr-28 sm:pr-36 py-2 font-normal"
            disabled={isLoading}
          />

          <div className="absolute right-2 flex items-center space-x-2">
            {!url && (
              <button
                type="button"
                onClick={handlePaste}
                className="hidden sm:flex items-center gap-1.5 px-3 py-2 rounded-xl bg-gray-800 hover:bg-gray-700 text-xs font-medium text-gray-300 transition"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Clipboard className="w-3.5 h-3.5" />}
                <span>{copied ? 'Pasted' : 'Paste'}</span>
              </button>
            )}

            <button
              type="submit"
              disabled={isLoading || !url.trim()}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white text-sm font-semibold shadow-md shadow-indigo-600/30 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span className="hidden sm:inline">Fetching</span>
                </>
              ) : (
                <>
                  <span>Fetch</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </div>

        {detectedPlatform && (
          <div className="mt-2.5 flex items-center gap-2 text-xs">
            <span className="text-gray-400 font-medium">Detected Platform:</span>
            <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-xs font-semibold ${detectedPlatform.color}`}>
              <detectedPlatform.icon className="w-3.5 h-3.5" />
              <span>{detectedPlatform.name}</span>
            </div>
          </div>
        )}
      </form>
    </div>
  );
}
