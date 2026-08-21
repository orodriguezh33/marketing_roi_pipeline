-- Publication + replication slot para CDC log-based (Fase 2: Airbyte Source Postgres).
-- Airbyte NO crea el replication slot al configurar la Source: el conector solo
-- verifica que exista (falla con "Replication slot 'airbyte_slot' not found" si no está)
-- y crearlo requiere el privilegio REPLICATION, que Airbyte no ejerce por su cuenta.
-- Por eso se crea acá, junto con la publication.
CREATE PUBLICATION airbyte_pub FOR ALL TABLES;
SELECT pg_create_logical_replication_slot('airbyte_slot', 'pgoutput');
