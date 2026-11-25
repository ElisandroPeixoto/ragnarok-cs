# Inventário

A tela **Inventory** (`/inventory`) mostra o que o personagem carrega. Abre pelo botão "Inventory" do sidebar.

## Layout

- No topo, à esquerda, o título "Inventory".
- **Esquerda: a bolsa.** 8 linhas × 5 colunas = 40 slots, numerados da esquerda para a direita, de cima para baixo (`bag_0` é o canto superior esquerdo, `bag_39` o inferior direito). Abaixo dos slots, no canto inferior direito, o zeny do personagem: só o ícone e o valor, sem a moldura do badge (`zeny_amount`).
- **Direita: os equipamentos.** O sprite do personagem de pé, de frente (clip `stand_s`, o mesmo do perfil), com 4 slots de cada lado:

| Lado esquerdo | Lado direito |
|---|---|
| Head (`head`) | Garment (`garment`, capa) |
| Armor (`armor`) | Shoes (`shoes`) |
| Right Hand (`right_hand`) | Left Hand (`left_hand`) |
| Accessory 1 (`accessory_1`) | Accessory 2 (`accessory_2`) |

O personagem está de frente para o jogador, por isso a mão direita fica do lado esquerdo da tela.

Cada item aparece com o ícone (ou um ícone genérico do tipo, enquanto não houver arte) e, em pilhas, a quantidade no canto. Passar o mouse mostra nome, quantidade e descrição.

## Arrastar itens

Todo item, na bolsa ou equipado, pode ser arrastado para outro slot:

- **Slot vazio**: o item vai para lá.
- **Slot ocupado**: os dois itens trocam de lugar.
- **Slot de equipamento**: só aceita itens do tipo certo. Se o item não couber, ou se a troca mandaria para um slot de equipamento um item que não cabe nele, o item volta para onde estava.

| Slot | Aceita `equip_type` |
|---|---|
| `head` | `head` |
| `armor` | `armor` |
| `right_hand` | `weapon` |
| `left_hand` | `weapon`, `shield` |
| `garment` | `garment` |
| `shoes` | `shoes` |
| `accessory_1`, `accessory_2` | `accessory` |
| `bag_0` … `bag_39` | qualquer item |

A regra está em `backend/core/inventory_rules.py` (`EQUIP_SLOTS`, `can_hold`), e o frontend tem uma cópia em `frontend/services/inventory_service.py`. Ao soltar o item, a tela move na hora (`move_entries`), envia o movimento ao backend e, quando a resposta chega, desenha o inventário salvo. Se o backend recusar, a tela recarrega o inventário.

Equipar ainda **não muda atributos** nem o sprite do personagem; por enquanto só guarda onde cada item está.

## Dados

- `items` (`ItemModel`): o catálogo de itens, definido em `ITEMS` no `seed_data.py`. Hoje: Knife (`weapon`), Cotton Shirt (`armor`) e Red Potion (`usable`, não equipável).
- `character_items` (`CharacterItemModel`): cada item de um personagem, com `slot` e `amount`. O par (personagem, slot) é único.

Itens iniciais (`STARTER_ITEMS`): todo personagem novo começa com 1 Knife, 1 Cotton Shirt e 5 Red Potions nos primeiros slots da bolsa. O seed dá esses itens, uma vez, aos personagens antigos que ainda não têm nenhum item.

Itens vindos de drops e de compras em lojas ainda não existem.

## Rotas

- `GET /api/v1/characters/{id}/inventory`: lista os itens com seus slots.
- `POST /api/v1/characters/{id}/inventory/move`: `{ "from_slot": "bag_0", "to_slot": "right_hand" }`. Veja [Endpoints do backend](endpoints-backend.md#inventário-apiv1endpointsinventorypy).

## Arquivos

| Arquivo | Papel |
|---|---|
| `frontend/pages/inventory_page.py` | A tela: bolsa, equipamentos, arrastar e soltar (`ft.Draggable` / `ft.DragTarget`) |
| `frontend/services/inventory_service.py` | Chamadas à API, cópia da regra dos slots, movimento local |
| `backend/api/v1/endpoints/inventory.py` | Rotas de leitura e de movimento |
| `backend/core/inventory_rules.py` | Tamanho da bolsa, slots de equipamento, itens iniciais |
| `backend/models/items_model.py`, `character_item_model.py` | Tabelas `items` e `character_items` |
