select
    hk_counting_station_id,
    hk_timestamp_id,
    value
from {{ ref('year_data_fahrradbarometer') }} ydf
where timestamp >= '2015-01-01'