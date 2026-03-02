WITH RECURSIVE datas(dia) AS (
    SELECT date('2026-03-01')
    UNION ALL
    SELECT date(dia, '+1 day')
    FROM datas
    WHERE dia < date('2026-03-31')
)

INSERT INTO base_fat (data, dia_semana, equipe)
SELECT 
    dia,
    
    -- Dia da semana em português
    CASE strftime('%w', dia)
        WHEN '0' THEN 'domingo'
        WHEN '1' THEN 'segunda-feira'
        WHEN '2' THEN 'terça-feira'
        WHEN '3' THEN 'quarta-feira'
        WHEN '4' THEN 'quinta-feira'
        WHEN '5' THEN 'sexta-feira'
        WHEN '6' THEN 'sábado'
    END,
    
    -- Alternar equipe começando com 2 no dia 01
    CASE 
        WHEN (julianday(dia) - julianday('2026-03-01')) % 2 = 0 THEN 2
        ELSE 1
    END

FROM datas;