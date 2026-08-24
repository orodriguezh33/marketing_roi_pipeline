# Engineering Notes

Registro de problemas de infraestructura no triviales encontrados durante la
construcción del pipeline, y cómo se diagnosticaron y resolvieron. Pensado
como evidencia de trabajo real (no un tutorial copiado) para quien quiera
entrar al detalle técnico — el [README](README.md) se mantiene enfocado en
arquitectura y decisiones de alto nivel.

## Airbyte Postgres source: SSL Modes en `disable`

**Síntoma:** el check de conexión de Airbyte al source de Postgres fallaba de
inmediato con `Config check failed`, apenas después de abrir la conexión.

**Causa:** el source de Postgres en Airbyte se configura por defecto con
`SSL Modes = require`. Eso le dice al driver JDBC que exija TLS. El Postgres
de este proyecto corre localmente vía `docker-compose.yml` (`postgres:16`,
sin certificados configurados, `ssl = off`) — el driver intenta forzar TLS,
el servidor no lo soporta, y la conexión se corta al instante.

**Fix:** cambiar `SSL Modes` a `disable`, para que el driver no intente
negociar TLS.

**Por qué es una decisión válida y no un atajo inseguro:** Airbyte (corriendo
en el cluster `kind` local de `abctl`) y Postgres viven en la misma máquina,
dentro de Docker Desktop. El tráfico nunca sale a una red real — no hay nadie
"en el medio" que pueda interceptarlo, así que cifrarlo no agrega protección
real en este contexto. Si el pipeline llegara a apuntar a un Postgres remoto,
este valor debe volver a `require`/`verify-full` con certificados configurados
en el servidor.

## `host.docker.internal` resolviendo a una IPv6 sin ruta desde los pods

**Síntoma:** con `SSL Modes = disable` ya aplicado, el check de Airbyte
seguía fallando igual de rápido, con un error distinto:
`Network is unreachable`.

**Causa:** `host.docker.internal` resuelve a dos direcciones: una IPv6 y una
IPv4. El conector de Postgres de Airbyte corre sobre una JVM, que al recibir
ambas direcciones prueba primero la IPv6. Desde la red interna de pods del
cluster `kind` de `abctl` (donde corre Airbyte), esa IPv6 no tiene ruta de
salida — falla al instante, y la JVM no reintenta automáticamente con la IPv4
que sí conecta.

**Diagnóstico** (desde un pod del cluster, antes de aplicar nada):

```bash
export KUBECONFIG=~/.airbyte/abctl/abctl.kubeconfig
kubectl run nettest --rm -i --restart=Never --image=busybox:1.36 -n airbyte-abctl -- sh -c "
  nslookup host.docker.internal
  nc -zvw5 host.docker.internal 5434
"
```

Si `nslookup` devuelve dos direcciones y el `nc` falla o tarda, es este
problema. Se confirma cuál IP conecta probando cada una por separado con
`nc -zvw5 <ip> 5434`.

**Fix:** en vez de parchear cada conector uno por uno, se aplicó un fix a
nivel de todo el cluster: editar el `ConfigMap` de CoreDNS (`kube-system`)
para agregar un bloque `hosts` que responda la IPv4 correcta antes de
reenviar la consulta al DNS del host. Así, cualquier otro conector que en el
futuro necesite hablarle a la máquina host por ese hostname (por ejemplo
MinIO, usado en la ingesta de S3) no vuelve a pisar el mismo problema.

```bash
export KUBECONFIG=~/.airbyte/abctl/abctl.kubeconfig

cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: coredns
  namespace: kube-system
data:
  Corefile: |
    .:53 {
        errors
        health {
           lameduck 5s
        }
        ready
        kubernetes cluster.local in-addr.arpa ip6.arpa {
           pods insecure
           fallthrough in-addr.arpa ip6.arpa
           ttl 30
        }
        hosts {
           192.168.65.254 host.docker.internal
           fallthrough
        }
        prometheus :9153
        forward . /etc/resolv.conf {
           max_concurrent 1000
        }
        cache 30 {
           disable success cluster.local
           disable denial cluster.local
        }
        loop
        reload
        loadbalance
    }
EOF

kubectl rollout restart deployment coredns -n kube-system
kubectl rollout status deployment coredns -n kube-system --timeout=60s
```

(`192.168.65.254` es la IPv4 que Docker Desktop asignó en esta máquina —
reemplazar por la que devuelva el `nslookup` del diagnóstico si es distinta.)

Verificación: repetir el comando de diagnóstico — `nslookup` debe devolver
una sola dirección (la IPv4) y el `nc` debe decir `open`.

**Nota:** este cambio vive en el cluster `kind` (no en este repo) — no
persiste si se corre `abctl local uninstall` seguido de `abctl local
install`; hay que reaplicarlo.
