import gol
import Combat
from Data.DataConfig import DataConfig

def __init__():
   pass

if __name__ == "__main__":
   
     gol.__init__()
     DB = DataConfig()
     gol.set_value("DataBase", DB)
     Combat.StartCombat()


     print("Main Start")