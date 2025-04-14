FROM python:3.12-slim
RUN apt-get update && apt-get install -y gettext && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY prefect/ ./prefect/
COPY dbt_fahrradbarometer/ ./dbt_fahrradbarometer/
RUN mkdir -p /root/.dbt
COPY profiles.yml .
RUN dbt deps --project-dir ./dbt_fahrradbarometer
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "prefect/extract_data.py"]