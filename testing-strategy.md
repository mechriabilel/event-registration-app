Testing Strategy & Delivery Path

Overview

This repository contains the implementation for Project 3: Event Registration CLI as requested in the course.

Local Execution & Automated Testing

Install requirements:
pip install -r requirements.txt

Execute Automated Unit Tests (Capacity Limit constraint check):
pytest test_events.py

Docker Execution

Build Container Image:
docker build -t event-app .

Run Container CLI:
docker run --rm event-app event add --name "DevOps Class" --capacity 10
docker run --rm event-app event list

Run via Docker Compose:
docker compose up