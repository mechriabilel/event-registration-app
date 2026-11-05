# Event Registration Web Application & REST API (Checkpoint 3)

Software Engineering Project - Checkpoint 3

## Overview
This project evolves the event registration tool into a modern web-based application and a resource-oriented REST API built with Python, FastAPI, SQLAlchemy, and SQLite, fully containerized using Docker and Docker Compose.

## Features
- **Web UI & Forms**: Interactive HTML dashboard allowing users to manage events and registrations directly via web forms without command-line input.
- **REST API**: Resource-oriented endpoints (`/api/events`, `/api/registrations`) supporting standard HTTP methods (`GET`, `POST`, `DELETE`), JSON payloads, and correct HTTP status codes (`201`, `400`, `404`, `204`).
- **OpenAPI Documentation**: Automatically generated interactive Swagger documentation covering all endpoints, parameters, examples, and errors.
- **Persistent Storage**: SQLite database stored in a persistent Docker volume mapped to the `data/` directory to ensure data durability across container restarts.
- **Automated Testing**: Unit tests (`pytest`) verifying key application rules, such as event capacity enforcement and overbooking prevention.

---

## Quick Start Guide (Fresh Checkout Instructions)

To run this application from a fresh checkout, make sure you have **Docker** and **Docker Compose** installed on your machine.

### 1. Start the Application
Run the following command to build the Docker image and start the container in the background with persistent volume enabled:
```powershell
docker compose up --build -d