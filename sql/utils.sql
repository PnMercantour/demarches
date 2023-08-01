SELECT
    query AS "TEXT",
    pid AS session_id,
    state AS status,
    query_start AS start_time,
    now() - query_start AS total_elapsed_time
FROM pg_stat_activity
WHERE state NOT LIKE 'idle%'
      AND state NOT LIKE 'idle in transaction%'
      AND state NOT LIKE 'idle in transaction (aborted)%';

