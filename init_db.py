import os

with open('./scripts/init.sql') as f:
    lines = f.readlines()

line = " ".join(line.strip() for line in lines)

os.system(f"docker-compose exec db mysql -u root --password=asdf -e \"{line}\"")
