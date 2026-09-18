-- v5.47: regras oficiais do MP-309 por quantidade de folhas.
-- 2 folhas: (L - 105) / 2
-- 4 folhas: (L - 178) / 4

INSERT INTO regras_tecnicas (code, expression, description)
VALUES
  ('L105_2', '(L - 105) / 2', 'MP-309 para janela de 2 folhas'),
  ('L178_4', '(L - 178) / 4', 'MP-309 para janela de 4 folhas')
ON CONFLICT (code) DO UPDATE
SET expression = EXCLUDED.expression,
    description = EXCLUDED.description;

UPDATE modelo_componentes
SET cut_rule='L105_2',
    notes='Travessa MP-309 — 2 folhas: (L - 105) / 2'
WHERE material_code='MP-309'
  AND model_id=(SELECT id FROM modelos WHERE code='MOD-001');
