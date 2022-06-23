#!/usr/bin/python3

class StzbSkill:
    type = 1

    def __init__(self, config_id, level):
        self.config_id = config_id
        self.level = level

    def SkillCast(self):
        self.level = 10

    def CastToTarget(self, target):
        pass