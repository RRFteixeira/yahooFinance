-- List tables in 'silver' (you'll use this often)
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'silver'
ORDER BY 1;