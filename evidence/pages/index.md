---
title: "Fahrradbarometer"
---

# Fahrradbarometer Berlin

These visualizations present current cycling traffic data in Berlin, collected through automatic permanent counting stations and bicycle counters operated by the Senate Department for Mobility, Transport, Climate Protection, and Environment. Their purpose is to illustrate long-term developments in cycling, document seasonal fluctuations, and evaluate the effectiveness of infrastructure measures. Bicycle traffic data has been collected in Berlin since 1983, with automatic permanent counting stations complementing traditional manual counts since 2012.

[Zählstellen und Fahrradbarometer](https://www.berlin.de/sen/uvk/mobilitaet-und-verkehr/verkehrsplanung/radverkehr/weitere-radinfrastruktur/zaehlstellen-und-fahrradbarometer/)

## Annual Totals and Average Counts

This visualization compares the total number of cyclists counted each year alongside the average count per station. The average count helps highlight general trends, accounting for the increasing number of counting stations over time. Observe how, despite the addition of more stations, the overall number of cyclists has remained relatively stable, reflecting consistent cycling activity in Berlin.

```trend
select
dd.year,
sum(ff.value) as total_count,
sum(ff.value) / count(distinct ff.hk_counting_station_id) as average_count_per_station
from
    bigquery.fct_fahrradbarometer as ff
left join
    bigquery.dim_date as dd
on 
    ff.hk_timestamp_id = dd.hk_timestamp_id
group by
    dd.year
```

<BarChart 
    data={trend} 
    x=year 
    y=total_count
    y2=average_count_per_station
    y2SeriesType=line
/>

## Annual Total Counts
This bar chart shows the total number of cyclists counted per year at each station. The year 2024 is pre-selected, but you can use the dropdown menu to explore data from other years. Discover which stations experience the highest cycling traffic and observe how these patterns change over time.

```available_years
select
distinct year
from
bigquery.dim_date
where year >= 2015
```

<Dropdown 
    data={available_years} 
    name=year_select 
    value=year 
    title="Select a year"
    defaultValue={2024}
/>


```top_station_2024
select
    ds.counting_station_name,
    sum(ff.value) as total_value
from 
    bigquery.fct_fahrradbarometer as ff
left join
    bigquery.dim_date as dd
on 
    ff.hk_timestamp_id = dd.hk_timestamp_id
left join bigquery.dim_station_fahrradbarometer as ds
on
    ff.hk_counting_station_id = ds.hk_counting_station_id
where
    ds.counting_station_name is not null
    and dd.year = '${inputs.year_select.value}'
group by
    ds.counting_station_name,

```

<BarChart
    data={top_station_2024}
    x=counting_station_name
    y=total_value
    swapXY=true
    yFmt=num2m
/>


## Daily Counts
This line chart displays the daily number of cyclists passing through a selected counting station. By default, it shows data for Oberbaumbrücke Ost for the year 2024. Use the date selector to focus on a specific time range and the dropdown to switch between different counting stations. Beneath the chart, a map shows the location of the selected counting station in Berlin. This interactive tool allows you to examine detailed daily trends and identify peak cycling periods.

```station_locations
select
    hk_counting_station_id,
    counting_station_name,
    latitude,
    longitude
from
    bigquery.dim_station_fahrradbarometer
```


```dates
select
    date
from
    bigquery.dim_date
```

<DateRange
    name=date_range
    data={dates}
    dates=date
    defaultValue={'Year to Date'}
/>

```stations
select
counting_station_name,
from
bigquery.dim_station_fahrradbarometer
```

<Dropdown 
    data={stations} 
    name=station_select 
    value=counting_station_name
    title="Select a station"
    defaultValue={'Oberbaumbrücke Ost'}
/>

```counts_in_range_by_station
select
    dd.date as day,
    sum(ff.value) as total_value
from 
    bigquery.fct_fahrradbarometer as ff
left join
    bigquery.dim_date as dd
on 
    ff.hk_timestamp_id = dd.hk_timestamp_id
left join
    bigquery.dim_station_fahrradbarometer as ds
on 
    ff.hk_counting_station_id = ds.hk_counting_station_id
where
    ds.counting_station_name = '${inputs.station_select.value}'
    and dd.date between ('${inputs.date_range.start}'::date + interval 1 day) and ('${inputs.date_range.end}'::date + interval 1 day)
group by
    dd.date
```


<LineChart 
    data={counts_in_range_by_station}
    x=day
    y=total_value 
    yAxisTitle="Counts per day"
/>

```station_locations_filterd
select
    counting_station_name,
    latitude,
    longitude
from
    bigquery.dim_station_fahrradbarometer
where
    counting_station_name = '${inputs.station_select.value}'
```

<PointMap
    data={station_locations_filterd} 
    lat=latitude 
    long=longitude  
    pointName=counting_station_name 
/>