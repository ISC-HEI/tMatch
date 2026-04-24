
from seed.keywords import create_keywords
from seed.roles import create_roles

print("This is the seed script. It should only be run when the database is freshly created.")
print("It will insert basic keywords and required roles inside the database.")
input("Please press enter to continue.")

create_roles()
print("Created roles")

create_keywords()
print("Created keywords")
