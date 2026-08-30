import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Universal Media Downloader - Download Audio & Video from Any Social Platform',
  description: 'Fast, high quality video and audio downloader for YouTube, Instagram, Facebook, Twitter/X, TikTok, Reddit, and 1000+ sites.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased selection:bg-indigo-500 selection:text-white">
        {children}
      </body>
    </html>
  );
}
