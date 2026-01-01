# src/docustruct/cli.py
import typer
import json
from pathlib import Path
from . import parser

app = typer.Typer(add_completion=False)

@app.callback(invoke_without_command=True)
def main(
    path: Path = typer.Argument(None, help="PDF file to analyze"),
    out: Path = typer.Option(None, "--out", help="Output JSON file"),
    max_pages: int = typer.Option(None, help="Maximum pages to process"),
):
    """
    Analyze a PDF and extract structured outline.
    """
    if path is None:
        typer.echo("Error: PDF path is required.")
        raise typer.Exit(code=1)

    if not path.exists():
        typer.echo(f"File not found: {path}")
        raise typer.Exit(code=1)

    try:
        result = parser.analyze_pdf_path(str(path), max_pages=max_pages)
    except Exception as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(code=2)

    if out:
        out.write_text(json.dumps(result, indent=2), encoding="utf-8")
        typer.echo(f"Wrote: {out}")
    else:
        typer.echo(json.dumps(result, indent=2))
