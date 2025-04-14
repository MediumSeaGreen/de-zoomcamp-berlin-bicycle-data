# DBT Fahrradbarometer Project

This folder contains the DBT project for processing and transforming bicycle barometer data. The project is structured to follow a multi-layered data pipeline, progressing from raw data ingestion to a refined star schema optimized for visualization.

## Data Pipeline Overview

The pipeline is divided into three main layers:

### 1. Landing Layer
The landing layer (fahrradbarometer dataset) contains the raw data. These files are first loaded into a bucket using Prefect and then ingested into the landing layer. This data serves as the starting point for transformations.

### 2. Silver Layer
The silver layer processes and cleans the raw data from the landing layer. This includes:
- Generating surrogate keys for consistency and efficient joins.
- Filtering and deduplicating data.
- Preparing the data for downstream transformations.

The silver layer ensures that the data is in a clean and structured format, ready for further enrichment in the gold layer.

### 3. Gold Layer
The gold layer represents the final stage of the pipeline and is designed as a star schema. This schema is optimized for analytical queries and efficient use with visualization tools like Evidence. The gold layer consists of:
- Fact Tables: Contain measures and foreign keys to dimension tables (e.g., `fct_fahrradbarometer`).
- Dimension Tables: Provide descriptive attributes for analysis (e.g., `dim_station_fahrradbarometer`, `dim_date`).

## Purpose of the Star Schema
The star schema in the gold layer enables:
- Fast and efficient querying for analytical purposes.
- Easy integration with visualization tools.
- A clear separation of measures (facts) and descriptive attributes (dimensions).

## Visualization with Evidence
The processed data in the gold layer is intended for use with Evidence, a modern visualization tool. Evidence allows users to create interactive dashboards and reports, leveraging the structured star schema for insightful analysis.

## Folder Structure
- models/silver: Contains SQL models for transforming raw data into the silver layer.
- models/gold: Contains SQL models for creating the star schema in the gold layer.
