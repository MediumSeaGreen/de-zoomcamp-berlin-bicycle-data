import os
import re
import shutil
from io import BytesIO
import subprocess

import pandas as pd
import requests
from constants import SRC_URL
from prefect_gcp import GcpCredentials, GcsBucket, BigQueryWarehouse

from prefect import flow, task
from prefect.logging import get_run_logger
from helper import clean_col_name, df_to_parquet, jahresdatei_df_to_long


@task
def get_data():
    logger = get_run_logger()
    logger.info(f"Get data from {SRC_URL}")
    response = requests.get(SRC_URL)
    response.raise_for_status()

    return BytesIO(response.content)


@task
def xlsx_to_parquet(raw_data):
    logger = get_run_logger()
    logger.info("Transform xlsx to paraquet")

    xls = pd.ExcelFile(raw_data)
    pattern = r"^Jahresdatei\s\d{4}$"

    sheet_names = xls.sheet_names
    for sheet_name in sheet_names:
        if sheet_name == "Standortdaten":
            df = xls.parse(sheet_name)
            df.columns = [clean_col_name(col) for col in df.columns]
            df_to_parquet(df, sheet_name)
        if re.match(pattern, sheet_name):
            df = xls.parse(sheet_name)
            df.columns = [col.split()[0] for col in df.columns]
            df = jahresdatei_df_to_long(df)
            df.columns = [clean_col_name(col) for col in df.columns]
            df_to_parquet(df, sheet_name)


@task
def upload_to_gcs():
    logger = get_run_logger()
    logger.info("Upload data to gcs bucket")

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
    logger = get_run_logger()
    logger.info("Load data to BigQuery")

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
    logger = get_run_logger()
    logger.info("Run dbt")

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


# Run the flow
if __name__ == "__main__":
    extract_data()
    extract_data.serve()
