-- scirag: personal RAG for a Portuguese science communicator
-- schema v1

CREATE TABLE IF NOT EXISTS sources (
    id          TEXT PRIMARY KEY,
    title       TEXT,
    author      TEXT,
    year        TEXT,
    url         TEXT,
    source_type TEXT,    -- 'article'|'book'|'column'|'field_note'|'talk'|'slide'
    language    TEXT DEFAULT 'pt',
    tier        INTEGER, -- 1=voice 2=knowledge 3=pedagogy 4=institutional
    ingested_at TEXT,
    full_text   TEXT,
    metadata    TEXT     -- JSON (includes original file_path for reingest)
);

CREATE TABLE IF NOT EXISTS nodes (
    id           TEXT PRIMARY KEY,
    content      TEXT NOT NULL,
    title        TEXT,
    node_type    TEXT DEFAULT 'excerpt',  -- 'excerpt'|'note'|'fig_caption'|'synthesis_frag'
    writing_mode TEXT,                    -- 'divulgacao'|'pedagogico'|'investigacao'
    source_id    TEXT REFERENCES sources(id),
    tier         INTEGER,
    tags         TEXT DEFAULT '[]',
    created_at   TEXT,
    updated_at   TEXT,
    embedding    BLOB                     -- numpy float32 tobytes()
);

-- FTS5: node_id stored unindexed so search results carry the id directly
CREATE VIRTUAL TABLE IF NOT EXISTS nodes_fts USING fts5(
    node_id UNINDEXED,
    content,
    title
);

CREATE TRIGGER IF NOT EXISTS nodes_fts_insert AFTER INSERT ON nodes BEGIN
    INSERT INTO nodes_fts(node_id, content, title)
    VALUES (new.id, new.content, COALESCE(new.title, ''));
END;

CREATE TRIGGER IF NOT EXISTS nodes_fts_delete AFTER DELETE ON nodes BEGIN
    DELETE FROM nodes_fts WHERE node_id = old.id;
END;

CREATE TRIGGER IF NOT EXISTS nodes_fts_update AFTER UPDATE ON nodes BEGIN
    DELETE FROM nodes_fts WHERE node_id = old.id;
    INSERT INTO nodes_fts(node_id, content, title)
    VALUES (new.id, new.content, COALESCE(new.title, ''));
END;

CREATE TABLE IF NOT EXISTS connections (
    id              TEXT PRIMARY KEY,
    from_node       TEXT REFERENCES nodes(id),
    to_node         TEXT REFERENCES nodes(id),
    connection_type TEXT,
    agent_name      TEXT,
    weight          REAL DEFAULT 0.8,
    rationale       TEXT,
    created_at      TEXT
);

CREATE INDEX IF NOT EXISTS idx_connections_from ON connections(from_node);
CREATE INDEX IF NOT EXISTS idx_connections_to   ON connections(to_node);
CREATE INDEX IF NOT EXISTS idx_connections_type ON connections(connection_type);

CREATE TABLE IF NOT EXISTS wikis (
    id            TEXT PRIMARY KEY,
    theme         TEXT UNIQUE,
    content       TEXT,
    seed_node_ids TEXT DEFAULT '[]',
    last_compiled TEXT,
    version       INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS syntheses (
    id           TEXT PRIMARY KEY,
    title        TEXT,
    content      TEXT,
    query        TEXT,
    node_ids     TEXT DEFAULT '[]',
    writing_mode TEXT,
    created_at   TEXT
);

CREATE TABLE IF NOT EXISTS figures (
    id           TEXT PRIMARY KEY,
    source_id    TEXT REFERENCES sources(id),
    node_id      TEXT REFERENCES nodes(id),
    caption      TEXT,
    caption_en   TEXT,
    file_path    TEXT,
    figure_type  TEXT,   -- 'map'|'diagram'|'photo'|'chart'|'fossil'
    tags         TEXT DEFAULT '[]'
);

CREATE INDEX IF NOT EXISTS idx_nodes_mode   ON nodes(writing_mode);
CREATE INDEX IF NOT EXISTS idx_nodes_tier   ON nodes(tier);
CREATE INDEX IF NOT EXISTS idx_nodes_source ON nodes(source_id);
