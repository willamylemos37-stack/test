-- v5.48: cadastro técnico inicial do MOD-002 — Janela Módulo Prático 4 Folhas.
-- MP-309: (L - 178) / 4, 8 peças.
-- MP-352: H - 40, exclusivo do modelo de 4 folhas.
-- BG-202: mesmas regras dimensionais estabelecidas para o modelo de 2 folhas.

INSERT INTO modelos (code, name, leaves, product_type, status)
VALUES ('MOD-002', 'Janela Módulo Prático 4 Folhas', 4, 'ESQUADRIA', 'ATIVO')
ON CONFLICT (code) DO UPDATE
SET name=EXCLUDED.name, leaves=EXCLUDED.leaves, product_type=EXCLUDED.product_type, status=EXCLUDED.status;

INSERT INTO regras_tecnicas (code, expression, description) VALUES
  ('L178_4', '(L - 178) / 4', 'MP-309 para janela de 4 folhas'),
  ('H40', 'H - 40', 'MP-300/MP-302/MP-321/MP-352'),
  ('H134', 'H - 134', 'BG-202 vertical'),
  ('VIDRO78', 'largura = MP-309 - 8 mm; altura = MP-300 - 78 mm', 'Vidro: largura = MP-309 - 8 mm; altura = H - 118 mm')
ON CONFLICT (code) DO UPDATE
SET expression=EXCLUDED.expression, description=EXCLUDED.description;

DELETE FROM modelo_componentes WHERE model_id=(SELECT id FROM modelos WHERE code='MOD-002');
INSERT INTO modelo_componentes (model_id, material_code, quantity, cut_rule, notes)
SELECT m.id,x.material_code,x.quantity,x.cut_rule,x.notes
FROM modelos m CROSS JOIN (VALUES
  ('MP-357',1,'L30','Marco superior — L - 30 mm'),
  ('MP-358',1,'L30','Marco inferior — L - 30 mm'),
  ('MP-360',2,'H','Marco lateral — H'),
  ('MP-300',4,'H40','Montante de folha — H - 40 mm'),
  ('MP-302',2,'H40','Montante central externo — H - 40 mm'),
  ('MP-321',2,'H40','Montante central interno — H - 40 mm'),
  ('MP-352',2,'H40','Batente simples/batedor — exclusivo 4 folhas — H - 40 mm'),
  ('MP-309',8,'L178_4','Travessa — 4 folhas: (L - 178) / 4'),
  ('BG-202',8,'L178_4','Baguete horizontal — mesma dimensão do MP-309'),
  ('BG-202',8,'H134','Baguete vertical — H - 134 mm')
) AS x(material_code,quantity,cut_rule,notes)
WHERE m.code='MOD-002';
