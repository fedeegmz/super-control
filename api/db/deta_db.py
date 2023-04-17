import os
from deta import Deta

deta = Deta(os.getenv("DETA_PROJECT_KEY"))

# BASE #
db_users = deta.Base("users")
db_super = deta.Base("super_lists")

# DRIVE #
drive_super_lists = deta.Drive("super_lists")