'use client';

import React from 'react';
import { Reference } from '../lib/types';

type Props = {
  references: Reference[];
};

export function ReferenceList({ references }: Props) {
  if (!references.length) {
    return <div className="text-slate-400">No references retrieved yet.</div>;
  }
  return (
    <ol className="space-y-2">
      {references.map((ref) => (
        <li key={ref.key} className={`rounded border p-3 ${ref.needs_review ? 'border-amber-400 bg-amber-900/30' : 'border-slate-800 bg-slate-900/40'}`}>
          <div className="text-sm font-semibold text-white">{ref.title}</div>
          <div className="text-xs text-slate-300">{ref.authors.join(', ')} ({ref.year ?? 'n.d.'})</div>
          {ref.doi && (
            <div className="text-xs text-cyan-300">
              DOI: <a href={`https://doi.org/${ref.doi}`} target="_blank" rel="noreferrer">{ref.doi}</a>
            </div>
          )}
          {!ref.doi && <div className="text-xs text-red-300">Requires manual verification</div>}
        </li>
      ))}
    </ol>
  );
}
