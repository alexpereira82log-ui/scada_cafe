WITH RECURSIVE datas(XXXXX) AS (
    SELECT date('2026-03-01')
    UNION ALL
    SELECT date(data, '+1 day')
    FROM datas
    WHERE data < '2026-03-31'
)
INSERT INTO comissao (data)
SELECT data FROM datas;