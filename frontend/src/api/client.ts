import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface Post {
  id: string;
  content: string;
  content_hash?: string;
  post_type: 'original' | 'reply' | 'quote';
  format_type: 'short' | 'thread' | 'long';
  virtue?: 'wisdom' | 'courage' | 'justice' | 'temperance' | 'general';
  status: 'pending_review' | 'approved' | 'posted' | 'rejected' | 'recycled';
  x_post_id?: string;
  approved_at?: string;
  posted_at?: string;
  recycle_count: number;
  created_at: string;
  updated_at: string;
}

export interface GenerateRequest {
  virtue?: string;
  format_type?: 'short' | 'thread' | 'long';
  topic?: string;
}

export interface GenerateResponse {
  content: string;
  tweets: string[];
  format_type: string;
  virtue: string;
  tweet_count: number;
  topic: string;
  model: string;
  citations?: any;
  post_id: string;
}

export interface Settings {
  key: string;
  value: any;
}

export interface QueueItem {
  id: string;
  post_id: string;
  scheduled_for: string;
  status: 'pending' | 'posted' | 'failed' | 'cancelled';
  error_message?: string;
  created_at: string;
}

export interface TrendingPost {
  tweet_id: string;
  content: string;
  username: string;
  likes?: number;
  retweets?: number;
  relevance_score?: number;
  cache_status?: string;
}

export interface GenerateReplyRequest {
  tweet_id: string;
  tweet_text: string;
  username?: string;
  virtue?: string;
}

// API functions
export const postsApi = {
  getAll: (status?: string) =>
    api.get<Post[]>('/posts', { params: { status } }),
  getById: (id: string) =>
    api.get<Post>(`/posts/${id}`),
  update: (id: string, data: Partial<Post>) =>
    api.patch<Post>(`/posts/${id}`, data),
  delete: (id: string) =>
    api.delete(`/posts/${id}`),
  approve: (id: string) =>
    api.post(`/posts/${id}/approve`),
  reject: (id: string) =>
    api.post(`/posts/${id}/reject`),
};

export const generateApi = {
  generate: (data: GenerateRequest) =>
    api.post<GenerateResponse>('/generate', data),
  generateReply: (data: GenerateReplyRequest) =>
    api.post<GenerateResponse>('/generate/reply', data),
};

export const trendingApi = {
  getAll: (limit?: number, excludeSeen?: boolean) =>
    api.get<TrendingPost[]>('/trending', { params: { limit, exclude_seen: excludeSeen } }),
  getCache: (status?: string, limit?: number) =>
    api.get<TrendingPost[]>('/trending/cache', { params: { status, limit } }),
  skip: (tweetId: string) =>
    api.post(`/trending/cache/${tweetId}/skip`),
  markReplied: (tweetId: string) =>
    api.post(`/trending/cache/${tweetId}/replied`),
  getTopics: () =>
    api.get<{ topics: string[] }>('/trending/topics'),
  updateTopics: (topics: string[]) =>
    api.put('/trending/topics', topics),
};

export const settingsApi = {
  getAll: () =>
    api.get<Settings[]>('/settings'),
  get: (key: string) =>
    api.get<Settings>(`/settings/${key}`),
  update: (key: string, value: any) =>
    api.put(`/settings/${key}`, { value }),
};

export const queueApi = {
  getAll: () =>
    api.get<QueueItem[]>('/queue'),
  add: (postId: string, scheduledFor?: string) =>
    api.post('/queue', { post_id: postId, scheduled_for: scheduledFor }),
  cancel: (id: string) =>
    api.delete(`/queue/${id}`),
};

export const schedulerApi = {
  getStatus: () =>
    api.get('/scheduler/status'),
  start: () =>
    api.post('/scheduler/start'),
  stop: () =>
    api.post('/scheduler/stop'),
  postNow: (postId: string) =>
    api.post(`/scheduler/post-now/${postId}`),
};
