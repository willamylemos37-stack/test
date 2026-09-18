INSERT INTO modelos (code,name,leaves,status)
VALUES ('MOD-001','Janela Módulo Prático 2 Folhas',2,'ATIVO')
ON CONFLICT (code) DO UPDATE SET name=EXCLUDED.name,leaves=EXCLUDED.leaves,status=EXCLUDED.status;

INSERT INTO regras_tecnicas (code,expression,description) VALUES
('L30','L - 30','MP-357/MP-358 — marco superior/inferior'),
('H','H','MP-360 — marco lateral'),
('H40','H - 40','MP-300/MP-302/MP-321'),
('L108_2','(L - 108) / 2','MP-309 e BG-202 horizontal'),
('H134','H - 134','BG-202 vertical'),
('VIDRO7','dimensão_da_folha - 7','Folga total de 7 mm; 3,5 mm por lado')
ON CONFLICT (code) DO UPDATE SET expression=EXCLUDED.expression,description=EXCLUDED.description;

DELETE FROM modelo_componentes WHERE model_id=(SELECT id FROM modelos WHERE code='MOD-001');
INSERT INTO modelo_componentes (model_id,material_code,quantity,cut_rule,notes)
SELECT m.id,x.material_code,x.quantity,x.cut_rule,x.notes
FROM modelos m CROSS JOIN (VALUES
('MP-357',1,'L30','Marco superior — L - 30 mm'),
('MP-358',1,'L30','Marco inferior — L - 30 mm'),
('MP-360',2,'H','Marco lateral — H'),
('MP-300',2,'H40','Montante de folha — H - 40 mm'),
('MP-302',1,'H40','Montante central externo — H - 40 mm'),
('MP-321',1,'H40','Montante central interno — H - 40 mm'),
('MP-309',4,'L108_2','Travessa — (L - 108) / 2'),
('BG-202',4,'L108_2','Baguete horizontal — (L - 108) / 2'),
('BG-202',4,'H134','Baguete vertical — H - 134 mm')
) AS x(material_code,quantity,cut_rule,notes)
WHERE m.code='MOD-001';

DELETE FROM modelo_componentes WHERE model_id=(SELECT id FROM modelos WHERE code='MOD-001') AND material_code='MP-352';
