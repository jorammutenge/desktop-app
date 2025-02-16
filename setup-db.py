import sqlite3
import polars as pl
import os

# Delete the existing database file to start fresh
db_path = "actresses.db"
if os.path.exists(db_path):
    os.remove(db_path)

# Read and process the data
df = (pl.read_parquet('data/movie_shows.parquet')
    .select('Person', 'Title', 'Type')
    .with_columns(pl.col('Person').str.split(' | '))
    .explode('Person')
    .with_columns(Image=pl.col('Person').str.replace_all(' ', '_').add('.jpg'))
)

# Recreate the database and connect
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create the table from scratch
cursor.execute("""
CREATE TABLE actresses (
    Person TEXT,
    Title TEXT,
    Type TEXT CHECK(Type IN ('Movie', 'Series')),
    Image TEXT
)
""")

# Insert DataFrame data into the database
cursor.executemany("INSERT INTO actresses VALUES (?, ?, ?, ?)", df.iter_rows())

# Commit and close the connection
conn.commit()
conn.close()

print("Database has been reset and updated with new data.")
