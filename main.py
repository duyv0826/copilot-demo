""".py 项目入口：命令行演示整个装备与任务流程。"""

from pathlib import Path

from models import Player
import service
from storage import PlayerRepository

HERE = Path(__file__).parent


def main() -> None:
    player_repository = PlayerRepository()
    svc = service.GameService(HERE / "data" / "items.json", HERE / "data" / "quests.json",
                              player_repository)
    player = svc.load_player()
    is_new = player is None
    if is_new:
        player = Player(name="Mario")
        svc.give_item(player, "木剑")
        svc.give_item(player, "铁盾")

    svc.equip(player, "木剑")
    svc.drop_item(player, "铁盾")
    print(f"{player.name} 装备了: {[(s.value, i.name) for s, i in player.equipped.items()]}")
    print(f"背包剩余: {[i.name for i in player.inventory]}")

    quest = svc.quests[0]
    if quest.fid not in player.completed_quests:
        print(f"接取任务: {quest.title}（需要上缴 {quest.required_item}）")
        ok = svc.try_complete_quest(player, quest)
        print(f"任务完成: {ok}，等级 -> {player.level}，攻击力 -> {player.attack}，防御力 -> {player.defense}")
    else:
        print(f"[读档] {player.name} Lv.{player.level}，任务 {quest.title} 已完成，无新结算")

    player_repository.save(player)
    print("玩家数据已保存。")


if __name__ == "__main__":
    main()