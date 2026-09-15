# -*- coding: utf-8 -*-
"""Cada instancia con su propia galleta de sesion. Se borra despues."""
import io

p = '/app/config/settings.py'
s = io.open(p, encoding='utf-8').read()

ROTO = '''# Las dos instancias -la v1 en el 8100 y la v2 en el 8101- corren en el MISMO
# localhost, y una galleta de sesion no distingue puerto: se llaman igual y se
# pisan. Entrar en una deslogueaba la otra, y parecia que el usuario o la clave
# estaban mal. Se le pone a cada una el nombre de su base, asi conviven abiertas
# en dos pestanas.
SESSION_COOKIE_NAME = fsesion_{DATABASES[default][NAME]}
CSRF_COOKIE_NAME = fcsrf_{DATABASES[default][NAME]}

'''

BUENO = '''# Las dos instancias -la v1 en el 8100 y la v2 en el 8101- corren en el MISMO
# localhost, y una galleta de sesion NO distingue puerto: se llamaban igual y se
# pisaban. Entrar en una deslogueaba la otra, y desde la pantalla parecia que el
# usuario o la contrasena estaban mal. Se le pone a cada una el nombre de su
# base, asi conviven abiertas en dos pestanas.
_BASE = DATABASES["default"]["NAME"]
SESSION_COOKIE_NAME = "sesion_" + _BASE
CSRF_COOKIE_NAME = "csrf_" + _BASE

'''

if ROTO in s:
    s = s.replace(ROTO, BUENO, 1)
else:
    ancla = 'AUTH_PASSWORD_VALIDATORS = []  # prototipo: no molestar al equipo con esto'
    assert ancla in s, 'no esta el ancla'
    s = s.replace(ancla, BUENO + ancla, 1)

io.open(p, 'w', encoding='utf-8').write(s)
print('settings.py: galletas separadas por base')
