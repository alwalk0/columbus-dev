import yaml
import os
import typer
import uvicorn
import yaml
import inspect
from .framework.parse_yaml import create_app
from .framework.parse_yaml import CONFIG_NAME

app = typer.Typer()


@app.command()
def start():

    try:

        with open(CONFIG_NAME, "r") as file:
            config_dict = yaml.safe_load(file)
    
    except:
        raise Exception('No config file.')    

    host = config_dict['host']
    port = config_dict['port']
    app = create_app()


    uvicorn.run(app, host=str(host), port=port)
        




if __name__ == "__main__":
    typer.run(run)