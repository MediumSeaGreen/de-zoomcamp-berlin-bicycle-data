resource "google_bigquery_dataset" "bike_dataset" {
  dataset_id = var.bq_dataset_name
  location   = var.location
}

resource "google_bigquery_table" "jahresdatei_table" {
  dataset_id = google_bigquery_dataset.bike_dataset.dataset_id
  table_id   = var.jahresdatei_table_id
  deletion_protection = false
}

resource "google_bigquery_table" "standortdaten_table" {
  dataset_id = google_bigquery_dataset.bike_dataset.dataset_id
  table_id   = var.standortdaten_table_id
  deletion_protection = false
}
