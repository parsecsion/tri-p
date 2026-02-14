SELECT component FROM components GROUP BY component ORDER BY count(*) DESC LIMIT 1;
