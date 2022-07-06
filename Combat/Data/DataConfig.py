import pandas as pd


ServantTable = "./Combat/Data/Tables/servant.csv"

class ServantConfigData:
    config_id = 1
    main_skill_id = 1
    base_attack = 1
    attack_grow = 0.5
    base_defense = 1
    defense_grow = 0.5
    base_speed = 1
    speed_grow = 0.5
    name = ""

class SkillConfigData:
    config_id = 1
    skill_type = 1
    target_type = 1
    target_num = 1
    effect_radius = 5

class DataConfig:
    ServantMap = {}
    SkillMap = {}
    def __init__(self) :
        data_csv = pd.read_csv(ServantTable)
        for index, row in data_csv.iterrows():
            #print(row["ID"])
            row_id = row["ID"]
            self.ServantMap[row_id] = row
            #print(row)

    def GetServantInfoByConfigID(self, config_id):
        servant_data = ServantConfigData()
        servant_data.config_id = config_id
        mServantConfigData = self.ServantMap[config_id]
        servant_data.main_skill_id = mServantConfigData.main_skill
        servant_data.base_attack = mServantConfigData.attack
        servant_data.attack_grow = mServantConfigData.attack_grow
        servant_data.base_defense = mServantConfigData.defense
        servant_data.defense_grow = mServantConfigData.defense_grow
        servant_data.base_speed = mServantConfigData.speed
        servant_data.speed_grow = mServantConfigData.speed_grow
        servant_data.name = mServantConfigData.wujiangname
        #print(mServantConfigData.wujiangname)
        return servant_data
    
    def GetSkillInfoByConfigID(config_id):
        skill_data = SkillConfigData()
        skill_data.config_id = config_id
        return skill_data