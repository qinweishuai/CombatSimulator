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
_SKILL_TYPE_LABEL = {1: "主动", 2: "被动", 3: "指挥", 4: "追击"}


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


# ── Stat buff ─────────────────────────────────────────────────────────────────
class StatBuff:
    """
    A temporary or permanent stat modifier attached to a TeamMember.

    buff_type       : 'atk' | 'def' | 'tactics' | 'speed'
    value           : additive ratio (e.g. 0.3 = +30 %)
    remaining_turns : -1 = lasts the entire battle; >0 = turns remaining
    """

    def __init__(self, buff_type, value, remaining_turns):
        self.buff_type = buff_type
        self.value = value
        self.remaining_turns = remaining_turns


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

        # Stat buffs and status effects
        self.stat_buffs = []        # list[StatBuff]
        self.silence_remaining = 0  # turns of silence remaining

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
        bonus = sum(b.value for b in self.stat_buffs if b.buff_type == 'atk')
        return self.servant.attack * (1 + bonus)

    def GetServantDef(self):
        bonus = sum(b.value for b in self.stat_buffs if b.buff_type == 'def')
        return self.servant.defense * (1 + bonus)

    def GetServantName(self):
        return self.servant.name

    def GetServantLevel(self):
        return self.servant.level

    def GetServantSpeed(self):
        bonus = sum(b.value for b in self.stat_buffs if b.buff_type == 'speed')
        return self.servant.speed * (1 + bonus)

    def GetServantTactics(self):
        bonus = sum(b.value for b in self.stat_buffs if b.buff_type == 'tactics')
        return self.servant.tactics * (1 + bonus)

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

    # ── Buff / status helpers ──────────────────────────────────────────────────
    def IsSilenced(self):
        """Return True when this unit is under silence and cannot use active skills."""
        return self.silence_remaining > 0

    def ApplyStatBuff(self, buff_type, value, remaining_turns):
        """
        Attach a stat buff.  *remaining_turns* = -1 for whole-battle duration,
        or a positive integer for a fixed number of turns.
        """
        self.stat_buffs.append(StatBuff(buff_type, value, remaining_turns))

    def ApplySilence(self, turns):
        """Apply silence for *turns* turns (takes the maximum if already silenced)."""
        self.silence_remaining = max(self.silence_remaining, turns)

    def TickStates(self):
        """Tick buff durations and silence counter at end of this member's action."""
        if self.silence_remaining > 0:
            self.silence_remaining -= 1
        updated = []
        for b in self.stat_buffs:
            if b.remaining_turns == -1:
                updated.append(b)           # permanent – never expires
            else:
                b.remaining_turns -= 1
                if b.remaining_turns > 0:
                    updated.append(b)       # still has time remaining
        self.stat_buffs = updated


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

    # Duration for any buffs this skill applies (-1 = whole battle, else turns)
    buff_duration = -1 if skill.buff_turns == 0 else skill.buff_turns

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

        # ── Stat buffs ────────────────────────────────────────────────────────
        if skill.buff_atk != 0:
            target.ApplyStatBuff('atk', skill.buff_atk, buff_duration)
            sign = "+" if skill.buff_atk > 0 else ""
            print(f"    -> [{target.GetServantName()}] 攻击{sign}{skill.buff_atk * 100:.0f}%"
                  f"({'永久' if buff_duration == -1 else f'{buff_duration}回合'})")

        if skill.buff_def != 0:
            target.ApplyStatBuff('def', skill.buff_def, buff_duration)
            sign = "+" if skill.buff_def > 0 else ""
            print(f"    -> [{target.GetServantName()}] 防御{sign}{skill.buff_def * 100:.0f}%"
                  f"({'永久' if buff_duration == -1 else f'{buff_duration}回合'})")

        if skill.buff_tactics != 0:
            target.ApplyStatBuff('tactics', skill.buff_tactics, buff_duration)
            sign = "+" if skill.buff_tactics > 0 else ""
            print(f"    -> [{target.GetServantName()}] 谋略{sign}{skill.buff_tactics * 100:.0f}%"
                  f"({'永久' if buff_duration == -1 else f'{buff_duration}回合'})")

        if skill.buff_speed != 0:
            target.ApplyStatBuff('speed', skill.buff_speed, buff_duration)
            sign = "+" if skill.buff_speed > 0 else ""
            print(f"    -> [{target.GetServantName()}] 速度{sign}{skill.buff_speed * 100:.0f}%"
                  f"({'永久' if buff_duration == -1 else f'{buff_duration}回合'})")

        # ── Silence ───────────────────────────────────────────────────────────
        if skill.silence_turns > 0:
            target.ApplySilence(skill.silence_turns)
            print(f"    -> [{target.GetServantName()}] 陷入沉默 {skill.silence_turns} 回合！")

    skill.SetCooldown()
    return True


def ExecuteBasicAttack(attacker, alive_enemies):
    """
    Perform a basic attack against a random enemy within basic_attack_range.
    Returns the target that was hit, or None when no valid target exists.
    """
    basic_range = attacker.GetServantBasicRange()
    valid = [
        e for e in alive_enemies
        if e.GetServantPower() > 0 and CalculateDistance(attacker, e) <= basic_range
    ]
    if not valid:
        print(f"  [{attacker.GetServantName()}] 没有射程内的敌方目标，跳过普攻")
        return None

    target = random.choice(valid)
    raw = attacker.GetServantAtk() * 100.0 / (100.0 + target.GetServantDef())
    dmg = target.TakeDamage(raw)
    status = "倒下！" if target.GetServantPower() <= 0 else f"剩余HP {target.GetServantPower()}/{target.max_power}"
    print(f"  [{attacker.GetServantName()}] 普攻 -> [{target.GetServantName()}] "
          f"造成 {dmg} 伤害，{status}")
    return target


def ExecuteChaseSkills(attacker, alive_allies, alive_enemies):
    """
    After a basic attack, roll for each chase skill (skill_type=4).
    Each chase skill triggers independently based on its trigger_prob.
    Chase skills use their own targeting configuration.
    """
    for skill in attacker.skills:
        if skill is None or skill.skill_type != 4:
            continue
        if random.random() < skill.trigger_prob:
            print(f"  [{attacker.GetServantName()}] 触发追击技能【{skill.name}】")
            ExecuteSkill(attacker, skill, alive_allies, alive_enemies)


def ExecutePreBattleSkills(TeamA, TeamB):
    """
    Execute command (type=3) and passive (type=2) skills before combat begins,
    in descending speed order.  Command skills fire first, then passive skills.
    Neither type is blocked by silence.
    """
    all_members = TeamA + TeamB
    all_members.sort(key=lambda x: x.GetServantSpeed(), reverse=True)

    print("\n=== 开战技能阶段 ===")

    # ── Command skills (指挥技能) ─────────────────────────────────────────────
    has_command = any(
        s is not None and s.skill_type == 3
        for m in all_members for s in m.skills
    )
    if has_command:
        print("\n-- 指挥技能 --")
        for member in all_members:
            allies = TeamA if member.team_id == 1 else TeamB
            enemies = TeamB if member.team_id == 1 else TeamA
            for skill in member.skills:
                if skill is not None and skill.skill_type == 3:
                    ExecuteSkill(member, skill, allies, enemies)

    # ── Passive skills (被动技能) ─────────────────────────────────────────────
    has_passive = any(
        s is not None and s.skill_type == 2
        for m in all_members for s in m.skills
    )
    if has_passive:
        print("\n-- 被动技能 --")
        for member in all_members:
            allies = TeamA if member.team_id == 1 else TeamB
            enemies = TeamB if member.team_id == 1 else TeamA
            for skill in member.skills:
                if skill is not None and skill.skill_type == 2:
                    ExecuteSkill(member, skill, allies, enemies)


# ── Main simulation loop ──────────────────────────────────────────────────────
def CombatSimulate(TeamA, TeamB):
    print("\n=== 战斗开始 ===\n")

    # ── Pre-battle: command and passive skills ────────────────────────────────
    ExecutePreBattleSkills(TeamA, TeamB)

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
            silence_tag = " [沉默]" if member.IsSilenced() else ""
            print(f"[{team_label}·{pos_label}] {member.GetServantName()} 行动 "
                  f"(HP:{member.GetServantPower()}/{member.max_power}){silence_tag}")

            # Resolve allies and living enemies for this action
            if member.team_id == 1:
                alive_allies = [m for m in TeamA if m.GetServantPower() > 0]
                alive_enemies = [m for m in TeamB if m.GetServantPower() > 0]
            else:
                alive_allies = [m for m in TeamB if m.GetServantPower() > 0]
                alive_enemies = [m for m in TeamA if m.GetServantPower() > 0]

            # 1. Attempt to cast an active skill (type=1) –
            #    skips passive/command/chase; checks silence and trigger probability.
            skill_cast = False
            if member.IsSilenced():
                print(f"  [{member.GetServantName()}] 处于沉默状态，无法释放主动技能")
            else:
                for skill in member.skills:
                    if skill is None:
                        continue
                    if skill.skill_type != 1:   # Only active skills trigger here
                        continue
                    if not skill.IsReady():
                        continue
                    if not (random.random() < skill.trigger_prob):
                        continue                # Failed probability roll
                    if ExecuteSkill(member, skill, alive_allies, alive_enemies):
                        skill_cast = True
                        break                   # One active skill per turn

            # 2. Perform basic attack (only if the caster is still alive)
            if member.GetServantPower() > 0:
                hit_target = ExecuteBasicAttack(member, alive_enemies)

                # 3. Chase skills trigger after a successful basic attack
                if hit_target is not None and member.GetServantPower() > 0:
                    ExecuteChaseSkills(member, alive_allies, alive_enemies)

            # 4. Tick cooldowns and state durations at end of this member's action
            member.TickSkillCooldowns()
            member.TickStates()

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
    # a1 carries command skill 30001 (指挥鼓舞 – ATK buff for all allies)
    a1 = TeamMember(TeamA_Config[0], 50, 1, 1)
    # a2 carries active skill 20001 + chase skill 30003 (连击)
    a2 = TeamMember(TeamA_Config[1], 40, 1, 2, [30003])
    # a3 carries passive skill 30002 (坚韧防守 – self DEF buff) + active heal 20003
    a3 = TeamMember(TeamA_Config[2], 38, 1, 3, [20003])

    # Team B: positions 4(前锋) / 5(中军) / 6(大营)
    b1 = TeamMember(TeamB_Config[0], 37, 2, 4)
    # b2 carries active AoE skill 20002
    b2 = TeamMember(TeamB_Config[1], 45, 2, 5, [20002])
    # b3 carries active silence skill 20006 (震慑)
    b3 = TeamMember(TeamB_Config[2], 48, 2, 6, [20006])

    TeamArrayA = [a1, a2, a3]
    TeamArrayB = [b1, b2, b3]

    # ── Pre-battle summary ────────────────────────────────────────────────────
    print("=== 战斗配置 ===")
    for label, team in [("甲方", TeamArrayA), ("乙方", TeamArrayB)]:
        print(f"\n{label}队伍:")
        for m in team:
            skill_names = [
                f"{s.name}({_SKILL_TYPE_LABEL.get(s.skill_type, '?')})"
                for s in m.skills if s is not None
            ]
            print(f"  [{m.GetPositionName()}] {m.GetServantName()} "
                  f"攻:{m.GetServantAtk():.1f} 防:{m.GetServantDef():.1f} "
                  f"速:{m.GetServantSpeed():.1f} 谋:{m.GetServantTactics():.1f} "
                  f"HP:{m.max_power} 普攻范围:{m.GetServantBasicRange()} "
                  f"技能:{skill_names}")

    CombatSimulate(TeamArrayA, TeamArrayB)
