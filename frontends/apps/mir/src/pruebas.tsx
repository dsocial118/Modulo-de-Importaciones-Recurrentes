// Lo que toda pantalla necesita alrededor para probarse: el tema, los avisos,
// el router y el cliente de consultas. Sólo lo usan las pruebas.
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AppRoot, Avisos } from '@mir/ui';
import { render } from '@testing-library/react';
import type { ReactNode } from 'react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';

export function mostrar(pantalla: ReactNode, { ruta = '/', patron = '*' }: { ruta?: string; patron?: string } = {}) {
  const consultas = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={consultas}>
      <AppRoot>
        <Avisos>
          <MemoryRouter initialEntries={[ruta]}>
            <Routes>
              <Route path={patron} element={pantalla} />
            </Routes>
          </MemoryRouter>
        </Avisos>
      </AppRoot>
    </QueryClientProvider>,
  );
}

/** Una consulta de react-query ya resuelta, para simular los hooks de @mir/api. */
export const resuelta = <T,>(data: T) => ({ data, isPending: false, isError: false, isFetching: false });

/** Un envío que no hace nada, para simular los hooks de envío. */
export const envio = () => ({ mutate: () => {}, mutateAsync: async () => ({}), isPending: false, variables: undefined });
