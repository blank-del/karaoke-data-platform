import random
import psycopg2
from datetime import datetime, timedelta
import time
from typing import Optional

class SubscriptionsCRUD:
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
        """Create subscriptions table if it doesn't exist"""
        # Postgres: use SERIAL for autoincrement and DATE type for subscription_date
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                subscription_id SERIAL PRIMARY KEY,
                subscription_type TEXT NOT NULL,
                subscription_price DECIMAL(10, 2)
            )
        ''')
        self.conn.commit()
        print("Subscriptions table created/verified")
    
    def create_subscription(self, subscription_id=None,
                               type=None,
                               price=None):
        """Create a new subscription (INSERT)"""
        self.cursor.execute('SELECT count(*) FROM subscriptions')
        count = self.cursor.fetchone()[0]
        if count > 0:
            print("Subscriptions table already has data")
            return None
        else:
            # This table will mostlbe be statis since subscriptions rarely change, mostly the prices are updates
            plan_types = ['free', 'basic', 'premium', 'pro']
            plan_prices = {'free': 0.00, 'basic': 4.99, 'premium': 9.99}
            new_id = []
            try:
                # Postgres: prefer letting SERIAL assign subscription_id unless provided
                for i, plan_type in enumerate(plan_types):
                    monthly_price = plan_prices.get(plan_type, 0.00)

                    self.cursor.execute(
                        'INSERT INTO subscriptions (subscription_type, subscription_price) VALUES (%s, %s) RETURNING subscription_id',
                        (plan_type, monthly_price)
                    )
                    new_id.append(self.cursor.fetchone()[0])
                    self.conn.commit()
                    print(f"Created subscription {new_id}: plan={plan_type}, price=${monthly_price}")
                return new_id
            except Exception as e:
                print(f"Failed to create subscription: {e}")
                self.conn.rollback()
                return None
    
    def read_subscription(self, subscription_id):
        """Read a subscription by ID (SELECT)"""
        self.cursor.execute('SELECT * FROM subscriptions WHERE subscription_id = %s', (subscription_id,))
        subscription = self.cursor.fetchone()
        # returns a tuple like (subscription_id, plan_type, monthly_price) or None if not found
        if subscription:
            print(f"Subscription {subscription_id}: {subscription}")
            return subscription
        else:
            print(f"Subscription {subscription_id} not found")
            return None
    
    def read_all_subscriptions(self):
        """Read all subscriptions (SELECT)"""
        self.cursor.execute('SELECT subscription_id FROM subscriptions')
        subscriptions = self.cursor.fetchall()
        return subscriptions

    def update_subscription(self, subscription_id, plan_type=None, monthly_price=None):
        """Update an existing subscription (UPDATE)"""
        # First check if subscription exists
        if self.read_subscription(subscription_id) is None:
            print(f"Subscription {subscription_id} does not exist")
            return False
        
        updates = []
        
        if plan_type:
            updates.append(f'plan_type = {plan_type}')
        if monthly_price is not None:
            updates.append(f'monthly_price = {monthly_price}')
        
        if not updates:
            print("No fields to update")
            return False
        
        query = f"UPDATE subscriptions SET {', '.join(updates)} WHERE subscription_id = %s"
        self.cursor.execute(query)
        self.conn.commit()
        print(f"Updated subscription {subscription_id}")
        return True
    
    def delete_subscription(self, subscription_id):
        """Delete a subscription (DELETE)"""

        self.cursor.execute('DELETE FROM subscriptions WHERE subscription_id = %s', (subscription_id,))

        if self.cursor.rowcount > 0:
            self.conn.commit()
            print(f"Deleted subscription {subscription_id}")
            return True
        else:
            print(f"Subscription {subscription_id} not found")
            return False
    
    def random_crud_operation(self):
        """Perform a random CRUD operation"""
        # For subscriptions, we will mostly read since they are mostly static

        subscriptions = self.read_all_subscriptions()
        if subscriptions:
            random_sub = random.choice(subscriptions)
            self.read_subscription(random_sub[0])
        else:
            print("No subscriptions available to read")
    
    def close(self):
        """Close database connection"""
        self.conn.close()
        print("\n Database connection closed")


# Example usage
if __name__ == "__main__":
    # Initialize CRUD manager
    crud = SubscriptionsCRUD('postgresql://admin:admin@application-db:5432/application_db')
    # Create some subscriptions
    crud.create_subscription()
    
    print("\n" + "="*50)
    # Perform random CRUD operations
    try:
        while True:
            # In the subsciption table the only random operation will be reading
            # since subscriptions are mostly static create once and then read, rarely update or delete
            crud.random_crud_operation()
            time.sleep(random.uniform(30, 60))  # Sleep for a bit to simulate time between operations
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user.")
    finally:
        # Close connection
        crud.close()
