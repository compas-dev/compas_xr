import os
import sys
import json
import time
import random
from rethinkdb import r


def insert_data(config_fp):
    """
    Connects to RethinkDB and performs insert and update operations on the 'Users' table
    to trigger streaming events.
    """
    if not os.path.exists(config_fp):
        print(f"Config file not found: {config_fp}")
        return

    with open(config_fp, "r") as f:
        config = json.load(f)

    host = config.get("host", "localhost")
    port = config.get("port", 28015)
    db_name = config.get("database", "test")
    table_name = "Users"

    try:
        print(f"Connecting to RethinkDB at {host}:{port}/{db_name}...")
        conn = r.connect(host=host, port=port, db=db_name)

        # Ensure table exists
        if table_name not in r.table_list().run(conn):
            print(f"Creating table '{table_name}'...")
            r.table_create(table_name).run(conn)

        # Get existing IDs to manage
        cursor = r.table(table_name).pluck("id").run(conn)
        active_ids = [doc["id"] for doc in cursor]
        print(f"Found {len(active_ids)} existing users.")

        print("Starting random operations (Ctrl+C to stop)...")
        while True:
            action = random.choice(["insert", "update", "delete", "insert"])  # slightly more inserts to grow

            if not active_ids:
                action = "insert"

            if action == "insert":
                user_id = f"user_{random.randint(10000, 99999)}"
                user_data = {
                    "id": user_id,
                    "name": f"User {user_id}",
                    "email": f"{user_id}@example.com",
                    "timestamp": time.time(),
                    "status": "online",
                    "score": random.randint(0, 100),
                }
                r.table(table_name).insert(user_data).run(conn)
                active_ids.append(user_id)
                print(f"[INSERT] {user_id}")

            elif action == "update":
                user_id = random.choice(active_ids)
                new_status = random.choice(["online", "offline", "busy", "away"])
                new_score = random.randint(0, 100)
                r.table(table_name).get(user_id).update({"status": new_status, "score": new_score, "last_updated": time.time()}).run(conn)
                print(f"[UPDATE] {user_id} -> status={new_status}, score={new_score}")

            elif action == "delete":
                user_id = random.choice(active_ids)
                r.table(table_name).get(user_id).delete().run(conn)
                active_ids.remove(user_id)
                print(f"[DELETE] {user_id}")

            wait_time = random.uniform(1.0, 3.0)
            time.sleep(wait_time)

    except KeyboardInterrupt:
        print("\nStopped.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if "conn" in locals() and conn.is_open():
            conn.close()


if __name__ == "__main__":
    # Default relative to this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    default_config = os.path.join(current_dir, "rethink_config.json")

    if len(sys.argv) >= 2:
        config_fp = sys.argv[1]
    else:
        config_fp = default_config
        print(f"Using config: {config_fp}")

    insert_data(config_fp)
