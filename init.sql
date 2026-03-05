-- ============================================================
--  PGA Production Database - Initial Schema
-- ============================================================

-- ------------------------------------------------------------
--  PARTS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS parts (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

INSERT INTO parts (name) VALUES
    ('Transporter łańcuchowy'),
    ('Transporter łańcuchowy'),
    ('Robot'),
    ('Miejsce odłożenia'),
    ('Chwytak'),
    ('Pozycjoner koszy');

-- ------------------------------------------------------------
--  ERRORS  (wiele błędów → jeden part)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS errors (
    id          SERIAL PRIMARY KEY,
    code        VARCHAR(64) NOT NULL,
    context     TEXT,
    part_id     INTEGER NOT NULL
        REFERENCES parts (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
--  CONDITION  (niezależna tabela – na razie pusta)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS condition (
    id         SERIAL PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);