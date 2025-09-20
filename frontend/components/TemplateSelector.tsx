'use client';

import React from 'react';
import useSWR from 'swr';
import { Template } from '../lib/types';

const fetcher = (url: string) => fetch(url).then((res) => res.json());

type Props = {
  selected?: string;
  onSelect: (template: Template) => void;
};

export function TemplateSelector({ selected, onSelect }: Props) {
  const { data, error } = useSWR<Template[]>(`${process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000'}/api/templates`, fetcher);

  if (error) {
    return <div className="text-red-400">Failed to load templates.</div>;
  }

  if (!data) {
    return <div className="text-slate-400">Loading templates…</div>;
  }

  return (
    <div className="grid gap-3 md:grid-cols-2">
      {data.map((template) => (
        <button
          key={template.identifier}
          onClick={() => onSelect(template)}
          className={`rounded border p-4 text-left transition ${selected === template.identifier ? 'border-cyan-400 bg-cyan-900/30' : 'border-slate-800 hover:border-cyan-600'}`}
        >
          <div className="text-base font-semibold text-white">{template.display_name}</div>
          <div className="text-xs text-slate-400">License: {template.license}</div>
          <p className="mt-2 text-sm text-slate-300">{template.description}</p>
        </button>
      ))}
    </div>
  );
}
