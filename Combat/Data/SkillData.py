#!/usr/bin/python3


class StzbSkill:
    """
    Represents a skill instance attached to a TeamMember.

    skill_type  : 1=主动(active)  2=被动(passive)  3=指挥(command)  4=追击(chase)
    target_type : 1=敌方(enemy)   2=友方(ally)      3=无限制(all)
    """

    def __init__(self, config_id, level, config_data=None):
        self.config_id = config_id
        self.level = level  # Reserved for future per-level stat scaling

        if config_data is not None:
            self.name = config_data.name
            self.skill_type = config_data.skill_type
            self.target_type = config_data.target_type
            self.target_num = config_data.target_num
            self.effect_radius = config_data.effect_radius
            self.damage_ratio = config_data.damage_ratio
            self.heal_ratio = config_data.heal_ratio
            self.cooldown = config_data.cooldown
            self.trigger_prob = config_data.trigger_prob
            self.buff_atk = config_data.buff_atk
            self.buff_def = config_data.buff_def
            self.buff_tactics = config_data.buff_tactics
            self.buff_speed = config_data.buff_speed
            self.buff_turns = config_data.buff_turns
            self.silence_turns = config_data.silence_turns
        else:
            self.name = f"技能{config_id}"
            self.skill_type = 1
            self.target_type = 1
            self.target_num = 1
            self.effect_radius = 2
            self.damage_ratio = 1.0
            self.heal_ratio = 0.0
            self.cooldown = 2
            self.trigger_prob = 1.0
            self.buff_atk = 0.0
            self.buff_def = 0.0
            self.buff_tactics = 0.0
            self.buff_speed = 0.0
            self.buff_turns = 0
            self.silence_turns = 0

        # Remaining cooldown turns; starts at 0 so the skill is ready on the first turn.
        self.current_cooldown = 0

    def IsReady(self):
        """Return True when the skill can be cast this turn."""
        return self.current_cooldown == 0

    def TickCooldown(self):
        """Decrease the remaining cooldown by one turn (called at end of each turn)."""
        if self.current_cooldown > 0:
            self.current_cooldown -= 1

    def SetCooldown(self):
        """Reset cooldown after the skill has been cast."""
        self.current_cooldown = self.cooldown
