# Roadmap do sistema de combate

Este documento separa o que **já funciona**, o que é **lacuna conhecida** (encontrada lendo o código) e uma **proposta de evolução** por fases. As fases são sugestões de ordem, não decisões tomadas: servem de ponto de partida para planejar.

Detalhes do funcionamento atual estão em [Sistema de combate](sistema-de-combate.md).

## Estado atual

| Área | Situação |
|---|---|
| Montagem do encontro | ✅ `POST /api/v1/battles/` sorteia 1 monstro do mapa pelo `spawn_rate` |
| Dados de herói e monstro | ✅ vêm do banco (`JobModel`, `MonsterModel`, `SkillModel`); o antigo `mockup.py` foi removido |
| Posições iniciais | ✅ sorteadas em `spawn_units` (jogador na coluna 0, inimigos nas colunas 7–9) |
| Turnos | ✅ ordem fixa (herói, depois monstro), 30 s por turno, AP recarregado a cada turno |
| Movimento | ✅ arrastar e soltar, 1 AP por tile (distância de Manhattan) |
| Ataque | ✅ skill selecionada + clique no inimigo; alvo em linha reta dentro do alcance; dano fixo |
| IA | ✅ `passive`, `attack_every_turn`, `approach_and_attack` |
| Animação | ✅ sprite sheets com clips por direção (idle, attack, hurt, dead) |
| Vitória/derrota | ✅ detectadas e exibidas; ⚠️ sem consequência alguma |
| Log | ⚠️ registra movimento, derrota e fim, mas não os ataques |
| Persistência | ❌ nada volta para o backend |

## Lacunas conhecidas

Pontos encontrados no código, em ordem aproximada de impacto:

1. **O resultado não é salvo.** Vencer não dá EXP, zeny nem drops; perder não custa nada; o HP do personagem não muda. Não existe endpoint para isso.
2. **Ataques não aparecem no Battle Log.** `perform_attack` (`services/battle_actions.py`) só registra `defeat`. `LogEntry` já sabe formatar `kind="attack"`; falta adicionar a entrada.
3. **Só um monstro por batalha.** O endpoint devolve sempre `monster_1`. O frontend já aceita vários (turnos, spawn e IA iteram sobre todas as unidades).
4. **Só uma skill.** `Basic Attack` (dano 10, alcance 1) é a única skill no seed.
5. **Dano fixo.** Sem atributos, defesa, crítico, esquiva ou variação. O personagem não tem atributos (STR, AGI…) no modelo.
6. **Movimento sem caminho.** O custo é a distância de Manhattan e só o destino é verificado; uma unidade "atravessa" outras.
7. **Ordem de turno fixa.** `turn_order = list(units.keys())`: o herói sempre começa, sem iniciativa ou velocidade.
8. **Sem obstáculos.** `BoardConfig.blocked_tiles` existe e é respeitado por movimento e spawn, mas está sempre vazio; o fundo também é sempre o mesmo.
9. **Regras duplicadas fora do servidor.** Toda a regra roda no cliente; quando houver recompensa, o backend precisa validar ou recalcular o resultado.
10. **Monstros sem dados de batalha.** Lunatic e Wilow aparecem nos mapas, mas não podem ser caçados (não têm `sheet`).
11. **Erros invisíveis.** Se `POST /battles/` falhar, o botão Hunt não dá nenhum retorno ao jogador.
12. **Restos do mockup.** O ramo de `battle_board.py` para unidades sem sheet usa campos (`sprite`, `width`, `height`, `placeholder_color`) que o backend nunca envia.
13. **Dados de job repetidos.** `services/sprite_selector.py` repete `sheet` e `avatar` que já existem em `JobModel`.

## Proposta de fases

### Fase 1: fechar o ciclo da batalha

Objetivo: lutar passar a ter consequência.

- Endpoint para encerrar a batalha (ex.: `POST /api/v1/battles/{id}/finish` ou `POST /api/v1/battles/result`) com o resultado e o HP final do herói.
- Gravar a batalha em uma tabela (ex.: `battles`: personagem, mapa, monstros, status) quando ela começa. Assim o backend sabe que o encontro existe e pode recusar resultados de batalhas inventadas.
- Recompensas simples por monstro (colunas `base_exp`, `zeny` em `MonsterModel`) e atualização de `CharacterModel` (`exp`, `zeny`, `hp`).
- Atualizar o personagem em `session_state` com a resposta, para o perfil mostrar os novos valores.
- Registrar os ataques no log (lacuna 2).
- Mostrar o erro quando o Hunt falhar (lacuna 11).

### Fase 2: conteúdo e variedade

- Gerar as sheets de Lunatic e Wilow e preencher os dados de batalha no seed.
- Mais skills, com alcances e custos diferentes, e skills por job.
- Vários monstros por encontro (`monster_1`, `monster_2`… vindos do backend; a quantidade pode depender do mapa).
- Usar `blocked_tiles` e fundos diferentes por mapa (ex.: um campo `battle_board` em `MapModel`).

### Fase 3: atributos e fórmulas

- Atributos no personagem e no monstro (ex.: STR, AGI, VIT, DEX) e cálculo de ATK/DEF/HIT/FLEE.
- Dano calculado em vez de fixo: `damage` da skill vira um multiplicador.
- Progressão de nível: tabela de EXP por nível (substitui `MAX_EXP_DEFAULT` em `profile_page.py`) e ganho de atributos.
- Ordem de turno por velocidade/AGI.

### Fase 4: regras táticas

- Caminho real (BFS/A*) no movimento, respeitando unidades e obstáculos, com custo pelo caminho percorrido.
- Skills de área, à distância e de suporte (cura, buffs), com efeitos de status (ex.: veneno, atordoamento) e duração em turnos.
- Novos comportamentos de IA em `battle_ai.BEHAVIORS` (fugir com pouco HP, manter distância, priorizar alvos fracos).
- Drops de itens, o que depende do inventário (item já presente na sidebar, ainda sem tela).

### Fase 5: autoridade do servidor (se fizer sentido)

Se houver multijogador, ranking ou economia entre jogadores, mover a validação das ações para o backend: o cliente manda intenções ("mover para X", "usar skill em Y") e o servidor aplica as regras. `battle_actions.py` já separa validação (`can_*`) de execução (`perform_*`), o que facilita levar essa lógica para o servidor.

## Limpezas pequenas (a qualquer momento)

- Remover o ramo de unidades sem sheet em `battle_board.py`.
- Usar `JobModel` como fonte única de `sheet` e `avatar`, por exemplo expondo os jobs numa rota `GET /jobs`, e aposentar `JOBS_SHEETS`/`JOBS_BADGES`.
- O TODO em `BattleState.closed` ("Check if its necessary"): a flag é necessária, porque é o que para `turn_loop` e `anim_loop` ao sair da tela.
