-- PostgreSQL init script
-- This file runs automatically when the container starts for the first time.

CREATE TABLE IF NOT EXISTS items (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ  DEFAULT NOW()
);

INSERT INTO items (name) VALUES
    ('Docker'),
    ('PostgreSQL'),
    ('Redis');
