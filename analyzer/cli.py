"""Entry point CLI: daftarkan semua command analyzer."""

import typer

from analyzer.commands import load, plot, report

app = typer.Typer(
    name="analyzer",
    help="Data Analyzer CLI — analisis CSV/log dari terminal.",
    no_args_is_help=True,
    add_completion=False,
)
app.command()(load)
app.command()(plot)
app.command()(report)


@app.command()
def version() -> None:
    """Tampilkan versi analyzer."""
    from analyzer import __version__

    typer.echo(f"analyzer {__version__}")


if __name__ == "__main__":
    app()
