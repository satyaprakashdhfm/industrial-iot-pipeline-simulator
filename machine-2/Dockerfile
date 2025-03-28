FROM python:3.9-slim
WORKDIR /app
COPY sensor.py /app/
RUN pip install opcua
CMD ["python", "sensor.py"]
