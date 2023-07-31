# Step-by-step MLOps Framework

This is N-lesson course to design, implement, deploy and monitor an ML batch system


# Data
We used the daily energy consumption from Denmark data which you can access [here](https://www.energidataservice.dk/tso-electricity/ConsumptionDE35Hour).


# Set Up Additional Tools
**The code is tested only on Ubuntu 20.04 and 22.04 using Python 3.9.**

We use a `.env` file to store all our credentials. Every module that needs a `.env` file has a `.env.default` in the module's main directory that acts as a template. Thus, you have to run:
```shell
cp .env.default .env
```

## Prerequisites

1. [Poetry](https://python-poetry.org/docs/#installation)
2. [Docker](https://docs.docker.com/engine/install/ubuntu/)


## Hopsworks 

Create an account for [Hopsworks](https://www.hopsworks.ai/) as your serverless feature store.
Get an API key from your Hopsworks account settings. Afterward, you must create a new project and add these credentials to the `.env` file under the `FS_` prefix.

**!!!** The project name has to be different than **energy_consumption_02** as Hopsworks requires unique names across its serverless deployment.

## Weights & Biases

Create an account and a project on [Weights & Biases](https://wandb.ai/).
Go to your W&B user settings and create the API Key from there and the W&B entity & project. After you have to add these credentials to the `.env` file under the `WANDB_` prefix.

**If you want everything to work with the default settings, use the following naming conventions:**
- create an `entity` called `multimode-mlops`
- create a `project` called `energy_consumption`


# Pipelines
**To install every project individually:**
- [Feature Pipeline](/feature-pipeline/README.md)
- [Training Pipeline](/training-pipeline/README.md)
- [Batch Prediction Pipeline](/batch-prediction-pipeline/README.md)

# Orchestration
## Airflow
Run:
```shell
# Move to the airflow directory.
cd airflow

# Make expected directories and environment variables
mkdir -p ./logs ./plugins
sudo chmod 777 ./logs ./plugins

# It will be used by Airflow to identify your user.
echo -e "AIRFLOW_UID=$(id -u)" > .env
# This shows where our project root directory is located.
echo "ML_PIPELINE_ROOT_DIR=/opt/airflow/dags" >> .env
```

Now from the `airflow` directory move to the `dags` directory and run:
```shell
cd ./dags

# Make a copy of the env default file.
cp .env.default .env
# Open the .env file and complete the FS_API_KEY, FS_PROJECT_NAME and WANDB_API_KEY credentials 

# Create the folder where the program expects its GCP credentials.
mkdir -p credentials/gcp/energy_consumption
# Copy the GCP service credetials that gives you admin access to GCS. 
cp -r /path/to/admin/gcs/credentials/admin-buckets.json credentials/gcp/energy_consumption
# NOTE that if you want everything to work outside the box your JSON file should be called admin-buckets.json.
# Otherwise, you have to manually configure the GOOGLE_CLOUD_SERVICE_ACCOUNT_JSON_PATH variable from the .env file. 
```

Now go back to the `airflow` directory and run the following:
```shell
cd ..

# Initialize the Airflow database
docker compose up airflow-init

# Start up all services
# Note: You should set up the private PyPi server credentials before running this command.
docker compose --env-file .env up --build -d
```


# Clean Up
```
docker compose down --volumes --rmi all
```
