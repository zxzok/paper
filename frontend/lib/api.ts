'use client';

import { createParser } from 'eventsource-parser';
import { CitationSlot, ProjectCreateResponse, Reference, PreflightReport } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000';

async function jsonFetch<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options?.headers ?? {})
    },
    cache: 'no-store'
  });
  if (!res.ok) {
    throw new Error(`API request failed: ${res.status}`);
  }
  return (await res.json()) as T;
}

export async function createProject(manuscript: string, templateId: string): Promise<ProjectCreateResponse> {
  return jsonFetch<ProjectCreateResponse>(`${API_BASE}/api/projects`, {
    method: 'POST',
    body: JSON.stringify({ manuscript_text: manuscript, template_id: templateId })
  });
}

export async function triggerCitationDetection(projectId: string) {
  return jsonFetch<{ project_id: string; slots: CitationSlot[]; job_id?: string }>(
    `${API_BASE}/api/projects/${projectId}/detect-citations`,
    { method: 'POST' }
  );
}

export async function triggerReferenceSearch(projectId: string) {
  return jsonFetch<{ project_id: string; references: Reference[]; job_id?: string }>(
    `${API_BASE}/api/projects/${projectId}/search-refs`,
    { method: 'POST' }
  );
}

export async function triggerFormat(projectId: string) {
  return jsonFetch<{ project_id: string; main_tex: string; job_id?: string }>(`${API_BASE}/api/projects/${projectId}/format`, {
    method: 'POST'
  });
}

export async function triggerCompile(projectId: string) {
  return jsonFetch<{ project_id: string; pdf_path?: string; job_id?: string }>(
    `${API_BASE}/api/projects/${projectId}/compile`,
    { method: 'POST', body: JSON.stringify({}) }
  );
}

export async function triggerPreflight(projectId: string) {
  return jsonFetch<{ project_id: string; report: PreflightReport; job_id?: string }>(
    `${API_BASE}/api/projects/${projectId}/preflight`,
    { method: 'POST' }
  );
}

export async function fetchArtifacts(projectId: string) {
  return jsonFetch<{ project_id: string; files: Record<string, string> }>(`${API_BASE}/api/projects/${projectId}/artifacts`);
}

export function streamJob(jobId: string, onMessage: (line: string) => void, signal?: AbortSignal) {
  const url = `${API_BASE}/api/jobs/${jobId}/stream`;
  fetch(url, { signal }).then(async (res) => {
    if (!res.body) return;
    const reader = res.body.getReader();
    const parser = createParser((event) => {
      if (event.type === 'event' && event.data) {
        if (event.data === '__COMPLETE__') return;
        onMessage(event.data);
      }
    });
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const chunk = new TextDecoder().decode(value);
      parser.feed(chunk);
    }
  });
}
