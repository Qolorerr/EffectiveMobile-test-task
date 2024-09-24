# Simple FastAPI project for EffectiveMobile
This project provides an API for managing orders and products on trading platform

## Project Overview
The Item API allows creating, updating, and deleting items

## Installation
1. Install Docker on your system
2. Clone this repository: `git clone https://github.com/Qolorerr/EffectiveMobile-test-task.git order_api`
3. Build the Docker image: `docker build -t order-api .`
4. Run the Docker container: `docker run -p 8000:8000 order-api`
The API will now be available on port 8000 of your Docker host.

## Configuration
The database file is defined at `src/config/config.yaml`.

## Usage
You can now make requests to the API running inside the Docker container on port 8000.

## API Documentation
Documentation can be seen on `<your-server-ip>:8000/docs` or on `<your-server-ip>:8000/redoc`
