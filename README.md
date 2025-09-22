# postgres_for_leetcode

## Quick start

```bash
git clone <repo_url>
cd <repo_name>
vim .env

# In the .env file set:
# POSTGRES_USER=your_user
# POSTGRES_PASSWORD=your_password
# POSTGRES_DB=your_db
# POSTGRES_HOST=postgres

docker-compose up -d

+---------------+----------------------------------------------+--------------------------------------+
| Service       | URL / Host                                   | Comment                              |
+---------------+----------------------------------------------+--------------------------------------+
| Data Generator| http://localhost:8005/docs                   | Swagger UI for test data             |
| Grafana       | http://localhost:3000/dashboards             | Dashboards, login/password from .env |
| Prometheus    | http://localhost:9090/targets                | Monitoring targets                   |
| Postgres      | localhost:5432                               | Connect with client (pgAdmin, psql)  |
| pgAdmin       | http://localhost:5050                        | Web interface for Postgres           |
+---------------+----------------------------------------------+--------------------------------------+

