from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.character_model import CharacterModel
from schemas.character_schema import CharacterSchemaCreate, CharacterSchemaResponse
from core.deps import get_session
from typing import List


router = APIRouter()


# POST Character
"""Create a new character"""
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CharacterSchemaResponse)
async def post_character(character: CharacterSchemaCreate, db: AsyncSession = Depends(get_session)):
    new_character : CharacterModel = CharacterModel(
        name=character.name
    )

    db.add(new_character)
    await db.commit()
    await db.refresh(new_character)

    return new_character


# GET Character
"""Retrieve all the characters"""
@router.get("/", status_code=status.HTTP_200_OK, response_model=List[CharacterSchemaResponse])
async def get_characters(db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(CharacterModel)
        result = await session.execute(query)
        characters: List[CharacterModel] = result.scalars().unique().all()  # noqa

        return characters


# GET Character by ID
@router.get("/{character_id}", status_code=status.HTTP_200_OK, response_model=CharacterSchemaResponse)
async def get_character_by_id(character_id: int, db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(CharacterModel).where(CharacterModel.id == character_id)  # noqa
        result = await session.execute(query)
        character: CharacterModel | None = result.scalars().unique().one_or_none()

        if character is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Character not found"
            )

        return character
