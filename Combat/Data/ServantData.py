#!/usr/bin/python3
from Combat import gol


class StzbServant:
    def __init__(self, config_id, level):
        DB = gol.get_value("DataBase")
        self.config_id = config_id
        self.level = level
        config_data = DB.GetServantInfoByConfigID(config_id)
        self.attack = config_data.base_attack + config_data.attack_grow * (level - 1)
        self.defense = config_data.base_defense + config_data.defense_grow * (level - 1)
        self.speed = config_data.base_speed + config_data.speed_grow * (level - 1)
        self.health = int(config_data.base_health + config_data.health_grow * (level - 1))
        self.tactics = config_data.base_tactics + config_data.tactics_grow * (level - 1)
        self.basic_attack_range = config_data.basic_attack_range
        self.main_skill_id = config_data.main_skill_id
        self.name = config_data.name

    def SetNewLevel(self, level):
        DB = gol.get_value("DataBase")
        self.level = level
        config_data = DB.GetServantInfoByConfigID(self.config_id)
        self.attack = config_data.base_attack + config_data.attack_grow * (level - 1)
        self.defense = config_data.base_defense + config_data.defense_grow * (level - 1)
        self.speed = config_data.base_speed + config_data.speed_grow * (level - 1)
        self.health = int(config_data.base_health + config_data.health_grow * (level - 1))
        self.tactics = config_data.base_tactics + config_data.tactics_grow * (level - 1)
