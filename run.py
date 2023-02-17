import yaml
import os
import typer
import uvicorn
import yaml
import inspect
from .framework.parse_yaml import create_app_from_config


app = typer.Typer()


@app.command()
def start():


    MAIN_CONFIG_PATH = 'main.yml'

    with open(MAIN_CONFIG_PATH, 'r') as file:
        config = yaml.safe_load(file)

    app = create_app_from_config(config)
    host = config.get('host')
    port = config.get('port')


    uvicorn.run(app, host=str(host), port=port)
        




if __name__ == "__main__":
    typer.run(run)