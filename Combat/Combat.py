#!/usr/bin/python3

from ast import For
from Data.ServantData import StzbServant


TeamA_Config = [10001, 10002, 10003]
TeamB_Config = [10004, 10005, 10006]
DistanceList = [-2, -1, 0, 1, 2, 3]

#状态
class ServantState:
    state_id = 1
    left_turn = 1


class TeamMember:
    team_id = 1
    position = 1
    
    def __init__(self, _ServantConfigID, _ServantLevel, _TeamID, _Position):
        self.servant = StzbServant(_ServantConfigID, _ServantLevel)
        self.team_id = _TeamID
        self.position = _Position

    def SetTeamID(_TeamID):
        team_id = _TeamID

    def SetPosition(_Position):
        position = _Position
    
    def GetServantAtk(self):
        return self.servant.attack

    def GetServantDef(self):
        return self.servant.defense
    
    def GetServantName(self):
        return self.servant.name
    
    def GetServantLevel(self):
        return self.servant.level

def CombatSimulate(TeamArray):
    print("StartSimulate")


def StartCombat():
    print("startcombat")
    a1 = TeamMember(TeamA_Config[0], 50, 1, 1)
    a2 = TeamMember(TeamA_Config[1], 40, 1, 2)
    a3 = TeamMember(TeamA_Config[2], 38, 1, 3)

    b1 = TeamMember(TeamB_Config[0], 40, 2, 1)
    b2 = TeamMember(TeamB_Config[1], 40, 2, 1)
    b3 = TeamMember(TeamB_Config[2], 40, 2, 1)

    print(a1.GetServantAtk())
    print(a2.GetServantDef())
    print(a3.GetServantName())
    print(b1.GetServantLevel())
    TeamArray = [a1, a2, a3, b1, b2, b3]
    CombatSimulate(TeamArray)