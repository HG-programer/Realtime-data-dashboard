CREATE TABLE IF NOT EXISTS realtime_results (
    id SERIAL PRIMARY KEY,
    stream VARCHAR(100) UNIQUE NOT NULL,
    votes INTEGER NOT NULL DEFAULT 0 CHECK (votes >= 0),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

INSERT INTO realtime_results (stream, votes)
VALUES
    ('Stream A', 1200),
    ('Stream B', 980),
    ('Stream C', 760)
ON CONFLICT (stream)
DO NOTHING;
