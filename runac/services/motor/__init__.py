"""El motor de RUNAC, tal como se probó fuera de Django.

Estos módulos son los mismos que usa la skill `runac-capa1`. Se copian acá para
que la aplicación los use sin depender de nada externo, y para que el día que
esto se integre a SISOC se muden con la app.

No dependen de Django: son Python puro más openpyxl. Esa es la razón por la que
se pueden mover sin reescribir.
"""
