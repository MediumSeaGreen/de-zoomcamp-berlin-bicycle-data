variable "location" {
  description = "Project location in GCP"
  type        = string
}

variable "bq_dataset_name" {
  description = "BigQuery dataset name"
  type        = string
  default = "fahrradbarometer"
}

variable "gcs_bucket_name" {
  description = "Storage Bucket Name"
  type        = string
}

variable "jahresdatei_table_id" {
  description = "BigQuery table ID for jahresdatei_table"
  type        = string
  default = "jahresdatei_fahrradbarometer"
}

variable "standortdaten_table_id" {
  description = "BigQuery table ID for standortdaten_table"
  type        = string
  default = "standortdaten_fahrradbarometer"
}