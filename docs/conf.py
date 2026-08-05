"""Configuração do Sphinx para o Módulo Escolhas."""

project = "Módulo Escolhas"
author = "SME - SIGLA"
copyright = "2026, SME - SIGLA"

extensions: list[str] = []

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

language = "pt_BR"

html_theme = "alabaster"

html_theme_options = {
    "description": ("Documentação do módulo de escolhas da SIGLA."),
    "github_button": False,
}
