from pathlib import Path

from models import Player, Slot
from service import GameService
from storage import PlayerRepository


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ITEMS_PATH = PROJECT_ROOT / "data" / "items.json"
QUESTS_PATH = PROJECT_ROOT / "data" / "quests.json"


def test_save_then_load_restores_player_state(tmp_path):
    service = GameService(str(ITEMS_PATH), str(QUESTS_PATH))
    repository = PlayerRepository(tmp_path / "player_save.json")
    player = Player(
        name="存档玩家",
        level=7,
        hp=83,
        attack=21,
        defense=14,
        completed_quests=["q1"],
    )
    service.give_item(player, "木剑")
    service.give_item(player, "皮甲")
    service.equip(player, "木剑")
    service.equip(player, "皮甲")

    repository.save(player)
    loaded = repository.load(service.items)

    assert loaded is not None
    assert loaded.name == player.name
    assert loaded.level == player.level
    assert loaded.hp == player.hp
    assert loaded.attack == player.attack
    assert loaded.defense == player.defense
    assert [item.name for item in loaded.inventory] == ["木剑", "皮甲"]
    assert {slot: item.name for slot, item in loaded.equipped.items()} == {
        Slot.HAND: "木剑",
        Slot.BODY: "皮甲",
    }
    assert loaded.completed_quests == ["q1"]


def test_load_returns_none_when_save_file_does_not_exist(tmp_path):
    repository = PlayerRepository(tmp_path / "missing_save.json")

    assert repository.load({}) is None