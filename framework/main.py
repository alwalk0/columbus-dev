import yaml
from columbus.start import MAIN_CONFIG_NAME
from columbus.framework.application import create_app

try:
    with open(MAIN_CONFIG_NAME, "r") as file:
        config_dict = yaml.safe_load(file)

except:
    raise Exception(
        "No config file in the root directory. Please add a main.yml config."
    )

host = config_dict["host"]
port = config_dict["port"]
app = create_app(config_dict["apis"])
