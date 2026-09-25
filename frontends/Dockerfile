# Front v2 del MIR. Un solo Dockerfile para todas las apps de frontends/, como
# en SISOC: la app se elige con APP.
#
#   dev   Vite con recarga en caliente. El código se monta desde afuera.
#   prod  La app compilada, servida por nginx bajo /v2/<APP>/.
#
# El certificado es opcional: sólo para redes que inspeccionan el tráfico
# seguro. Ver docs/INSTALAR.md.

FROM node:22.14.0-alpine AS dependencias
WORKDIR /frontends
COPY . .
RUN --mount=type=secret,id=certificado_ca,required=false \
    if [ -s /run/secrets/certificado_ca ]; then export NODE_EXTRA_CA_CERTS=/run/secrets/certificado_ca; fi; \
    npm ci --no-audit --no-fund

FROM dependencias AS dev
ARG APP=mir
ENV APP=${APP}
EXPOSE 5173
CMD ["sh", "-c", "npm run dev -w apps/${APP}"]

FROM dependencias AS compilado
ARG APP=mir
RUN npm run build -w apps/${APP}

FROM nginx:1.29-alpine AS prod
ARG APP=mir
ENV APP=${APP}
COPY --from=compilado /frontends/apps/${APP}/dist /usr/share/nginx/html/v2/${APP}
# Una app de una sola página: cualquier ruta de /v2/<APP>/ que no sea un
# archivo devuelve index.html, y el ruteo lo resuelve React.
RUN printf 'server {\n  listen 5173;\n  root /usr/share/nginx/html;\n  location /v2/%s/ {\n    try_files $uri /v2/%s/index.html;\n  }\n}\n' "$APP" "$APP" \
      > /etc/nginx/conf.d/default.conf
EXPOSE 5173
