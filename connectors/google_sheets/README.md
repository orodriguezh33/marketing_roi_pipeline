# Google Sheets — `google-sheets-budget`

Metas de presupuesto de marketing por mes/canal: escritas por
`generators/generate_budget.py` a la tab `budget` de un Google Sheet.

## Source

- Tipo: **Google Sheets**.
- Authentication: el selector de método de auth por default suele mostrar
  "Authenticate via Google (OAuth)" con login interactivo — **no usar esa**, no es
  reproducible. Cambiar el método a **Service Account Key Authentication**; ahí
  aparece un textarea para pegar el JSON de credenciales ("Service Account
  Information" / "Service Account JSON Key").
- Credenciales: pegar el **contenido completo** del archivo (no la ruta) — de `{` a
  `}`:

  ```bash
  cat "$(grep '^GOOGLE_SHEETS_CREDENTIALS_JSON=' .env | cut -d= -f2-)"
  ```

- Spreadsheet: según la versión del conector el campo se llama **"Spreadsheet
  Link"** (URL completa, `https://docs.google.com/spreadsheets/d/<ID>/edit`) o
  **"Spreadsheet ID"** (solo el ID, `GOOGLE_SHEETS_SPREADSHEET_ID` de `.env`) — usar
  la etiqueta que efectivamente muestra la UI, no adivinar el formato.
- Sync mode: **Full Refresh | Overwrite** — igual que S3, no hay cursor/PK natural en
  una tabla de metas de presupuesto.
- Destination Namespace de la connection: dejar en "Destination default" — el schema
  `raw_sheets` ya lo define la Destination (ver abajo), no hace falta pisarlo por
  connection.

## Destination

- `motherduck-raw-sheets` → `md:marketing_roi`, `schema = raw_sheets`.

## Prerequisitos

- La tab `budget` del Sheet necesita al menos la fila de encabezados
  (`month,channel,budget_target`) para que el discover encuentre el stream. Si está
  vacía, correr el generador una vez antes de configurar la Source:

  ```bash
  uv run python generators/generate_budget.py
  ```

- El Sheet tiene que estar compartido (permiso **Editor**) con el email del service
  account, no solo con el usuario. Verificar cuál es ese email:

  ```bash
  CREDS=$(grep '^GOOGLE_SHEETS_CREDENTIALS_JSON=' .env | cut -d= -f2-)
  python3 -c "import json; print(json.load(open('$CREDS'))['client_email'])"
  ```

## Troubleshooting

**`PermissionError(13, 'Permission denied')` al guardar una Destination MotherDuck**
(no es específico de esta Source, pero apareció al configurar
`motherduck-raw-sheets`) — el log mostraba `Using DuckDB file at
/local/​md:marketing_roi`, señal de un carácter invisible pegado justo antes de
`md:` en el campo `destination_path`, que hace que el conector trate el valor como
ruta local en vez de como destino MotherDuck. Fix: borrar el campo por completo y
tipear `md:marketing_roi` a mano (sin pegar).

## Estado

Verificado en MotherDuck: `raw_sheets.budget` con 48 filas.
