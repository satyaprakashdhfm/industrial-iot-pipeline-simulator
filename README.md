<img width="1036" height="724" alt="image" src="https://github.com/user-attachments/assets/b720144a-6a2c-4f56-88b2-9aeda806b5e7" />
## Factory IoT Simulator — digital twin for an Industry 4.0 pipeline

**Overview**
A compact on-premises simulation of a factory IoT pipeline. Simulated machines produce OPC UA sensor data that flows through a gateway and MQTT broker into a local ingestion client and SQL Server. This repo demonstrates the general data flow used in modern industrial IoT (Industry 4.0) and is ready to be extended to cloud analytics (Azure IoT Hub, Stream Analytics, Data Lake, ML, Power BI).

**Quick start**

1. Clone the repo and from the repo root run:

```bash
docker-compose up --build
```

2. Services started by docker-compose: simulated machines, gateway (OPC UA), Eclipse Mosquitto (MQTT), mqtt-client (ingest), and SQL Server Express.

**Architecture (simple flow)**
Machine-1 / Machine-2  ->  Gateway (OPC UA)  ->  MQTT Broker  ->  MQTT Client  ->  SQL Database
(Cloud extension option) MQTT Client  ->  Azure IoT Hub  ->  Stream Analytics / Data Lake / SQL / ML / Power BI

**What this repo shows**

* On-premises simulation of device telemetry and industrial protocols (OPC UA, MQTT)
* Message ingestion and persistence into a relational store for analytics
* Clear extension points for cloud integration (IoT Hub, streaming, storage, ML)

**Files & folders to inspect**

* `docker-compose.yml` — service orchestration and examples of env vars used
* `machine-1/`, `machine-2/` — simulated sensor/device containers
* `gateway/` — OPC UA server/translator logic
* `mqtt-client/` — subscribes to MQTT and writes to DB (can be adapted to forward to IoT Hub)
* `database/` — SQL Server setup and persistence scripts
* `README.md` — this file

**Security & deployment notes**

* The compose file includes example credentials (SA\_PASSWORD). Change secrets before any public or production use.
* For production-ready deployment, use managed brokers (Azure IoT Hub), managed databases, secure identity (managed identities, key vault), TLS for MQTT, and network isolation.

**How to extend to Azure (brief)**

* Have the MQTT client forward messages to Azure IoT Hub (or use an IoT Edge module).
* Route events from IoT Hub to Stream Analytics or Event Hub for real-time processing.
* Store raw data in Data Lake Gen2 and processed results in Azure SQL / Synapse.
* Build dashboards with Power BI and models with Azure Machine Learning; deploy models to IoT Edge for local action.

**License & contact**

* Add your preferred license (MIT recommended for demos).
* For questions or help adding Azure deployment scripts, include a short note in the repo and I’ll provide the next steps.

Use this as README.md in your repo root. If you want, I can also create a condensed “Quick Architecture” PNG and a one-file Azure deployment checklist to go with it.
