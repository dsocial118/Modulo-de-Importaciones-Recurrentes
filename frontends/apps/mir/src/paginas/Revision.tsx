import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  LinearProgress,
  Stack,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import { mensajeDeError, useAccion, useObservar, useRevision, type PresentacionEnRevision } from '@mir/api';
import { EtiquetaDeEstado, Titulo, useAvisar, useConfirmar } from '@mir/ui';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { tonoDeLaPresentacion } from '../comun/estados';
import { fechaHora } from '../comun/formato';
import { SelectorDePeriodo, conFiltros, useFiltros } from '../comun/Selectores';

function Presentacion({ p, periodo }: { p: PresentacionEnRevision; periodo?: string }) {
  const navegar = useNavigate();
  const accion = useAccion();
  const observar = useObservar();
  const avisar = useAvisar();
  const confirmar = useConfirmar();
  const [texto, setTexto] = useState('');
  const alTerminar = {
    onSuccess: (r: { mensaje: string }) => avisar({ texto: r.mensaje }),
    onError: (e: unknown) => avisar({ texto: mensajeDeError(e), error: true }),
  };

  return (
    <Box sx={{ py: 2, borderTop: 1, borderColor: 'divider' }}>
      <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} sx={{ alignItems: { md: 'center' } }}>
        <Box sx={{ flexGrow: 1 }}>
          <Stack direction="row" spacing={1} sx={{ alignItems: 'center', flexWrap: 'wrap', rowGap: 0.5 }}>
            <Typography sx={{ fontWeight: 500 }}>{p.jurisdiccion}</Typography>
            <EtiquetaDeEstado tono={tonoDeLaPresentacion(p.estado)} texto={p.estado_legible} />
            {p.observaciones > 0 && (
              <EtiquetaDeEstado tono="attention" texto={`${p.observaciones} observaciones abiertas`} />
            )}
          </Stack>
          <Typography variant="body2" color="text.secondary">
            versión {p.version} · {p.importados} archivos importados · cierre de carga {fechaHora(p.cerrada_el)}
            {p.expediente && ` · expediente ${p.expediente}`}
          </Typography>
        </Box>
        <Stack direction="row" sx={{ flexWrap: 'wrap', gap: 1 }}>
          <Button
            size="small"
            variant="outlined"
            onClick={() => navegar(conFiltros('/resultado', periodo, p.jurisdiccion))}
          >
            Ver carga
          </Button>
          {p.acciones.map((a) => (
            <Tooltip key={a.accion} title={a.ayuda}>
              <span>
                <Button
                  size="small"
                  variant="contained"
                  disabled={accion.isPending}
                  onClick={async () => {
                    if (a.accion === 'habilitar') {
                      const ok = await confirmar({
                        titulo: a.etiqueta,
                        texto: `Concluye la revisión de ${p.jurisdiccion} y la habilita a presentar formalmente.`,
                        confirmar: a.etiqueta,
                      });
                      if (ok === null) return;
                    }
                    accion.mutate({ presentacion: p.id, accion: a.accion }, alTerminar);
                  }}
                >
                  {a.etiqueta}
                </Button>
              </span>
            </Tooltip>
          ))}
        </Stack>
      </Stack>
      {p.puede_observar && (
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} sx={{ mt: 1.5, maxWidth: 760 }}>
          <TextField
            size="small"
            fullWidth
            label="Observación para la jurisdicción"
            value={texto}
            onChange={(e) => setTexto(e.target.value)}
          />
          <Button
            variant="outlined"
            disabled={!texto.trim() || observar.isPending}
            onClick={() =>
              observar.mutate(
                { presentacion: p.id, texto },
                {
                  ...alTerminar,
                  onSuccess: (r) => {
                    setTexto('');
                    avisar({ texto: r.mensaje });
                  },
                },
              )
            }
          >
            Observar
          </Button>
        </Stack>
      )}
    </Box>
  );
}

export function Revision() {
  const { periodo, cambiar } = useFiltros();
  const consulta = useRevision(periodo);
  if (consulta.isPending) return <LinearProgress aria-label="Cargando" />;
  if (consulta.isError) return <Alert severity="error">No se pudo cargar la revisión.</Alert>;
  const d = consulta.data;

  return (
    <>
      <Titulo
        titulo="Revisión nacional"
        subtitulo={
          <>
            El revisor técnico nacional revisa la calidad de lo cargado, formula observaciones y habilita la
            presentación. <strong>No modifica datos provinciales.</strong>
          </>
        }
      >
        {d.periodo && (
          <SelectorDePeriodo periodos={d.periodos} valor={d.periodo.codigo} alCambiar={(x) => cambiar({ periodo: x })} />
        )}
      </Titulo>
      {!d.es_revisor && (
        <Alert severity="info" sx={{ mb: 2 }}>
          Este rol permite consultar la bandeja, pero no ejecutar acciones de revisión.
        </Alert>
      )}
      <Card variant="outlined">
        <CardContent sx={{ pt: 0, '&:last-child': { pb: 0 } }}>
          {d.presentaciones.length === 0 ? (
            <Typography color="text.secondary" sx={{ py: 4, textAlign: 'center' }}>
              Ninguna jurisdicción inició la carga de este período.
            </Typography>
          ) : (
            d.presentaciones.map((p) => <Presentacion key={p.id} p={p} periodo={d.periodo?.codigo} />)
          )}
        </CardContent>
      </Card>
      <Typography variant="body2" color="text.secondary" sx={{ mt: 3 }}>
        El ciclo de observación y subsanación no tiene límite de rondas. La presentación es el último acto del
        circuito y sólo se habilita cuando la revisión concluye.
      </Typography>
    </>
  );
}
