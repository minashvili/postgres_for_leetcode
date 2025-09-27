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

| Service           | URL / Host                                                           | Comment                              |
| ----------------- | -------------------------------------------------------------------- | ------------------------------------ |
| Data Generator    | [http://localhost:8005/docs](http://localhost:8005/docs)             | Swagger UI for test data             |
| Grafana           | [http://localhost:3000/dashboards](http://localhost:3000/dashboards) | Dashboards, login/password from .env |
| Prometheus        | [http://localhost:9090/targets](http://localhost:9090/targets)       | Monitoring targets                   |
| Postgres          | localhost:5432                                                       | Connect with client (pgAdmin, psql)  |
| PG Exporter       | [http://localhost:9153/metrics](http://localhost:9153/metrics)       | Postgres performance metrics         |
| Postgres Exporter | [http://localhost:9187/metrics](http://localhost:9187/metrics)       | Postgres Prometheus metrics          |
| Node Exporter     | [http://localhost:9100/metrics](http://localhost:9100/metrics)       | Node exporter metrics                |
| Loki Ready        | [http://localhost:3100/ready](http://localhost:3100/ready)           | Loki readiness endpoint              |

go to the postgres container and initialize pgbench

```bash
PGPASSWORD=$POSTGRES_PASSWORD pgbench -i -s 10 -h postgres -U $POSTGRES_USER -d $POSTGRES_DB

-s 10 means scale factor 10, you can change it to other values like 1, 5, 20, etc. 
that will create more or less data in the database.

you should see output like this:

root@1088cad14dab:/# PGPASSWORD=$POSTGRES_PASSWORD pgbench -i -s 10 -h postgres -U $POSTGRES_USER -d $POSTGRES_DB
dropping old tables...
NOTICE:  table "pgbench_accounts" does not exist, skipping
NOTICE:  table "pgbench_branches" does not exist, skipping
NOTICE:  table "pgbench_history" does not exist, skipping
NOTICE:  table "pgbench_tellers" does not exist, skipping
creating tables...
generating data (client-side)...
vacuuming...                                                                                
creating primary keys...
done in 0.83 s (drop tables 0.00 s, create tables 0.01 s, client-side generate 0.58 s, vacuum 0.06 s, primary keys 0.18 s).

next run a benchmark test:

```bash like example:
# 100 TPS
PGPASSWORD=$POSTGRES_PASSWORD pgbench -h postgres -U $POSTGRES_USER -d $POSTGRES_DB -c 10 -j 2 -t 100

# 1000 TPS
PGPASSWORD=$POSTGRES_PASSWORD pgbench -h postgres -U $POSTGRES_USER -d $POSTGRES_DB -c 10 -j 2 -t 1000

# 5 minutes stress test (300 seconds)
PGPASSWORD=$POSTGRES_PASSWORD pgbench -h postgres -U $POSTGRES_USER -d $POSTGRES_DB -c 10 -j 2 -T 300

you should see output like this:

root@1088cad14dab:/# PGPASSWORD=$POSTGRES_PASSWORD pgbench -h postgres -U $POSTGRES_USER -d $POSTGRES_DB -c 10 -j 2 -T 300
pgbench (17.6 (Debian 17.6-1.pgdg13+1))
starting vacuum...end.
transaction type: <builtin: TPC-B (sort of)>
scaling factor: 10
query mode: simple
number of clients: 10
number of threads: 2
maximum number of tries: 1
duration: 300 s
number of transactions actually processed: 1540676
number of failed transactions: 0 (0.000%)
latency average = 1.947 ms
initial connection time = 26.921 ms
tps = 5135.845479 (without initial connection time)


