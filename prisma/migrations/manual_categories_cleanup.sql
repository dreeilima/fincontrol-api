-- Primeiro, identificar categorias duplicadas
WITH duplicates AS (
  SELECT user_id, name, COUNT(*) as count
  FROM categories
  GROUP BY user_id, name
  HAVING COUNT(*) > 1
)

-- Manter apenas a categoria mais antiga e deletar as duplicatas
DELETE FROM categories c1
WHERE EXISTS (
  SELECT 1 FROM categories c2
  WHERE c2.user_id = c1.user_id
  AND c2.name = c1.name
  AND c2.created_at < c1.created_at
);

-- Agora é seguro adicionar a constraint única 