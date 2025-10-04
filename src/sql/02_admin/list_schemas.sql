-- List schemas (meta-commands like \dn won't work here; use SQL)
SELECT schema_name 
FROM information_schema.schemata
ORDER BY 1;