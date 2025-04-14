# 🚴 Berlin Bicycle Data Pipeline
This project implements a modern end-to-end data pipeline that ingests, transforms, and visualizes public [bicycle traffic data from the city of Berlin](https://www.berlin.de/sen/uvk/mobilitaet-und-verkehr/verkehrsplanung/radverkehr/weitere-radinfrastruktur/zaehlstellen-und-fahrradbarometer/). It was developed as part of the DataTalksClub [Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp) and demonstrates key data engineering concepts.
## 📊 About the Data
The dataset used in this project comes from [Berlin’s official Fahrradbarometer](https://www.berlin.de/sen/uvk/mobilitaet-und-verkehr/verkehrsplanung/radverkehr/weitere-radinfrastruktur/zaehlstellen-und-fahrradbarometer/) program, which continuously measures bicycle traffic at various locations throughout the city. These automatic counting stations record the number of bicycles passing by every hour and have been collecting data for over a decade. The Berlin Senate Department provides this data publicly as yearly XLSX files, making it a regularly maintained open dataset.

The dataset includes:
- Hourly counts of cyclists per station
- Station metadata including location names and coordinates
- Time coverage from 2012 onward

It offers valuable insight into mobility patterns, commuting behavior, and long-term trends in urban cycling – especially relevant as Berlin expands its cycling infrastructure.
## 🔧 Stack Overview
The pipeline is built using the following tools and architecture:
- Infrastructure as Code: Google Cloud resources (GCS, BigQuery) are provisioned with [Terraform](https://www.terraform.io).
- Orchestration: [Prefect](https://www.prefect.io) handles the data pipeline
	- Downloads the XLSX file
	- Converts it to Parquet
	- Uploads to a Google Cloud Storage bucket
	- Loads data in BigQuery
	- Runs dbt
- Data transformation: [dbt](https://www.getdbt.com) is used for transforming data into a star schema, making it usable for visualization
	- dim_date: calendar table
	- dim_station_fahrradbarometer: station metadata (e.g. name, coordinates)
	- fact_fahrradbarometer: hourly bicycle counts
- Visualization: Data is visualized using [Evidence](https://evidence.dev), allowing users to explore trends and patterns in cycling activity.

This project shows how publicly available government data can be turned into a usable data product using modern tools and best practices in data engineering. It is also easily extendable – for example by integrating weather data, or more interactive dashboards.
## ▶️ Run the project
### 1. Terraform
#### Prerequisites
- Terraform must be installed. Download and installation instructions can be found [here](https://developer.hashicorp.com/terraform/tutorials/gcp-get-started/install-cli).
- A [Google Cloud Service Account](https://cloud.google.com/iam/docs/service-accounts-create) with the following roles:
	- Compute Admin
	- Storage Admin
	- BigQuery Admin

Ensure your service account has the necessary permissions to manage resources within your Google Cloud Project.
#### Authentication and Provider Configuration
This project uses the [hashicorp/google](https://registry.terraform.io/providers/hashicorp/google/latest) provider.
For authentication, Terraform expects certain environment variables to be exported (More information can be found  [here](https://registry.terraform.io/providers/hashicorp/google/latest/docs/guides/provider_reference#authentication-configuration) and [here](https://registry.terraform.io/providers/hashicorp/google/latest/docs/guides/provider_reference#provider-default-values-configuration)):
- GOOGLE_CREDENTIALS: Path to your service account JSON key file
- GOOGLE_PROJECT: ID of your Google Cloud Project
- GOOGLE_REGION: The default region for your resources
  
Additionally, the following Terraform-specific variables must be set in your environment (More information can be found [here](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket#argument-reference)):
- TF_VAR_location: The location (region) for the GCS bucket
- TF_VAR_gcs_bucket_name: Globally unique bucket name (must be created individually)
See the provided terraform/.env_template file for reference.
#### Usage
After setting the required environment variables, initialize and apply the Terraform configuration:
```
terraform init
terraform apply
```
This will create all necessary resources defined in this Terraform project within your specified Google Cloud environment.
### 2. Prefect and DBT
This project uses Prefect to orchestrate the entire data pipeline, from loading data to triggering a dbt run. dbt is used to transform raw data tables into a star schema, optimized for analytics with Evidence.
#### Prerequisites
Docker must be installed to run Prefect and dbt in containers. You can download Docker from [here](https://www.docker.com).
#### Environment Setup
Before running the containers with Docker Compose, ensure that the same Google Cloud environment variables used in the Terraform step are exported on your host system:
- GOOGLE_CREDENTIALS: Path to your service account JSON key file
- GOOGLE_PROJECT: ID of your Google Cloud Project
- GOOGLE_REGION: The default region for your resources

Refer to the terraform/.env_template file for guidance.
Additionally, you must configure the .env_template file located in the root of the project. This file contains container-specific environment variables.
##### Steps:
- Replace placeholders in the .env_template file with your previously chosen GCS bucket name.
- Rename the file from .env_template to .env.
#### Running the Pipeline
Once everything is set up, you can start the full pipeline with:
```
docker compose up
```
This will:
- Load the raw data
- Upload it to your specified GCS bucket
- Transform the data using dbt
- Store the final tables in BigQuery in the *dbt_gold* dataset

You can also monitor and interact with Prefect via its UI:
- Open http://localhost:4200/dashboard in your browser
- View the run progress or manually trigger a new flow
### 3. Evidence
Evidence is used to visualize the transformed data from BigQuery.
#### Prerequisites
- Node.js must be installed. You can get it from [here](https://nodejs.org/en)
- Evidence can be used either:
	- As a standalone tool installed via npm
	- As a Visual Studio Code extension

Refer to the official documentation for installation options: [Evidence Installation Guide](https://docs.evidence.dev/install-evidence/)
#### Running Evidence
After installing Evidence, navigate to the /evidence directory and run:
```
npm run dev
```
This starts the Evidence development server, which can be accessed at:
http://localhost:3000

##### Configuring BigQuery as a Data Source
In the Evidence settings, you need to authorize access to BigQuery. Instructions for this can be found in the official documentation: [Evidence BigQuery Configuration](https://docs.evidence.dev/core-concepts/data-sources/bigquery)

Once configured:
- Stop the running Evidence server.
- Run the following commands from the /evidence directory:
```
npm run sources
npm run dev
```
This will load the data from BigQuery and your dashboards should now display the correct visualizations.