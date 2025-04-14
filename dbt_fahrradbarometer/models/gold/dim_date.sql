{{ config(
    materialized='incremental',
    unique_key='timestamp'
) }}

with params as (
    select
        timestamp('2015-01-01 00:00:00 UTC') as start_timestamp,
        timestamp_trunc(current_timestamp(), year) - interval 1 hour as end_timestamp
),

hourly_series as (
    select
        timestamp
    from params,
    unnest(generate_timestamp_array(
        start_timestamp,
        end_timestamp,
        interval 1 hour
    )) as timestamp
),

dim_date as (
    select
        timestamp,
        cast(timestamp as date) as date,
        extract(hour from timestamp) as hour,
        mod(extract(dayofweek from timestamp) + 5, 7) + 1 as day_of_week,
        extract(dayofyear from timestamp) as day_of_year,
        extract(week from timestamp) as week,
        extract(month from timestamp) as month,
        extract(quarter from timestamp) as quarter,
        extract(year from timestamp) as year
    from hourly_series
),

add_key as (
    select
        {{ dbt_utils.generate_surrogate_key(['timestamp']) }} as hk_timestamp_id,
        *
    from dim_date
)

select * from add_key
{% if is_incremental() %}
where timestamp > (select max(timestamp) from {{ this }})
{% endif %}
