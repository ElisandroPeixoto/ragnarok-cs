# Progressão de level

Como o personagem sobe de nível. O nível máximo, por enquanto, é **99**. A regra está em `backend/core/level_progression.py`; o cálculo de quanta EXP cada monstro dá está em [Regra de experiência](regra-de-experiencia.md).

## EXP total

`CharacterModel.exp` guarda a **EXP total acumulada** do personagem, e o `level` sai dela. Com 100 de EXP total ele está no nível 2; com 200, no nível 3; e assim por diante. Subir de nível **não zera** a EXP.

## Custo de cada nível

Cada faixa diz quanta EXP é preciso para subir de **qualquer nível da faixa** para o seguinte.

| Níveis | EXP por nível | Subidas | EXP total ao longo da faixa |
|---|---|---|---|
| 1 a 5 | 100 | 5 | 0 → 500 (nível 6) |
| 6 a 10 | 150 | 5 | 500 → 1250 (nível 11) |
| 11 a 20 | 200 | 10 | 1250 → 3250 (nível 21) |
| 21 a 30 | 300 | 10 | 3250 → 6250 (nível 31) |
| 31 a 40 | 400 | 10 | 6250 → 10250 (nível 41) |
| 41 a 50 | 500 | 10 | 10250 → 15250 (nível 51) |
| 51 a 60 | 600 | 10 | 15250 → 21250 (nível 61) |
| 61 a 70 | 800 | 10 | 21250 → 29250 (nível 71) |
| 71 a 80 | 1000 | 10 | 29250 → 39250 (nível 81) |
| 81 a 90 | 1200 | 10 | 39250 → 51250 (nível 91) |
| 91 a 98 | 1500 | 8 | 51250 → 63250 (nível 99) |

O último nível (99) não tem custo: é o máximo. A EXP total do nível 99 é **63250**; ganhos além disso não são guardados.

### Exemplos

| EXP total | Nível | EXP no nível |
|---|---|---|
| 0 a 99 | 1 | 0 a 99 de 100 |
| 100 | 2 | 0 de 100 |
| 250 | 3 | 50 de 100 |
| 500 | 6 | 0 de 150 |
| 810 | 8 | 10 de 150 |
| 1250 | 11 | 0 de 200 |

## Barra de EXP

A barra do perfil mostra a EXP **dentro do nível atual** sobre o que o nível pede (por exemplo, `50/100` no nível 3 com 250 de EXP total). No nível 99 a barra fica cheia com o texto `MAX`. O backend calcula os dois valores e os manda no personagem (`exp_progress` e `exp_needed`, ver [Endpoints](endpoints-backend.md)).

## Quando o nível sobe

`POST /api/v1/characters/{id}/battle-result` (fim da caçada, ver [Regra de experiência](regra-de-experiencia.md)):

1. soma a EXP dos abates à EXP total (limitada a 63250);
2. recalcula o nível (`level_for_exp`); **pode subir vários níveis de uma vez**;
3. grava `exp` e `level` no personagem.

O frontend mostra "Charname reached level N!" no Battle Log quando a resposta chega.

Detalhes:
- A EXP de cada monstro da caçada usa o **nível que o personagem tinha ao começar** a caçada: subir de nível só vale para a caçada seguinte.
- Morrer tira 20% da EXP acumulada **no nível atual**, nunca da EXP total, então **morrer não faz perder nível** (ver [Regra de experiência](regra-de-experiencia.md)).
- O `seed_data.py` recalcula o nível de todos os personagens a partir da EXP total a cada execução. Assim, mudar a tabela ou ter personagens antigos não deixa nível e EXP inconsistentes.

## No código

- `exp_to_next(level)`: EXP para subir do nível; `None` no máximo.
- `total_exp_for_level(level)`: EXP total em que o nível é atingido.
- `level_for_exp(total)`: nível de uma EXP total.
- `exp_progress(level, total)`: EXP dentro do nível.
- A tabela é a lista `TIERS` `(último nível da faixa, custo)`. Para mudar a progressão (ou o nível máximo, `MAX_LEVEL`), edite só esse arquivo e rode o seed.

## O que ainda falta

- Pontos de atributo/skill ao subir de nível, HP e SP que crescem com o nível: hoje subir de nível só muda o número.
- Subida de nível no meio da caçada (hoje só ao fechar a caçada).
