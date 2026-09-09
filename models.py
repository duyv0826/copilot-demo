"""领域模型：本项目的所有数据类都定义在这里，供其他模块引用。"""

from dataclasses import dataclass, field
from enum import Enum


class Slot(str, Enum):
    HEAD = "head"
    BODY = "body"
    HAND = "hand"
    ACCESSORY = "accessory"


@dataclass
class Item:
    name: str
    slot: Slot
    attack: int = 0
    defense: int = 0


@dataclass
class Player:
    name: str
    level: int = 1
    hp: int = 100
    attack: int = 10
    defense: int = 5
    inventory: list[Item] = field(default_factory=list)
    equipped: dict[Slot, Item] = field(default_factory=dict)
    completed_quests: list[str] = field(default_factory=list)


@dataclass
class Quest:
    fid: str
    title: str
    reward_gold: int
    reward_exp: int
    required_item: str | None = None
    completed: bool = False