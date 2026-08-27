"""Create and populate the SQLite database.

Deterministic: every run produces byte-identical data (fixed RNG seed, fixed
reference date). Run via `make seed` or `python -m app.seed`.
"""

import random
from datetime import date, timedelta

from .db import DB_PATH, get_conn

SCHEMA = """
CREATE TABLE orgs (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE people (
    id INTEGER PRIMARY KEY,
    org_id INTEGER NOT NULL REFERENCES orgs(id),
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    city TEXT,
    state TEXT,
    created_at TEXT NOT NULL
);
CREATE TABLE tags (
    id INTEGER PRIMARY KEY,
    org_id INTEGER NOT NULL REFERENCES orgs(id),
    name TEXT NOT NULL,
    UNIQUE (org_id, name)
);
CREATE TABLE person_tags (
    person_id INTEGER NOT NULL REFERENCES people(id),
    tag_id INTEGER NOT NULL REFERENCES tags(id),
    PRIMARY KEY (person_id, tag_id)
);
"""

ORGS = ["Bluebonnet Action Fund", "Prairie Wind Collective"]

TAG_NAMES = {
    1: [
        "volunteer", "canvasser", "donor", "host", "precinct-captain",
        "phone-banker", "driver", "organizer", "member", "poll-watcher",
        "new-signup",
    ],
    2: [
        "volunteer", "canvasser", "donor", "host", "precinct-captain",
        "phone-banker", "driver", "organizer", "member", "texter",
    ],
}

FIRST_NAMES = [
    "Maria", "James", "Sofia", "Daniel", "Aisha", "Miguel", "Grace", "Ethan",
    "Priya", "Marcus", "Elena", "Tyler", "Naomi", "Carlos", "Hannah", "Devon",
    "Lucia", "Andre", "Ruth", "Omar",
]

LAST_NAMES = [
    "Garcia", "Nguyen", "Johnson", "Patel", "Hernandez", "Kim", "Brooks",
    "Okafor", "Reyes", "Thompson", "Castillo", "Lee", "Washington", "Flores",
    "Novak", "Jackson", "Tran", "Morales", "Bennett", "Diaz",
]

CITIES = [
    ("Houston", "TX"), ("Austin", "TX"), ("Dallas", "TX"),
    ("San Antonio", "TX"), ("El Paso", "TX"),
    ("Tulsa", "OK"), ("Oklahoma City", "OK"), ("Norman", "OK"),
]

EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "example.org"]

REFERENCE_DATE = date(2026, 8, 1)

PEOPLE_COUNT = 200

# Carried over from the previous CRM on 2025-02-14. Field values and tag
# links are imported exactly as they appeared in the export.
LEGACY_PEOPLE = [
    # (id, org_id, first, last, email, city, state, created_at)
    (201, 1, "Rosa", "Delgado", "rosa.delgado201@gmail.com", " Houston", "TX", "2024-11-03"),
    (202, 1, "Frank", "Osei", "frank.osei202@yahoo.com", "Houston ", "TX", "2024-06-19"),
    (203, 1, "Iris", "Calloway", "iris.calloway203@outlook.com", "houston", "TX", "2023-12-02"),
    (204, 1, "Sam", "Whitfield", "sam.whitfield204@gmail.com", None, None, "2025-01-08"),
    (205, 1, "Nora", "Beltran", "nora.beltran205@example.org", "Austin", "tx", "2024-03-27"),
    (206, 1, "Ivan", "Petrov", "ivan.petrov206@gmail.com", "El Paso", "TX", "2024-09-14"),
    (207, 2, "Dena", "Marsh", "dena.marsh207@yahoo.com", " Tulsa", "OK", "2024-05-30"),
    (208, 2, "Theo", "Lindqvist", "theo.lindqvist208@gmail.com", None, None, "2024-10-21"),
    (209, 2, "Faye", "Okonkwo", "faye.okonkwo209@outlook.com", "norman", "OK", "2023-11-15"),
    (210, 2, "Gus", "Palmer", "gus.palmer210@example.org", None, "OK", "2025-01-30"),
    (211, 2, "Lena", "Vargas", "lena.vargas211@gmail.com", "Oklahoma City", "OK", "2024-08-07"),
    (212, 2, "Cole", "Ashford", "cole.ashford212@yahoo.com", "Tulsa ", "OK", "2024-02-11"),
]

# Tag rows and person->tag links from the same export, keyed the way the
# export keyed them: (org_id, tag_name).
LEGACY_TAGS = [(1, "donor ")]
LEGACY_TAG_LINKS = [
    (201, 1, "volunteer"),
    (201, 1, "donor "),
    (203, 1, "donor "),
    (204, 1, "new-signup"),
    (206, 2, "texter"),
    (207, 2, "canvasser"),
    (207, 1, "poll-watcher"),
    (209, 2, "member"),
    (211, 1, "donor"),
]


def seed() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = get_conn()
    conn.executescript(SCHEMA)
    rng = random.Random(42)

    for i, name in enumerate(ORGS, start=1):
        conn.execute("INSERT INTO orgs (id, name) VALUES (?, ?)", (i, name))

    tag_ids: dict[int, list[int]] = {1: [], 2: []}
    next_tag_id = 1
    for org_id in (1, 2):
        for tag_name in TAG_NAMES[org_id]:
            conn.execute(
                "INSERT INTO tags (id, org_id, name) VALUES (?, ?, ?)",
                (next_tag_id, org_id, tag_name),
            )
            tag_ids[org_id].append(next_tag_id)
            next_tag_id += 1

    for person_id in range(1, PEOPLE_COUNT + 1):
        org_id = 1 if person_id <= PEOPLE_COUNT // 2 else 2
        first = rng.choice(FIRST_NAMES)
        last = rng.choice(LAST_NAMES)
        city, state = rng.choice(CITIES)
        domain = rng.choice(EMAIL_DOMAINS)
        email = f"{first.lower()}.{last.lower()}{person_id}@{domain}"
        created = REFERENCE_DATE - timedelta(days=rng.randrange(400))
        conn.execute(
            "INSERT INTO people (id, org_id, first_name, last_name, email,"
            " city, state, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (person_id, org_id, first, last, email, city, state, created.isoformat()),
        )
        how_many = rng.choice([0, 1, 1, 2, 2, 3])
        for tag_id in rng.sample(tag_ids[org_id], how_many):
            conn.execute(
                "INSERT INTO person_tags (person_id, tag_id) VALUES (?, ?)",
                (person_id, tag_id),
            )

    for pid, org_id, first, last, email, city, state, created in LEGACY_PEOPLE:
        conn.execute(
            "INSERT INTO people (id, org_id, first_name, last_name, email,"
            " city, state, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (pid, org_id, first, last, email, city, state, created),
        )

    for org_id, name in LEGACY_TAGS:
        conn.execute(
            "INSERT INTO tags (id, org_id, name) VALUES (?, ?, ?)",
            (next_tag_id, org_id, name),
        )
        next_tag_id += 1

    tag_id_by_key = {
        (r["org_id"], r["name"]): r["id"]
        for r in conn.execute("SELECT id, org_id, name FROM tags")
    }
    for pid, tag_org, name in LEGACY_TAG_LINKS:
        conn.execute(
            "INSERT INTO person_tags (person_id, tag_id) VALUES (?, ?)",
            (pid, tag_id_by_key[(tag_org, name)]),
        )

    conn.commit()
    people = conn.execute("SELECT COUNT(*) FROM people").fetchone()[0]
    tags = conn.execute("SELECT COUNT(*) FROM tags").fetchone()[0]
    conn.close()
    print(f"seeded {DB_PATH}: {people} people, {tags} tags, {len(ORGS)} orgs")


if __name__ == "__main__":
    seed()
