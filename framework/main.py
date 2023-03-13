import yaml
from columbus.framework.utils import run_without_database
from columbus.startup_script import MAIN_CONFIG_NAME

try:
    with open(MAIN_CONFIG_NAME, "r") as file:
        config_dict = yaml.safe_load(file)

except:
    raise Exception(
        "No config file in the root directory. Please add a main.yml config."
    )

host = config_dict["host"]
port = config_dict["port"]

if config_dict["database"] == None:
    app = run_without_database()

else:
    from columbus.framework.application import create_app
    app = create_app(config_dict["apis"])
