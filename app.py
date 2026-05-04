import os
import time

import psycopg2
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "db"),
        database=os.getenv("POSTGRES_DB", "haru_db"),
        user=os.getenv("POSTGRES_USER", "haru"),
        password=os.getenv("POSTGRES_PASSWORD", "haru123"),
        port=os.getenv("POSTGRES_PORT", "5432"),
    )
    return conn


def init_database(max_retries=10, retry_delay=2):
    for attempt in range(1, max_retries + 1):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS realtime_results (
                    id SERIAL PRIMARY KEY,
                    candidate VARCHAR(100) UNIQUE NOT NULL,
                    votes INTEGER NOT NULL DEFAULT 0 CHECK (votes >= 0),
                    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
                );
                """
            )
            cur.execute(
                """
                INSERT INTO realtime_results (candidate, votes)
                VALUES
                    ('Candidate A', 1200),
                    ('Candidate B', 980),
                    ('Candidate C', 760)
                ON CONFLICT (candidate)
                DO NOTHING;
                """
            )
            conn.commit()
            cur.close()
            conn.close()
            return
        except psycopg2.OperationalError:
            if attempt == max_retries:
                raise
            time.sleep(retry_delay)


@app.route("/")
def home():
    return jsonify(
        {
            "message": "Real-time Data Dashboard backend is running.",
            "services": ["flask", "postgres"],
            "next_step": "Deploy this stack on AWS",
        }
    )


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/db-test")
def db_test():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT version();")
    db_version = cur.fetchone()
    cur.close()
    conn.close()

    return jsonify({"postgres_version": db_version})


@app.route("/api/results", methods=["GET"])
def get_results():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, candidate, votes, updated_at
        FROM realtime_results
        ORDER BY votes DESC, candidate ASC;
        """
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    results = [
        {
            "id": row[0],
            "candidate": row[1],
            "votes": row[2],
            "updated_at": row[3].isoformat(),
        }
        for row in rows
    ]
    return jsonify(results)


@app.route("/api/results", methods=["POST"])
def upsert_result():
    payload = request.get_json(silent=True) or {}
    candidate = (payload.get("candidate") or "").strip()
    votes = payload.get("votes")

    if not candidate:
        return jsonify({"error": "'candidate' is required."}), 400
    if not isinstance(votes, int) or votes < 0:
        return jsonify({"error": "'votes' must be a non-negative integer."}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO realtime_results (candidate, votes)
        VALUES (%s, %s)
        ON CONFLICT (candidate)
        DO UPDATE SET votes = EXCLUDED.votes, updated_at = NOW()
        RETURNING id, candidate, votes, updated_at;
        """,
        (candidate, votes),
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    return (
        jsonify(
            {
                "id": row[0],
                "candidate": row[1],
                "votes": row[2],
                "updated_at": row[3].isoformat(),
            }
        ),
        201,
    )


if __name__ == "__main__":
    init_database()
    app.run(host="0.0.0.0", port=5000, debug=False)