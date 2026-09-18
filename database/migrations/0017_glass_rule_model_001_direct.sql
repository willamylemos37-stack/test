-- v5.46: consolida a regra final do vidro do MOD-001.
-- Largura = MP-309 - 8 mm = ((L - 103) / 4) - 8.
-- Altura = MP-300 - 78 mm = (H - 40) - 78 = H - 118.
UPDATE regras_tecnicas
SET expression='largura = MP-309 - 8 mm; altura = MP-300 - 78 mm',
    description='Largura = ((L - 103) / 4) - 8 mm; altura = H - 118 mm (MP-300 - 78 mm).'
WHERE code='VIDRO78';
