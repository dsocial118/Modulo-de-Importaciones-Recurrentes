import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AppRoot } from '@mir/ui';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { App } from './App';

const consultas = new QueryClient({
  defaultOptions: { queries: { retry: 1, refetchOnWindowFocus: false } },
});

createRoot(document.getElementById('raiz')!).render(
  <StrictMode>
    <QueryClientProvider client={consultas}>
      <AppRoot>
        <BrowserRouter basename="/v2/mir">
          <App />
        </BrowserRouter>
      </AppRoot>
    </QueryClientProvider>
  </StrictMode>,
);
