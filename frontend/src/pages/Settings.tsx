import { useState, useEffect } from 'react';
import { useSettings, useUpdateSetting } from '../hooks/useSettings';

export function Settings() {
  const { data: settings, isLoading } = useSettings();
  const updateSetting = useUpdateSetting();

  const schedulerSettings = settings?.find(s => s.key === 'scheduler')?.value || {};
  const generationSettings = settings?.find(s => s.key === 'generation')?.value || {};
  const rateLimits = settings?.find(s => s.key === 'rate_limits')?.value || {};

  const [scheduler, setScheduler] = useState(schedulerSettings);
  const [_generation, _setGeneration] = useState(generationSettings);
  const [limits, setLimits] = useState(rateLimits);

  useEffect(() => {
    if (settings) {
      setScheduler(settings.find(s => s.key === 'scheduler')?.value || {});
      _setGeneration(settings.find(s => s.key === 'generation')?.value || {});
      setLimits(settings.find(s => s.key === 'rate_limits')?.value || {});
    }
  }, [settings]);

  const handleSave = (key: string, value: any) => {
    updateSetting.mutate({ key, value });
  };

  if (isLoading) {
    return <div className="text-gray-600">Loading...</div>;
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Settings</h1>
        <p className="text-gray-600 dark:text-gray-400">Configure your content generator</p>
      </div>

      {/* Scheduler Settings */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          Scheduler
        </h2>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-gray-700 dark:text-gray-300">Enabled</span>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={scheduler.enabled || false}
                onChange={(e) => setScheduler({ ...scheduler, enabled: e.target.checked })}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div>
            <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
              Intervals (minutes, comma separated)
            </label>
            <input
              type="text"
              value={scheduler.intervals?.join(', ') || ''}
              onChange={(e) =>
                setScheduler({
                  ...scheduler,
                  intervals: e.target.value.split(',').map(n => parseInt(n.trim())).filter(n => !isNaN(n)),
                })
              }
              className="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:text-white"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
                Blackout Start
              </label>
              <input
                type="time"
                value={scheduler.blackout_start || '23:00'}
                onChange={(e) => setScheduler({ ...scheduler, blackout_start: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:text-white"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
                Blackout End
              </label>
              <input
                type="time"
                value={scheduler.blackout_end || '05:00'}
                onChange={(e) => setScheduler({ ...scheduler, blackout_end: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:text-white"
              />
            </div>
          </div>

          <button
            onClick={() => handleSave('scheduler', scheduler)}
            disabled={updateSetting.isPending}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            Save Scheduler Settings
          </button>
        </div>
      </div>

      {/* Rate Limits */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          Rate Limits
        </h2>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
                Daily Posts
              </label>
              <input
                type="number"
                value={limits.daily_posts || 17}
                onChange={(e) => setLimits({ ...limits, daily_posts: parseInt(e.target.value) })}
                className="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:text-white"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
                Daily Replies
              </label>
              <input
                type="number"
                value={limits.daily_replies || 10}
                onChange={(e) => setLimits({ ...limits, daily_replies: parseInt(e.target.value) })}
                className="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:text-white"
              />
            </div>
          </div>

          <button
            onClick={() => handleSave('rate_limits', limits)}
            disabled={updateSetting.isPending}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            Save Rate Limits
          </button>
        </div>
      </div>

      {updateSetting.isSuccess && (
        <div className="bg-green-100 text-green-800 p-4 rounded-lg">
          Settings saved successfully!
        </div>
      )}
    </div>
  );
}
