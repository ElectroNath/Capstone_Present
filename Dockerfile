FROM apache/airflow:2.8.3
ADD requirements.txt .
# Copy the .env file into the container
COPY .env .

# # Debugging - Print the content of the .env file
# RUN cat .env

# # Load the environment variables from the .env file
# RUN set -o allexport && source .env && set +o allexport

# # Debugging - Print the content of the environment variables
# RUN printenv

RUN pip install --no-cache-dir apache-airflow==${AIRFLOW_VERSION} -r requirements.txt


# Remember to run with the below code 
# env $(cat .env | grep -v '^#' | xargs) docker build -t apache/airflow:2.8.3 .
