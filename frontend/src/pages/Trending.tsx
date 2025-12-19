import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { trendingApi, generateApi, schedulerApi, postsApi } from '../api/client';
import type { TrendingPost, GenerateReplyRequest } from '../api/client';

const virtues = [
  { value: '', label: 'Auto' },
  { value: 'wisdom', label: 'Wisdom' },
  { value: 'courage', label: 'Courage' },
  { value: 'justice', label: 'Justice' },
  { value: 'temperance', label: 'Temperance' },
];

export function Trending() {
  const [selectedTweet, setSelectedTweet] = useState<TrendingPost | null>(null);
  const [replyVirtue, setReplyVirtue] = useState('');
  const [editedReply, setEditedReply] = useState('');
  const [generatedPostId, setGeneratedPostId] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const { data: trending, isLoading, refetch } = useQuery({
    queryKey: ['trending'],
    queryFn: () => trendingApi.getAll(20, true).then(res => res.data),
  });

  const skipTweet = useMutation({
    mutationFn: (tweetId: string) => trendingApi.skip(tweetId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['trending'] });
    },
  });

  const generateReply = useMutation({
    mutationFn: (data: GenerateReplyRequest) => generateApi.generateReply(data).then(res => res.data),
    onSuccess: (data) => {
      setEditedReply(data.content);
      setGeneratedPostId(data.post_id);
      queryClient.invalidateQueries({ queryKey: ['posts'] });
    },
  });

  const postNow = useMutation({
    mutationFn: async (postId: string) => {
      // First update the post content if edited
      if (editedReply) {
        await postsApi.update(postId, { content: editedReply });
      }
      // Approve the post
      await postsApi.approve(postId);
      // Post immediately
      return schedulerApi.postNow(postId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['posts'] });
      queryClient.invalidateQueries({ queryKey: ['queue'] });
      queryClient.invalidateQueries({ queryKey: ['trending'] });
      if (selectedTweet) {
        trendingApi.markReplied(selectedTweet.tweet_id);
      }
      setSelectedTweet(null);
      setEditedReply('');
      setGeneratedPostId(null);
    },
  });

  const handleGenerateReply = (tweet: TrendingPost) => {
    setSelectedTweet(tweet);
    setEditedReply('');
    setGeneratedPostId(null);
    generateReply.mutate({
      tweet_id: tweet.tweet_id,
      tweet_text: tweet.content,
      username: tweet.username,
      virtue: replyVirtue || undefined,
    });
  };

  if (isLoading) {
    return <div className="text-gray-600">Loading trending posts...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Trending</h1>
          <p className="text-gray-600 dark:text-gray-400">
            {trending?.length || 0} trending posts found
          </p>
        </div>
        <div className="flex gap-3">
          <select
            value={replyVirtue}
            onChange={(e) => setReplyVirtue(e.target.value)}
            className="px-4 py-2 border rounded-lg bg-white dark:bg-gray-800 dark:text-white"
          >
            {virtues.map((v) => (
              <option key={v.value} value={v.value}>
                Reply as: {v.label}
              </option>
            ))}
          </select>
          <button
            onClick={() => refetch()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Reply Modal */}
      {selectedTweet && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <div className="flex justify-between items-start">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Generate Reply
                </h2>
                <button
                  onClick={() => setSelectedTweet(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
            </div>

            <div className="p-6 space-y-4">
              {/* Original Tweet */}
              <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                <p className="text-sm text-gray-500 mb-2">
                  @{selectedTweet.username}
                </p>
                <p className="text-gray-800 dark:text-gray-200 whitespace-pre-wrap">
                  {selectedTweet.content}
                </p>
              </div>

              {/* Generated Reply */}
              {generateReply.isPending && (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <span className="ml-3 text-gray-600">Generating reply...</span>
                </div>
              )}

              {generateReply.isError && (
                <div className="bg-red-100 text-red-800 p-4 rounded-lg">
                  Error: {generateReply.error?.message || 'Failed to generate reply'}
                </div>
              )}

              {editedReply && (
                <div className="space-y-3">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Your Reply (edit if needed)
                  </label>
                  <textarea
                    value={editedReply}
                    onChange={(e) => setEditedReply(e.target.value)}
                    className="w-full p-4 border rounded-lg bg-white dark:bg-gray-700 dark:text-white resize-none"
                    rows={4}
                  />
                  <div className="flex justify-between items-center">
                    <span className={`text-sm ${editedReply.length > 280 ? 'text-red-600' : 'text-gray-500'}`}>
                      {editedReply.length}/280 characters
                    </span>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleGenerateReply(selectedTweet)}
                        className="px-4 py-2 text-blue-600 hover:text-blue-800"
                        disabled={generateReply.isPending || postNow.isPending}
                      >
                        Regenerate
                      </button>
                      <button
                        onClick={() => setSelectedTweet(null)}
                        className="px-4 py-2 text-gray-600 hover:text-gray-800"
                      >
                        Save for later
                      </button>
                      <button
                        onClick={() => generatedPostId && postNow.mutate(generatedPostId)}
                        disabled={!generatedPostId || editedReply.length > 280 || postNow.isPending}
                        className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                      >
                        {postNow.isPending ? 'Posting...' : 'Post Now'}
                      </button>
                    </div>
                  </div>

                  {postNow.isError && (
                    <div className="bg-red-100 text-red-800 p-3 rounded-lg text-sm">
                      Error posting: {(postNow.error as Error)?.message || 'Failed to post'}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Trending Posts */}
      <div className="space-y-4">
        {trending?.map((tweet) => (
          <TrendingCard
            key={tweet.tweet_id}
            tweet={tweet}
            onReply={() => handleGenerateReply(tweet)}
            onSkip={() => skipTweet.mutate(tweet.tweet_id)}
            isGenerating={generateReply.isPending && selectedTweet?.tweet_id === tweet.tweet_id}
          />
        ))}
        {trending?.length === 0 && (
          <div className="text-center py-12 text-gray-500 bg-white dark:bg-gray-800 rounded-lg">
            No trending posts found. Check your TwitterAPI.io key or topics configuration.
          </div>
        )}
      </div>
    </div>
  );
}

function TrendingCard({
  tweet,
  onReply,
  onSkip,
  isGenerating,
}: {
  tweet: TrendingPost;
  onReply: () => void;
  onSkip: () => void;
  isGenerating: boolean;
}) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      {/* Header */}
      <div className="flex justify-between items-start mb-3">
        <a
          href={`https://x.com/${tweet.username}`}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 hover:underline font-medium"
        >
          @{tweet.username}
        </a>
        <div className="flex gap-4 text-sm text-gray-500">
          {tweet.likes !== undefined && tweet.likes !== null && (
            <span>❤️ {tweet.likes.toLocaleString()}</span>
          )}
          {tweet.retweets !== undefined && tweet.retweets !== null && (
            <span>🔁 {tweet.retweets.toLocaleString()}</span>
          )}
        </div>
      </div>

      {/* Content */}
      <p className="text-gray-800 dark:text-gray-200 whitespace-pre-wrap leading-relaxed mb-4">
        {tweet.content}
      </p>

      {/* Actions */}
      <div className="flex gap-3 pt-4 border-t border-gray-100 dark:border-gray-700">
        <button
          onClick={onReply}
          disabled={isGenerating}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50"
        >
          {isGenerating ? 'Generating...' : 'Generate Reply'}
        </button>
        <button
          onClick={onSkip}
          className="px-4 py-2 text-gray-600 hover:text-gray-800 text-sm"
        >
          Skip
        </button>
        <a
          href={`https://x.com/i/status/${tweet.tweet_id}`}
          target="_blank"
          rel="noopener noreferrer"
          className="px-4 py-2 text-gray-500 hover:text-blue-600 text-sm ml-auto"
        >
          View on X →
        </a>
      </div>
    </div>
  );
}
