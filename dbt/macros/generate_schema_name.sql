{#
    Override estándar de dbt: usa el `+schema:` de cada carpeta (staging/marts)
    tal cual, sin prefijarlo con el schema del target (`dev`). Sin esto dbt
    crea `dev_staging`/`dev_marts` en vez de `staging`/`marts`.
    Ver docs/ROADMAP.md -> Fase 3 -> "Listo para implementar", decisión #5.
#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
