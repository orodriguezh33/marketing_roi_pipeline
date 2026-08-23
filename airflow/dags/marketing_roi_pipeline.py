"""Fase 5: dispara las 4 syncs de Airbyte (Fase 2) y, si todas terminan OK,
corre dbt run -> dbt test -> checkpoint de Great Expectations (Fase 3/4).

schedule=None: el trigger es manual (Airbyte también corre en modo manual-trigger,
ver docs/ROADMAP.md "Decisiones cerradas") — no hay backfill que considerar porque
no hay intervalos de tiempo que reprocesar, cada run es "el estado actual de las
4 fuentes, ahora".

Las 4 syncs corren encadenadas (una detrás de otra), no en paralelo: el cluster
local de Airbyte (abctl/k3d) y el scheduler de Airflow comparten los ~11.67 GB de
Docker Desktop en una Mac de 16 GB de RAM total -- 4 syncs simultáneas saturaban esa
memoria y mataban al pod airbyte-server (OOM, exit 137), lo que en cascada dejaba
jobs huérfanos y provocaba 409 state-conflict en el siguiente trigger (visto en el
run manual__2026-08-22T16:21:44). Ver docs/ROADMAP.md, Fase 5, decisión #1.

Alertas de Slack: ver docs/ROADMAP.md, Fase 5, ampliación 2026-08-22 (decisión #15,
skill data-observability-slack) -- Level 1: on_failure_callback genérico por task
(incluye el checkpoint de GE, que no manda alerta propia -- Policy B) y un único
on_success_callback a nivel DAG.
"""

from __future__ import annotations

import csv
import itertools
import os
from datetime import timedelta
from pathlib import Path

import pendulum
from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.airbyte.operators.airbyte import AirbyteTriggerSyncOperator
from airflow.providers.slack.notifications.slack_webhook import (
    send_slack_webhook_notification,
)

REPO_DIR = "/opt/airflow/repo"
DBT_DIR = f"{REPO_DIR}/dbt"
# Mismo volumen que ./logs (ver docker-compose.yml) -- persiste entre corridas de
# contenedor y queda consultable sin entrar a la UI de Airflow.
PIPELINE_DURATIONS_LOG = Path("/opt/airflow/logs/pipeline_durations.csv")
AIRBYTE_CONN_ID = "airbyte_default"
# Nombre real por default de slack_webhook_conn_id en el provider -- así no hace falta
# pasarlo explícito en cada notifier. Se crea a mano en la UI de Airflow (ver
# docs/ROADMAP.md, Fase 5, decisión #14); la URL del webhook nunca vive en código/env
# leída por el DAG.
SLACK_WEBHOOK_CONN_ID = "slack_default"
# Proyecto sin despliegue multi-entorno (todo corre local vía docker compose) -- valor fijo.
ENVIRONMENT = "local"

task_failure_alert = send_slack_webhook_notification(
    slack_webhook_conn_id=SLACK_WEBHOOK_CONN_ID,
    text="""
:rotating_light: *ERROR -- task failed*

*Environment:* `"""
    + ENVIRONMENT
    + r"""`
*Pipeline:* `{{ dag.dag_id }}`
*Task:* `{{ ti.task_id }}`
*Run:* `{{ run_id }}`
*Attempt:* `{{ ti.try_number }}`

*Next:* revisar logs de Airflow.
<{{ ti.log_url }}|Ver logs>
""",
)


def log_pipeline_duration(context: dict) -> None:
    """Registra la duración end-to-end de la corrida en un CSV persistente.

    El success callback corre después de que el DAG completa, así que
    dag_run.end_date ya está seteado (a diferencia de un task dentro del DAG).
    """
    dag_run = context["dag_run"]
    duration_seconds = (dag_run.end_date - dag_run.start_date).total_seconds()
    PIPELINE_DURATIONS_LOG.parent.mkdir(parents=True, exist_ok=True)
    is_new_file = not PIPELINE_DURATIONS_LOG.exists()
    with PIPELINE_DURATIONS_LOG.open("a", newline="") as f:
        writer = csv.writer(f)
        if is_new_file:
            writer.writerow(["run_id", "start_date", "end_date", "duration_seconds"])
        writer.writerow(
            [
                dag_run.run_id,
                dag_run.start_date.isoformat(),
                dag_run.end_date.isoformat(),
                duration_seconds,
            ]
        )


dag_success_alert = send_slack_webhook_notification(
    slack_webhook_conn_id=SLACK_WEBHOOK_CONN_ID,
    text="""
:white_check_mark: *INFO -- pipeline completado*

*Environment:* `"""
    + ENVIRONMENT
    + r"""`
*Pipeline:* `{{ dag.dag_id }}`
*Run:* `{{ run_id }}`
*Duration:* `{{ dag_run.end_date - dag_run.start_date }}`

Las 4 syncs de Airbyte, dbt y el checkpoint de Great Expectations terminaron OK.
""",
)

# UUIDs reales de las 4 connections de Airbyte (Fase 2). No se conocen hasta que se
# crean en la UI/API de Airbyte del usuario -- ver docs/ROADMAP.md, Fase 5,
# "Listo para implementar", decisión #9 (Pendiente, no bloquea). Se leen con
# .get(..., "") en vez de os.environ[...] para que un valor faltante no rompa el
# parseo del DAG (lo que lo haría desaparecer de la UI) -- en cambio, la sync
# correspondiente falla en runtime con un mensaje de Airbyte claro.
AIRBYTE_SYNC_CONNECTIONS = {
    "sync_postgres_olist_cdc": os.environ.get("AIRBYTE_CONNECTION_ID_POSTGRES", ""),
    "sync_stripe_marketing_roi": os.environ.get("AIRBYTE_CONNECTION_ID_STRIPE", ""),
    "sync_minio_ads_spend": os.environ.get("AIRBYTE_CONNECTION_ID_S3", ""),
    "sync_google_sheets_budget": os.environ.get("AIRBYTE_CONNECTION_ID_SHEETS", ""),
}

default_args = {
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "on_failure_callback": task_failure_alert,
}

with DAG(
    dag_id="marketing_roi_pipeline",
    description="4 syncs de Airbyte -> dbt run -> dbt test -> checkpoint de Great Expectations",
    default_args=default_args,
    schedule=None,
    start_date=pendulum.datetime(2026, 8, 21, tz="UTC"),
    catchup=False,
    max_active_runs=1,
    tags=["marketing-roi"],
    on_success_callback=[log_pipeline_duration, dag_success_alert],
) as dag:
    sync_tasks = [
        AirbyteTriggerSyncOperator(
            task_id=task_id,
            airbyte_conn_id=AIRBYTE_CONN_ID,
            connection_id=connection_id,
            asynchronous=False,
            wait_seconds=5,
            timeout=3600,
        )
        for task_id, connection_id in AIRBYTE_SYNC_CONNECTIONS.items()
    ]
    # Encadenadas (no en paralelo) -- ver nota de memoria en el docstring del módulo.
    for upstream, downstream in itertools.pairwise(sync_tasks):
        upstream >> downstream

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="DBT_PROFILES_DIR=. uv run dbt run",
        cwd=DBT_DIR,
        execution_timeout=timedelta(minutes=30),
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="DBT_PROFILES_DIR=. uv run dbt test",
        cwd=DBT_DIR,
        execution_timeout=timedelta(minutes=15),
    )

    great_expectations_checkpoint = BashOperator(
        task_id="great_expectations_checkpoint",
        bash_command="uv run python quality/great_expectations/run_checkpoint.py",
        cwd=REPO_DIR,
        execution_timeout=timedelta(minutes=15),
    )

    sync_tasks >> dbt_run >> dbt_test >> great_expectations_checkpoint
