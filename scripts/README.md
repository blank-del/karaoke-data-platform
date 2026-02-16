# Simulation Scripts

This directory contains Python scripts used to simulate CRUD (Create, Read, Update, Delete) activity against a PostgreSQL database for the Singa assignment project. The simulators generate random data and operate continuously, mimicking real workload patterns for users, songs, and subscriptions tables. A Dockerfile is also included to build a container image for running the scripts in an isolated environment.

## Contents

- **`users_db_simulate.py`** – provides `UsersCRUD` class that manages a `users` table. It creates the table (if necessary) and continuously performs random create, read, update, or delete operations.

- **`songs_db_simulate.py`** – encapsulates the logic for a `songs` table. The `SongsCRUD` class supports random CRUD operations and prints actions to stdout, with occasional updates and deletes.

- **`subscriptions_db_simulate.py`** – handles a mostly static `subscriptions` table. The script inserts default subscription plans if the table is empty and then periodically reads records.

- **`requirements.txt`** – Python dependencies required by the simulation scripts.

- **`dockerfile`** – builds a lightweight Python 3.12 container with the simulation scripts copied in

## Customization

- Edit the scripts to change CRUD operation probabilities, sleep intervals, or generated values.

## Notes

- The `users` and `songs` scripts include logic to randomly update or delete rows; adjust thresholds as needed.
- The `subscriptions` script is designed for one-time population and periodic reads since subscription plans seldom change.