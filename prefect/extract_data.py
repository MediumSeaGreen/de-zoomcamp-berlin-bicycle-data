import os
import re
import shutil
import subprocess
from io import BytesIO

import pandas as pd
import requests
from constants import SRC_URL
from helper import clean_col_name, df_to_parquet, jahresdatei_df_to_long
from prefect_gcp import BigQueryWarehouse, GcpCredentials, GcsBucket

from prefect import flow, task
from prefect.logging import get_run_logger


@task
def get_data():
    """
    Fetches data from the source URL defined in the constants module.

    Returns:
        BytesIO: The content of the fetched data as a BytesIO object.
    """
    logger = get_run_logger()
    logger.info(f"Fetching data from {SRC_URL}")
    response = requests.get(SRC_URL)
    response.raise_for_status()
    return BytesIO(response.content)


@task
def xlsx_to_parquet(raw_data):
    """
    Transforms Excel data into Parquet format. Processes specific sheets
    based on their names and applies transformations as needed.

    Args:
        raw_data (BytesIO): The raw Excel data to be processed.
    """
    logger = get_run_logger()
    logger.info("Transforming Excel data to Parquet format")

    xls = pd.ExcelFile(raw_data)
    pattern = r"^Jahresdatei\s\d{4}$"

    for sheet_name in xls.sheet_names:
        if sheet_name == "Standortdaten":
            df = xls.parse(sheet_name)
            df.columns = [clean_col_name(col) for col in df.columns]
            df_to_parquet(df, sheet_name)
        elif re.match(pattern, sheet_name):
            df = xls.parse(sheet_name)
            df.columns = [col.split()[0] for col in df.columns]
            df = jahresdatei_df_to_long(df)
            df.columns = [clean_col_name(col) for col in df.columns]
            df_to_parquet(df, sheet_name)


@task
def upload_to_gcs():
    """
    Uploads the transformed Parquet files to a Google Cloud Storage bucket.
    The bucket name and credentials are retrieved from environment variables.
    """
    logger = get_run_logger()
    logger.info("Uploading Parquet files to Google Cloud Storage")

    gcp_credentials = GcpCredentials(
        service_account_file=os.getenv("GOOGLE_CREDENTIALS")
    )
    gcs_bucket = GcsBucket(
        bucket=os.getenv("GCS_BUCKET_NAME"),
        gcp_credentials=gcp_credentials,
    )
    gcs_bucket.upload_from_folder("parquet")


@task
def load_data_to_bq():
    """
    Loads data from Google Cloud Storage into BigQuery tables. The source URIs
    and table names are retrieved from environment variables.
    """
    logger = get_run_logger()
    logger.info("Loading data into BigQuery")

    gcp_credentials = GcpCredentials(
        service_account_file=os.getenv("GOOGLE_CREDENTIALS")
    )

    with BigQueryWarehouse(gcp_credentials=gcp_credentials) as warehouse:
        warehouse.execute(f"""
        LOAD DATA OVERWRITE fahrradbarometer.jahresdatei_fahrradbarometer
            FROM FILES (
                format = 'PARQUET', 
                uris = {os.getenv("JAHRESDATEI_TABLE_SRC_URIS")}
            );
        """)
        warehouse.execute(f"""
        LOAD DATA OVERWRITE fahrradbarometer.standortdaten_fahrradbarometer
            FROM FILES (
                format = 'PARQUET', 
                uris = {os.getenv("STANDORTDATEN_TABLE_SRC_URIS")}
            );
        """)


@task
def run_dbt():
    """
    Executes dbt (data build tool) transformations. Logs the output or errors
    if the process fails.
    """
    logger = get_run_logger()
    logger.info("Running dbt transformations")

    try:
        result = subprocess.run(
            ["dbt", "run"],
            cwd="/app/dbt_fahrradbarometer",
            capture_output=True,
            text=True,
            check=True,
        )
        logger.info(result.stdout)
    except subprocess.CalledProcessError as e:
        logger.error("Error while running dbt:")
        logger.error(e.stderr)
        raise


@flow(log_prints=True)
def extract_data():
    """
    Main flow to orchestrate the data extraction, transformation, and loading process.
    It performs the following steps:
    1. Fetches raw data from the source.
    2. Transforms the data into Parquet format.
    3. Uploads the Parquet files to Google Cloud Storage.
    4. Loads the data into BigQuery tables.
    5. Runs dbt transformations.
    """
    if not os.path.exists("parquet"):
        os.makedirs("parquet/standortdaten")
        os.makedirs("parquet/jahresdatei")

    raw_data = get_data()
    xlsx_to_parquet(raw_data)
    upload_to_gcs()

    if os.path.exists("parquet"):
        shutil.rmtree("parquet")

    load_data_to_bq()
    run_dbt()


if __name__ == "__main__":
    extract_data()
    extract_data.serve()
