"""Import pilot users from CSV: user_id,name,email,groups   (groups separated by ';')
   python scripts/import_users.py pilot_users.csv
Groups must be reviewed by the data owner. Re-running updates existing users."""
import csv
import sys
from kb.db import connect

if __name__ == "__main__":
    conn = connect()
    n = 0
    for r in csv.DictReader(open(sys.argv[1], newline="")):
        groups = [g.strip() for g in r["groups"].split(";") if g.strip()]
        conn.execute("""INSERT INTO users (user_id,name,email,groups) VALUES (%s,%s,%s,%s)
                        ON CONFLICT (user_id) DO UPDATE SET name=EXCLUDED.name, email=EXCLUDED.email, groups=EXCLUDED.groups""",
                     (r["user_id"].strip(), r["name"].strip(), r["email"].strip().lower(), groups))
        n += 1
    print(f"imported {n} users")
