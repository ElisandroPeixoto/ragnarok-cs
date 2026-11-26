"""Schemas of the management (admin) API, see docs/gerenciamento.md"""
from typing import Optional
from pydantic import BaseModel, Field


class AdminCharacterUpdate(BaseModel):
    """Every field is optional: only what is sent changes. `level` sets the total EXP to the start of that level"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    job: Optional[str] = None
    level: Optional[int] = Field(default=None, ge=1)
    exp: Optional[int] = Field(default=None, ge=0)
    zeny: Optional[int] = Field(default=None, ge=0)
    hp: Optional[int] = Field(default=None, ge=0)
    max_hp: Optional[int] = Field(default=None, ge=1)
    max_sp: Optional[int] = Field(default=None, ge=0)
    current_map_id: Optional[str] = None


class AdminMonsterUpdate(BaseModel):
    sheet: Optional[str] = None
    ai: Optional[str] = None
    level: Optional[int] = Field(default=None, ge=1)
    base_exp: Optional[int] = Field(default=None, ge=0)
    max_hp: Optional[int] = Field(default=None, ge=1)
    max_ap: Optional[int] = Field(default=None, ge=0)
    drops: Optional[list[str]] = None   # item ids; replaces the monster's whole drop list


class AdminJobUpdate(BaseModel):
    sheet: Optional[str] = None
    avatar: Optional[str] = None
    max_ap: Optional[int] = Field(default=None, ge=0)


class AdminItemUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    type: Optional[str] = None
    description: Optional[str] = None
    drop_rate: Optional[float] = Field(default=None, ge=0, le=100)


class SpriteUpload(BaseModel):
    """A sprite sheet made by tools/ro_to_sheet.py: the PNG (base64) and its JSON. The JSON's "src" is rewritten
    to the folder the sheet is saved in"""
    sheet_png_base64: str
    sheet_json: dict
