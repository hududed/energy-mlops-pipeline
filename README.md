# Step-by-step MLOps Framework

This is N-lesson course to design, implement, deploy and monitor an ML batch system


# Data
We used the daily energy consumption from Denmark data which you can access [here](https://www.energidataservice.dk/tso-electricity/ConsumptionDE35Hour).

# Pipelines
**To install every project individually:**
- [Feature Pipeline](/feature-pipeline/README.md)
- [Training Pipeline](/training-pipeline/README.md)
- [Batch Prediction Pipeline](/batch-prediction-pipeline/README.md)

# Orchestration
## Airflow
### Setup

You can read the official documentation here or follow the steps bellow for a fast start.

**TODO:** This setup is used for development. Check out what I have to do for production.  

### Install Python Package  
**TODO:** Move the installation to poetry. Do I need it as this code is running directly in Airflow?

```
pip install "apache-airflow[celery]==2.5.2" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.5.2/constraints-3.7.txt"
```

# Run
```
# Move to the airflow directory.
cd airflow

# Download the docker-compose.yaml file
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/stable/docker-compose.yaml'

# Make expected directories and set an expected environment variable
mkdir -p ./dags ./logs ./plugins
echo -e "AIRFLOW_UID=$(id -u)" > .env

# Initialize the database
docker-compose up airflow-init

# Start up all services
docker-compose up --build
```

# Clean Up
```
docker compose down --volumes --rmi all
```
