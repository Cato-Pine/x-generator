import { useQuery } from '@tanstack/react-query';
import { queueApi, postsApi } from '../api/client';

export function Posted() {
  const { data: queue, isLoading: queueLoading } = useQuery({
    queryKey: ['queue'],
    queryFn: () => queueApi.getAll().then(res => res.data),
  });

  const { data: posts } = useQuery({
    queryKey: ['posts'],
    queryFn: () => postsApi.getAll().then(res => res.data),
  });

  const postedItems = queue?.filter(item => item.status === 'posted') ?? [];

  const getPostContent = (postId: string) => {
    const post = posts?.find(p => p.id === postId);
    return post?.content || 'Loading...';
  };

  const getPostVirtue = (postId: string) => {
    const post = posts?.find(p => p.id === postId);
    return post?.virtue;
  };

  if (queueLoading) {
    return <div className="text-gray-600">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Posted</h1>
        <p className="text-gray-600 dark:text-gray-400">
          {postedItems.length} posts published
        </p>
      </div>

      <div className="space-y-4">
        {postedItems.map((item) => (
          <div key={item.id} className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            {/* Header */}
            <div className="flex justify-between items-start mb-4">
              <div className="flex items-center gap-3">
                <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">
                  Posted
                </span>
                {getPostVirtue(item.post_id) && (
                  <span className="px-2 py-1 text-xs rounded-full bg-purple-100 text-purple-800">
                    {getPostVirtue(item.post_id)}
                  </span>
                )}
              </div>
              <span className="text-sm text-gray-500">
                {item.scheduled_for
                  ? new Date(item.scheduled_for).toLocaleString()
                  : 'Unknown date'}
              </span>
            </div>

            {/* Post Content */}
            <p className="text-gray-800 dark:text-gray-200 whitespace-pre-wrap leading-relaxed">
              {getPostContent(item.post_id)}
            </p>
          </div>
        ))}
        {postedItems.length === 0 && (
          <div className="text-center py-12 text-gray-500 bg-white dark:bg-gray-800 rounded-lg">
            No posts have been published yet.
          </div>
        )}
      </div>
    </div>
  );
}
