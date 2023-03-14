import typer
import os

app = typer.Typer()

MAIN_CONFIG_NAME = "main.yml"

MODELS_NAME = "models.py"


@app.command()
def start():
    if not os.path.exists(MAIN_CONFIG_NAME):
        with open(MAIN_CONFIG_NAME, "w") as f:
            f.write(
                """\
host: 0.0.0.0
port: 8000
models: models.py
database:
apis:
  hello_world:
    table:
    methods: [GET]
            
    """
            )

    if not os.path.exists(MODELS_NAME):
        with open(MODELS_NAME, "w") as f:
            f.write(
                """\
import databases

DATABASE_URL = ' '

database = databases.Database(DATABASE_URL)

            
    """
            )


if __name__ == "__main__":
    typer.run(startup_script)
