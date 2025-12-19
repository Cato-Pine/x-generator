import { useState } from 'react';
import { useGenerate } from '../hooks/useGenerate';
import type { GenerateRequest } from '../api/client';

const virtues = [
  { value: '', label: 'Random' },
  { value: 'wisdom', label: 'Wisdom' },
  { value: 'courage', label: 'Courage' },
  { value: 'justice', label: 'Justice' },
  { value: 'temperance', label: 'Temperance' },
  { value: 'general', label: 'General' },
];

const formats = [
  { value: 'short', label: 'Short (single tweet)' },
  { value: 'thread', label: 'Thread (multi-tweet)' },
  { value: 'long', label: 'Long (280 chars)' },
];

export function Generate() {
  const [virtue, setVirtue] = useState('');
  const [formatType, setFormatType] = useState<'short' | 'thread' | 'long'>('short');
  const [topic, setTopic] = useState('');
  const generate = useGenerate();

  const handleGenerate = () => {
    const request: GenerateRequest = {
      format_type: formatType,
    };
    if (virtue) request.virtue = virtue;
    if (topic) request.topic = topic;

    generate.mutate(request);
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Generate Content</h1>
        <p className="text-gray-600 dark:text-gray-400">Create new Stoic content with AI</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Options */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 space-y-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Options</h2>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Virtue
            </label>
            <select
              value={virtue}
              onChange={(e) => setVirtue(e.target.value)}
              className="w-full px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 dark:text-white"
            >
              {virtues.map((v) => (
                <option key={v.value} value={v.value}>
                  {v.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Format
            </label>
            <select
              value={formatType}
              onChange={(e) => setFormatType(e.target.value as any)}
              className="w-full px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 dark:text-white"
            >
              {formats.map((f) => (
                <option key={f.value} value={f.value}>
                  {f.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Topic (optional)
            </label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., dealing with adversity"
              className="w-full px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 dark:text-white"
            />
          </div>

          <button
            onClick={handleGenerate}
            disabled={generate.isPending}
            className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {generate.isPending ? 'Generating...' : 'Generate Content'}
          </button>
        </div>

        {/* Result */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Result</h2>

          {generate.isPending && (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          )}

          {generate.isError && (
            <div className="bg-red-100 text-red-800 p-4 rounded-lg">
              Error: {generate.error?.message || 'Failed to generate'}
            </div>
          )}

          {generate.data && (
            <div className="space-y-4">
              <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                <p className="text-gray-900 dark:text-white whitespace-pre-wrap">
                  {generate.data.content}
                </p>
              </div>

              <div className="flex flex-wrap gap-2 text-sm">
                <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded">
                  {generate.data.virtue}
                </span>
                <span className="px-2 py-1 bg-gray-100 text-gray-800 rounded">
                  {generate.data.format_type}
                </span>
                <span className="px-2 py-1 bg-green-100 text-green-800 rounded">
                  {generate.data.tweet_count} tweet(s)
                </span>
                <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded">
                  {generate.data.model}
                </span>
              </div>

              <p className="text-sm text-gray-500">
                Saved as post ID: {generate.data.post_id}
              </p>
            </div>
          )}

          {!generate.isPending && !generate.data && !generate.isError && (
            <p className="text-gray-500 text-center py-12">
              Click "Generate Content" to create new Stoic wisdom
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
