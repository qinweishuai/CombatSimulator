from Combat import gol
from Combat import Combat
from Combat.Data.DataConfig import DataConfig


if __name__ == "__main__":
     print("Main Start")
     gol.__init__()
     DB = DataConfig()
     gol.set_value("DataBase", DB)
     Combat.StartCombat()
