import os
import pandas as pd

ServantTable = os.path.join(os.path.dirname(__file__), "Tables", "servant.csv")
SkillTable = os.path.join(os.path.dirname(__file__), "Tables", "skill.csv")


class ServantConfigData:
    config_id = 1
    main_skill_id = 1
    base_attack = 1
    attack_grow = 0.5
    base_defense = 1
    defense_grow = 0.5
    base_speed = 1
    speed_grow = 0.5
    base_health = 30
    health_grow = 1.5
    base_tactics = 10
    tactics_grow = 0.5
    basic_attack_range = 1
    name = ""


class SkillConfigData:
    config_id = 1
    name = ""
    skill_type = 1
    target_type = 1
    target_num = 1
    effect_radius = 2
    damage_ratio = 1.0
    heal_ratio = 0.0
    cooldown = 2


class DataConfig:
    def __init__(self):
        self.ServantMap = {}
        self.SkillMap = {}

        data_csv = pd.read_csv(ServantTable, encoding='utf-8-sig')
        for index, row in data_csv.iterrows():
            row_id = row["ID"]
            self.ServantMap[row_id] = row

        if os.path.exists(SkillTable):
            skill_csv = pd.read_csv(SkillTable, encoding='utf-8-sig')
            if not skill_csv.empty:
                for index, row in skill_csv.iterrows():
                    row_id = row["ID"]
                    self.SkillMap[row_id] = row

    def GetServantInfoByConfigID(self, config_id):
        servant_data = ServantConfigData()
        servant_data.config_id = config_id
        mServantConfigData = self.ServantMap[config_id]
        servant_data.main_skill_id = int(mServantConfigData["main_skill"])
        servant_data.base_attack = mServantConfigData["attack"]
        servant_data.attack_grow = mServantConfigData["attack_grow"]
        servant_data.base_defense = mServantConfigData["defense"]
        servant_data.defense_grow = mServantConfigData["defense_grow"]
        servant_data.base_speed = mServantConfigData["speed"]
        servant_data.speed_grow = mServantConfigData["speed_grow"]
        servant_data.base_health = mServantConfigData["health"]
        servant_data.health_grow = mServantConfigData["health_grow"]
        servant_data.base_tactics = mServantConfigData["tactics"]
        servant_data.tactics_grow = mServantConfigData["tactics_grow"]
        servant_data.basic_attack_range = int(mServantConfigData["basic_attack_range"])
        servant_data.name = mServantConfigData["wujiangname"]
        return servant_data

    def GetSkillInfoByConfigID(self, config_id):
        skill_data = SkillConfigData()
        skill_data.config_id = config_id
        if config_id in self.SkillMap:
            mSkillConfigData = self.SkillMap[config_id]
            skill_data.name = mSkillConfigData["name"]
            skill_data.skill_type = int(mSkillConfigData["skill_type"])
            skill_data.target_type = int(mSkillConfigData["target_type"])
            skill_data.target_num = int(mSkillConfigData["target_num"])
            skill_data.effect_radius = int(mSkillConfigData["effect_radius"])
            skill_data.damage_ratio = float(mSkillConfigData["damage_ratio"])
            skill_data.heal_ratio = float(mSkillConfigData["heal_ratio"])
            skill_data.cooldown = int(mSkillConfigData["cooldown"])
        return skill_data
