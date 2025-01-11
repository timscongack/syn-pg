# syn-pg

**syn-pg** is a Dockerized Python application designed to generate synthetic data at regular intervals for a PostgreSQL database. It leverages OpenAI's GPT to create SQL queries, executing them via transactions to ensure consistency. This tool is ideal for testing, building, and validating data pipelines or creating synthetic data in the data layer of an application.

## Features
- Scheduled synthetic data generation for PostgreSQL.
- Uses GPT to craft SQL statements dynamically.
- Transactional query execution for data integrity.
- Fully containerized for portability and ease of deployment.
- Suitable for testing, pipeline creation, and development environments.

## Requirements
- Docker
- OpenAI API key
- Locally running PostgreSQL database. Note: if you're looking for a good sample database, I recommending using the [northwind](https://github.com/pthom/northwind_psql) database.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/timscongack/syn-pg.git
   cd syn-pg
   ```

2. Build Docker Image
   `docker build -t syn-pg .`

3. Configure Environment Variables in .env

```
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_database
OPENAI_API_KEY=your_openai_api_key
SCHEDULE_CRON=* * * * *  # Set your desired cron schedule
```

4. Update docker-compose.yml network to match your postgres network (line 22).

6. Run docker container `docker compose up`