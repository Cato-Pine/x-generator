import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { postsApi } from '../api/client';
import type { Post } from '../api/client';

export function Approval() {
  const queryClient = useQueryClient();
  const [processingIds, setProcessingIds] = useState<Set<string>>(new Set());

  const { data: posts, isLoading } = useQuery({
    queryKey: ['posts', 'pending'],
    queryFn: () => postsApi.getAll('pending').then(res => res.data),
  });

  const approveMutation = useMutation({
    mutationFn: (id: string) => postsApi.approve(id),
    onMutate: (id) => {
      setProcessingIds(prev => new Set(prev).add(id));
    },
    onSuccess: (_data, id) => {
      // Remove from local cache immediately
      queryClient.setQueryData(['posts', 'pending'], (old: Post[] | undefined) =>
        old?.filter(p => p.id !== id) ?? []
      );
      queryClient.invalidateQueries({ queryKey: ['queue'] });
    },
    onSettled: (_data, _error, id) => {
      setProcessingIds(prev => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    },
  });

  const rejectMutation = useMutation({
    mutationFn: (id: string) => postsApi.reject(id),
    onMutate: (id) => {
      setProcessingIds(prev => new Set(prev).add(id));
    },
    onSuccess: (_data, id) => {
      // Remove from local cache immediately
      queryClient.setQueryData(['posts', 'pending'], (old: Post[] | undefined) =>
        old?.filter(p => p.id !== id) ?? []
      );
    },
    onSettled: (_data, _error, id) => {
      setProcessingIds(prev => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    },
  });

  // Filter out posts being processed
  const visiblePosts = posts?.filter(p => !processingIds.has(p.id));

  if (isLoading) {
    return <div className="text-gray-600">Loading pending posts...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Pending Approval</h1>
        <p className="text-gray-600 dark:text-gray-400">
          {visiblePosts?.length || 0} posts awaiting approval
        </p>
      </div>

      <div className="space-y-4">
        {visiblePosts?.map((post) => (
          <ApprovalCard
            key={post.id}
            post={post}
            onApprove={() => approveMutation.mutate(post.id)}
            onReject={() => rejectMutation.mutate(post.id)}
          />
        ))}
        {visiblePosts?.length === 0 && (
          <div className="text-center py-12 text-gray-500 bg-white dark:bg-gray-800 rounded-lg">
            No posts pending approval. Generate some content first!
          </div>
        )}
      </div>
    </div>
  );
}

function ApprovalCard({
  post,
  onApprove,
  onReject,
}: {
  post: Post;
  onApprove: () => void;
  onReject: () => void;
}) {
  const [editedContent, setEditedContent] = useState(post.content);
  const [isEditing, setIsEditing] = useState(false);
  const queryClient = useQueryClient();

  const updateMutation = useMutation({
    mutationFn: (content: string) => postsApi.update(post.id, { content }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['posts'] });
      setIsEditing(false);
    },
  });

  const handleSave = () => {
    if (editedContent !== post.content) {
      updateMutation.mutate(editedContent);
    } else {
      setIsEditing(false);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      {/* Header */}
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center gap-3">
          {post.virtue && (
            <span className="px-2 py-1 text-xs rounded-full bg-purple-100 text-purple-800">
              {post.virtue}
            </span>
          )}
          {post.post_type && (
            <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
              {post.post_type}
            </span>
          )}
          <span className="text-sm text-gray-500">
            {new Date(post.created_at).toLocaleDateString()}
          </span>
        </div>
        <span className={`text-sm ${editedContent.length > 280 ? 'text-red-600 font-medium' : 'text-gray-500'}`}>
          {editedContent.length}/280
        </span>
      </div>

      {/* Content */}
      {isEditing ? (
        <div className="space-y-3">
          <textarea
            value={editedContent}
            onChange={(e) => setEditedContent(e.target.value)}
            className="w-full p-4 border rounded-lg bg-white dark:bg-gray-700 dark:text-white resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={4}
          />
          <div className="flex gap-2">
            <button
              onClick={handleSave}
              disabled={updateMutation.isPending}
              className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 disabled:opacity-50"
            >
              {updateMutation.isPending ? 'Saving...' : 'Save'}
            </button>
            <button
              onClick={() => {
                setEditedContent(post.content);
                setIsEditing(false);
              }}
              className="px-3 py-1 text-gray-600 hover:text-gray-800 text-sm"
            >
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <p
          onClick={() => setIsEditing(true)}
          className="text-gray-800 dark:text-gray-200 whitespace-pre-wrap leading-relaxed mb-4 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 p-2 -m-2 rounded"
          title="Click to edit"
        >
          {post.content}
        </p>
      )}

      {/* Actions */}
      {!isEditing && (
        <div className="flex gap-3 pt-4 border-t border-gray-100 dark:border-gray-700">
          <button
            onClick={onApprove}
            disabled={editedContent.length > 280}
            className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700 disabled:opacity-50"
          >
            Approve
          </button>
          <button
            onClick={onReject}
            className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700"
          >
            Reject
          </button>
        </div>
      )}
    </div>
  );
}
