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

Cada item aparece com o ícone (`icon`, 24×24 desenhado em cerca de 1,6×, 38 px) e, em pilhas, a quantidade no canto. Passar o mouse mostra o nome e a quantidade.

## Detalhes do item

A descrição do item abre num pop up (`components/item_details_dialog.py`) com a imagem de coleção (`collection`, 75×100 desenhada em 1,5×), o nome, o tipo, a quantidade (em pilhas) e a descrição. Há dois jeitos de abrir:

- **Botão direito** sobre o item.
- **Clicar** no item para selecioná-lo (o slot ganha borda dourada; clicar de novo desmarca) e apertar o botão **Details**: só um ícone de livro, sem texto, no canto inferior esquerdo, abaixo da bolsa. Sem item selecionado, o botão não faz nada. A seleção acompanha o item quando ele é arrastado.

## Arrastar itens

Todo item, na bolsa ou equipado, pode ser arrastado para outro slot:

- **Slot vazio**: o item vai para lá.
- **Slot ocupado**: os dois itens trocam de lugar.
- **Slot de equipamento**: só aceita itens do tipo certo. Se o item não couber, ou se a troca mandaria para um slot de equipamento um item que não cabe nele, o item volta para onde estava.

| Slot | Aceita o `type` |
|---|---|
| `head` | Helmet |
| `armor` | Armor |
| `right_hand` | armas: Sword, Rod, Axe, Dagger, Mace, Spear, Bow |
| `left_hand` | armas e Shield |
| `garment` | Cape |
| `shoes` | Boots |
| `accessory_1`, `accessory_2` | Accessory |
| `bag_0` … `bag_39` | qualquer item |

Hoje só existem itens Misc, então os slots de equipamento ainda não aceitam nada.

A regra está em `backend/core/inventory_rules.py` (`EQUIP_SLOTS`, `can_hold`), e o frontend tem uma cópia em `frontend/services/inventory_service.py`. Ao soltar o item, a tela move na hora (`move_entries`), envia o movimento ao backend e, quando a resposta chega, desenha o inventário salvo. Se o backend recusar, a tela recarrega o inventário.

Equipar ainda **não muda atributos** nem o sprite do personagem; por enquanto só guarda onde cada item está.

## Itens

Cada item (`items`, `ItemModel`, definido em `ITEMS` no `seed_data.py`) tem:

| Atributo | Coluna | Observação |
|---|---|---|
| Nome | `name` | |
| Tipo | `type` | só **Misc** (miscelânea) por enquanto; depois virão Helmet, Armor, Cape, Boots, Sword, Rod, Axe… |
| Descrição | `description` | aparece no pop up de detalhes |
| Taxa de drop | `drop_rate` | chance em porcentagem (70 = 70%) de o item cair de um monstro que o dropa |

E dois assets em `assets/items/<id>/`: `icon.png` (24×24, o ícone da bolsa) e `collection.png` (75×100, a imagem dos detalhes).

Itens atuais (todos drops do Poring):

| Item | Tipo | Taxa de drop |
|---|---|---|
| Jellopy | Misc | 70% |
| Empty Bottle | Misc | 15% |
| Apple | Misc | 2% |
| Poring Card | Misc | 0,2% |

Toda carta de monstro usa a taxa de **0,2%** (`CARD_DROP_RATE`, em `backend/core/drop_rules.py`).

`character_items` (`CharacterItemModel`) guarda cada item de um personagem, com `slot` e `amount`. O par (personagem, slot) é único. Itens Misc se empilham: um drop de um item que já está na bolsa soma na mesma pilha.

Personagens começam com a bolsa vazia. Itens que saem de `ITEMS` são apagados pelo seed, inclusive das bolsas.

## Drops

`monster_drops` (`MonsterDropModel`) diz quais itens cada monstro dropa (a lista `drops` do monstro em `MONSTERS`, no seed). A chance é a `drop_rate` do item.

Numa **vitória**, o backend (`POST /characters/{id}/battle-result`) sorteia, para **cada monstro morto**, **cada item** que ele dropa, uma vez (`roll_drops`, em `core/drop_rules.py`). Exemplo: 3 Porings fazem 3 sorteios de Jellopy a 70%, 3 de Empty Bottle a 15% etc. Os itens que caem vão para a bolsa (`give_item`, em `core/inventory.py`): primeiro para a pilha que já existe, senão para o primeiro slot livre. Se a bolsa estiver cheia, o item se perde.

Derrota e Leave não dão itens.

O pop up de resultado da vitória lista os itens em **Items** (ícone, nome e quantidade), ou "No items dropped". O que não coube aparece em "Bag full, left behind".

## Rotas

- `GET /api/v1/characters/{id}/inventory`: lista os itens com seus slots.
- `POST /api/v1/characters/{id}/inventory/move`: `{ "from_slot": "bag_0", "to_slot": "right_hand" }`. Veja [Endpoints do backend](endpoints-backend.md#inventário-apiv1endpointsinventorypy).

## Arquivos

| Arquivo | Papel |
|---|---|
| `frontend/pages/inventory_page.py` | A tela: bolsa, equipamentos, arrastar e soltar (`ft.Draggable` / `ft.DragTarget`), seleção, botão Details e botão direito (`ft.GestureDetector`) |
| `frontend/components/item_details_dialog.py` | Pop up de detalhes do item |
| `frontend/services/inventory_service.py` | Chamadas à API, cópia da regra dos slots, movimento local |
| `backend/api/v1/endpoints/inventory.py` | Rotas de leitura e de movimento |
| `backend/core/inventory_rules.py` | Tamanho da bolsa, slots de equipamento, tipos que empilham, primeiro slot livre |
| `backend/core/inventory.py` | `give_item`: coloca itens na bolsa |
| `backend/core/drop_rules.py` | `roll_drops` e `CARD_DROP_RATE` |
| `backend/models/items_model.py`, `character_item_model.py`, `monster_drop_model.py` | Tabelas `items`, `character_items` e `monster_drops` |
| `assets/items/<id>/` | `icon.png` e `collection.png` de cada item |
