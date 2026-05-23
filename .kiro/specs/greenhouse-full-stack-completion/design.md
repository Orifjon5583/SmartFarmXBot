# Design Document: Greenhouse Full-Stack Completion

## Overview

SmartFarmXBot is an IoT greenhouse control system running on Raspberry Pi 4 with a Flask backend and React + Vite frontend. The current system has a working skeleton with mock/real sensor reading, GPIO device control, and a dashboard UI, but lacks production-critical infrastructure: real-time MQTT communication from sensors, persistent PostgreSQL storage, JWT authentication, server-side automation, and camera streaming.

This design introduces MQTT (Mosquitto) as the transport layer between Raspberry Pi sensors and the Flask backend, PostgreSQL for persistent storage (replacing JSON file and in-memory stores), flask-socketio for real-time frontend updates, JWT authentication via PyJWT, a unified backend automation engine, and Pi Camera MJPEG streaming. The architecture ensures a single source of truth for device control decisions on the backend, eliminating the current duplicate frontend automation logic.

## Architecture

```mermaid
graph TD
    subgraph "Raspberry Pi"
        SENSORS[DHT22 / MCP3008 / Photoresistor]
        GPIO[GPIO Relays]
        CAMERA[Pi Camera]
        MQTT_PUB[MQTT Publisher Script]
    end

    subgraph "Mosquitto Broker"
        BROKER[MQTT Broker :1883]
    end

    subgraph "Flask Backend"
        MQTT_SUB[flask-mqtt Subscriber]
        AUTO[Automation Engine]
        AUTH[Auth Service - JWT]
        SETTINGS[Settings Service]
        CAM_SVC[Camera Service]
        REST[REST API]
        WS[flask-socketio WebSocket]
    end

    subgraph "PostgreSQL"
        DB[(sensor_history / users / settings / device_logs)]
    end

    subgraph "React Frontend"
        DASHBOARD[Dashboard + Charts]
        CONTROLS[Device Controls]
        LOGIN[Login Page]
        SETTINGS_UI[Settings Page]
    end

    SENSORS --> MQTT_PUB
    MQTT_PUB -->|greenhouse/sensors| BROKER
    BROKER -->|greenhouse/sensors| MQTT_SUB
    MQTT_SUB --> AUTO
    MQTT_SUB --> DB
    AUTO --> GPIO
    REST -->|greenhouse/devices| BROKER
    BROKER -->|greenhouse/devices| GPIO
    AUTH --> DB
    SETTINGS --> DB
    WS -->|sensor_update / device_update| DASHBOARD
    REST --> DASHBOARD
    CONTROLS -->|POST /api/device| REST
    LOGIN -->|POST /api/auth/login| AUTH
    SETTINGS_UI -->|GET/POST /api/settings| SETTINGS
    CAMERA --> CAM_SVC
    CAM_SVC -->|MJPEG stream| DASHBOARD
```
