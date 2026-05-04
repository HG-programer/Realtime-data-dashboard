CREATE TABLE IF NOT EXISTS realtime_results (
    id SERIAL PRIMARY KEY,
    candidate VARCHAR(100) UNIQUE NOT NULL,
    votes INTEGER NOT NULL DEFAULT 0 CHECK (votes >= 0),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

INSERT INTO realtime_results (candidate, votes)
VALUES
    ('Candidate A', 1200),
    ('Candidate B', 980),
    ('Candidate C', 760)
ON CONFLICT (candidate)
DO NOTHING;
