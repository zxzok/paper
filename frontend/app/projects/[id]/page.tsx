'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  triggerCitationDetection,
  triggerReferenceSearch,
  triggerFormat,
  triggerCompile,
  triggerPreflight,
  fetchArtifacts
} from '../../../lib/api';
import { CitationSlot, Reference, PreflightReport } from '../../../lib/types';
import { JobLogViewer } from '../../../components/JobLogViewer';
import { ReferenceList } from '../../../components/ReferenceList';
import { PreflightTable } from '../../../components/PreflightTable';

export default function ProjectPage({ params }: { params: { id: string } }) {
  const projectId = params.id;
  const [citationSlots, setCitationSlots] = useState<CitationSlot[]>([]);
  const [references, setReferences] = useState<Reference[]>([]);
  const [preflight, setPreflight] = useState<PreflightReport | null>(null);
  const [mainTex, setMainTex] = useState<string>('');
  const [artifacts, setArtifacts] = useState<Record<string, string>>({});
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const refreshArtifacts = async () => {
    try {
      const bundle = await fetchArtifacts(projectId);
      setArtifacts(bundle.files);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    refreshArtifacts();
  }, []);

  const handleDetectCitations = async () => {
    const response = await triggerCitationDetection(projectId);
    setCitationSlots(response.slots);
    setActiveJobId(response.job_id ?? null);
    setMessage('Citation detection triggered. Review highlighted sentences.');
  };

  const handleReferenceSearch = async () => {
    const response = await triggerReferenceSearch(projectId);
    setReferences(response.references);
    setActiveJobId(response.job_id ?? null);
    setMessage('Reference search started across Crossref, OpenAlex, PubMed, and arXiv.');
    refreshArtifacts();
  };

  const handleFormat = async () => {
    const response = await triggerFormat(projectId);
    setMainTex(response.main_tex);
    setActiveJobId(response.job_id ?? null);
    setMessage('Formatting completed. Inspect the LaTeX draft below.');
    refreshArtifacts();
  };

  const handleCompile = async () => {
    const response = await triggerCompile(projectId);
    setActiveJobId(response.job_id ?? null);
    setMessage(`Compilation finished. PDF stored at ${response.pdf_path ?? 'pending'}.`);
    refreshArtifacts();
  };

  const handlePreflight = async () => {
    const response = await triggerPreflight(projectId);
    setPreflight(response.report);
    setActiveJobId(response.job_id ?? null);
    setMessage('Preflight checks generated.');
    refreshArtifacts();
  };

  return (
    <div className="space-y-8">
      <header className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Project {projectId}</h1>
          <p className="text-sm text-slate-400">
            Use the workflow actions to analyze structure, audit citations, and build a submission package.
          </p>
        </div>
        <div className="flex flex-wrap gap-2 text-sm">
          <button onClick={handleDetectCitations} className="rounded bg-slate-800 px-3 py-2 hover:bg-slate-700">
            Detect Citations
          </button>
          <button onClick={handleReferenceSearch} className="rounded bg-slate-800 px-3 py-2 hover:bg-slate-700">
            Search References
          </button>
          <button onClick={handleFormat} className="rounded bg-slate-800 px-3 py-2 hover:bg-slate-700">
            Format &amp; Render
          </button>
          <button onClick={handleCompile} className="rounded bg-slate-800 px-3 py-2 hover:bg-slate-700">
            Compile PDF
          </button>
          <button onClick={handlePreflight} className="rounded bg-slate-800 px-3 py-2 hover:bg-slate-700">
            Preflight Report
          </button>
        </div>
      </header>

      {message && <div className="rounded border border-cyan-500/60 bg-cyan-900/20 p-3 text-sm text-cyan-100">{message}</div>}

      <section className="grid gap-6 md:grid-cols-2">
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-white">Citation Recommendations</h2>
          <ul className="space-y-2 text-sm">
            {citationSlots.map((slot, idx) => (
              <li key={idx} className={`rounded border p-3 ${slot.need_citation ? 'border-amber-500 bg-amber-900/30' : 'border-slate-800 bg-slate-900/40'}`}>
                <p className="text-slate-100">{slot.sentence}</p>
                <p className="text-xs text-slate-300">Confidence: {(slot.confidence * 100).toFixed(0)}%</p>
                {slot.need_citation && (
                  <p className="text-xs text-amber-200">Reasons: {slot.reasons.join(', ')}</p>
                )}
              </li>
            ))}
            {citationSlots.length === 0 && <li className="text-slate-500">Run detection to populate citation slots.</li>}
          </ul>
        </div>
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-white">References</h2>
          <ReferenceList references={references} />
        </div>
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-semibold text-white">LaTeX Draft</h2>
        <div className="rounded border border-slate-800 bg-black/50 p-3 font-mono text-xs leading-relaxed text-slate-100">
          {mainTex ? mainTex : 'Run formatting to view the generated LaTeX.'}
        </div>
      </section>

      <section className="grid gap-6 md:grid-cols-[2fr_1fr]">
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-white">Preflight Checks</h2>
          <PreflightTable report={preflight} />
        </div>
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-white">Live Task Logs</h2>
          <JobLogViewer jobId={activeJobId} />
        </div>
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-semibold text-white">Artifacts</h2>
        <ul className="text-sm text-cyan-300">
          {Object.entries(artifacts).map(([key, value]) => (
            <li key={key}>
              <span className="text-slate-300">{key}:</span> <code className="text-xs">{value}</code>
            </li>
          ))}
          {Object.keys(artifacts).length === 0 && <li className="text-slate-500">No artifacts yet.</li>}
        </ul>
        <Link href="/" className="text-xs text-slate-400 underline hover:text-slate-200">
          ← Back to dashboard
        </Link>
      </section>
    </div>
  );
}
