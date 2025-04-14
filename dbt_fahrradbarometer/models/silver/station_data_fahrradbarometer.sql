/*
This model processes counting station meta data by:
- Generating surrogate keys for counting stations.
- Filtering new data during incremental runs.
- Preparing the data for downstream transformations in the silver layer.
*/

{{ config(
    unique_key='counting_station_id'
) }}

WITH source_data AS (

    SELECT
        {{ dbt_utils.generate_surrogate_key(['zahlstelle']) }} as hk_counting_station_id,
        zahlstelle as counting_station_id,
        beschreibung_fahrtrichtung as counting_station_name,
        breitengrad as latitude,
        langengrad as longitude,
        installationsdatum as installation_date,
    FROM {{ source('fahrradbarometer', 'standortdaten_fahrradbarometer') }}

    {% if is_incremental() %}
        WHERE 
          zahlstelle NOT IN (
              SELECT counting_station_id
              FROM {{ this }}
          )
    {% endif %}

)

SELECT * FROM source_data
