import os
from deta import Deta

deta = Deta(os.getenv("DETA_PROJECT_KEY"))

db_users = deta.Base("users")
db_super = deta.Base("super_lists")