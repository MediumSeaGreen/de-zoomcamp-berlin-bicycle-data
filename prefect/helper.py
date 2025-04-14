import unicodedata
import re
import pyarrow as pa
import pyarrow.parquet as pq


def clean_col_name(col_name):
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
        allow_truncated_timestamps=True
    )

def jahresdatei_df_to_long(df):
    df.rename(columns={'Zählstelle': 'timestamp'}, inplace=True)
    df = df.melt(
        id_vars='timestamp',
        var_name='Zählstelle',
        value_name='value'
    )
    return df