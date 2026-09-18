-- Etapa 62: consolidação das regras técnicas atuais do MOD-001.
-- MP-309 e BG-202 horizontal usam (L - 103) / 4.
-- BG-202 vertical mantém H - 134.
-- O vidro usa MP-309 - 8 mm na largura e MP-300 - 78 mm na altura.
UPDATE regras_tecnicas
SET expression='(L - 103) / 4',
    description='MP-309 e BG-202 horizontal; largura útil da folha em milímetros inteiros.'
WHERE code='L108_2';

INSERT INTO regras_tecnicas (code, expression, description)
VALUES ('L103_4','(L - 103) / 4','MP-309 e BG-202 horizontal')
ON CONFLICT (code) DO UPDATE
SET expression=EXCLUDED.expression, description=EXCLUDED.description;

UPDATE modelo_componentes
SET cut_rule='L103_4',
    notes='Travessa — (L - 103) / 4'
WHERE material_code='MP-309'
  AND model_id=(SELECT id FROM modelos WHERE code='MOD-001');

UPDATE modelo_componentes
SET cut_rule='L103_4',
    notes='Baguete horizontal — (L - 103) / 4'
WHERE material_code='BG-202'
  AND cut_rule='L108_2'
  AND model_id=(SELECT id FROM modelos WHERE code='MOD-001');

UPDATE regras_tecnicas
SET expression='largura = MP-309 - 8 mm; altura = MP-300 - 78 mm',
    description='Folga total de 8 mm na largura e 8 mm na altura; na altura são descontados 35 mm de cada MP-309 + 8 mm de folga.'
WHERE code='VIDRO78';
