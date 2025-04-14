import re
import unicodedata

import pyarrow as pa
import pyarrow.parquet as pq


def clean_col_name(col_name):
    """
    Cleans a column name by normalizing, removing special characters,
    and converting it to a standardized format.

    Args:
        col_name (str): The original column name.

    Returns:
        str: The cleaned column name.
    """
    nfkd_form = unicodedata.normalize("NFKD", col_name)
    name = "".join(c for c in nfkd_form if not unicodedata.combining(c))
    name = name.lower()
    name = name.replace("-", "_")
    name = re.sub(r"\s+", "", name)
    name = re.sub(r"[^0-9a-z_]", "", name)
    name = re.sub(r"_+", "_", name)
    name = name.strip("_")

    return name


def df_to_parquet(df, sheet_name):
    """
    Converts a pandas DataFrame to a Parquet file based on the sheet name.

    Args:
        df (pandas.DataFrame): The DataFrame to be converted.
        sheet_name (str): The name of the sheet, used to determine the output path.

    Raises:
        ValueError: If the sheet name is invalid.
    """
    sheet_name_clean = sheet_name.lower().replace(" ", "_")
    match sheet_name_clean:
        case "standortdaten":
            filename = f"standortdaten/{sheet_name_clean}.parquet"
        case _ if sheet_name_clean.startswith("jahresdatei"):
            filename = f"jahresdatei/{sheet_name_clean}.parquet"
        case _:
            raise ValueError(f"Invalid sheet name: {sheet_name_clean}")

    table = pa.Table.from_pandas(df)
    pq.write_table(
        table,
        f"parquet/{filename}",
        coerce_timestamps="ms",
        allow_truncated_timestamps=True,
    )


def jahresdatei_df_to_long(df):
    """
    Transforms a DataFrame from wide format to long format for 'jahresdatei' data.

    Args:
        df (pandas.DataFrame): The input DataFrame in wide format.

    Returns:
        pandas.DataFrame: The transformed DataFrame in long format.
    """
    df.rename(columns={"Zählstelle": "timestamp"}, inplace=True)
    df = df.melt(id_vars="timestamp", var_name="Zählstelle", value_name="value")
    return df
