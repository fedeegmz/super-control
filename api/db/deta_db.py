import os
from deta import Deta

deta = Deta(os.getenv("DETA_PROJECT_KEY"))

db_main = deta.Base("main")