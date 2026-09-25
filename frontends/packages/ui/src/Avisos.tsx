import {
  Alert,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Snackbar,
  TextField,
  useTheme,
} from '@mui/material';
import { createContext, useCallback, useContext, useRef, useState, type ReactNode } from 'react';
import { coloresDe } from './estados';

// --- Avisos: qué pasó después de una acción ----------------------------------

type Aviso = { texto: string; error?: boolean };

const AvisoContext = createContext<(a: Aviso) => void>(() => {});

/** Para avisar el resultado de una acción: `avisar({ texto, error })`. */
export const useAvisar = () => useContext(AvisoContext);

// --- Confirmar: antes de algo que no se deshace -------------------------------

type Pregunta = {
  titulo: string;
  texto: ReactNode;
  confirmar?: string;
  // Si se pide, la confirmación trae un campo de texto —por ejemplo, el motivo
  // de una corrección— y su valor es lo que devuelve.
  campo?: { etiqueta: string; obligatorio?: boolean };
};

const ConfirmarContext = createContext<(p: Pregunta) => Promise<string | null>>(async () => null);

/**
 * `await confirmar({...})`: devuelve el texto del campo (o '' si no hay), o
 * null si se canceló.
 */
export const useConfirmar = () => useContext(ConfirmarContext);

export function Avisos({ children }: { children: ReactNode }) {
  const theme = useTheme();
  const [aviso, setAviso] = useState<Aviso | null>(null);
  const [pregunta, setPregunta] = useState<Pregunta | null>(null);
  const [valor, setValor] = useState('');
  const resolver = useRef<(v: string | null) => void>(() => {});

  const avisar = useCallback((a: Aviso) => setAviso(a), []);
  const confirmar = useCallback(
    (p: Pregunta) =>
      new Promise<string | null>((resolve) => {
        resolver.current = resolve;
        setValor('');
        setPregunta(p);
      }),
    [],
  );
  const cerrar = (resultado: string | null) => {
    resolver.current(resultado);
    setPregunta(null);
  };

  // Neutrales, como pide el diseño: un aviso bueno no se pinta de verde.
  const tono = coloresDe(aviso?.error ? 'attention' : 'info', theme.palette.mode);
  const falta = !!pregunta?.campo?.obligatorio && !valor.trim();

  return (
    <AvisoContext.Provider value={avisar}>
      <ConfirmarContext.Provider value={confirmar}>
        {children}
        <Snackbar
          open={!!aviso}
          autoHideDuration={aviso?.error ? null : 6000}
          onClose={(_, motivo) => motivo !== 'clickaway' && setAviso(null)}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert
            onClose={() => setAviso(null)}
            icon={false}
            sx={{ bgcolor: tono.surface, color: tono.text, border: `1px solid ${tono.border}`, maxWidth: 560 }}
          >
            {aviso?.texto}
          </Alert>
        </Snackbar>
        <Dialog open={!!pregunta} onClose={() => cerrar(null)} maxWidth="sm" fullWidth>
          <DialogTitle>{pregunta?.titulo}</DialogTitle>
          <DialogContent>
            <DialogContentText component="div">{pregunta?.texto}</DialogContentText>
            {pregunta?.campo && (
              <TextField
                autoFocus
                fullWidth
                multiline
                minRows={2}
                margin="normal"
                label={pregunta.campo.etiqueta}
                value={valor}
                onChange={(e) => setValor(e.target.value)}
              />
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => cerrar(null)}>Cancelar</Button>
            <Button variant="contained" disabled={falta} onClick={() => cerrar(valor.trim())}>
              {pregunta?.confirmar ?? 'Confirmar'}
            </Button>
          </DialogActions>
        </Dialog>
      </ConfirmarContext.Provider>
    </AvisoContext.Provider>
  );
}
