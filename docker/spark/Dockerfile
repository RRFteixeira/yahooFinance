FROM apache/spark-py:v3.4.0
USER root
WORKDIR /app

# copy only requirements first to leverage layer caching
COPY requirements.txt /app/requirements.txt
RUN python3 -m pip install --no-cache-dir -r /app/requirements.txt

ENV PYSPARK_PYTHON=python3 \
    PYSPARK_DRIVER_PYTHON=python3

# default command (can be overridden by compose)
CMD ["python3", "-m", "src.transforms._smoke_spark"]
