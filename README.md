# Market Data Service

## Overview
The **Market Data Service** is a microservice designed to:

- Fetch real-time market data from Finnhub.
- Publish price updates to a Kafka topic.
- Compute 5-point moving averages via a Kafka consumer.
- Persist raw and processed data in PostgreSQL.
- Expose RESTful APIs using FastAPI.

## Table of Contents
1. Architecture
2. Folder Structure
3. Setup Instructions
4. Running the Service
5. API Documentation
6. Testing
7. Troubleshooting
8. Future Enhancements

## Architecture


### Components
- **FastAPI App**: Serves RESTful endpoints.
- **Finnhub Provider**: Fetches stock quotes.
- **Kafka Producer**: Publishes price events to the `price-events` topic.
- **Kafka Consumer**: Calculates 5-point moving averages and stores them.
- **PostgreSQL**: Stores raw responses, polling job configs, and averages.
- **Scheduler**: Manages background polling jobs.
- **Docker Compose**: Orchestrates Postgres, Zookeeper, Kafka, and Adminer.

### Sequence Diagram
```sequence
Client->>FastAPI: GET /prices/latest
FastAPI->>Finnhub: Fetch quote
Finnhub-->>FastAPI: Return price
FastAPI->>PostgreSQL: Store raw data
FastAPI->>Kafka: Publish price-event
Kafka->>Consumer: Deliver price-event
Consumer->>PostgreSQL: Store moving average
FastAPI-->>Client: Respond JSON
```

## Folder Structure
```
market-data-service/
├── app/
│   ├── api/             # API routes (prices.py, poll_job.py)
│   ├── core/            # Config and DI (config.py, dependencies.py)
│   ├── models/          # SQLAlchemy ORM models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic (provider, producer, consumer, scheduler)
│   └── main.py          # FastAPI application entrypoint
├── tests/               # Pytest unit and integration tests
├── docker-compose.yml   # Infrastructure (Postgres, Kafka, Zookeeper, Adminer)
├── requirements.txt     # Python dependencies
└── .env                 # Environment variables
```



## Setup Instructions

1. **Clone the repository**

   ```
   git clone <repo-url>
   cd market-data-service
   ```

2. **Create and activate a virtual environment**

   ```
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Python dependencies**

   ```
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   * Create a file named `.env` in the project root.
   * Add the following:

     ```
     FINNHUB_API_KEY=API_KEY
     DATABASE_URL=postgresql://postgres:postgres@db:5432/marketdb
     KAFKA_BOOTSTRAP_SERVERS=localhost:9092
     ```

## Running the Service

### 1. Start the infrastructure

```
docker-compose up -d
```

* **PostgreSQL**: `localhost:5432`
* **Zookeeper**: `localhost:2181`
* **Kafka**: `localhost:9092`
* **Adminer**: `localhost:8080`

### 2. Launch the FastAPI app

```
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
uvicorn app.main:app --reload --port 8001
```

The API is available at `http://localhost:8001`.

## API Documentation

### GET `/prices/latest?symbol={symbol}`

Fetch the latest price for a given stock symbol.

* **Query Parameters**:

  * `symbol` (string, required): e.g., `AAPL`, `MSFT`.
* **Response** (`200 OK`):

  ```
  {
    "symbol": "AAPL",
    "price": 172.5,
    "timestamp": "2025-06-12T14:23:45Z",
    "provider": "finnhub"
  }
  ```
* **Errors**:

  * `502 Bad Gateway` if the external API call fails.

### POST `/prices/poll`

Start a polling job for one or more symbols.

* **Request Body**:

  ```
  {
    "symbols": ["AAPL", "MSFT"],
    "interval": 60,
    "provider": "finnhub"
  }
  ```
* **Response** (`202 Accepted`):

  ```
  {
    "job_id": "poll_123",
    "status": "accepted",
    "config": {
      "symbols": ["AAPL", "MSFT"],
      "interval": 60
    }
  }
  ```

## Testing

Run all tests with:
```
pytest tests/ -W ignore
```

Key test files:

* `test_api.py`: tests for `/prices/latest`
* `test_poll_api.py`: tests for polling endpoint
* `test_consumer.py`: tests for moving-average consumer

## Troubleshooting

* **Port conflicts**:

  ```
  lsof -i :8001
  kill -9 <PID>
  ```
* **Module import errors**: Ensure each `app/` subdirectory contains an `__init__.py` file.
* **Kafka topic missing**: Confirm `price-events` exists or enable auto-creation in Kafka.

## Future Enhancements

* Integrate Swagger/OpenAPI UI.
* Add Redis caching for hot prices.
* Implement Prometheus/Grafana monitoring dashboards.
* Deploy to AWS ECS/Fargate or Heroku.



