SELECT user_id, name, COUNT(*) as count
FROM categories
GROUP BY user_id, name
HAVING COUNT(*) > 1; 