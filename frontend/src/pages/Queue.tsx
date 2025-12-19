import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { queueApi, postsApi } from '../api/client';

export function Queue() {
  const queryClient = useQueryClient();
  const { data: queue, isLoading: queueLoading } = useQuery({
    queryKey: ['queue'],
    queryFn: () => queueApi.getAll().then(res => res.data),
  });

  const { data: posts } = useQuery({
    queryKey: ['posts'],
    queryFn: () => postsApi.getAll().then(res => res.data),
  });

  const cancelItem = useMutation({
    mutationFn: (id: string) => queueApi.cancel(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['queue'] });
    },
  });

  const getPostContent = (postId: string) => {
    const post = posts?.find(p => p.id === postId);
    return post?.content || 'Loading...';
  };

  if (queueLoading) {
    return <div className="text-gray-600">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Queue</h1>
        <p className="text-gray-600 dark:text-gray-400">
          {queue?.length || 0} posts scheduled
        </p>
      </div>

      <div className="space-y-4">
        {queue?.map((item) => (
          <div key={item.id} className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            {/* Header */}
            <div className="flex justify-between items-start mb-4">
              <div className="flex items-center gap-3">
                <StatusBadge status={item.status} />
                <span className="text-sm text-gray-500">
                  {item.scheduled_for
                    ? `Scheduled: ${new Date(item.scheduled_for).toLocaleString()}`
                    : 'Not scheduled'}
                </span>
              </div>
              {item.status === 'pending' && (
                <button
                  onClick={() => cancelItem.mutate(item.id)}
                  className="text-red-600 hover:text-red-800 text-sm font-medium"
                  disabled={cancelItem.isPending}
                >
                  Cancel
                </button>
              )}
            </div>

            {/* Post Content */}
            <p className="text-gray-800 dark:text-gray-200 whitespace-pre-wrap leading-relaxed">
              {getPostContent(item.post_id)}
            </p>

            {/* Error Message */}
            {item.error_message && (
              <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm">
                Error: {item.error_message}
              </div>
            )}
          </div>
        ))}
        {queue?.length === 0 && (
          <div className="text-center py-12 text-gray-500 bg-white dark:bg-gray-800 rounded-lg">
            Queue is empty. Approve posts to add them to the queue.
          </div>
        )}
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    pending: 'bg-yellow-100 text-yellow-800',
    posted: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
    cancelled: 'bg-gray-100 text-gray-800',
  };

  return (
    <span className={`px-2 py-1 text-xs rounded-full ${colors[status] || 'bg-gray-100'}`}>
      {status}
    </span>
  );
}
