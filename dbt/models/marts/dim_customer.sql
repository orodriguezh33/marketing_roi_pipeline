-- Grano: un customer_id (equivalente a "cliente por pedido" en el dataset
-- Olist -- customer_unique_id es la persona real, customer_id es su alias
-- por pedido). Se mantiene customer_id como grano para que el join 1:1
-- contra fct_orders.customer_id sea directo.

with customers as (

    select * from {{ ref('stg_postgres__customers') }}

)

select
    customer_id,
    customer_unique_id,
    customer_city,
    customer_state,
    customer_zip_code_prefix
from customers
