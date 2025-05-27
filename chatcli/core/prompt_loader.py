from jinja2 import Environment, FileSystemLoader
from pathlib import Path

# Initialize Jinja2 environment pointing to the prompts directory
env = Environment(
    loader=FileSystemLoader(Path(__file__).parent / "prompts"),
    trim_blocks=True,
    lstrip_blocks=True,
)

def render_template(name: str, **kwargs) -> str:
    template = env.get_template(name)
    return template.render(**kwargs)
