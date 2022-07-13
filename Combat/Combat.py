#!/usr/bin/python3

from ast import For, While

from pyparsing import Or
from Data.ServantData import StzbServant


TeamA_Config = [10001, 10002, 10003]
TeamB_Config = [10004, 10005, 10006]
DistanceList = [-2, -1, 0, 1, 2, 3]

def CheckTeamFail(TeamArray):
    for v in TeamArray:
        if v.GetServantPower() > 0:
            return False

    return True

#状态
class ServantState:
    state_id = 1
    left_turn = 1


class TeamMember:
    team_id = 1
    position = 1

    def __init__(self, _ServantConfigID, _ServantLevel, _TeamID, _Position, _Power):
        self.servant = StzbServant(_ServantConfigID, _ServantLevel)
        self.team_id = _TeamID
        self.position = _Position
        self.power = _Power

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
    
    def GetServantSpeed(self):
        return self.servant.speed

    def GetServantPower(self):
        return self.power

    def SetServantPower(self, _Power):
        if _Power <= 0 :
            self.power = 0
        else:
            self.power = _Power


def CombatSimulate(TeamA, TeamB):
    print("StartSimulate")
    SpeedArray = []
    for v in TeamA:
        SpeedArray.append(v)
    
    for v in TeamB:
        SpeedArray.append(v)

    SpeedArray.sort(key=lambda x:x.GetServantSpeed())
    for v in SpeedArray:
        print(v.GetServantSpeed(), v.GetServantName())

    bHasTeamFail = CheckTeamFail(TeamA) or CheckTeamFail(TeamB)
    while (bHasTeamFail):
       print("NoTeamFail")
       




def StartCombat():
    print("startcombat")
    a1 = TeamMember(TeamA_Config[0], 50, 1, 1, 10000)
    a2 = TeamMember(TeamA_Config[1], 40, 1, 2, 10000)
    a3 = TeamMember(TeamA_Config[2], 38, 1, 3, 10000)

    b1 = TeamMember(TeamB_Config[0], 37, 2, 4, 10000)
    b2 = TeamMember(TeamB_Config[1], 45, 2, 5, 10000)
    b3 = TeamMember(TeamB_Config[2], 48, 2, 6, 10000)

    print(a1.GetServantAtk())
    print(a2.GetServantDef())
    print(a3.GetServantName())
    print(b1.GetServantLevel())
    TeamArrayA = [a1, a2, a3]
    TeamArrayB = [b1, b2, b3]
    CombatSimulate(TeamArrayA, TeamArrayB)