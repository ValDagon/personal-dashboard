"""Named ClickHouse SQL. Shown on the board so a hiring manager can read the engine."""

# Per clickhouse-best-practices schema-pk-cardinality-order:
# ORDER BY starts with low-cardinality world, then status, then id.
CREATE_PROJECTS = """
CREATE TABLE projects
(
    id String,
    world LowCardinality(String),
    status LowCardinality(String),
    public_title String,
    blurb String,
    stack String,
    links String,
    updated Date,
    is_open UInt8,
    is_archive UInt8,
    hire_private UInt8
)
ENGINE = MergeTree
ORDER BY (world, status, id)
AS SELECT
    CAST(id AS String) AS id,
    CAST(world AS String) AS world,
    CAST(status AS String) AS status,
    CAST(public_title AS String) AS public_title,
    CAST(blurb AS String) AS blurb,
    CAST(stack AS String) AS stack,
    CAST(links AS String) AS links,
    toDate(updated) AS updated,
    CAST(is_open AS UInt8) AS is_open,
    CAST(is_archive AS UInt8) AS is_archive,
    CAST(hire_private AS UInt8) AS hire_private
FROM file('{path}', Parquet)
"""

CREATE_OPEN_VIEW = """
CREATE VIEW open_by_world AS
SELECT *
FROM projects
WHERE is_open = 1
"""

CREATE_ARCHIVE_VIEW = """
CREATE VIEW archive_by_world AS
SELECT *
FROM projects
WHERE is_archive = 1
"""

SQL_VERSION = "SELECT version() AS clickhouse_version"

SQL_OPEN_COUNTS = """
SELECT
    world,
    count() AS open_count
FROM open_by_world
GROUP BY world
ORDER BY world
LIMIT 100
"""

SQL_OPEN_MIX = """
SELECT
    world,
    countIf(status = 'now') AS now_n,
    countIf(status = 'queued') AS queued_n,
    countIf(status = 'paused') AS paused_n,
    count() AS open_n,
    round(avg(dateDiff('day', updated, today())), 1) AS avg_stale_days
FROM projects
WHERE is_open = 1
GROUP BY world
ORDER BY world
LIMIT 100
"""

SQL_STALE = """
SELECT
    id,
    dateDiff('day', updated, today()) AS stale_days
FROM projects
LIMIT 100
"""

SQL_OPEN_TOTAL = "SELECT count() AS n FROM open_by_world LIMIT 1"
SQL_ARCHIVE_TOTAL = "SELECT count() AS n FROM archive_by_world LIMIT 1"

INSPECTOR = (
    ("Версия движка", SQL_VERSION),
    ("Открытые по миру", SQL_OPEN_COUNTS),
    ("Смесь статусов", SQL_OPEN_MIX),
    ("Свежесть карточек", SQL_STALE),
)
