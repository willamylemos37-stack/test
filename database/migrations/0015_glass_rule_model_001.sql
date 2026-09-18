-- Etapa 59: regra técnica definitiva do vidro para os modelos validados.
-- Largura: MP-309 - 8 mm. Altura: MP-300 - 78 mm (= 35 + 35 + 8).
INSERT INTO regras_tecnicas (code,expression,description) VALUES
('VIDRO78','largura = MP-309 - 8 mm; altura = MP-300 - 78 mm','Folga total de 8 mm na largura e 8 mm na altura; na altura são descontados 35 mm de cada MP-309 + 8 mm de folga.')
ON CONFLICT (code) DO UPDATE SET expression=EXCLUDED.expression,description=EXCLUDED.description;
