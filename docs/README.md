# Documentação do Ragnarok Chaos Saga

Ragnarok Chaos Saga é um RPG de desktop com tema de Ragnarok Online. O projeto tem dois processos Python que conversam por HTTP:

- **`backend/`**: API em FastAPI com SQLAlchemy assíncrono e SQLite. Guarda personagens, mapas, monstros, jobs e skills.
- **`frontend/`**: app de desktop em Flet 0.86, com componentes declarativos (`@ft.component`, `ft.use_state`) e rotas (`ft.Router`).

## Por onde começar

| Documento | O que explica |
|---|---|
| [Arquitetura geral](arquitetura.md) | Pastas, responsabilidades de cada parte, como rodar o projeto, assets |
| [Integração frontend/backend](integracao-frontend-backend.md) | Como o app chama a API, `ApiClient`, services, estado de sessão, fluxo de telas |
| [Endpoints do backend](endpoints-backend.md) | Cada rota da API, parâmetros, respostas e erros |
| [Modelo de dados](modelo-de-dados.md) | Tabelas, relacionamentos, `seed_data.py`, como mudar o schema |
| [Criação e seleção de personagens](personagens.md) | Criar, listar e escolher personagens; perfil; o que ainda falta |
| [Mapas e navegação](mapas-e-navegacao.md) | Rotas de mapa, tela de mapa, botão Hunt, navegação entre mapas |
| [Sistema de combate](sistema-de-combate.md) | Como a batalha funciona hoje: estado, turnos, ações, IA, tabuleiro |
| [Sprites e animação](sprites-e-animacao.md) | Pipeline `.spr`/`.act` → sprite sheet, formato do JSON, como os frames são desenhados |
| [Roadmap do combate](roadmap-combate.md) | O que existe, o que falta e uma proposta de ordem para evoluir o combate |

## Resumo em uma frase por camada

- **Dados**: definidos em `backend/seed_data.py` e gravados em `backend/ragnarokcs.db`. Não há painel de administração nem migrações.
- **API**: `/api/v1/characters`, `/api/v1/maps` e `/api/v1/battles` na porta **8001**.
- **App**: telas em `frontend/pages/`, peças visuais em `frontend/components/`, lógica e chamadas HTTP em `frontend/services/`.
- **Batalha**: o backend monta o encontro (herói + monstro), e o frontend roda o combate inteiro localmente.
