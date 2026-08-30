'use client';

import React from 'react';
import { User, Clock, Globe, Film } from 'lucide-react';

interface MediaInfo {
  id: string;
  title: string;
  uploader: string;
  duration: number;
  thumbnail?: string;
  platform: string;
  webpage_url: string;
}

interface MediaPreviewProps {
  info: MediaInfo;
}

export default function MediaPreview({ info }: MediaPreviewProps) {
  const formatDuration = (seconds: number) => {
    if (!seconds) return 'Live / Unknown';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    const hrs = Math.floor(mins / 60);
    if (hrs > 0) {
      return `${hrs}:${(mins % 60).toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="bg-gray-900/80 border border-gray-800 rounded-2xl overflow-hidden shadow-xl p-4 sm:p-5 flex flex-col md:flex-row gap-5 items-start">
      <div className="relative w-full md:w-72 aspect-video bg-gray-950 rounded-xl overflow-hidden flex-shrink-0 border border-gray-800/80 shadow-md">
        {info.thumbnail ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={info.thumbnail}
            alt={info.title}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex flex-col items-center justify-center text-gray-600">
            <Film className="w-10 h-10 mb-2" />
            <span className="text-xs">No Thumbnail</span>
          </div>
        )}
        <div className="absolute bottom-2 right-2 px-2 py-1 rounded-md bg-black/80 backdrop-blur-md text-[11px] font-semibold text-white flex items-center gap-1">
          <Clock className="w-3 h-3 text-indigo-400" />
          <span>{formatDuration(info.duration)}</span>
        </div>
      </div>

      <div className="flex-1 min-w-0 flex flex-col justify-between self-stretch">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="capitalize px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              {info.platform}
            </span>
          </div>
          <h2 className="text-base sm:text-lg font-bold text-white leading-snug line-clamp-2 mb-2">
            {info.title}
          </h2>
        </div>

        <div className="flex flex-wrap items-center gap-4 text-xs text-gray-400 pt-2 border-t border-gray-800/60">
          <div className="flex items-center gap-1.5">
            <User className="w-3.5 h-3.5 text-gray-500" />
            <span className="font-medium text-gray-300 truncate max-w-[200px]">{info.uploader}</span>
          </div>
          <a
            href={info.webpage_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-indigo-400 hover:text-indigo-300 font-medium transition"
          >
            <Globe className="w-3.5 h-3.5" />
            <span>Open Source Link</span>
          </a>
        </div>
      </div>
    </div>
  );
}
