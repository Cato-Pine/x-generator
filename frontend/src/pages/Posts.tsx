import { useState } from 'react';
import { usePosts, useApprovePost, useRejectPost, useDeletePost, useUpdatePost } from '../hooks/usePosts';
import type { Post } from '../api/client';

const statusOptions = [
  { value: '', label: 'All' },
  { value: 'pending_review', label: 'Pending Review' },
  { value: 'approved', label: 'Approved' },
  { value: 'posted', label: 'Posted' },
  { value: 'rejected', label: 'Rejected' },
];

export function Posts() {
  const [statusFilter, setStatusFilter] = useState('');
  const { data: posts, isLoading } = usePosts(statusFilter || undefined);

  if (isLoading) {
    return <div className="text-gray-600">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Posts</h1>
          <p className="text-gray-600 dark:text-gray-400">
            {posts?.length || 0} posts found
          </p>
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-4 py-2 border rounded-lg bg-white dark:bg-gray-800 dark:text-white"
        >
          {statusOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      <div className="space-y-4">
        {posts?.map((post) => (
          <PostCard key={post.id} post={post} />
        ))}
        {posts?.length === 0 && (
          <div className="text-center py-12 text-gray-500 bg-white dark:bg-gray-800 rounded-lg">
            No posts found
          </div>
        )}
      </div>
    </div>
  );
}

function PostCard({ post }: { post: Post }) {
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState(post.content);
  const approvePost = useApprovePost();
  const rejectPost = useRejectPost();
  const deletePost = useDeletePost();
  const updatePost = useUpdatePost();

  const handleSave = () => {
    updatePost.mutate(
      { id: post.id, data: { content: editContent } },
      {
        onSuccess: () => setIsEditing(false),
      }
    );
  };

  const handleCancel = () => {
    setEditContent(post.content);
    setIsEditing(false);
  };

  const charCount = editContent.length;
  const isOverLimit = charCount > 280;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      {/* Header */}
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center gap-3">
          <StatusBadge status={post.status} />
          {post.virtue && (
            <span className="px-2 py-1 text-xs bg-purple-100 text-purple-800 rounded">
              {post.virtue}
            </span>
          )}
          <span className="text-sm text-gray-500">
            {new Date(post.created_at).toLocaleString()}
          </span>
        </div>
        <div className="flex gap-2">
          {!isEditing && (
            <button
              onClick={() => setIsEditing(true)}
              className="text-blue-600 hover:text-blue-800 text-sm font-medium"
            >
              Edit
            </button>
          )}
          <button
            onClick={() => {
              if (confirm('Delete this post?')) {
                deletePost.mutate(post.id);
              }
            }}
            className="text-gray-400 hover:text-red-600 text-sm"
          >
            Delete
          </button>
        </div>
      </div>

      {/* Content */}
      {isEditing ? (
        <div className="space-y-3">
          <textarea
            value={editContent}
            onChange={(e) => setEditContent(e.target.value)}
            className={`w-full p-4 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:text-white resize-none font-mono text-sm ${
              isOverLimit ? 'border-red-500' : 'border-gray-200'
            }`}
            rows={6}
          />
          <div className="flex justify-between items-center">
            <span className={`text-sm ${isOverLimit ? 'text-red-600' : 'text-gray-500'}`}>
              {charCount}/280 characters
            </span>
            <div className="flex gap-2">
              <button
                onClick={handleCancel}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 text-sm"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={updatePost.isPending || isOverLimit}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50"
              >
                {updatePost.isPending ? 'Saving...' : 'Save'}
              </button>
            </div>
          </div>
        </div>
      ) : (
        <p className="text-gray-800 dark:text-gray-200 whitespace-pre-wrap leading-relaxed">
          {post.content}
        </p>
      )}

      {/* Actions */}
      {post.status === 'pending_review' && !isEditing && (
        <div className="flex gap-3 mt-4 pt-4 border-t border-gray-100 dark:border-gray-700">
          <button
            onClick={() => approvePost.mutate(post.id)}
            disabled={approvePost.isPending}
            className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700 disabled:opacity-50"
          >
            {approvePost.isPending ? 'Approving...' : 'Approve'}
          </button>
          <button
            onClick={() => rejectPost.mutate(post.id)}
            disabled={rejectPost.isPending}
            className="px-4 py-2 bg-red-100 text-red-700 rounded-lg text-sm hover:bg-red-200 disabled:opacity-50"
          >
            {rejectPost.isPending ? 'Rejecting...' : 'Reject'}
          </button>
        </div>
      )}

      {/* Posted info */}
      {post.status === 'posted' && post.x_post_id && (
        <div className="mt-4 pt-4 border-t border-gray-100 dark:border-gray-700">
          <a
            href={`https://x.com/i/status/${post.x_post_id}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:underline text-sm"
          >
            View on X →
          </a>
        </div>
      )}
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    pending_review: 'bg-yellow-100 text-yellow-800',
    approved: 'bg-green-100 text-green-800',
    posted: 'bg-blue-100 text-blue-800',
    rejected: 'bg-red-100 text-red-800',
    recycled: 'bg-purple-100 text-purple-800',
  };

  return (
    <span className={`px-2 py-1 text-xs rounded-full ${colors[status] || 'bg-gray-100'}`}>
      {status.replace('_', ' ')}
    </span>
  );
}
