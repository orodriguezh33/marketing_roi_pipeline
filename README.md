# Marketing ROI Pipeline

Proyecto de portafolio de data engineering: pipeline de ingesta para responder,
para un e-commerce, "¿cuánto gastamos en marketing por canal vs. cuánto revenue nos
trae?" (CAC, ROAS, revenue vs. presupuesto). Combina cuatro fuentes heterogéneas
(Postgres vía CDC, Stripe, S3/MinIO, Google Sheets) orquestadas con Airflow, cargadas
vía Airbyte OSS a MotherDuck y transformadas con dbt.

**Estado:** diseño cerrado; Fases 1-4 implementadas (infra, ingesta 4 fuentes, dbt,
calidad de datos), Fase 5 (Airflow + Power BI) pendiente.

## Stack

Airbyte OSS (`abctl`) → MotherDuck → dbt (`dbt-duckdb`) → Power BI, orquestado por
Airflow. Detalle completo de arquitectura y decisiones en la documentación de diseño
del proyecto (no incluida en este repo — ver nota abajo).

## Notas de desarrollo local

### Airbyte Postgres source: SSL Modes en `disable`

El source de Postgres en Airbyte se configura con **SSL Modes = `disable`**, en vez
del `require` que la UI propone por defecto.

El Postgres de este proyecto corre localmente vía `docker-compose.yml`
(`postgres:16`, sin certificados configurados, `ssl = off`). Con `require`, el driver
JDBC intenta forzar TLS, el servidor no lo soporta, y la conexión se corta de
inmediato ("Config check failed" en el check de Airbyte, apenas después de abrir la
conexión).

Es una decisión deliberada, no un descuido: Airbyte (corriendo en el cluster `kind`
local de `abctl`) y Postgres viven en la misma máquina, dentro de Docker Desktop —
cifrar ese tráfico no agrega protección real. Si el pipeline llegara a apuntar a un
Postgres remoto, este valor debe volver a `require`/`verify-full` con certificados
configurados en el servidor.

### `host.docker.internal` resolviendo a una IPv6 sin ruta desde los pods

Con `SSL Modes = disable` el check de Airbyte seguía fallando igual de rápido. Causa
real: `host.docker.internal` devuelve tanto una dirección IPv6 como una IPv4; desde
la red de pods del cluster `kind` de `abctl`, la IPv6 no tiene ruta de salida
("Network is unreachable"), y el conector (JVM) prueba esa dirección primero, falla
al instante, y nunca reintenta con la IPv4 que sí conecta.

Fix aplicado: un `ConfigMap` de CoreDNS (`kube-system`, dentro del cluster `kind`,
fuera de este repo) que fija `host.docker.internal` a la IPv4 que efectivamente
conecta, para todo el cluster — así cualquier conector futuro que use ese hostname
(MinIO en Fase 2, por ejemplo) no vuelve a pisar el mismo problema. El paso a paso
completo (diagnóstico + comando) está en la documentación de setup local (ver nota
abajo).

---

Nota: la documentación de diseño y planificación de este proyecto vive en `docs/`,
que está excluido del repo (`.gitignore`) por ser material de trabajo en progreso.
