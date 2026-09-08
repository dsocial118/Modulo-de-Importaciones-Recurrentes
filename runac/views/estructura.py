"""Consulta de la estructura definida en la Capa 1.

Es de sólo lectura: la estructura la produce la skill `runac-capa1`. Acá se
muestra para poder revisarla y discutirla.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import connection
from django.views.generic import TemplateView

from runac.permissions import SeccionPermitidaMixin

from runac.services import importacion_service as svc


class EstructuraView(SeccionPermitidaMixin, LoginRequiredMixin, TemplateView):
    seccion = "estructura"
    template_name = "runac/estructura.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        periodo = self.request.GET.get("periodo") or "2026_T1"
        ctx["periodo_elegido"] = periodo
        ctx["periodos"] = svc.periodos()
        ctx["archivos"] = svc.archivos_esperados(periodo)

        with connection.cursor() as cur:
            cur.execute(
                """
                SELECT c.codigo, c.nombre, COUNT(o.id) AS opciones,
                       (SELECT COUNT(*) FROM runac_c1_campo k WHERE k.catalogo_id = c.id) AS usos
                FROM runac_c1_catalogo c
                LEFT JOIN runac_c1_catalogo_opcion o ON o.catalogo_id = c.id AND o.activo = 1
                GROUP BY c.id ORDER BY usos DESC, opciones DESC LIMIT 20
            """
            )
            cols = [x[0] for x in cur.description]
            ctx["catalogos"] = [dict(zip(cols, f)) for f in cur.fetchall()]

            cur.execute(
                """
                SELECT tr.nombre AS tipo, cr.severidad, COUNT(*) AS cantidad
                FROM runac_c1_campo_regla cr
                JOIN runac_c1_regla r ON r.id = cr.regla_id
                JOIN runac_c1_tipo_regla tr ON tr.id = r.tipo_regla_id
                GROUP BY tr.nombre, cr.severidad ORDER BY cantidad DESC
            """
            )
            cols = [x[0] for x in cur.description]
            ctx["reglas"] = [dict(zip(cols, f)) for f in cur.fetchall()]
        return ctx


class CamposView(SeccionPermitidaMixin, LoginRequiredMixin, TemplateView):
    seccion = "estructura"
    """Los campos de un archivo, con su tipo, su lista y su ayuda."""

    template_name = "runac/campos.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        codigo = kwargs["codigo"]
        campos = svc.campos_de(codigo)
        buscar = (self.request.GET.get("buscar") or "").lower()
        if buscar:
            campos = [
                c
                for c in campos
                if buscar in (c["titulo_esperado"] or "").lower()
                or buscar in (c["nombre"] or "").lower()
            ]

        por_hoja: dict[str, list] = {}
        for c in campos:
            por_hoja.setdefault(c["hoja"], []).append(c)

        ctx.update(
            {
                "codigo": codigo,
                "por_hoja": por_hoja,
                "total": len(campos),
                "buscar": self.request.GET.get("buscar") or "",
                "periodo_elegido": self.request.GET.get("periodo") or "2026_T1",
            }
        )
        return ctx
