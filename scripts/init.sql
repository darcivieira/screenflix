-- Schema inicial para o Screenflix
-- PostgreSQL

BEGIN;

CREATE TABLE IF NOT EXISTS media (
    id              BIGSERIAL PRIMARY KEY,
    title           VARCHAR(255) NOT NULL,
    original_title  VARCHAR(255),
    media_type      VARCHAR(10) NOT NULL DEFAULT 'movie',
    year            INTEGER NOT NULL,
    release_date    DATE,
    plot            TEXT NOT NULL,
    genres          TEXT,
    tags            TEXT,
    actors          TEXT,
    writers         TEXT,
    directors       TEXT,
    poster_url      VARCHAR,
    awards          VARCHAR(255),
    rating          DOUBLE PRECISION,
    runtime         INTEGER,
    total_seasons   INTEGER,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_media_type
        CHECK (media_type IN ('movie', 'series'))
);

CREATE INDEX IF NOT EXISTS idx_media_title ON media (title);
CREATE INDEX IF NOT EXISTS idx_media_media_type ON media (media_type);

CREATE TABLE IF NOT EXISTS episode (
    id              BIGSERIAL PRIMARY KEY,
    season_id       BIGINT NOT NULL,
    title           VARCHAR NOT NULL,
    original_title  VARCHAR(255),
    plot            TEXT NOT NULL,
    released        DATE,
    poster_url      VARCHAR,
    season          INTEGER NOT NULL,
    episode         INTEGER NOT NULL,
    rating          DOUBLE PRECISION,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_episode_media
        FOREIGN KEY (season_id)
        REFERENCES media (id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_episode_season_id ON episode (season_id);
CREATE INDEX IF NOT EXISTS idx_episode_season_episode ON episode (season, episode);

COMMIT;