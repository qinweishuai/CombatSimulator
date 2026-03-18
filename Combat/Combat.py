#!/usr/bin/python3

import random

from Combat.Data.ServantData import StzbServant
from Combat.Data.SkillData import StzbSkill
from Combat import gol

# ── Default team configurations ───────────────────────────────────────────────
TeamA_Config = [10001, 10002, 10003]
TeamB_Config = [10004, 10005, 10006]

# ── Position labels ───────────────────────────────────────────────────────────
_POSITION_LABEL_A = {1: "前锋", 2: "中军", 3: "大营"}
_POSITION_LABEL_B = {4: "前锋", 5: "中军", 6: "大营"}
_TEAM_LABEL = {1: "甲方", 2: "乙方"}


# ── Helper: check whether an entire team has been defeated ────────────────────
def CheckTeamFail(team_array):
    """Return True if every member in *team_array* has 0 HP."""
    return all(m.GetServantPower() <= 0 for m in team_array)


# ── Distance calculation ──────────────────────────────────────────────────────
def GetRelativePosition(member):
    """
    Normalise the raw position to a 0-indexed distance from the front line.

    Team A uses raw positions 1/2/3 → relative 0/1/2.
    Team B uses raw positions 4/5/6 → relative 0/1/2.
    """
    if member.team_id == 1:
        return member.position - 1
    else:
        return member.position - 4


def CalculateDistance(member_a, member_b):
    """
    Calculate the distance between two TeamMembers according to the rules:

    - Same team  : abs(rel_a - rel_b)            (0 = same slot)
    - Enemy team : rel_a + rel_b + 1             (front vs front = 1;
                                                   base  vs base  = 5)
    """
    rel_a = GetRelativePosition(member_a)
    rel_b = GetRelativePosition(member_b)
    if member_a.team_id == member_b.team_id:
        return abs(rel_a - rel_b)
    return rel_a + rel_b + 1


# ── State marker (future use) ─────────────────────────────────────────────────
class ServantState:
    state_id = 1
    left_turn = 1


# ── TeamMember ────────────────────────────────────────────────────────────────
class TeamMember:
    """
    A deployed unit on the battlefield.

    Parameters
    ----------
    _ServantConfigID : int
        Row ID in servant.csv.
    _ServantLevel : int
        Current level, used to scale stats.
    _TeamID : int
        1 = Team A, 2 = Team B.
    _Position : int
        1/2/3 for Team A (前锋/中军/大营), 4/5/6 for Team B.
    skill_ids : list[int] | None
        Optional list of up to two additional skill IDs for slots 2 and 3.
    """

    def __init__(self, _ServantConfigID, _ServantLevel, _TeamID, _Position,
                 skill_ids=None):
        self.servant = StzbServant(_ServantConfigID, _ServantLevel)
        self.team_id = _TeamID
        self.position = _Position
        self.relative_position = GetRelativePosition(self)

        # HP
        self.max_power = self.servant.health
        self.power = self.servant.health

        # Build skill slots: [main_skill, second_skill, third_skill]
        DB = gol.get_value("DataBase")
        main_id = self.servant.main_skill_id
        self.skills = [
            StzbSkill(main_id, 1, DB.GetSkillInfoByConfigID(main_id))
        ]
        extra = skill_ids or []
        for sid in extra[:2]:
            if sid and sid > 0:
                self.skills.append(StzbSkill(sid, 1, DB.GetSkillInfoByConfigID(sid)))
            else:
                self.skills.append(None)
        while len(self.skills) < 3:
            self.skills.append(None)

    # ── Accessors ──────────────────────────────────────────────────────────────
    def GetServantAtk(self):
        return self.servant.attack

    def GetServantDef(self):
        return self.servant.defense

    def GetServantName(self):
        return self.servant.name

    def GetServantLevel(self):
        return self.servant.level

    def GetServantSpeed(self):
        return self.servant.speed

    def GetServantTactics(self):
        return self.servant.tactics

    def GetServantBasicRange(self):
        return self.servant.basic_attack_range

    def GetServantPower(self):
        return self.power

    def SetServantPower(self, _Power):
        self.power = max(0, min(_Power, self.max_power))

    def GetPositionName(self):
        if self.team_id == 1:
            return _POSITION_LABEL_A.get(self.position, "未知")
        return _POSITION_LABEL_B.get(self.position, "未知")

    # ── Combat helpers ─────────────────────────────────────────────────────────
    def TakeDamage(self, damage):
        """Apply *damage* (minimum 1) and return the actual amount dealt."""
        actual = max(1, int(damage))
        self.power = max(0, self.power - actual)
        return actual

    def Heal(self, amount):
        """Heal up to *amount* HP (capped at max) and return actual amount."""
        actual = min(int(amount), self.max_power - self.power)
        self.power = min(self.max_power, self.power + int(amount))
        return actual

    def TickSkillCooldowns(self):
        """Decrease all skill cooldowns by 1 at end of turn."""
        for skill in self.skills:
            if skill is not None:
                skill.TickCooldown()


# ── Targeting helpers ─────────────────────────────────────────────────────────
def GetValidSkillTargets(caster, alive_allies, alive_enemies, skill):
    """
    Return a list of randomly chosen targets for *skill* cast by *caster*.

    Respects target_type (1=enemy / 2=ally / 3=all), effect_radius, and
    target_num.  Returns [] when no valid target exists within range.
    """
    if skill.target_type == 1:
        pool = alive_enemies
    elif skill.target_type == 2:
        pool = alive_allies
    else:
        pool = alive_allies + alive_enemies

    candidates = [
        t for t in pool
        if t.GetServantPower() > 0 and CalculateDistance(caster, t) <= skill.effect_radius
    ]
    if not candidates:
        return []
    count = min(skill.target_num, len(candidates))
    return random.sample(candidates, count)


# ── Action execution ──────────────────────────────────────────────────────────
def ExecuteSkill(caster, skill, alive_allies, alive_enemies):
    """
    Attempt to cast *skill*.  Returns True if the skill was actually cast
    (valid targets found), False otherwise.
    """
    targets = GetValidSkillTargets(caster, alive_allies, alive_enemies, skill)
    if not targets:
        return False

    target_names = "、".join(t.GetServantName() for t in targets)
    print(f"  [{caster.GetServantName()}] 释放技能【{skill.name}】-> [{target_names}]")

    for target in targets:
        if skill.damage_ratio > 0:
            raw = caster.GetServantAtk() * skill.damage_ratio * 100.0 / (
                100.0 + target.GetServantDef()
            )
            dmg = target.TakeDamage(raw)
            status = "倒下！" if target.GetServantPower() <= 0 else f"剩余HP {target.GetServantPower()}/{target.max_power}"
            print(f"    -> [{target.GetServantName()}] 受到 {dmg} 伤害，{status}")

        if skill.heal_ratio > 0:
            amount = caster.GetServantTactics() * skill.heal_ratio
            healed = target.Heal(amount)
            print(f"    -> [{target.GetServantName()}] 恢复 {healed} HP，"
                  f"当前HP {target.GetServantPower()}/{target.max_power}")

    skill.SetCooldown()
    return True


def ExecuteBasicAttack(attacker, alive_enemies):
    """
    Perform a basic attack against a random enemy within basic_attack_range.
    Does nothing when no valid target exists.
    """
    basic_range = attacker.GetServantBasicRange()
    valid = [
        e for e in alive_enemies
        if e.GetServantPower() > 0 and CalculateDistance(attacker, e) <= basic_range
    ]
    if not valid:
        print(f"  [{attacker.GetServantName()}] 没有射程内的敌方目标，跳过普攻")
        return

    target = random.choice(valid)
    raw = attacker.GetServantAtk() * 100.0 / (100.0 + target.GetServantDef())
    dmg = target.TakeDamage(raw)
    status = "倒下！" if target.GetServantPower() <= 0 else f"剩余HP {target.GetServantPower()}/{target.max_power}"
    print(f"  [{attacker.GetServantName()}] 普攻 -> [{target.GetServantName()}] "
          f"造成 {dmg} 伤害，{status}")


# ── Main simulation loop ──────────────────────────────────────────────────────
def CombatSimulate(TeamA, TeamB):
    print("\n=== 战斗开始 ===\n")
    turn = 0
    max_turns = 50  # Safety cap to prevent infinite loops

    while not (CheckTeamFail(TeamA) or CheckTeamFail(TeamB)) and turn < max_turns:
        turn += 1
        print(f"\n{'='*40}")
        print(f"  【第 {turn} 回合】")
        print(f"{'='*40}")

        # Sort all living members by speed (descending) for this turn's order
        alive_all = [m for m in TeamA + TeamB if m.GetServantPower() > 0]
        alive_all.sort(key=lambda x: x.GetServantSpeed(), reverse=True)

        order_str = " → ".join(
            f"{m.GetServantName()}({m.GetServantSpeed():.0f})" for m in alive_all
        )
        print(f"行动顺序: {order_str}\n")

        for member in alive_all:
            if member.GetServantPower() <= 0:
                continue  # May have been killed earlier this turn

            team_label = _TEAM_LABEL[member.team_id]
            pos_label = member.GetPositionName()
            print(f"[{team_label}·{pos_label}] {member.GetServantName()} 行动 "
                  f"(HP:{member.GetServantPower()}/{member.max_power})")

            # Resolve allies and living enemies for this action
            if member.team_id == 1:
                alive_allies = [m for m in TeamA if m.GetServantPower() > 0]
                alive_enemies = [m for m in TeamB if m.GetServantPower() > 0]
            else:
                alive_allies = [m for m in TeamB if m.GetServantPower() > 0]
                alive_enemies = [m for m in TeamA if m.GetServantPower() > 0]

            # 1. Attempt to cast skills (prioritise in slot order; cast first ready skill)
            skill_cast = False
            for skill in member.skills:
                if skill is None or not skill.IsReady():
                    continue
                if skill.skill_type == 2:  # Passive – not triggered here
                    continue
                if ExecuteSkill(member, skill, alive_allies, alive_enemies):
                    skill_cast = True
                    break  # One skill per turn

            # 2. Perform basic attack (only if the caster is still alive)
            if member.GetServantPower() > 0:
                ExecuteBasicAttack(member, alive_enemies)

            # 3. Tick cooldowns at end of this member's action
            member.TickSkillCooldowns()

        # End-of-turn status
        a_alive = [m for m in TeamA if m.GetServantPower() > 0]
        b_alive = [m for m in TeamB if m.GetServantPower() > 0]
        print(f"\n--- 回合 {turn} 结束  甲方存活:{len(a_alive)}/3  乙方存活:{len(b_alive)}/3 ---")

    # ── Result ────────────────────────────────────────────────────────────────
    print(f"\n{'='*40}")
    print("  【战斗结束】")
    print(f"{'='*40}")
    if CheckTeamFail(TeamA) and CheckTeamFail(TeamB):
        print("双方同归于尽，平局！")
    elif CheckTeamFail(TeamA):
        print("乙方获胜！")
    elif CheckTeamFail(TeamB):
        print("甲方获胜！")
    else:
        print(f"超过 {max_turns} 回合，战斗平局！")


# ── Entry point ───────────────────────────────────────────────────────────────
def StartCombat():
    # Team A: positions 1(前锋) / 2(中军) / 3(大营)
    a1 = TeamMember(TeamA_Config[0], 50, 1, 1)              # front
    a2 = TeamMember(TeamA_Config[1], 40, 1, 2)              # middle
    a3 = TeamMember(TeamA_Config[2], 38, 1, 3)              # base  (healer)

    # Team B: positions 4(前锋) / 5(中军) / 6(大营)
    b1 = TeamMember(TeamB_Config[0], 37, 2, 4)              # front
    b2 = TeamMember(TeamB_Config[1], 45, 2, 5, [20002])     # middle – extra AoE skill
    b3 = TeamMember(TeamB_Config[2], 48, 2, 6)              # base

    TeamArrayA = [a1, a2, a3]
    TeamArrayB = [b1, b2, b3]

    # ── Pre-battle summary ────────────────────────────────────────────────────
    print("=== 战斗配置 ===")
    for label, team in [("甲方", TeamArrayA), ("乙方", TeamArrayB)]:
        print(f"\n{label}队伍:")
        for m in team:
            skill_names = [
                s.name for s in m.skills if s is not None
            ]
            print(f"  [{m.GetPositionName()}] {m.GetServantName()} "
                  f"攻:{m.GetServantAtk():.1f} 防:{m.GetServantDef():.1f} "
                  f"速:{m.GetServantSpeed():.1f} 谋:{m.GetServantTactics():.1f} "
                  f"HP:{m.max_power} 普攻范围:{m.GetServantBasicRange()} "
                  f"技能:{skill_names}")

    CombatSimulate(TeamArrayA, TeamArrayB)
