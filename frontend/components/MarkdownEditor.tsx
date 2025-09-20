'use client';

import React from 'react';
import CodeMirror from '@uiw/react-codemirror';
import { markdown } from '@codemirror/lang-markdown';
import { oneDark } from '@codemirror/theme-one-dark';

type Props = {
  value: string;
  onChange: (value: string) => void;
  height?: string;
};

export function MarkdownEditor({ value, onChange, height = '400px' }: Props) {
  return (
    <CodeMirror
      value={value}
      height={height}
      extensions={[markdown()]}
      onChange={onChange}
      theme={oneDark}
    />
  );
}
