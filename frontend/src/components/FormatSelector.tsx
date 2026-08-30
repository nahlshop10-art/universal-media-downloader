'use client';

import React, { useState } from 'react';
import { Video, Music, Download, CheckCircle2, Sparkles, AlertCircle } from 'lucide-react';

interface VideoFormat {
  format_id: string;
  resolution: string;
  height: number;
  ext: string;
  filesize_str: string;
  note?: string;
}

interface AudioFormat {
  format_id: string;
  ext: string;
  quality: string;
  filesize_str: string;
}

interface FormatSelectorProps {
  formats: {
    video: VideoFormat[];
    audio: AudioFormat[];
  };
  onDownload: (type: 'video' | 'audio', formatId: string, ext: string) => void;
  isDownloading: boolean;
}

export default function FormatSelector({ formats, onDownload, isDownloading }: FormatSelectorProps) {
  const [activeTab, setActiveTab] = useState<'video' | 'audio'>('video');
  const [selectedFormatId, setSelectedFormatId] = useState<string>(
    formats.video[0]?.format_id || 'bestvideo'
  );

  const handleTabChange = (tab: 'video' | 'audio') => {
    setActiveTab(tab);
    if (tab === 'video' && formats.video[0]) {
      setSelectedFormatId(formats.video[0].format_id);
    } else if (tab === 'audio' && formats.audio[0]) {
      setSelectedFormatId(formats.audio[0].format_id);
    }
  };

  const handleDownloadClick = () => {
    if (activeTab === 'video') {
      const selected = formats.video.find((f) => f.format_id === selectedFormatId) || formats.video[0];
      onDownload('video', selected?.format_id || 'bestvideo', selected?.ext || 'mp4');
    } else {
      const selected = formats.audio.find((f) => f.format_id === selectedFormatId) || formats.audio[0];
      onDownload('audio', selected?.format_id || 'bestaudio', 'mp3');
    }
  };

  return (
    <div className="bg-gray-900/80 border border-gray-800 rounded-2xl p-5 shadow-xl">
      {/* Tabs */}
      <div className="flex border-b border-gray-800 pb-3 gap-2">
        <button
          type="button"
          onClick={() => handleTabChange('video')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition ${
            activeTab === 'video'
              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
              : 'text-gray-400 hover:text-white hover:bg-gray-800/60'
          }`}
        >
          <Video className="w-4 h-4" />
          <span>Video (MP4)</span>
          <span className="text-xs px-1.5 py-0.5 rounded bg-black/20 font-normal">
            {formats.video.length}
          </span>
        </button>

        <button
          type="button"
          onClick={() => handleTabChange('audio')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition ${
            activeTab === 'audio'
              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
              : 'text-gray-400 hover:text-white hover:bg-gray-800/60'
          }`}
        >
          <Music className="w-4 h-4" />
          <span>Audio (MP3)</span>
          <span className="text-xs px-1.5 py-0.5 rounded bg-black/20 font-normal">
            {formats.audio.length}
          </span>
        </button>
      </div>

      {/* Format list options */}
      <div className="mt-4 space-y-2 max-h-64 overflow-y-auto pr-1">
        {activeTab === 'video' ? (
          formats.video.map((f, idx) => {
            const isSelected = selectedFormatId === f.format_id;
            return (
              <div
                key={`${f.format_id}-${idx}`}
                onClick={() => setSelectedFormatId(f.format_id)}
                className={`flex items-center justify-between p-3 rounded-xl border cursor-pointer transition ${
                  isSelected
                    ? 'bg-indigo-600/10 border-indigo-500/80 text-white ring-1 ring-indigo-500/50'
                    : 'bg-gray-950/60 border-gray-800/80 text-gray-300 hover:border-gray-700 hover:bg-gray-800/40'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className={`w-4 h-4 rounded-full border flex items-center justify-center ${isSelected ? 'border-indigo-400 bg-indigo-500' : 'border-gray-600'}`}>
                    {isSelected && <div className="w-1.5 h-1.5 rounded-full bg-white" />}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-sm text-white">{f.resolution}</span>
                      <span className="uppercase text-[10px] font-semibold px-2 py-0.5 rounded bg-gray-800 text-gray-300 border border-gray-700">
                        {f.ext}
                      </span>
                    </div>
                    {f.note && <span className="text-xs text-gray-400">{f.note}</span>}
                  </div>
                </div>

                <div className="text-right text-xs text-gray-400 font-medium">
                  {f.filesize_str}
                </div>
              </div>
            );
          })
        ) : (
          formats.audio.map((f, idx) => {
            const isSelected = selectedFormatId === f.format_id;
            return (
              <div
                key={`${f.format_id}-${idx}`}
                onClick={() => setSelectedFormatId(f.format_id)}
                className={`flex items-center justify-between p-3 rounded-xl border cursor-pointer transition ${
                  isSelected
                    ? 'bg-indigo-600/10 border-indigo-500/80 text-white ring-1 ring-indigo-500/50'
                    : 'bg-gray-950/60 border-gray-800/80 text-gray-300 hover:border-gray-700 hover:bg-gray-800/40'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className={`w-4 h-4 rounded-full border flex items-center justify-center ${isSelected ? 'border-indigo-400 bg-indigo-500' : 'border-gray-600'}`}>
                    {isSelected && <div className="w-1.5 h-1.5 rounded-full bg-white" />}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-sm text-white">{f.quality}</span>
                      <span className="uppercase text-[10px] font-semibold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        MP3 Audio
                      </span>
                    </div>
                    <span className="text-xs text-gray-400">High bitrate conversion</span>
                  </div>
                </div>

                <div className="text-right text-xs text-gray-400 font-medium">
                  {f.filesize_str}
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Trigger Download Button */}
      <div className="mt-5 pt-4 border-t border-gray-800">
        <button
          type="button"
          onClick={handleDownloadClick}
          disabled={isDownloading}
          className="w-full py-3.5 px-4 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-white font-bold text-sm sm:text-base flex items-center justify-center gap-2 shadow-lg shadow-emerald-600/30 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Download className="w-5 h-5" />
          <span>{isDownloading ? 'Processing & Downloading...' : `Download ${activeTab === 'video' ? 'Video (MP4)' : 'Audio (MP3)'}`}</span>
        </button>
      </div>
    </div>
  );
}
