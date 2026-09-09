"""持久化层：负责把模型对象读写成 JSON，依赖 models 里的类型。"""

import json
from pathlib import Path

from models import Item, Player, Quest, Slot


class PlayerRepository:
    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path else Path(__file__).parent / "data" / "player_save.json"

    def load(self, items: dict[str, Item]) -> Player | None:
        if not self.path.exists():
            return None
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        inventory = [items[name] for name in raw["inventory"] if name in items]
        equipped = {
            Slot(slot): items[name]
            for slot, name in raw.get("equipped", {}).items()
            if name in items
        }
        return Player(name=raw["name"], level=raw.get("level", 1), hp=raw["hp"],
                  attack=raw["attack"],
                      defense=raw["defense"], inventory=inventory, equipped=equipped,
                      completed_quests=raw.get("completed_quests", []))
    def save(self, player: Player) -> None:
        data = {
            "name": player.name,
            "level": player.level,
            "hp": player.hp,
            "attack": player.attack,
            "defense": player.defense,
            "inventory": [i.name for i in player.inventory],
            "equipped": {s.value: (it.name if it else None) for s, it in player.equipped.items()},
            "completed_quests": player.completed_quests,
        }
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_items(path: str) -> list[Item]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return [Item(name=i["name"], slot=Slot(i["slot"]), attack=i.get("attack", 0),
                 defense=i.get("defense", 0)) for i in raw["items"]]


def load_quests(path: str) -> list[Quest]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return [Quest(fid=q["id"], title=q["title"], reward_gold=q["gold"],
                  reward_exp=q["exp"], required_item=q.get("required_item"))
            for q in raw["quests"]]

