import os
import time

import psycopg2
from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")


def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "db"),
        database=os.getenv("POSTGRES_DB", "haru_db"),
        user=os.getenv("POSTGRES_USER", "haru"),
        password=os.getenv("POSTGRES_PASSWORD", "haru123"),
        port=os.getenv("POSTGRES_PORT", "5432"),
    )
    return conn


def fetch_results():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, stream, votes, updated_at
        FROM realtime_results
        ORDER BY votes DESC, stream ASC;
        """
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "id": row[0],
            "stream": row[1],
            "votes": row[2],
            "updated_at": row[3].isoformat(),
        }
        for row in rows
    ]


def broadcast_results():
    socketio.emit("results_updated", fetch_results())


def init_database(max_retries=10, retry_delay=2):
    for attempt in range(1, max_retries + 1):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS realtime_results (
                    id SERIAL PRIMARY KEY,
                    stream VARCHAR(100) UNIQUE NOT NULL,
                    votes INTEGER NOT NULL DEFAULT 0 CHECK (votes >= 0),
                    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
                );
                """
            )
            cur.execute(
                """
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1
                        FROM information_schema.columns
                        WHERE table_name = 'realtime_results'
                          AND column_name = 'candidate'
                    ) AND NOT EXISTS (
                        SELECT 1
                        FROM information_schema.columns
                        WHERE table_name = 'realtime_results'
                          AND column_name = 'stream'
                    ) THEN
                        ALTER TABLE realtime_results RENAME COLUMN candidate TO stream;
                    END IF;
                END $$;
                """
            )
            cur.execute(
                """
                INSERT INTO realtime_results (stream, votes)
                VALUES
                    ('Stream A', 1200),
                    ('Stream B', 980),
                    ('Stream C', 760)
                ON CONFLICT (stream)
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
    return jsonify(fetch_results())


@app.route("/api/results", methods=["POST"])
def upsert_result():
    payload = request.get_json(silent=True) or {}
    stream = (payload.get("stream") or payload.get("candidate") or "").strip()
    votes = payload.get("votes")

    if not stream:
        return jsonify({"error": "'stream' is required."}), 400
    if not isinstance(votes, int) or votes < 0:
        return jsonify({"error": "'votes' must be a non-negative integer."}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO realtime_results (stream, votes)
        VALUES (%s, %s)
        ON CONFLICT (stream)
        DO UPDATE SET votes = EXCLUDED.votes, updated_at = NOW()
        RETURNING id, stream, votes, updated_at;
        """,
        (stream, votes),
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    broadcast_results()

    return (
        jsonify(
            {
                "id": row[0],
                "stream": row[1],
                "votes": row[2],
                "updated_at": row[3].isoformat(),
            }
        ),
        201,
    )


@app.route("/api/results/<int:result_id>", methods=["DELETE"])
def delete_result(result_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        DELETE FROM realtime_results
        WHERE id = %s
        RETURNING id, stream;
        """,
        (result_id,),
    )
    row = cur.fetchone()

    if row is None:
        cur.close()
        conn.close()
        return jsonify({"error": "Result not found."}), 404

    conn.commit()
    cur.close()
    conn.close()

    broadcast_results()

    return jsonify({"id": row[0], "stream": row[1], "deleted": True})


if __name__ == "__main__":
    init_database()
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, allow_unsafe_werkzeug=True)