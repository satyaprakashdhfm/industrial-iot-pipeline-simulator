FROM python:3.9-slim
WORKDIR /app
COPY gateway.py /app/
RUN pip install opcua paho-mqtt
CMD ["python", "gateway.py"]
