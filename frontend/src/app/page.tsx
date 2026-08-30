'use client';

import React, { useState } from 'react';
import axios from 'axios';
import Navbar from '@/components/Navbar';
import UrlInput from '@/components/UrlInput';
import MediaPreview from '@/components/MediaPreview';
import FormatSelector from '@/components/FormatSelector';
import { 
  Sparkles, 
  AlertCircle, 
  CheckCircle2, 
  Youtube, 
  Instagram, 
  Facebook, 
  Twitter, 
  Film, 
  Music, 
  Download, 
  Zap, 
  ShieldCheck, 
  Layers 
} from 'lucide-react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Home() {
  const [mediaInfo, setMediaInfo] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [downloadProgress, setDownloadProgress] = useState<string | null>(null);

  const handleFetch = async (url: string) => {
    setIsLoading(true);
    setErrorMsg(null);
    setMediaInfo(null);
    setDownloadProgress(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/info`, { url });
      setMediaInfo(response.data);
    } catch (err: any) {
      const detail = err.response?.data?.detail?.error || err.message || 'Failed to fetch media details.';
      setErrorMsg(detail);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = (type: 'video' | 'audio', formatId: string, ext: string) => {
    if (!mediaInfo) return;
    setErrorMsg(null);
    setDownloadProgress('Starting direct download in your browser download manager...');

    const downloadUrl = `${API_BASE_URL}/api/download?url=${encodeURIComponent(mediaInfo.webpage_url)}&type=${type}&format_id=${encodeURIComponent(formatId)}&ext=${ext}`;

    // Trigger native browser download manager
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.setAttribute('target', '_blank');
    link.setAttribute('download', '');
    document.body.appendChild(link);
    link.click();
    link.remove();

    setTimeout(() => {
      setDownloadProgress('Download sent to your device download manager! Check your notifications or downloads bar.');
    }, 1500);
  };

  const platforms = [
    { name: 'YouTube', icon: Youtube, color: 'text-red-500 bg-red-500/10 border-red-500/20' },
    { name: 'Instagram', icon: Instagram, color: 'text-pink-500 bg-pink-500/10 border-pink-500/20' },
    { name: 'Twitter / X', icon: Twitter, color: 'text-sky-400 bg-sky-400/10 border-sky-400/20' },
    { name: 'Facebook', icon: Facebook, color: 'text-blue-500 bg-blue-500/10 border-blue-500/20' },
    { name: 'TikTok', icon: Film, color: 'text-cyan-400 bg-cyan-400/10 border-cyan-400/20' },
    { name: 'SoundCloud', icon: Music, color: 'text-orange-500 bg-orange-500/10 border-orange-500/20' },
  ];

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />

      <main className="flex-1 max-w-5xl mx-auto px-4 sm:px-6 py-10 sm:py-16 w-full">
        {/* Hero */}
        <div className="text-center max-w-3xl mx-auto mb-10">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold mb-4">
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            <span>Universal Audio & Video Extractor</span>
          </div>

          <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight leading-tight sm:leading-none mb-4">
            Download Any Video or Audio <br className="hidden sm:block" />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-violet-400 to-pink-400">
              In Highest Quality
            </span>
          </h1>

          <p className="text-sm sm:text-base text-gray-400 max-w-xl mx-auto">
            Paste any link from YouTube, Instagram, Facebook, Twitter, TikTok, and 1000+ websites to extract MP4 video or 320kbps MP3 audio instantly.
          </p>
        </div>

        {/* Input Bar */}
        <UrlInput onSearch={handleFetch} isLoading={isLoading} />

        {/* Error Alert */}
        {errorMsg && (
          <div className="max-w-3xl mx-auto mt-4 p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm flex items-center gap-3">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Status Message */}
        {downloadProgress && (
          <div className="max-w-3xl mx-auto mt-4 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-sm flex items-center gap-3">
            <CheckCircle2 className="w-5 h-5 flex-shrink-0" />
            <span>{downloadProgress}</span>
          </div>
        )}

        {/* Media Results Card & Format Selector */}
        {mediaInfo && (
          <div className="max-w-3xl mx-auto mt-8 space-y-6">
            <MediaPreview info={mediaInfo} />
            <FormatSelector
              formats={mediaInfo.formats}
              onDownload={handleDownload}
              isDownloading={isDownloading}
            />
          </div>
        )}

        {/* Supported Platforms Grid */}
        <section id="supported-platforms" className="mt-20 pt-10 border-t border-gray-800/80">
          <div className="text-center mb-8">
            <h3 className="text-lg font-bold text-white mb-1">Supported Platforms</h3>
            <p className="text-xs text-gray-400">Extracts streams from over 1,000 video and audio streaming sites.</p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
            {platforms.map((p) => (
              <div
                key={p.name}
                className={`flex flex-col items-center justify-center p-4 rounded-xl border ${p.color} bg-opacity-30 backdrop-blur-sm`}
              >
                <p.icon className="w-6 h-6 mb-2" />
                <span className="text-xs font-semibold text-white">{p.name}</span>
              </div>
            ))}
          </div>

          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
            <div className="p-5 rounded-2xl bg-gray-900/50 border border-gray-800">
              <div className="w-9 h-9 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mb-3">
                <Zap className="w-5 h-5" />
              </div>
              <h4 className="font-bold text-white text-sm mb-1">High Speed & Direct</h4>
              <p className="text-xs text-gray-400">Stream directly through accelerated yt-dlp pipe with fast encoding.</p>
            </div>

            <div className="p-5 rounded-2xl bg-gray-900/50 border border-gray-800">
              <div className="w-9 h-9 rounded-xl bg-pink-500/10 border border-pink-500/20 flex items-center justify-center text-pink-400 mb-3">
                <Layers className="w-5 h-5" />
              </div>
              <h4 className="font-bold text-white text-sm mb-1">MP4 & MP3 Options</h4>
              <p className="text-xs text-gray-400">Choose between 1080p, 720p HD video or extract studio-quality 320kbps MP3 audio.</p>
            </div>

            <div className="p-5 rounded-2xl bg-gray-900/50 border border-gray-800">
              <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 mb-3">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <h4 className="font-bold text-white text-sm mb-1">No Ads & Privacy-First</h4>
              <p className="text-xs text-gray-400">Runs locally on your system without tracking, intrusive popups, or limits.</p>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-gray-800/60 py-6 text-center text-xs text-gray-500">
        Universal Media Downloader &copy; 2026. Powered by FastAPI, yt-dlp, and Next.js.
      </footer>
    </div>
  );
}
