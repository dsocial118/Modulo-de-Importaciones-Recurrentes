# Propuesta general de seguridad, escalabilidad y confiabilidad de MIR

**Fecha:** 2 de octubre de 2026
**Estado:** propuesta documentada; controles sujetos a definición, implementación y verificación.

Se incorpora docs/mir/seguridad.md, a partir del texto revisado y autorizado por el responsable funcional, como arquitectura objetivo general del módulo.

La propuesta equilibra importación, protección de la base y utilización de los datos. Incluye auditoría de consultas sobre la Capa 3, cargas por lotes, recuperación ante cortes y rendimiento. Mantiene abierta la elección del motor de base de datos y no establece cifrado individual de campos como requisito general.

Se enlaza desde el README principal, el índice de MIR, la API y los pendientes de arquitectura. Se distingue la propuesta del estado implementado y se explicita que el relevamiento histórico de pertenencia a entidades debe leerse junto con los avances documentados de la API nueva.

Se conservó el contenido aportado por el usuario, con formato Markdown, una corrección terminológica de «autentificación» a «autenticación», referencias técnicas y enlaces de navegación. No se modificaron código, datos ni configuración de servicios.
