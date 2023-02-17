import yaml
import os
import typer


app = typer.Typer()


@app.command()
def start():


    main_file = {'host': '0.0.0.0', 'port': 8000, 'models': 'models.py', 'database': '/', 'endpoints': {'hello':{'url': '/hello', 'text': 'hello columbus'} }}

    with open('main.yml', 'w') as file:
        document = yaml.dump(main_file, file, sort_keys=False)

    with open('models.py', 'w') as f:
        f.write('''\
import databases

DATABASE_URL = ' '

database = databases.Database(DATABASE_URL)

            
    ''')





if __name__ == "__main__":
    typer.run(startup_script)