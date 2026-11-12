from dsc.constants.plantillas import PL_SYSTEM_PROMPT

def build_prompt_from_template(config: dict, plantilla: str = PL_SYSTEM_PROMPT) -> str:
    """Rellena la plantilla con las secciones del config."""
    return plantilla.format(**config)