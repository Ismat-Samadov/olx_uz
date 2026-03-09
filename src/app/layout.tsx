import type { Metadata, Viewport } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Bubble Shooter — Neon Edition',
  description:
    'A neon cyberpunk bubble-shooter built with Next.js, TypeScript, and Tailwind CSS. ' +
    'Match 3+ same-coloured bubbles to pop them before they reach the danger line!',
  keywords: ['bubble shooter', 'game', 'neon', 'nextjs', 'typescript'],
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  themeColor: '#07071a',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        {/* Neon-themed SVG favicon is placed in /public/favicon.svg */}
        <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
      </head>
      <body className="antialiased h-full bg-[#07071a] text-slate-100">
        {children}
      </body>
    </html>
  );
}
