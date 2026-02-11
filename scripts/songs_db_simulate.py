import random
import psycopg2
import time
from typing import Optional
from faker import Faker
fake = Faker()

class SongsCRUD:
    def __init__(self, db_path: str = 'songs.db', db_type: str = 'sqlite', pg_conn: Optional[str] = None):
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
        """Create songs table if it doesn't exist"""
        # Postgres: use SERIAL for autoincrement and DATE type for release_date
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS songs (
                song_id SERIAL PRIMARY KEY,
                song_name TEXT NOT NULL,
                song_duration INTEGER NOT NULL,
                country TEXT
            )
        ''')
        self.conn.commit()
        print("Songs table created/verified")
    
    def create_song(self, song_id=None,
                        name=None, 
                        duration=None, 
                        country=None):
        """Create a new song (INSERT)"""
        # Generate random data if not provided
        song_countries = ['US', 'UK', 'FI', 'JP', 'CA', 'AU']
        if name is None:
             name = fake.word() 
        if duration is None:
            duration = random.randint(120, 360)  # Duration in seconds
        if country is None:
            country = random.choice(song_countries)
        
        try:
            # Postgres: prefer letting SERIAL assign song_id unless provided
            self.cursor.execute(
                'INSERT INTO songs (song_name, song_duration, country) VALUES (%s, %s, %s) RETURNING song_id',
                (name, duration, country)
            )
            new_id = self.cursor.fetchone()[0]
            self.conn.commit()
            print(f"Created song {new_id}: {name}, {duration}s, {country}")
            return new_id
        except Exception as e:
            print(f"Failed to create song: {e}")
            return None
    
    def read_song(self, song_id):
        """Read a specific song (SELECT)"""
        self.cursor.execute('SELECT * FROM songs WHERE song_id = %s', (song_id,))
        song = self.cursor.fetchone()
        if song:
            print(f"Read song {song_id}: {song}")
            return song
        else:
            print(f"Song {song_id} not found")
            return None
    
    def read_all_songs(self):
        """Read all songs (SELECT)"""
        self.cursor.execute('SELECT song_id FROM songs')
        songs = self.cursor.fetchall()
        return songs
    
    def update_song(self, song_id, name=None, duration=None, country=None):
        """Update an existing song (UPDATE)"""
        # There is a very less chance of updating a song, since the song title or duration or country hardly changes
        # First check if song exists
        if not self.read_song(song_id):
            print(f"Song {song_id} does not exist")
            return False
        
        updates = []
        
        if name:
            updates.append(f'song_name = {name}')
        if duration:
            updates.append(f'song_duration = {duration}')
        if country:
            updates.append(f'country = {country}')
        
        if not updates:
            print("No fields to update")
            return False
  
        query = f"UPDATE songs SET {', '.join(updates)} WHERE song_id = {song_id}"
        self.cursor.execute(query)
        self.conn.commit()
        return True
    
    def delete_song(self, song_id):
        """Delete a song (DELETE)"""
        self.cursor.execute('DELETE FROM songs WHERE song_id = %s', (song_id,))

        if self.cursor.rowcount > 0:
            self.conn.commit()
            print(f"Deleted song {song_id}")
            return True
        else:
            print(f"Song {song_id} not found")
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
            operation = operations[1]
        else:            
            operation = operations[3]

        print(f"\n--- Random Operation: {operation.upper()} ---")
        
        if operation == 'create':
            self.create_song()
                
        elif operation == 'update':
            songs = self.read_all_songs()
            if songs:
                random_song = random.choice(songs)
                song_id = random_song[0]
                
                song_countries = ['US', 'UK', 'FI', 'JP', 'CA', 'AU']
                # Randomly update one or more fields
                new_country = random.choice(song_countries)
                
                self.update_song(song_id, country=new_country)
            else:
                print("No songs to update")
                
        elif operation == 'delete':
            songs = self.read_all_songs()
            if songs:
                random_song = random.choice(songs)
                self.delete_song(random_song[0])
            else:
                print("No songs to delete")
    
    def close(self):
        """Close database connection"""
        self.conn.close()
        print("\n Database connection closed")


# Example usage
if __name__ == "__main__":
    # Initialize CRUD manager
    crud = SongsCRUD('postgresql://admin:admin@application-db:5432/application_db')

    print("\n" + "="*50)
    # Perform random CRUD operations
    try:
        while True:
            crud.random_crud_operation()
            time.sleep(random.uniform(10, 30))  # Sleep for a bit to simulate time between operations
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user.")
    finally:
        # Close connection
        crud.close()
