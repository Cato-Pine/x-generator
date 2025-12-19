import { usePosts } from '../hooks/usePosts';
import { useSettings } from '../hooks/useSettings';

export function Dashboard() {
  const { data: posts, isLoading: postsLoading } = usePosts();
  const { data: settings, isLoading: settingsLoading } = useSettings();

  const pendingCount = posts?.filter(p => p.status === 'pending_review').length || 0;
  const approvedCount = posts?.filter(p => p.status === 'approved').length || 0;
  const postedCount = posts?.filter(p => p.status === 'posted').length || 0;

  const schedulerSettings = settings?.find(s => s.key === 'scheduler')?.value;

  if (postsLoading || settingsLoading) {
    return <div className="text-gray-600">Loading...</div>;
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <p className="text-gray-600 dark:text-gray-400">Overview of your Stoic content generator</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard
          title="Pending Review"
          value={pendingCount}
          color="yellow"
        />
        <StatCard
          title="Approved"
          value={approvedCount}
          color="green"
        />
        <StatCard
          title="Posted"
          value={postedCount}
          color="blue"
        />
        <StatCard
          title="Scheduler"
          value={schedulerSettings?.enabled ? 'Active' : 'Paused'}
          color={schedulerSettings?.enabled ? 'green' : 'gray'}
        />
      </div>

      {/* Recent Posts */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
          Recent Posts
        </h2>
        <div className="space-y-4">
          {posts?.slice(0, 5).map((post) => (
            <div
              key={post.id}
              className="border-b border-gray-200 dark:border-gray-700 pb-4 last:border-0"
            >
              <p className="text-gray-800 dark:text-gray-200">{post.content}</p>
              <div className="flex gap-4 mt-2 text-sm">
                <span className={`px-2 py-1 rounded ${getStatusColor(post.status)}`}>
                  {post.status}
                </span>
                {post.virtue && (
                  <span className="text-gray-500">{post.virtue}</span>
                )}
                <span className="text-gray-400">
                  {new Date(post.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, color }: { title: string; value: string | number; color: string }) {
  const colorClasses: Record<string, string> = {
    yellow: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    green: 'bg-green-100 text-green-800 border-green-200',
    blue: 'bg-blue-100 text-blue-800 border-blue-200',
    gray: 'bg-gray-100 text-gray-800 border-gray-200',
  };

  return (
    <div className={`p-6 rounded-lg border ${colorClasses[color]}`}>
      <h3 className="text-sm font-medium opacity-80">{title}</h3>
      <p className="text-3xl font-bold mt-2">{value}</p>
    </div>
  );
}

function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    pending_review: 'bg-yellow-100 text-yellow-800',
    approved: 'bg-green-100 text-green-800',
    posted: 'bg-blue-100 text-blue-800',
    rejected: 'bg-red-100 text-red-800',
    recycled: 'bg-purple-100 text-purple-800',
  };
  return colors[status] || 'bg-gray-100 text-gray-800';
}
