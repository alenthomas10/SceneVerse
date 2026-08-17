
import sqlite3
import os

def inspect_db(db_path):
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        print(f"Found {len(tables)} tables in {db_path}:\n")

        for table in tables:
            table_name = table[0]
            print(f"Table: {table_name}")
            print("-" * (len(table_name) + 7))

            # Get column info
            cursor.execute(f"PRAGMA table_info(\"{table_name}\")")
            columns = cursor.fetchall()
            
            # Print headers
            print(f"{'ID':<5} {'Name':<20} {'Type':<15} {'NotNull':<10} {'PK':<5}")
            print("-" * 60)

            for col in columns:
                # col structure: (id, name, type, notnull, dflt_value, pk)
                cid, name, dtype, notnull, dflt_value, pk = col
                print(f"{cid:<5} {name:<20} {dtype:<15} {notnull:<10} {pk:<5}")
            
            print("\n")

        conn.close()

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")

if __name__ == "__main__":
    db_file = "e:\\SceneVerse\\db.sqlite3"
    inspect_db(db_file)
