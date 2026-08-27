from app.db import get_conn


def test_people_count():
    conn = get_conn()
    assert conn.execute("SELECT COUNT(*) FROM people").fetchone()[0] == 212


def test_people_split_across_orgs():
    conn = get_conn()
    rows = conn.execute(
        "SELECT org_id, COUNT(*) AS n FROM people GROUP BY org_id ORDER BY org_id"
    ).fetchall()
    assert [(r["org_id"], r["n"]) for r in rows] == [(1, 106), (2, 106)]


def test_tags_per_org():
    conn = get_conn()
    rows = conn.execute(
        "SELECT org_id, COUNT(*) AS n FROM tags GROUP BY org_id ORDER BY org_id"
    ).fetchall()
    assert [(r["org_id"], r["n"]) for r in rows] == [(1, 12), (2, 10)]


def test_emails_unique():
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) FROM people").fetchone()[0]
    distinct = conn.execute("SELECT COUNT(DISTINCT email) FROM people").fetchone()[0]
    assert total == distinct
