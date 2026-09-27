import ChatBubbleOutline from '@mui/icons-material/ChatBubbleOutlineOutlined';
import { Box, Button, Stack, TextField, Typography, useTheme } from '@mui/material';
import {
  mensajeDeError,
  useDesestimarObservacion,
  useObservarDato,
  useReabrirObservacion,
  useResponder,
  type Observacion,
} from '@mir/api';
import { EtiquetaDeEstado, coloresDe, useAvisar, type Tono } from '@mir/ui';
import { useState } from 'react';
import { fechaHora } from './formato';

/**
 * Observaciones sobre un dato: una celda, no la fila (27-09-2026).
 *
 * El revisor nacional observa. La jurisdicción la resuelve corrigiendo el dato
 * —la observación se subsana sola— o respondiendo que está bien así. El
 * revisor puede no aceptar la respuesta y reabrirla, o retirar su observación.
 * Todo en la página: los modales quedan para confirmar lo que pisa algo.
 */

const ESTADO_DE_LA_OBSERVACION: Record<string, { texto: string; tono: Tono }> = {
  ABIERTA: { texto: 'Sin resolver', tono: 'critical' },
  RESPONDIDA: { texto: 'Respondida', tono: 'info' },
  SUBSANADA: { texto: 'Corregida', tono: 'info' },
  DESESTIMADA: { texto: 'Desestimada', tono: 'pending' },
};

type Permisos = { puedeObservar: boolean; puedeResponder: boolean };

/** Un texto que se escribe en el lugar, con Enviar y Cancelar. */
function Escribir({
  etiqueta,
  enviar,
  alTerminar,
  ayuda,
}: {
  etiqueta: string;
  enviar: (texto: string) => Promise<unknown>;
  alTerminar: () => void;
  ayuda?: string;
}) {
  const [texto, setTexto] = useState('');
  const [enviando, setEnviando] = useState(false);
  const avisar = useAvisar();
  return (
    <Stack spacing={1} sx={{ mt: 1 }}>
      <TextField
        size="small"
        multiline
        minRows={2}
        autoFocus
        label={etiqueta}
        value={texto}
        onChange={(e) => setTexto(e.target.value)}
        helperText={ayuda}
      />
      <Stack direction="row" spacing={1}>
        <Button
          size="small"
          variant="contained"
          disabled={!texto.trim() || enviando}
          onClick={async () => {
            setEnviando(true);
            try {
              const r = (await enviar(texto.trim())) as { mensaje?: string };
              avisar({ texto: r?.mensaje ?? 'Listo.' });
              alTerminar();
            } catch (e) {
              avisar({ texto: mensajeDeError(e), error: true });
            } finally {
              setEnviando(false);
            }
          }}
        >
          Enviar
        </Button>
        <Button size="small" onClick={alTerminar}>
          Cancelar
        </Button>
      </Stack>
    </Stack>
  );
}

/** Una observación, con lo que cada rol puede hacer con ella. */
export function TarjetaDeObservacion({
  o,
  permisos,
  ubicacion,
}: {
  o: Observacion;
  permisos: Permisos;
  // En la lista de pendientes se dice dónde está; junto al dato no hace falta.
  ubicacion?: string;
}) {
  const { palette } = useTheme();
  const responder = useResponder();
  const reabrir = useReabrirObservacion();
  const desestimar = useDesestimarObservacion();
  const avisar = useAvisar();
  const [modo, setModo] = useState<'' | 'responder' | 'reabrir'>('');
  const forma = ESTADO_DE_LA_OBSERVACION[o.estado] ?? { texto: o.estado, tono: 'pending' as Tono };
  const c = coloresDe(forma.tono, palette.mode);
  const abierta = o.estado === 'ABIERTA';
  const resuelta = o.estado === 'RESPONDIDA' || o.estado === 'SUBSANADA';

  return (
    <Box sx={{ borderLeft: `3px solid ${c.border}`, bgcolor: c.surface, borderRadius: 1, p: 1.25, mt: 1 }}>
      <Stack direction="row" spacing={1} sx={{ alignItems: 'center', flexWrap: 'wrap', rowGap: 0.5 }}>
        <EtiquetaDeEstado tono={forma.tono} texto={forma.texto} />
        {ubicacion && (
          <Typography variant="body2" sx={{ fontWeight: 500 }}>
            {ubicacion}
          </Typography>
        )}
        <Typography variant="caption" color="text.secondary">
          {o.usuario_observa} · {fechaHora(o.creada_el)}
        </Typography>
      </Stack>
      <Typography variant="body2" sx={{ mt: 0.5, whiteSpace: 'pre-line', color: c.text }}>
        {o.texto}
      </Typography>
      {o.respuesta && (
        <Typography variant="body2" sx={{ mt: 0.5 }}>
          <strong>Respuesta</strong> ({o.usuario_responde}, {fechaHora(o.respondida_el)}): {o.respuesta}
        </Typography>
      )}

      {modo === '' && (
        <Stack direction="row" spacing={1} sx={{ mt: 1, flexWrap: 'wrap', rowGap: 1 }}>
          {abierta && permisos.puedeResponder && (
            <Button size="small" variant="outlined" onClick={() => setModo('responder')}>
              Está bien así
            </Button>
          )}
          {resuelta && permisos.puedeObservar && (
            <Button size="small" variant="outlined" onClick={() => setModo('reabrir')}>
              No se acepta
            </Button>
          )}
          {o.estado !== 'DESESTIMADA' && permisos.puedeObservar && (
            <Button
              size="small"
              color="inherit"
              onClick={async () => {
                try {
                  const r = await desestimar.mutateAsync({ observacion: o.id });
                  avisar({ texto: r.mensaje });
                } catch (e) {
                  avisar({ texto: mensajeDeError(e), error: true });
                }
              }}
            >
              Desestimar
            </Button>
          )}
        </Stack>
      )}
      {abierta && permisos.puedeResponder && modo === '' && (
        <Typography variant="caption" color="text.secondary" component="div" sx={{ mt: 0.5 }}>
          Si el dato está mal, corregilo: la observación queda resuelta sola.
        </Typography>
      )}
      {modo === 'responder' && (
        <Escribir
          etiqueta="Por qué el dato está bien así"
          enviar={(texto) => responder.mutateAsync({ observacion: o.id, respuesta: texto })}
          alTerminar={() => setModo('')}
        />
      )}
      {modo === 'reabrir' && (
        <Escribir
          etiqueta="Por qué no se acepta la respuesta"
          enviar={(texto) => reabrir.mutateAsync({ observacion: o.id, texto })}
          alTerminar={() => setModo('')}
        />
      )}
    </Box>
  );
}

/** Debajo de cada dato: su observación, o el botón para observarlo. */
export function ObservacionDelDato({
  observacion,
  permisos,
  ubicacion,
}: {
  observacion: Observacion | null | undefined;
  permisos: Permisos;
  ubicacion: { presentacion: number; importacion: number; numero_fila: number; campo_id: number };
}) {
  const observar = useObservarDato();
  const [escribiendo, setEscribiendo] = useState(false);
  const puedeObservarAca = permisos.puedeObservar && (!observacion || observacion.estado !== 'ABIERTA');
  return (
    <>
      {observacion && <TarjetaDeObservacion o={observacion} permisos={permisos} />}
      {puedeObservarAca &&
        (escribiendo ? (
          <Escribir
            etiqueta="Qué hay que revisar en este dato"
            ayuda="La jurisdicción lo ve en el dato y en la lista de observaciones sin resolver."
            enviar={(texto) => observar.mutateAsync({ ...ubicacion, texto })}
            alTerminar={() => setEscribiendo(false)}
          />
        ) : (
          <Button size="small" startIcon={<ChatBubbleOutline />} onClick={() => setEscribiendo(true)} sx={{ mt: 0.5 }}>
            Observar
          </Button>
        ))}
    </>
  );
}
