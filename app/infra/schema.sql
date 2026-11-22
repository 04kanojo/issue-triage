-- M0 只建 issues 一张表；M1 会在这里追加 issue_labels 与 issue_links。
-- 所有时间字段存 ISO 8601 字符串，SQLite 没有原生 datetime，避免类型转换分歧。

CREATE TABLE IF NOT EXISTS issues (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    repo        TEXT    NOT NULL,
    number      INTEGER NOT NULL,
    title       TEXT    NOT NULL,
    body        TEXT    NOT NULL DEFAULT '',
    state       TEXT    NOT NULL DEFAULT 'open',
    created_at  TEXT    NOT NULL DEFAULT '',
    closed_at   TEXT,
    UNIQUE (repo, number)
);

CREATE INDEX IF NOT EXISTS idx_issues_repo ON issues(repo);
CREATE INDEX IF NOT EXISTS idx_issues_state ON issues(state);