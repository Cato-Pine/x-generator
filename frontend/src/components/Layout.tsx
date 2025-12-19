import { Link, useLocation } from 'react-router-dom';

const navItems = [
  { path: '/', label: 'Dashboard', icon: '📊' },
  { path: '/generate', label: 'Generate', icon: '✨' },
  { path: '/approval', label: 'Pending', icon: '✅' },
  { path: '/queue', label: 'Queue', icon: '📋' },
  { path: '/posted', label: 'Posted', icon: '📤' },
  { path: '/trending', label: 'Trending', icon: '🔥' },
  { path: '/posts', label: 'All Posts', icon: '📝' },
  { path: '/settings', label: 'Settings', icon: '⚙️' },
];

export function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation();

  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-800 text-white flex-shrink-0">
        <div className="p-4 border-b border-gray-700">
          <h1 className="text-xl font-bold">x-generator</h1>
          <p className="text-sm text-gray-400">Stoic Content Generator</p>
        </div>
        <nav className="p-4">
          <ul className="space-y-2">
            {navItems.map((item) => (
              <li key={item.path}>
                <Link
                  to={item.path}
                  className={`flex items-center gap-3 px-4 py-2 rounded-lg transition-colors ${
                    location.pathname === item.path
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-300 hover:bg-gray-700'
                  }`}
                >
                  <span>{item.icon}</span>
                  <span>{item.label}</span>
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      </aside>

      {/* Main content */}
      <main className="flex-1 bg-gray-100 dark:bg-gray-900">
        <div className="p-8">{children}</div>
      </main>
    </div>
  );
}
