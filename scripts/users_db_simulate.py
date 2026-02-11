import random
import psycopg2
from datetime import datetime, timedelta
import time
from typing import Optional

class UsersCRUD:
    def __init__(self, pg_conn: Optional[str] = None):
        """Initialize database connection.

        db_type: 'postgres'
        For Postgres supply a libpq connection string in `pg_conn`, e.g.:
            "postgresql://user:pass@host:5432/dbname"
        """

        self.conn = psycopg2.connect(pg_conn)
        self.cursor = self.conn.cursor()
        print('PostgreSQL database version:')
        self.cursor.execute('SELECT version()')
        version = self.cursor.fetchone()[0]
        print(version)
        self.create_table()
        
    def create_table(self):
        """Create users table if it doesn't exist"""
        # Postgres: use SERIAL for autoincrement and DATE type for join_date
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                country TEXT NOT NULL,
                signup_source TEXT NOT NULL,
                join_date DATE NOT NULL
            )
        ''')
        self.conn.commit()
        print("Users table created/verified")
    
    def create_user(self, user_id=None,
                        country=None,
                        signup_source=None, 
                        join_date=None):
        """Create a new user (INSERT)"""
        channels = ['Google', 'Facebook', 'Organic']
        countries = ['US', 'UK', 'FI', 'JP']
            
        country = country or random.choice(countries)
        signup_source = signup_source or random.choice(channels)
        
        if join_date is None:
            days_ago = random.randint(0, 365)
            join_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        
        try:
            # Postgres: prefer letting SERIAL assign user_id unless provided
            self.cursor.execute(
                'INSERT INTO users (country, signup_source, join_date) VALUES (%s, %s, %s) RETURNING user_id',
                (country, signup_source, join_date)
            )
            new_id = self.cursor.fetchone()[0]
            self.conn.commit()
            print(f"Created user {new_id}: {country}, {signup_source}, {join_date}")
            return new_id
        except Exception as e:
            print(f"Failed to create user: {e}")
            return None
    
    def read_user(self, user_id):
        """Read a user by ID (SELECT)"""
        self.cursor.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
        user = self.cursor.fetchone()
        # returns a tuple like (user_id, country, signup_source, join_date) or None if not found
        if user:
            print(f"User {user_id}: {user}")
            return user
        else:
            print(f"User {user_id} not found")
            return None
    
    def read_all_users(self):
        """Read all users (SELECT)"""
        self.cursor.execute('SELECT user_id FROM users')
        users = self.cursor.fetchall()
        return users

    def update_user(self, user_id, country=None, signup_source=None, join_date=None):
        """Update an existing user (UPDATE)"""
        # First check if user exists
        if self.read_user(user_id) is None:
            print(f"User {user_id} does not exist")
            return False
        
        updates = []
        
        if country:
            updates.append(f'country = \'{country}\'')
        if signup_source:
            updates.append(f'signup_source = \'{signup_source}\'')
        if join_date:
            updates.append(f'join_date = \'{join_date}\'')
        
        if not updates:
            print("No fields to update")
            return False
        
        query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = {user_id}"
        self.cursor.execute(query)
        self.conn.commit()
        return True
    
    def delete_user(self, user_id):
        """Delete a user (DELETE)"""

        self.cursor.execute('DELETE FROM users WHERE user_id = %s', (user_id,))

        if self.cursor.rowcount > 0:
            self.conn.commit()
            print(f"Deleted user {user_id}")
            return True
        else:
            print(f"User {user_id} not found")
            return False
    
    def random_crud_operation(self):
        """Perform a random CRUD operation"""
        operations = ['create', 'read', 'update', 'delete']
        rand = random.random()
        if rand < 0.50:
            operation = operations[0]
        elif rand < 0.90:
            operation = operations[1]
        elif rand < 0.95:            
            operation = operations[2]
        else:            
            operation = operations[3]

        print(f"\n--- Random Operation: {operation.upper()} ---")
        
        if operation == 'create':
            self.create_user()
            
        elif operation == 'update':
            users = self.read_all_users()
            if users:
                random_user = random.choice(users)
                user_id = random_user[0]
                
                # Randomly update one or more fields
                new_country = random.choice(['US', 'UK', 'FI', 'JP']) if random.random() > 0.5 else None
                
                self.update_user(user_id, country=new_country)
            else:
                print("No users to update")
                
        elif operation == 'delete':
            users = self.read_all_users()
            if users:
                random_user = random.choice(users)
                self.delete_user(random_user[0])
            else:
                print("No users to delete")
    
    def close(self):
        """Close database connection"""
        self.conn.close()
        print("\n Database connection closed")


# Example usage
if __name__ == "__main__":
    # Initialize CRUD manager
    crud = UsersCRUD('postgresql://admin:admin@application-db:5432/application_db')
    
    print("\n" + "="*50)
    # Perform random CRUD operations
    try:
        while True:
            crud.random_crud_operation()
            time.sleep(random.uniform(5, 10))  # Sleep for a bit to simulate time between operations
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user.")
    finally:
        # Close connection
        crud.close()