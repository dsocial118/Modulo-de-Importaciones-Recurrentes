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
import { useCallback, useRef, useState, type ReactNode } from 'react';
import { AvisoContext, ConfirmarContext, type Aviso, type Pregunta } from './contextos';
import { coloresDe } from './estados';

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
