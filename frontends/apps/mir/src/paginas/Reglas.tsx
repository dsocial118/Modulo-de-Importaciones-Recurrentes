import LockOutlined from '@mui/icons-material/LockOutlined';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Checkbox,
  LinearProgress,
  MenuItem,
  Paper,
  Stack,
  TextField,
  Typography,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import { mensajeDeError, useGuardarReglas, useReglas, type CampoDeReglas, type Reglas as TReglas } from '@mir/api';
import { EtiquetaDeEstado, Titulo, useAvisar } from '@mir/ui';
import { useMemo, useState } from 'react';
import { SEVERIDAD, formaDe } from '../comun/estados';
import { useFiltros } from '../comun/filtros';

// Lo editado de un campo: sólo lo que se tocó. Los dos límites de cada techo
// van juntos, o no van: si llegara uno solo, el otro se leería como «vaciado».
type Cambio = { obligatorio?: boolean; advierte?: [string, string]; bloquea?: [string, string] };

function Techo({
  etiqueta,
  tono,
  valor,
  editable,
  alCambiar,
  texto,
}: {
  etiqueta: string;
  tono: 'attention' | 'critical';
  valor: [string, string];
  editable: boolean;
  alCambiar: (v: [string, string]) => void;
  texto?: string;
}) {
  if (!editable) {
    return texto ? (
      <Box>
        <EtiquetaDeEstado tono={tono} texto={etiqueta} /> <Typography variant="body2" component="span">{texto}</Typography>
      </Box>
    ) : null;
  }
  return (
    <Stack direction="row" spacing={1} sx={{ alignItems: 'center' }}>
      <Box sx={{ minWidth: 72 }}>
        <EtiquetaDeEstado tono={tono} texto={etiqueta} />
      </Box>
      <TextField
        size="small"
        placeholder="mín"
        value={valor[0]}
        onChange={(e) => alCambiar([e.target.value, valor[1]])}
        slotProps={{ htmlInput: { inputMode: 'decimal', 'aria-label': `${etiqueta} desde` } }}
        sx={{ width: 110 }}
      />
      <TextField
        size="small"
        placeholder="máx"
        value={valor[1]}
        onChange={(e) => alCambiar([valor[0], e.target.value])}
        slotProps={{ htmlInput: { inputMode: 'decimal', 'aria-label': `${etiqueta} hasta` } }}
        sx={{ width: 110 }}
      />
    </Stack>
  );
}

function Campo({
  c,
  editable,
  verTecnico,
  cambio,
  severidades,
  alCambiar,
  alCambiarSeveridad,
}: {
  c: CampoDeReglas;
  editable: boolean;
  verTecnico: boolean;
  cambio: Cambio;
  severidades: Record<number, string>;
  alCambiar: (c: Cambio) => void;
  alCambiarSeveridad: (aplicacion: number, severidad: string) => void;
}) {
  const oblig = cambio.obligatorio ?? c.obligatorio;
  const avisa: [string, string] = cambio.advierte ?? [c.rangos.avisa?.minimo ?? '', c.rangos.avisa?.maximo ?? ''];
  const frena: [string, string] = cambio.bloquea ?? [c.rangos.frena?.minimo ?? '', c.rangos.frena?.maximo ?? ''];
  const tocado = Object.keys(cambio).length > 0 || c.otras.some((o) => severidades[o.aplicacion_id]);

  return (
    <Box
      sx={{
        py: 2,
        px: 1,
        borderTop: 1,
        borderColor: 'divider',
        display: 'grid',
        gap: 2,
        gridTemplateColumns: { xs: 'minmax(0, 1fr)', lg: '48px minmax(0,1.4fr) 120px minmax(0,1.4fr) minmax(0,1fr)' },
        alignItems: 'start',
        bgcolor: tocado ? 'action.hover' : undefined,
      }}
    >
      <Typography variant="body2" color="text.secondary" sx={{ fontFamily: 'monospace', pt: 0.5 }}>
        {c.letra}
      </Typography>
      <Box>
        <Typography variant="body2" sx={{ fontWeight: 500 }}>
          {c.titulo}
        </Typography>
        {c.ayuda && (
          <Typography variant="caption" color="text.secondary" component="div">
            {c.ayuda}
          </Typography>
        )}
        {verTecnico && c.nombre && (
          <Typography variant="caption" color="text.secondary" sx={{ fontFamily: 'monospace', wordBreak: 'break-all' }}>
            {c.nombre}
          </Typography>
        )}
      </Box>
      <Box>
        {c.condicionado ? (
          <Typography variant="body2" color="text.secondary" title="Se completa sólo en ciertos casos, así que no puede ser obligatorio siempre.">
            según el caso
          </Typography>
        ) : editable ? (
          <Stack direction="row" sx={{ alignItems: 'center' }}>
            <Checkbox
              size="small"
              checked={oblig}
              onChange={(e) => alCambiar({ ...cambio, obligatorio: e.target.checked })}
              slotProps={{ input: { 'aria-label': `${c.titulo}: obligatoria` } }}
            />
            <Typography variant="body2">obligatoria</Typography>
          </Stack>
        ) : (
          <Typography variant="body2">{c.obligatorio ? 'Obligatoria' : '—'}</Typography>
        )}
      </Box>
      <Box>
        <Typography variant="body2">{c.valores.texto}</Typography>
        {c.valores.opciones.length > 0 && (
          <Box component="ul" sx={{ m: 0, pl: 2.5 }}>
            {c.valores.opciones.map((o) => (
              <Typography key={o} component="li" variant="body2" color="text.secondary">
                {o}
              </Typography>
            ))}
          </Box>
        )}
        {c.valores.detalle && (
          <Box component="details" sx={{ mt: 0.5 }}>
            <Box component="summary" sx={{ cursor: 'pointer', color: 'primary.main', fontSize: 14 }}>
              ver las opciones
            </Box>
            <Typography variant="caption" color="text.secondary">
              {c.valores.detalle}
            </Typography>
          </Box>
        )}
        {c.numerico && (
          <Stack spacing={1} sx={{ mt: 1 }}>
            <Techo
              etiqueta="advierte"
              tono="attention"
              valor={avisa}
              editable={editable}
              texto={c.rangos.avisa?.texto}
              alCambiar={(v) => alCambiar({ ...cambio, advierte: v })}
            />
            <Techo
              etiqueta="bloquea"
              tono="critical"
              valor={frena}
              editable={editable}
              texto={c.rangos.frena?.texto}
              alCambiar={(v) => alCambiar({ ...cambio, bloquea: v })}
            />
          </Stack>
        )}
      </Box>
      <Stack spacing={1}>
        {c.otras.length === 0 && (
          <Typography variant="body2" color="text.secondary">
            —
          </Typography>
        )}
        {c.otras.map((o) => {
          const sev = severidades[o.aplicacion_id] ?? o.severidad;
          return (
            <Box key={o.aplicacion_id}>
              <Typography variant="body2">{o.texto}</Typography>
              {editable ? (
                <TextField
                  select
                  size="small"
                  value={sev}
                  onChange={(e) => alCambiarSeveridad(o.aplicacion_id, e.target.value)}
                  sx={{ mt: 0.5, minWidth: 130 }}
                  slotProps={{ htmlInput: { 'aria-label': 'Severidad' } }}
                >
                  <MenuItem value="ADVERTENCIA">advierte</MenuItem>
                  <MenuItem value="BLOQUEANTE">bloquea</MenuItem>
                </TextField>
              ) : (
                <EtiquetaDeEstado tono={formaDe(SEVERIDAD, sev).tono} texto={sev === 'BLOQUEANTE' ? 'bloquea' : 'advierte'} />
              )}
            </Box>
          );
        })}
      </Stack>
    </Box>
  );
}

function Hoja({ d }: { d: TReglas }) {
  const guardar = useGuardarReglas();
  const avisar = useAvisar();
  const ancho = useMediaQuery(useTheme().breakpoints.up('lg'));
  const [cambios, setCambios] = useState<Record<number, Cambio>>({});
  const [severidades, setSeveridades] = useState<Record<number, string>>({});

  // Se compara SIEMPRE contra lo que vino: si se cambia 20 por 30 y después se
  // vuelve a 20, deja de contar como cambio.
  const pendientes = useMemo(() => {
    const porCampo = new Map(d.campos.map((c) => [c.id, c]));
    const limpios: Record<number, Cambio> = {};
    for (const [id, cambio] of Object.entries(cambios)) {
      const c = porCampo.get(Number(id));
      if (!c) continue;
      const out: Cambio = {};
      if (cambio.obligatorio !== undefined && cambio.obligatorio !== c.obligatorio) out.obligatorio = cambio.obligatorio;
      const igual = (v: [string, string] | undefined, t?: { minimo: string; maximo: string } | null) =>
        !v || (v[0].trim() === (t?.minimo ?? '') && v[1].trim() === (t?.maximo ?? ''));
      if (!igual(cambio.advierte, c.rangos.avisa)) out.advierte = cambio.advierte;
      if (!igual(cambio.bloquea, c.rangos.frena)) out.bloquea = cambio.bloquea;
      if (Object.keys(out).length) limpios[Number(id)] = out;
    }
    const originales = new Map(d.campos.flatMap((c) => c.otras.map((o) => [o.aplicacion_id, o.severidad])));
    const sev = Object.fromEntries(Object.entries(severidades).filter(([k, v]) => originales.get(Number(k)) !== v));
    return { campos: limpios, severidades: sev };
  }, [cambios, severidades, d.campos]);
  const cuantos = Object.keys(pendientes.campos).length + Object.keys(pendientes.severidades).length;

  const alGuardar = () =>
    guardar.mutate(
      {
        cambios: Object.entries(pendientes.campos).map(([id, c]) => ({ campo_id: Number(id), ...c })),
        severidades: Object.entries(pendientes.severidades).map(([id, severidad]) => ({
          aplicacion_id: Number(id),
          severidad: severidad as 'ADVERTENCIA' | 'BLOQUEANTE',
        })),
      },
      {
        onSuccess: (r) => {
          setCambios({});
          setSeveridades({});
          avisar({ texto: r.detalle.length ? `${r.mensaje} ${r.detalle.join(' · ')}` : r.mensaje });
        },
        // O entra todo o no entra nada: los problemas llegan juntos.
        onError: (e) => avisar({ texto: mensajeDeError(e), error: true }),
      },
    );

  const obligatorias = d.campos.filter((c) => c.obligatorio).length;
  const conCondiciones = d.campos.filter((c) => c.otras.length || c.rangos.avisa || c.rangos.frena).length;

  return (
    <>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
        <strong>{d.campos.length}</strong> columnas · <strong>{obligatorias}</strong> obligatorias ·{' '}
        <strong>{conCondiciones}</strong> con condiciones propias
      </Typography>
      {d.puede_editar && (
        <Paper
          variant="outlined"
          sx={{ position: 'sticky', top: 104, zIndex: 2, p: 1.5, mb: 2, display: 'flex', alignItems: 'center', gap: 2 }}
        >
          <Typography variant="body2" color="text.secondary" sx={{ flexGrow: 1 }}>
            {cuantos === 0 ? 'Sin cambios' : cuantos === 1 ? '1 cambio sin guardar' : `${cuantos} cambios sin guardar`}
          </Typography>
          <Button variant="contained" disabled={!cuantos || guardar.isPending} onClick={alGuardar}>
            Guardar cambios
          </Button>
        </Paper>
      )}
      <Card variant="outlined">
        <CardContent sx={{ pt: 0, '&:last-child': { pb: 0 } }}>
          {ancho && (
            <Box
              sx={{
                display: 'grid',
                gap: 2,
                px: 1,
                py: 1.5,
                gridTemplateColumns: '48px minmax(0,1.4fr) 120px minmax(0,1.4fr) minmax(0,1fr)',
                color: 'text.secondary',
                fontSize: 14,
                fontWeight: 500,
              }}
            >
              <span>Col.</span>
              <span>Campo</span>
              <span>Oblig.</span>
              <span>Qué admite</span>
              <span>Condiciones</span>
            </Box>
          )}
          {d.campos.map((c) => (
            <Campo
              key={c.id}
              c={c}
              editable={d.puede_editar}
              verTecnico={d.ver_tecnico}
              cambio={cambios[c.id] ?? {}}
              severidades={severidades}
              alCambiar={(x) => setCambios((prev) => ({ ...prev, [c.id]: x }))}
              alCambiarSeveridad={(id, s) => setSeveridades((prev) => ({ ...prev, [id]: s }))}
            />
          ))}
        </CardContent>
      </Card>
      <Typography variant="body2" color="text.secondary" sx={{ mt: 3 }}>
        En <strong>Condiciones</strong> va lo que un rango no puede decir: obligatoriedad condicionada, relaciones
        entre columnas, o que un valor exista en otro archivo. Que la mayoría de las filas diga «—» es lo esperable.
        {d.puede_editar && (
          <>
            {' '}
            <strong>Se cambia acá mismo</strong> y se guarda todo junto con el botón de arriba. Un casillero vacío que
            se completa crea la condición; uno que se vacía la quita.
          </>
        )}
      </Typography>
    </>
  );
}

export function Reglas() {
  const { params, cambiar } = useFiltros();
  const consulta = useReglas(params.get('hoja'));
  if (consulta.isPending) return <LinearProgress aria-label="Cargando" />;
  if (consulta.isError) return <Alert severity="error">No se pudieron cargar las reglas.</Alert>;
  const d = consulta.data;

  return (
    <>
      <Titulo
        titulo="Qué se espera de cada archivo"
        subtitulo="Qué va en cada columna: si es obligatoria, qué tipo de dato admite y qué condiciones debe cumplir."
      >
        <TextField
          select
          size="small"
          label="Archivo y hoja"
          value={d.hoja}
          onChange={(e) => cambiar({ hoja: e.target.value })}
          sx={{ minWidth: 260 }}
        >
          {d.hojas.map((h) => (
            <MenuItem key={h.clave} value={h.clave}>
              {h.etiqueta}
            </MenuItem>
          ))}
        </TextField>
      </Titulo>
      {d.ver_tecnico && d.periodo_abierto && (
        <Alert severity="info" icon={<LockOutlined />} sx={{ mb: 2 }}>
          <strong>El período {d.periodo_abierto} está abierto, así que la definición no se toca.</strong> Con
          provincias cargando, mover una regla haría que a dos que presentaron lo mismo les fuera distinto.
        </Alert>
      )}
      {consulta.isFetching && <LinearProgress sx={{ mb: 1 }} />}
      {d.campos.length ? (
        // La clave es la hoja: al cambiar de hoja, lo que no se guardó se descarta.
        <Hoja key={d.hoja} d={d} />
      ) : (
        <Typography color="text.secondary">No hay columnas definidas para esta hoja.</Typography>
      )}
    </>
  );
}
