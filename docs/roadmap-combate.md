# Roadmap do sistema de combate

Este documento separa o que **já funciona**, o que é **lacuna conhecida** (encontrada lendo o código) e uma **proposta de evolução** por fases. As fases são sugestões de ordem, não decisões tomadas: servem de ponto de partida para planejar.

Detalhes do funcionamento atual estão em [Sistema de combate](sistema-de-combate.md).

## Estado atual

| Área | Situação |
|---|---|
| Montagem do encontro | ✅ `POST /api/v1/battles/` traz o herói e o pool de monstros do mapa; o frontend sorteia ondas infinitas (a cada 3 rodadas, `spawn_rate` do mapa, peso por monstro) |
| Dados de herói e monstro | ✅ vêm do banco (`JobModel`, `MonsterModel`, `SkillModel`); o antigo `mockup.py` foi removido |
| Posições iniciais | ✅ sorteadas em `spawn_units` (jogador na coluna 0, inimigos nas colunas 7–9) |
| Turnos | ✅ ordem fixa (herói, depois os monstros), 30 s por turno, AP recarregado a cada turno |
| Movimento | ✅ clique no tile; anda pelo caminho mais curto (BFS, desvia de unidades e obstáculos) com a animação `walk`, 1 AP por tile |
| Ataque | ✅ skill selecionada + clique no inimigo; alvo em linha reta dentro do alcance; dano fixo |
| IA | ✅ `passive`, `attack_every_turn`, `approach_and_attack` |
| Animação | ✅ sprite sheets com clips por direção (idle, walk, attack, hurt, dead) |
| Derrota | ✅ detectada e exibida; ⚠️ sem consequência alguma (a caçada é infinita, não há vitória) |
| Log | ✅ registra movimento, ataques (com o dano em vermelho), derrota e fim |
| Persistência | ❌ nada volta para o backend |

## Lacunas conhecidas

Pontos encontrados no código, em ordem aproximada de impacto:

1. **O resultado não é salvo.** Vencer não dá EXP, zeny nem drops; perder não custa nada; o HP do personagem não muda. Não existe endpoint para isso.
2. **Só uma skill.** `Basic Attack` (dano 10, alcance 1) é a única skill no seed.
3. **Dano fixo.** Sem atributos, defesa, crítico, esquiva ou variação. O personagem não tem atributos (STR, AGI…) no modelo.
4. **Ordem de turno fixa.** `turn_order`: o herói sempre começa, depois os monstros na ordem em que nasceram, sem iniciativa ou velocidade.
5. **Sem obstáculos.** `BoardConfig.blocked_tiles` existe e é respeitado por movimento e spawn, mas está sempre vazio; o fundo também é sempre o mesmo.
6. **Regras duplicadas fora do servidor.** Toda a regra roda no cliente; quando houver recompensa, o backend precisa validar ou recalcular o resultado.
7. **Erros invisíveis.** Se `POST /battles/` falhar, o botão Hunt não dá nenhum retorno ao jogador.
8. **Restos do mockup.** O ramo de `battle_board.py` para unidades sem sheet usa campos (`sprite`, `width`, `height`, `placeholder_color`) que o backend nunca envia.
9. **Dados de job repetidos.** `services/sprite_selector.py` repete `sheet` e `avatar` que já existem em `JobModel`.

## Proposta de fases

### Fase 1: fechar o ciclo da batalha

Objetivo: lutar passar a ter consequência.

- Endpoint para encerrar a batalha (ex.: `POST /api/v1/battles/{id}/finish` ou `POST /api/v1/battles/result`) com o resultado e o HP final do herói.
- Gravar a batalha em uma tabela (ex.: `battles`: personagem, mapa, monstros, status) quando ela começa. Assim o backend sabe que o encontro existe e pode recusar resultados de batalhas inventadas.
- Recompensas simples por monstro (colunas `base_exp`, `zeny` em `MonsterModel`) e atualização de `CharacterModel` (`exp`, `zeny`, `hp`).
- Atualizar o personagem em `session_state` com a resposta, para o perfil mostrar os novos valores.
- Mostrar o erro quando o Hunt falhar (lacuna 7).

### Fase 2: conteúdo e variedade

- Dar a Lunatic e Wilow atributos próprios (hoje copiam os do Poring).
- Mais skills, com alcances e custos diferentes, e skills por job.
- Usar `blocked_tiles` e fundos diferentes por mapa (ex.: um campo `battle_board` em `MapModel`).

### Fase 3: atributos e fórmulas

- Atributos no personagem e no monstro (ex.: STR, AGI, VIT, DEX) e cálculo de ATK/DEF/HIT/FLEE.
- Dano calculado em vez de fixo: `damage` da skill vira um multiplicador.
- Progressão de nível: tabela de EXP por nível (substitui `MAX_EXP_DEFAULT` em `profile_page.py`) e ganho de atributos.
- Ordem de turno por velocidade/AGI.

### Fase 4: regras táticas

- Skills de área, à distância e de suporte (cura, buffs), com efeitos de status (ex.: veneno, atordoamento) e duração em turnos.
- Novos comportamentos de IA em `battle_ai.BEHAVIORS` (fugir com pouco HP, manter distância, priorizar alvos fracos).
- Drops de itens, o que depende do inventário (item já presente na sidebar, ainda sem tela).

### Fase 5: autoridade do servidor (se fizer sentido)

Se houver multijogador, ranking ou economia entre jogadores, mover a validação das ações para o backend: o cliente manda intenções ("mover para X", "usar skill em Y") e o servidor aplica as regras. `battle_actions.py` já separa validação (`can_*`) de execução (`perform_*`), o que facilita levar essa lógica para o servidor.

## Limpezas pequenas (a qualquer momento)

- Remover o ramo de unidades sem sheet em `battle_board.py`.
- Usar `JobModel` como fonte única de `sheet` e `avatar`, por exemplo expondo os jobs numa rota `GET /jobs`, e aposentar `JOBS_SHEETS`/`JOBS_BADGES`.
- O TODO em `BattleState.closed` ("Check if its necessary"): a flag é necessária, porque é o que para `turn_loop` e `anim_loop` ao sair da tela.
