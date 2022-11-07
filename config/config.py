from dotenv import load_dotenv

load_dotenv()
import os
import subprocess

token = os.getenv("NEW_YEAR_TOKEN")
prefix = os.getenv("NEW_YEAR_PREFIX")
database_host = os.getenv("NEW_YEAR_DATABASE_HOST")
database_port = os.getenv("NEW_YEAR_DATABASE_PORT")
database_name = os.getenv("NEW_YEAR_DATABASE_NAME")
database_user = os.getenv("NEW_YEAR_DATABASE_USER")
database_password = os.getenv("NEW_YEAR_DATABASE_PASSWORD")
database_url = "postgresql://{}:{}@{}:{}/{}".format(
    database_user, database_password, database_host, database_port, database_name
)
git_repo = (
    subprocess.check_output("git config --get remote.origin.url".split(" "))
    .decode("ascii")
    .strip()
)[:-4]
