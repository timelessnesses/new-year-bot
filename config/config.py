from dotenv import load_dotenv

load_dotenv()
import os
import subprocess
import logging

logger = logging.getLogger('NewYearBot.config')

token = os.getenv("NEW_YEAR_TOKEN")
logger.info("Got Bot Token")
prefix = os.getenv("NEW_YEAR_PREFIX")
logger.info("Got Bot Prefix")
database_host = os.getenv("NEW_YEAR_DATABASE_HOST")
database_port = os.getenv("NEW_YEAR_DATABASE_PORT")
database_name = os.getenv("NEW_YEAR_DATABASE_NAME")
database_user = os.getenv("NEW_YEAR_DATABASE_USER")
database_password = os.getenv("NEW_YEAR_DATABASE_PASSWORD")
database_url = "postgresql://{}:{}@{}:{}/{}".format(
    database_user, database_password, database_host, database_port, database_name
)
logger.info(f"Got postgresql connection string {database_url}")
git_repo = (
    subprocess.check_output("git config --get remote.origin.url".split(" "))
    .decode("ascii")
    .strip()
)

git_repo = git_repo[:-4] if ".git" in git_repo else git_repo

logger.info(f"Got current remote git repository {git_repo}")
