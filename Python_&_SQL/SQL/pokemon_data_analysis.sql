DROP TABLE IF EXISTS pokemon;

CREATE TABLE pokemon (
    id INTEGER,
    name TEXT,
    height INTEGER,
    weight INTEGER,
    types TEXT
);

-- 2. Import data from CSV (SQLite-specific)
-- NOTE: You need to be in the SQLite CLI and run: .mode csv
-- Then run: .import 'python/data/caught_pokemon.csv' pokemon

-- 3. Query: Get all Pokémon heavier than 100kg
SELECT id, name, weight
FROM pokemon
WHERE weight > 100
ORDER BY weight DESC;

-- 4. Query: Count Pokémon by type
SELECT 
    types,
    COUNT(*) AS count
FROM pokemon
GROUP BY types
ORDER BY count DESC;

-- 5. Query: Find the tallest Pokémon
SELECT name, height
FROM pokemon
ORDER BY height DESC
LIMIT 1;
