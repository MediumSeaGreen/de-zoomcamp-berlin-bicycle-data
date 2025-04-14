/*
This file defines the fact table `fct_fahrradbarometer` in the star schema.
The table includes measures such as `value` (the count of bicycles) and foreign keys 
to dimensions like `hk_counting_station_id` and `hk_timestamp_id`.
The data is filtered to include records from 2015 onwards.
*/

select
    hk_counting_station_id,
    hk_timestamp_id,
    value
from {{ ref('year_data_fahrradbarometer') }} ydf
where timestamp >= '2015-01-01'