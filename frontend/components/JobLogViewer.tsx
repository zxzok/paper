'use client';

import React, { useEffect, useState } from 'react';
import { streamJob } from '../lib/api';

type Props = {
  jobId?: string | null;
};

export function JobLogViewer({ jobId }: Props) {
  const [lines, setLines] = useState<string[]>([]);

  useEffect(() => {
    if (!jobId) return;
    setLines([]);
    const abort = new AbortController();
    streamJob(jobId, (line) => setLines((prev) => [...prev, line]), abort.signal);
    return () => abort.abort();
  }, [jobId]);

  if (!jobId) {
    return <div className="text-slate-500">Trigger a task to view streaming logs.</div>;
  }

  return (
    <div className="h-48 overflow-y-auto rounded border border-slate-800 bg-black/40 p-3 font-mono text-xs">
      {lines.map((line, idx) => (
        <div key={idx} className="whitespace-pre">
          {line}
        </div>
      ))}
    </div>
  );
}
