import typer
import uvicorn
from columbus.framework.main import host, port


app = typer.Typer()


@app.command()
def start():
    uvicorn.run(
        "columbus.framework.main:app",
        host=str(host),
        port=port,
        reload=True,
        reload_includes="*.yml",
    )


if __name__ == "__main__":
    typer.run(run)
