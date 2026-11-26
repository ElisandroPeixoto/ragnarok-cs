# Painel de gerenciamento

O painel de gerenciamento (`management/`) é uma aplicação web em React (Vite) para o administrador do jogo ver e alterar os dados do backend sem mexer no código. Ele roda no navegador, em `http://localhost:5173`, e grava direto no banco do jogo (`backend/ragnarokcs.db`) pela API de administração.

## Como rodar

Na raiz do projeto:

```powershell
.\run-management.ps1
```

O script:

1. Sobe o backend na porta 8001, numa janela separada. Se ele já estiver no ar, reaproveita.
2. Na primeira vez, roda `npm install` em `management/`. Precisa do Node.js instalado.
3. Roda o painel (`npm run dev`) e abre o navegador. Com `-NoBrowser`, não abre o navegador.

Fechar o painel (Ctrl+C) também derruba o backend que o script subiu.

Sem o script: suba o backend (`cd backend && python main.py`) e, em `management/`, rode `npm install` uma vez e depois `npm run dev`.

## O que dá para fazer

A tela tem duas colunas: à esquerda, o menu principal, com um ícone simples e a contagem de cada página; à direita, maior, o conteúdo da página escolhida. Nesse conteúdo, a lista vem em cima e o painel de detalhes do que foi selecionado vem embaixo, com as seções lado a lado quando há espaço. Selecionar algo na lista rola a tela até os detalhes, se eles estiverem fora da vista. Os campos alterados só são gravados no **Save**, e o **Discard** desfaz as mudanças. Um aviso no canto da tela confirma o salvamento ou mostra o erro do backend.

| Página | Lista | O que se edita |
|---|---|---|
| **Characters** | todos os personagens, com busca por nome ou classe | nome, classe, mapa atual, level, zeny, HP, Max HP e Max SP |
| **Monsters** | cards com o monstro animado (clip `idle_sw`) | sprite sheet, **modo de combate**, level, EXP base, Max HP, Max AP e a **lista de drops** |
| **Classes** | os jobs, com o personagem animado (`stand_s`) | sprite sheet, Max AP e avatar da batalha |
| **Items & Drops** | grade de slots, como o inventário, com a taxa de cada item | **taxa de drop**, nome, tipo e descrição; mostra quais monstros dropam o item |
| **Sprite Sheets** | as sheets em `assets/sprites/characters/` e `assets/sprites/monsters/` | toca qualquer clip, mostra a sheet inteira e envia sheets novas |

Detalhes:

- **Level do personagem**: o nível sai da EXP total ([Progressão de level](progressao-de-level.md)), então mudar o level põe a EXP no início daquele nível. O HP nunca fica acima do Max HP.
- **Contas**: o jogo ainda não tem contas. Por enquanto a página Characters lista todos os personagens.
- **Modos de combate**: são os comportamentos de `frontend/services/battle_ai.py`. **Approach and attack** (`approach_and_attack`) anda até o inimigo mais próximo e ataca quando alcança. **Attack only** (`attack_every_turn`) não se move e ataca quem estiver no alcance. **Passive** (`passive`) não faz nada. A lista vem de `AI_MODES`, em `backend/api/v1/endpoints/admin.py`, e um modo novo precisa existir nos dois lugares.
- **Drops**: a lista de itens que o monstro dropa fica no monstro. A **taxa** é do item e vale para todo monstro que o dropa ([Inventário](inventario.md#drops)).
- **Sprite sheets**: qual sheet um monstro ou uma classe usa se escolhe nas páginas Monsters e Classes, com prévia animada. Para enviar uma sheet nova, gere o PNG e o JSON com `tools/ro_to_sheet.py` e use o formulário "Upload a sheet": grupo (Monsters ou Classes), nome (letras minúsculas, números e `_`) e os dois arquivos. Um nome que já existe substitui a sheet. O backend corrige o `src` do JSON para a pasta certa.

## Atenção: o seed desfaz as edições

`seed_data.py` regrava, a cada execução, os monstros, as classes, os itens e os drops com os valores do próprio script. Rodar o seed depois de editar algo no painel **volta** esses dados ao que está no seed. Os personagens não são afetados, a não ser pelos ajustes de sempre (nível pela EXP, nome do mapa).

## API de administração

Rotas em `backend/api/v1/endpoints/admin.py`, com o prefixo `/api/v1/admin`. **Não há login**: a API é pensada para a máquina do próprio jogo.

| Método | Rota | O que faz |
|---|---|---|
| GET | `/options` | modos de combate, tipos de item, classes, mapas e as sheets que existem no disco (para os selects) |
| GET | `/characters` | lista os personagens (`CharacterSchemaResponse`) |
| PATCH | `/characters/{id}` | altera só os campos enviados; `level` põe a EXP no início do nível |
| GET | `/monsters` | monstros com `drops` (ids dos itens) |
| PATCH | `/monsters/{id}` | `sheet`, `ai`, `level`, `base_exp`, `max_hp`, `max_ap`; `drops` substitui a lista inteira |
| GET / PATCH | `/jobs`, `/jobs/{name}` | `sheet`, `avatar`, `max_ap` |
| GET / PATCH | `/items`, `/items/{id}` | `name`, `type`, `description`, `drop_rate` (0 a 100); a resposta traz `dropped_by` |
| GET | `/sprites` | cada sheet do disco com o JSON dela |
| POST | `/sprites/{group}/{name}` | `{ "sheet_png_base64", "sheet_json" }`: grava `assets/sprites/<group>/<name>/` |

Valores inválidos voltam com **422** e uma mensagem: classe, mapa ou sheet que não existe, modo de combate desconhecido, item de drop desconhecido, nome de sheet inválido, arquivo que não é PNG ou JSON sem `frame_w`, `frame_h`, `anchor_x`, `anchor_y` ou `clips`.

O backend também serve a pasta `assets/` em `/assets/...`. É assim que o painel mostra ícones, sprites e imagens de coleção.

## Como o painel é feito

| Arquivo | Papel |
|---|---|
| `management/vite.config.js` | servidor na porta 5173; repassa `/api` e `/assets` para o backend (8001), então não precisa de CORS |
| `management/src/api.js` | chamadas à API de administração e `assetUrl` |
| `management/src/App.jsx` | carrega tudo, menu lateral com as contagens, avisos de salvamento |
| `management/src/pages/` | uma página por seção (Characters, Monsters, Classes, Items, Sprites) |
| `management/src/components/Window.jsx` | a "janela" no estilo do jogo: cabeçalho com ícone, título e subtítulo, corpo e rodapé |
| `management/src/components/Icons.jsx` | ícones de linha em SVG do menu e das janelas (pessoas, monstro, escudo, caixa, imagem, engrenagem) |
| `management/src/components/SpritePreview.jsx` | toca um clip da sheet com CSS (`background-position`) no fps do clip |
| `management/src/components/Fields.jsx` | campos em linhas "rótulo … valor", barra Save/Discard e `changedFields` (o PATCH leva só o que mudou) |
| `management/src/styles.css` | tema claro, inspirado na janela de inventário e de detalhes do item do cliente do jogo |

Dependências: só `react`, `react-dom`, `vite` e `@vitejs/plugin-react`, com versões fixas no `package.json`. `node_modules/` e `dist/` ficam fora do git.
