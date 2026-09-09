from pathlib import Path

from models import Player
from service import GameService


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ITEMS_PATH = PROJECT_ROOT / "data" / "items.json"
QUESTS_PATH = PROJECT_ROOT / "data" / "quests.json"


def make_service() -> GameService:
    return GameService(str(ITEMS_PATH), str(QUESTS_PATH))


def test_give_item_and_equip_puts_item_in_slot():
    service = make_service()
    player = Player("测试玩家")

    assert service.give_item(player, "木剑") is True
    assert [item.name for item in player.inventory] == ["木剑"]
    assert service.equip(player, "木剑") is True
    assert player.equipped[player.inventory[0].slot].name == "木剑"


def test_equip_returns_false_for_item_player_does_not_own():
    service = make_service()
    player = Player("测试玩家")

    assert service.equip(player, "木剑") is False
    assert player.equipped == {}


def test_complete_quest_consumes_required_item_from_inventory_and_equipment():
    service = make_service()
    player = Player("测试玩家")
    quest = next(quest for quest in service.quests if quest.fid == "q1")
    initial_attack = player.attack
    initial_defense = player.defense

    assert service.give_item(player, "木剑") is True
    assert service.equip(player, "木剑") is True
    assert service.try_complete_quest(player, quest) is True

    assert player.inventory == []
    assert player.equipped == {}
    assert quest.completed is True
    assert player.completed_quests == ["q1"]
    assert player.attack == initial_attack + quest.reward_exp
    assert player.defense == initial_defense + quest.reward_gold // 10


def test_completing_same_quest_twice_returns_false_without_second_reward():
    service = make_service()
    player = Player("测试玩家")
    quest = next(quest for quest in service.quests if quest.fid == "q1")
    service.give_item(player, "木剑")

    assert service.try_complete_quest(player, quest) is True
    attack_after_first = player.attack
    defense_after_first = player.defense

    assert service.try_complete_quest(player, quest) is False
    assert player.attack == attack_after_first
    assert player.defense == defense_after_first
    assert player.completed_quests == ["q1"]