## docker commands 

# Start containers (detached)
docker compose -f docker/compose.db.yml up -d
docker compose -f docker/compose.airflow.yml up -d

# See running containers
docker ps

# Follow Postgres logs
docker logs -f yfinance-postgres

# Stop containers	
docker compose -f docker/compose.db.yml stop

# Restart containers	
docker compose -f docker/compose.db.yml restart

# Remove containers	
docker compose -f docker/compose.db.yml down

# Remove containers + volume	
docker compose -f docker/compose.db.yml down -v

# List volumes	
docker volume ls

# Remove old volumes	
docker volume rm <volume_name>

# List images	
docker images