'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { MarkdownEditor } from '../components/MarkdownEditor';
import { TemplateSelector } from '../components/TemplateSelector';
import { createProject } from '../lib/api';
import { Template } from '../lib/types';

const placeholder = `# Title\n\nStart writing your manuscript in Markdown or paste content here. ManuWeaver will normalize headings, math, and citations.`;

export default function HomePage() {
  const router = useRouter();
  const [markdown, setMarkdown] = useState(placeholder);
  const [template, setTemplate] = useState<Template | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (!template) {
      setError('Select a template to continue.');
      return;
    }
    setError(null);
    setIsSubmitting(true);
    try {
      const project = await createProject(markdown, template.identifier);
      router.push(`/projects/${project.id}`);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-8">
      <section>
        <h1 className="text-3xl font-bold text-white">Create a Manuscript Project</h1>
        <p className="mt-2 max-w-2xl text-slate-300">
          Import Markdown, select a journal template, and ManuWeaver will orchestrate structural analysis, citation audits, and LaTeX compilation.
        </p>
      </section>
      <section className="grid gap-6 md:grid-cols-2">
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-white">1. Draft Manuscript</h2>
          <MarkdownEditor value={markdown} onChange={setMarkdown} height="420px" />
        </div>
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-white">2. Select Template</h2>
          <TemplateSelector selected={template?.identifier} onSelect={setTemplate} />
        </div>
      </section>
      {error && <div className="rounded border border-red-500 bg-red-900/40 p-3 text-sm text-red-100">{error}</div>}
      <button
        onClick={handleSubmit}
        disabled={isSubmitting}
        className="rounded bg-cyan-500 px-6 py-3 text-sm font-semibold text-black transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:bg-slate-600"
      >
        {isSubmitting ? 'Creating…' : 'Create Project'}
      </button>
    </div>
  );
}
