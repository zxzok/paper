'use client';

import React from 'react';
import { PreflightReport } from '../lib/types';

type Props = {
  report?: PreflightReport | null;
};

export function PreflightTable({ report }: Props) {
  if (!report) {
    return <div className="text-slate-500">Generate a preflight report to view checks.</div>;
  }
  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold text-white">Summary</h3>
        <ul className="mt-2 grid grid-cols-2 gap-2 text-sm text-slate-300">
          {Object.entries(report.summary).map(([key, value]) => (
            <li key={key} className="rounded border border-slate-800 bg-slate-900/40 p-2">
              <span className="block text-xs uppercase tracking-wide text-slate-500">{key}</span>
              <span className="text-base text-white">{String(value)}</span>
            </li>
          ))}
        </ul>
      </div>
      <div>
        <h3 className="text-lg font-semibold text-white">Issues</h3>
        {report.issues.length === 0 ? (
          <div className="mt-2 rounded border border-emerald-500/60 bg-emerald-900/40 p-4 text-emerald-100">
            No blocking issues detected.
          </div>
        ) : (
          <ul className="mt-2 space-y-2">
            {report.issues.map((issue) => (
              <li key={issue.code} className="rounded border border-amber-400 bg-amber-900/30 p-3">
                <div className="text-sm font-semibold text-white">[{issue.severity.upper()}] {issue.code}</div>
                <div className="text-xs text-slate-200">{issue.message}</div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
