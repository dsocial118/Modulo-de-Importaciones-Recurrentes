"""Recorrido de punta a punta del MIR con los seis usuarios, sobre una base descartable.

Se corre dentro del contenedor web de la 8110 con DATABASE_NAME y RUNAC_DB_NAME
apuntando a la base descartable. Imprime una línea por paso: OK o FALLA.
"""
import io
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402
from django.test import Client  # noqa: E402
from openpyxl import load_workbook  # noqa: E402

U = get_user_model()
CARPETA = "/app/entorno/mir-v2/archivos_de_prueba/Chubut_con_advertencias"
fallas = []


def cli(nombre):
    c = Client(HTTP_HOST="localhost")
    c.force_login(U.objects.get(username=nombre))
    return c


def paso(texto, condicion, detalle=""):
    print(("  OK    " if condicion else "  FALLA ") + texto + (f"  [{detalle}]" if detalle and not condicion else ""))
    if not condicion:
        fallas.append(texto)


op, resp, rev, adm, opch = (cli(u) for u in ("operador", "responsable", "revisor", "admin", "operador_chaco"))
J = "?jurisdiccion=Chubut"

print("== Plantillas y carga (operador de Chubut)")
r = op.get("/api/mir/plantillas/")
paso("Plantillas responde", r.status_code == 200)
per = r.json()["periodo"]["codigo"]
r = op.get(f"/api/mir/plantillas/{per}/MPI/")
paso("La plantilla se descarga", r.status_code == 200)
wb = load_workbook(io.BytesIO(b"".join(r.streaming_content) if hasattr(r, "streaming_content") else r.content))
ws = wb["MPI"]
colores = {c.fill.fgColor.rgb[-6:] for fila in ws.iter_rows(min_row=1, max_row=4) for c in fila if c.fill and c.fill.fgColor and c.fill.fgColor.rgb}
paso("La plantilla usa los verdes del MIR y no azul", {"045F5B", "9DCECB"} <= colores and "1F4E79" not in colores, str(colores))
titulos = [c.value for fila in ws.iter_rows(min_row=1, max_row=3) for c in fila if isinstance(c.value, str)]
paso("La plantilla lleva la marca", any("SISOC · MIR" in t for t in titulos), str(titulos[:2]))
r = op.get(f"/api/mir/plantillas/{per}/MPI/instructivo/")
paso("El instructivo se descarga", r.status_code == 200)

orden = ["DISP_PENAL", "DISP_SCP", "LEGAJO_NYA", "MPI", "MPE", "MPJ_DAE"]
for codigo in orden:
    nombre = next(f for f in os.listdir(CARPETA) if f.startswith(codigo + "_2026"))
    with open(os.path.join(CARPETA, nombre), "rb") as fh:
        r = op.post(f"/api/mir/carga/{codigo}/", {"archivo": fh, "periodo": per})
    paso(f"Importa {codigo}", r.status_code in (200, 201) and r.json().get("estado") in ("VALIDA", None), str(r.content[:200]))

res = op.get("/api/mir/resultado/").json()
imp = {a["codigo"]: a["importacion"]["id"] for a in res["archivos"] if a.get("importada")}
paso("Quedan los seis importados", len(imp) == 6, str(imp))
pid = res["presentacion"]["id"]

print("== Permisos y circuito")
r = op.post(f"/api/mir/presentaciones/{pid}/acciones/cerrar_carga/")
paso("El operador no puede cerrar la carga", r.status_code == 400)
d = rev.get(f"/api/mir/importaciones/{imp['MPI']}/datos/{J}").json()
paso("Durante la carga, el revisor no puede observar (pantalla)", d["puede_observar"] is False)
celda = d["filas"][0]["celdas"][1]
r = rev.post(f"/api/mir/presentaciones/{pid}/observaciones/", {"texto": "x", "importacion_id": imp["MPI"], "numero_fila": d["filas"][0]["numero_fila"], "campo_id": celda["campo_id"]}, content_type="application/json")
paso("Durante la carga, el revisor no puede observar (servidor)", r.status_code == 400, str(r.content[:120]))
da = op.get(f"/api/mir/importaciones/{imp['MPI']}/datos/?solo=avisos").json()
f0 = da["filas"][0]
c_aviso = next((c for c in f0["celdas"] if c["tiene_aviso"]), None)
r = op.post(f"/api/mir/importaciones/{imp['MPI']}/datos/", {"hoja_id": da["hoja"]["id"], "numero_fila": f0["numero_fila"], "campo": c_aviso["nombre"], "valor": "12" if c_aviso["tipo_dato"] == "ENTERO" else "Corregido", "motivo": "prueba e2e"}, content_type="application/json")
paso("El operador corrige una advertencia", r.status_code in (200, 409), str(r.content[:200]))
r = resp.post(f"/api/mir/presentaciones/{pid}/acciones/cerrar_carga/")
paso("El responsable cierra la carga", r.status_code == 200 and r.json()["estado"] == "CERRADA", str(r.content[:120]))
fr = rev.get("/api/mir/franja/" + J).json()
paso("La franja dice Revisión nacional", [p["nombre"] for p in fr["pasos"] if p["actual"]] == ["Revisión nacional"])
fr0 = rev.get("/api/mir/franja/").json()
paso("Sin provincia, la franja trae los pasos apagados", fr0["estado"] is None and fr0["pasos"] and not any(p["actual"] for p in fr0["pasos"]))
b = rev.get("/api/mir/revision/").json()
paso("Chubut aparece en la bandeja del revisor", any(p["jurisdiccion"] == "Chubut" and p["estado"] == "CERRADA" for p in b["presentaciones"]))
r = rev.post(f"/api/mir/presentaciones/{pid}/acciones/abrir_revision/")
paso("El revisor comienza la revisión", r.status_code == 200)
d = rev.get(f"/api/mir/importaciones/{imp['MPI']}/datos/{J}").json()
paso("En revisión, el revisor puede observar", d["puede_observar"] is True)
fila = d["filas"][1]
celda = fila["celdas"][2]
r = rev.post(f"/api/mir/presentaciones/{pid}/observaciones/", {"texto": "Revisar este dato", "importacion_id": imp["MPI"], "numero_fila": fila["numero_fila"], "campo_id": celda["campo_id"]}, content_type="application/json")
paso("El revisor observa un dato", r.status_code == 201, str(r.content[:120]))
paso("La presentación queda Observada", resp.get("/api/mir/resultado/").json()["presentacion"]["estado"] == "OBSERVADA")
r = rev.post(f"/api/mir/importaciones/{imp['MPI']}/datos/", {"hoja_id": d["hoja"]["id"], "numero_fila": fila["numero_fila"], "campo": celda["nombre"], "valor": "x"}, content_type="application/json")
paso("El revisor no puede corregir datos", r.status_code == 403)
obs = resp.get("/api/mir/resultado/").json()["observaciones"]
abierta = next(o for o in obs if o["estado"] == "ABIERTA")
r = resp.post(f"/api/mir/observaciones/{abierta['id']}/respuesta/", {"respuesta": "Está bien así"}, content_type="application/json")
paso("El responsable responde la observación", r.status_code == 200)
paso("La presentación queda Subsanada", resp.get("/api/mir/resultado/").json()["presentacion"]["estado"] == "SUBSANADA")
paso("El revisor ve las respuestas en Observaciones", any(o["estado"] == "RESPONDIDA" for o in rev.get("/api/mir/observaciones/").json()["filas"]))
resp.post(f"/api/mir/presentaciones/{pid}/acciones/cerrar_carga/")
rev.post(f"/api/mir/presentaciones/{pid}/acciones/abrir_revision/")
r = rev.post(f"/api/mir/presentaciones/{pid}/acciones/habilitar/")
paso("El revisor habilita la presentación", r.status_code == 200 and r.json()["estado"] == "HABILITADA", str(r.content[:120]))
r = resp.post(f"/api/mir/presentaciones/{pid}/acciones/presentar/")
paso("El responsable presenta", r.status_code == 200 and r.json()["estado"] == "PRESENTADA")
paso("Hay comprobante", resp.get(f"/api/mir/presentaciones/{pid}/comprobante/").status_code == 200)
r = resp.post(f"/api/mir/presentaciones/{pid}/expediente/", {"expediente": "EX-2026-00000001-APN-PRUEBA"}, content_type="application/json")
paso("Se registra el expediente", r.status_code == 200, str(r.content[:120]))

print("== Nivel nacional y administración")
s = rev.get("/api/mir/situacion/").json()
paso("Estado de situación: Chubut presentó", any(f["jurisdiccion"] == "Chubut" and f["estado"] == "PRESENTADA" for f in s["filas"]) and s["totales"]["presentaron"] >= 1)
paso("El historial de la presentación tiene cambios", len(rev.get(f"/api/mir/presentaciones/{pid}/historial/").json()["filas"]) >= 1)
a = adm.get("/api/mir/administracion/").json()
paso("Administración muestra que Chubut ya cargó", any(j["nombre"] == "Chubut" and j["ya_cargo"] for j in a["jurisdicciones"]))
r = adm.post("/api/mir/administracion/operativo/", {"nombre": "Chubut", "en_el_operativo": False}, content_type="application/json")
paso("No se puede sacar a Chubut del operativo", r.status_code == 400)
r = adm.post("/api/mir/administracion/operativo/", {"nombre": "Tucumán", "en_el_operativo": False}, content_type="application/json")
paso("Se puede sacar a una que no cargó", r.status_code == 200)
adm.post("/api/mir/administracion/operativo/", {"nombre": "Tucumán", "en_el_operativo": True}, content_type="application/json")
c = adm.get(f"/api/mir/periodos/{per}/resumen-de-cierre/").json()
paso("El resumen de cierre cuenta a Chubut como presentada", any(g["grupo"] == "PRESENTADA" and g["cantidad"] >= 1 for g in c["grupos"]))
r = adm.post(f"/api/mir/importaciones/{imp['MPI']}/datos/", {"hoja_id": 1, "numero_fila": 4, "campo": "edad", "valor": "3"}, content_type="application/json")
paso("El administrador no corrige datos", r.status_code in (400, 403))
paso("El operador no entra a Estado de situación", op.get("/api/mir/situacion/").status_code == 403)
paso("El revisor no entra a Administración", rev.get("/api/mir/administracion/").status_code == 403)
rch = opch.get("/api/mir/resultado/?jurisdiccion=Chubut").json()
paso("El operador de Chaco sólo ve Chaco", rch["jurisdiccion"] == "Chaco")

print("== Descargas")
for nombre, url in [
    ("informe", f"/api/mir/importaciones/{imp['MPI']}/errores.xlsx"),
    ("archivo para corregir", f"/api/mir/importaciones/{imp['MPI']}/marcado.xlsx"),
    ("historial", f"/api/mir/importaciones/{imp['MPI']}/historial.xlsx"),
]:
    r = op.get(url)
    contenido = b"".join(r.streaming_content) if hasattr(r, "streaming_content") else r.content
    ok = r.status_code == 200 and len(contenido) > 1000
    marca = False
    if ok:
        libro = load_workbook(io.BytesIO(contenido))
        marca = any("SISOC · MIR" in str(h["B1"].value or "") for h in libro.worksheets)
    paso(f"El {nombre} se descarga y lleva la marca", ok and marca)

print("== Volver a subir el legajo anula a sus dependientes")
resp.post(f"/api/mir/presentaciones/{pid}/acciones/reabrir_carga/")
print("   (presentada no se reabre: se prueba con Chaco)")
CH = "/app/entorno/mir-v2/archivos_de_prueba/Chaco_con_advertencias"
for codigo in orden:
    nombre = next(f for f in os.listdir(CH) if f.startswith(codigo + "_2026"))
    with open(os.path.join(CH, nombre), "rb") as fh:
        opch.post(f"/api/mir/carga/{codigo}/", {"archivo": fh, "periodo": per})
nombre = next(f for f in os.listdir(CH) if f.startswith("LEGAJO_NYA_2026"))
with open(os.path.join(CH, nombre), "rb") as fh:
    opch.post("/api/mir/carga/LEGAJO_NYA/", {"archivo": fh, "periodo": per})
estado = {a["codigo"]: a["importada"] for a in opch.get("/api/mir/resultado/").json()["archivos"]}
paso("MPI, MPE y MPJ y DAE quedaron para volver a cargar", not estado["MPI"] and not estado["MPE"] and not estado["MPJ_DAE"] and estado["DISP_PENAL"], str(estado))

print()
print("RESULTADO:", "todo OK" if not fallas else f"{len(fallas)} falla(s): " + "; ".join(fallas))
