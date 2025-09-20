import './globals.css';
import type { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'ManuWeaver',
  description: 'Manuscript structuring, citation curation, and LaTeX compilation'
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-950 text-slate-100">
        <header className="border-b border-slate-800 bg-slate-900/70 backdrop-blur">
          <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
            <Link href="/" className="text-lg font-semibold text-cyan-300">
              ManuWeaver
            </Link>
            <nav className="space-x-4 text-sm text-slate-300">
              <Link href="/" className="hover:text-white">
                New Project
              </Link>
              <a href="https://www.crossref.org/" target="_blank" rel="noreferrer" className="hover:text-white">
                Crossref
              </a>
              <a href="https://openalex.org/" target="_blank" rel="noreferrer" className="hover:text-white">
                OpenAlex
              </a>
            </nav>
          </div>
        </header>
        <main className="mx-auto max-w-6xl px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
