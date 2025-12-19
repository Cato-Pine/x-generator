import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { Posts } from './pages/Posts';
import { Generate } from './pages/Generate';
import { Approval } from './pages/Approval';
import { Queue } from './pages/Queue';
import { Posted } from './pages/Posted';
import { Trending } from './pages/Trending';
import { Settings } from './pages/Settings';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30000,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/posts" element={<Posts />} />
            <Route path="/generate" element={<Generate />} />
            <Route path="/approval" element={<Approval />} />
            <Route path="/queue" element={<Queue />} />
            <Route path="/posted" element={<Posted />} />
            <Route path="/trending" element={<Trending />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
