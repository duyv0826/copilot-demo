"""业务逻辑层：组合 models 与 storage，形成可供 main 调用的玩法规则。"""

from models import Item, Player, Quest
import storage


class GameService:
    def __init__(self, item_path: str, quest_path: str,
                 player_repository: storage.PlayerRepository | None = None):
        self.items = {i.name: i for i in storage.load_items(item_path)}
        self.quests = storage.load_quests(quest_path)
        self.player_repository = player_repository or storage.PlayerRepository()

    def load_player(self) -> Player | None:
        return self.player_repository.load(self.items)

    def give_item(self, player: Player, item_name: str) -> bool:
        if item_name not in self.items:
            return False
        player.inventory.append(self.items[item_name])
        return True

    def drop_item(self, player: Player, item_name: str) -> bool:
        """从背包移除一件物品；若已装备则同时卸下。不存在则返回 False。"""
        item = self.items.get(item_name)
        if not item or item not in player.inventory:
            return False
        player.inventory.remove(item)
        if player.equipped.get(item.slot) is item:
            del player.equipped[item.slot]
        return True

    def equip(self, player: Player, item_name: str) -> bool:
        for item in player.inventory:
            if item.name == item_name:
                player.equipped[item.slot] = item
                return True
        return False

    def try_complete_quest(self, player: Player, quest: Quest) -> bool:
        if quest.fid in player.completed_quests:
            return False
        need = self.items.get(quest.required_item or "")
        if need and need not in player.inventory:
            return False
        if need:
            player.inventory.remove(need)
            if player.equipped.get(need.slot) is need:
                del player.equipped[need.slot]
        quest.completed = True
        player.completed_quests.append(quest.fid)
        player.attack += quest.reward_exp
        player.defense += quest.reward_gold // 10
        return True