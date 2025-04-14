# Prefect Folder

This folder contains the implementation of the data pipeline orchestrated using Prefect. Below is an overview of its contents:

- extract_data.py: The main script defining the Prefect flow for the pipeline. It includes tasks for downloading, processing, and uploading data, as well as triggering dbt transformations.
- helper.py: A utility module with helper functions for data cleaning, file conversion, and other reusable logic.
- constants.py: Contains constants such as the source URL for the raw data.

## Key Features
- Data Extraction: Downloads raw data from the specified source.
- Data Transformation: Converts raw data into Parquet format and prepares it for further processing.
- Integration with GCS and BigQuery: Uploads processed data to Google Cloud Storage and loads it into BigQuery.
- Orchestration: Manages the end-to-end pipeline flow using Prefect.