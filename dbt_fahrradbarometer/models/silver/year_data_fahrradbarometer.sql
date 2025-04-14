/*
This model processes yearly bicycle barometer data by:
- Generating surrogate keys for counting stations and timestamps.
- Filtering new data during incremental runs.
- Preparing the data for downstream transformations in the silver layer.
*/

{{ config(
    unique_key=['counting_station_id', 'timestamp']
) }}

WITH source_data AS (

    SELECT
        {{ dbt_utils.generate_surrogate_key(['zahlstelle']) }} as hk_counting_station_id,
        {{ dbt_utils.generate_surrogate_key(['timestamp']) }} as hk_timestamp_id,
        zahlstelle as counting_station_id,
        timestamp,
        value
    FROM {{ source('fahrradbarometer', 'jahresdatei_fahrradbarometer') }}

    {% if is_incremental() %}
        WHERE 
          timestamp > (
              SELECT max(timestamp)
              FROM {{ this }}
          )
    {% endif %}

)

SELECT * FROM source_data
