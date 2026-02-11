# Architecture & Data Model
This file contains information on how the current stack will look in AWS tech stack for production analytics platform, and also highlighting data modeling strategy for tables in warehouse.
## Production Architecture AWS
### Ingestion and Loading
- Product Data: Product db will be maintained by the singa application which will use CRUD operations to make changes to the DB. **AWS DMS** can be used for CDC to replicate data from DB to Redshift (we can use full load to pull in the entire db at first and then the CDC can keep polling the db for replicating the transactions that are dont to the DB).
- Stripe/Marketing: **Airflow** running on EC2 (self-hosted) to trigger Python extractors that fetch the data from API and export them into S3 followed by `COPY` command to load them in Redshift.
### Storage
- AWS S3: For ingesting CSV from Stripe and marketing data using heirarchy format `source/year/month/day`
### Database and Warehouse
- AWS Redshift: For warehouse to store our Fact and Dim tables used for analysis
- AWS RDS: OLTP database used for storing transactions happening to DB, such as addition of user, modifying information etc.,
### Transformation
- Dbt: Runs on top of Redshift to transform raw staging tables into Fact and Dimension tables, dbt allows writing modular SQL code used for transformations, it also allows incremental loading, data quality tests, and version controlling SQL code.
### Orchestration
- Airflow: Manages the orchestration, dependecies, and also triggering of the tasks based on cron schedule or some rule based scheduling such as waiting for extraction to end and then triggering.
### Observability and Governance
- Cloudwatch + alerts for pipeline level monitoring and alerting
- dbt tests to ensure data quality checks at model level
- dbt docs for data lineage and metadata

## Data Model
I propose STAR schema which is optimized for analytical queries since it reduces data joins as compared to 3NF tables.
### Dimensions
- `dim_users`:
  - Granularity: One row per customer
  - Columns: `user_id`, `country`, `signup_source`, `joining_data`
- `dim_subscriptions`:
  - Granularity: One row per subscription
  - Columns: `subscription_id`, `subscription_price`, `subscription_type`
- `dim_songs`:
  - Granularity: One row per song
  - Columns: `song_id`, `song_name`, `song_duration`, `song_country`
### Facts
- `fact_payments`:
  - Granularity: One row per successful transaction
  - Columns: `payment_id`, `user_id`, `amount`, `currency`, `payment_date`, `method`.
- `fact_marketing_daily`:
  - Granularity: One row per channel per day
  - Columns: `date`, `channel`, `spend`, `clicks`, `impressions`.

### Trade offs
- We will be using the data to load in Redshift and not external tables, since our tables in redshift will populate the BI dashboards, and we need to fast query times, secondly, external tables are slower in terms of frequent joins, so we will be making performance vs cost tradeoff here.
- We will use self-hosted Airflow vs managed service, even though it will be a hassle to maintain and more engineering work hours (security patches, and updates) on the plus side it will be cheaper and more control over environment and configurations.
- We will use STAR schema even though it requires fact tables being joined by dim it will ensure modularity and ease of upates, e.g. if a dim dimension gets the column change, we can just change it one place and everywhere where that table is referenced will get the update.
- Managed AWS DMS vs snapshots, even though DMS is more complex to figure out initially than a simple snapshot and append, it will provide us with near-real time updates rather than waiting for python script to work.

### Assumptions
- This MVP assumes that the data enters in valid quality, obivously in production that would not be the case and there will be checks in place to enfore schema contracts.
- For this MVP I have assumed the payment to be in USD but in real life payment data comes in a mix of currencies (Singa is global) and there will be a need to convert the currency into one standard USD to calcuate standardized revenue and costs.
- Users are coming from 'US', 'UK', 'FI', or 'JP' but in real life it can be the countries where singa operates.
- Similarly, there are only two inorganic channels: Google, and Facebook, however there are other platforms as well such as Instagram.
- A user makes only one transaction in a month.