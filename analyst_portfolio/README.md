# Marketing ROI — Portafolio de Data Analyst

Análisis exploratorio en Python (pandas, matplotlib, seaborn) sobre los datos ya
modelados por el pipeline de este repo — la parte de ingeniería (Postgres/CDC, Airbyte,
MotherDuck, dbt, Airflow) vive en la raíz del repo y en `docs/ROADMAP.md`. Esta carpeta
es la capa de análisis: responde con notebooks a las preguntas de negocio del proyecto
en vez de construir el dashboard de Power BI planeado en el roadmap.

## Pregunta de negocio

> ¿Cuánto gasta la empresa por canal de marketing, cuánto revenue le trae ese gasto, y
> qué dice el resto de los datos (pedidos, clientes, productos, reviews) sobre por qué?

(Ver `docs/CASO-DE-NEGOCIO.md` para el contexto completo del proyecto.)

## Notebooks

| Notebook | Contenido |
| --- | --- |
| `01_exploracion_pedidos.ipynb` | Volumen de pedidos, estados, AOV, tiempos de entrega |
| `02_roi_marketing_por_canal.ipynb` | CAC/ROAS por canal, gasto vs. presupuesto |
| `03_clientes_productos_satisfaccion.ipynb` | Geografía de clientes, categorías de producto, delivery vs. review score |

Cada notebook está commiteado **ya ejecutado** (con outputs y gráficos embebidos), así
que se puede leer directamente en GitHub sin correr nada.

## Datos

Los notebooks leen Parquet local en `data/raw/` — un snapshot de los marts de dbt
(`marketing_roi.marts.*` en MotherDuck) más dos tablas de staging necesarias para el
detalle de línea de pedido (`stg_postgres__order_items`, `stg_postgres__order_reviews`).
El snapshot se commitea junto con el código: el portafolio corre sin credenciales ni
conexión al warehouse real.

Para regenerar el snapshot con datos frescos (requiere `MOTHERDUCK_TOKEN` en el `.env`
de la raíz del repo, igual que dbt):

```bash
uv run python analyst_portfolio/export_data.py
```

### Caveats de los datos (documentados en los propios modelos dbt, no descubiertos acá)

- **Atribución de marketing es estimada, no medida**: ningún pedido/pago trae un canal
  de origen en los datos fuente. `fct_marketing_performance` reparte revenue y clientes
  nuevos del día entre los canales activos, en proporción a su `spend_share`. El
  notebook 02 lo trata explícitamente como estimación.
- **Salto de fechas 2018 → 2026**: el histórico real (Olist, 2016-2018) convive con
  pedidos sintéticos que simulan operación "actual". El notebook 01 separa ambas eras
  en vez de graficarlas en un solo eje continuo.
- **`budget_target` es NULL antes del año en curso**: el Sheet de metas no tiene
  backfill retroactivo. La comparación gasto-vs-presupuesto del notebook 02 solo cubre
  los meses donde existe meta.

## Cómo reproducir

```bash
# desde la raíz del repo
uv run jupyter lab analyst_portfolio/notebooks/
```

O para re-ejecutar todo de punta a punta y regenerar los outputs:

```bash
uv run python analyst_portfolio/export_data.py
uv run jupyter nbconvert --to notebook --execute --inplace analyst_portfolio/notebooks/*.ipynb
```

## Stack

Python 3.12, pandas, matplotlib, seaborn, duckdb (solo para el export), Jupyter —
gestionado con `uv` igual que el resto del repo (mismo `pyproject.toml`/`uv.lock`, sin
entorno separado).
