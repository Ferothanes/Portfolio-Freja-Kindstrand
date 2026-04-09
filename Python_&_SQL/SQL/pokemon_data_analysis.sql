DROP TABLE IF EXISTS pokemon;

CREATE TABLE pokemon (
    id INTEGER,
    name TEXT,
    height INTEGER,
    weight INTEGER,
    types TEXT
);

-- Import from SQLite CLI:
-- .mode csv
-- .import 'data/caught_pokemon.csv' pokemon

-- Heaviest Pokemon
SELECT id, name, weight, types
FROM pokemon
ORDER BY weight DESC
LIMIT 5;

-- Tallest Pokemon
SELECT id, name, height, types
FROM pokemon
ORDER BY height DESC
LIMIT 5;

-- Count how often each Pokemon appears
SELECT
    name,
    COUNT(*) AS catches
FROM pokemon
GROUP BY name
ORDER BY catches DESC, name ASC;

-- Count Pokemon by type using a recursive CTE to split multi-type values
WITH RECURSIVE split_types (pokemon_name, type_name, remaining) AS (
    SELECT
        name,
        TRIM(SUBSTR(types, 1, INSTR(types || ',', ',') - 1)),
        LTRIM(SUBSTR(types || ',', INSTR(types || ',', ',') + 1))
    FROM pokemon
    UNION ALL
    SELECT
        pokemon_name,
        TRIM(SUBSTR(remaining, 1, INSTR(remaining, ',') - 1)),
        LTRIM(SUBSTR(remaining, INSTR(remaining, ',') + 1))
    FROM split_types
    WHERE remaining <> ''
)
SELECT
    type_name,
    COUNT(*) AS catches
FROM split_types
WHERE type_name <> ''
GROUP BY type_name
ORDER BY catches DESC, type_name ASC;
