#!/usr/bin/python3

from Data.ServantData import StzbServant


TeamA_Config = [10001, 10002, 10003]
TeamB_Config = [10004, 10005, 10006]
DistanceList = [-2, -1, 0, 1, 2, 3]

class TeamMember:
    team_id = 1
    position = 1
    
    def __init__(self) -> None:
        self.servant = StzbServant(1, 1)



def StartCombat():
    print("startcombat")
    a1 = StzbServant(TeamA_Config[0], 50)
    a2 = StzbServant(TeamA_Config[1], 40)
    a3 = StzbServant(TeamA_Config[2], 38)

    b1 = StzbServant(TeamB_Config[0], 40)
    b2 = StzbServant(TeamB_Config[1], 40)
    b3 = StzbServant(TeamB_Config[2], 40)
    print(a1.attack, a2.defense, a3.speed, b1.main_skill, b2.name)
    