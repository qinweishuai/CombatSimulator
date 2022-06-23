#!/usr/bin/python3
from Data.SkillData import StzbSkill
from Data.DataConfig import DataConfig
import gol

class StzbServant:
    main_skill = StzbSkill(1,1)
    second_skill = StzbSkill(1,1)
    third_skill = StzbSkill(1,1)
    health = 100
    attack = 100
    defense = 100
    speed = 100
    name = ""

    def __init__(self, config_id, level):
        DB = gol.get_value("DataBase")
        self.config_id = config_id
        self.level = level
        config_data = DB.GetServantInfoByConfigID(config_id)
        self.attack = config_data.base_attack + config_data.attack_grow * (level - 1)
        self.defense = config_data.base_defense + config_data.defense_grow * (level - 1)
        self.speed = config_data.base_speed + config_data.speed_grow * (level - 1)
        self.main_skill = config_data.main_skill_id
        self.name = config_data.name
 
    def GetMainSkill(self):
        return self.main_skill
        
    def SetNewLevel(self, level):
        self.level = level
        config_data = DataConfig.GetServantInfoByConfigID(self.config_id)
        self.attack = config_data.base_attack + config_data.attack_grow * (level - 1)
        self.defense = config_data.base_defense + config_data.defense_grow * (level - 1)
        self.speed = config_data.base_speed + config_data.speed_grow * (level - 1)
