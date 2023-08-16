import os
import nbformat as nbf


from docutils import nodes
from docutils.parsers.rst import directives


from pathlib import Path
from sphinx.ext.doctest import DoctestDirective
from sphinx.util.docutils import SphinxDirective
from sphinx.util.fileutil import copy_asset
from urllib.parse import quote
from uuid import uuid4


from .generate_notebook import generate_notebook


HERE = Path(__file__).parent

CONTENT_DIR = "_contents"
JUPYTERLITE_DIR = "lite"


class TryExamplesDirective(SphinxDirective):
    """Add button to try doctest examples in Jupyterlite notebook."""
    has_content = True
    required_arguments = 0
    option_spec = {
        "width": directives.unchanged,
        "height": directives.unchanged,
        "kernel": directives.unchanged,
        "toolbar": directives.unchanged,
        "theme": directives.unchanged,
        "prompt": directives.unchanged,
        "prompt_color": directives.unchanged,
    }

    def run(self):
        if 'generated_notebooks' not in self.env.temp_data:
            self.env.temp_data['generated_notebooks'] = {}

        directive_key = f"{self.env.docname}-{self.lineno}"
        notebook_unique_name = self.env.temp_data['generated_notebooks'].get(
            directive_key
        )

        width = self.options.pop("width", "100%")
        height = self.options.pop("height", "1000px")
        prefix = os.path.join("..", JUPYTERLITE_DIR)
        lite_app = "retro/"
        notebooks_path = "notebooks/"

        # Instantiate doctest directive so we can get it's html output
        doctest = DoctestDirective(
            self.name,
            self.arguments,
            self.options,
            self.content,
            self.lineno,
            self.content_offset,
            self.block_text,
            self.state,
            self.state_machine,
        )
        example_node = doctest.run()[0]

        if notebook_unique_name is None:
            nb = generate_notebook(self.content)
            self.content = None
            notebooks_dir = Path(self.env.app.srcdir) / CONTENT_DIR
            notebook_unique_name = f"{uuid4()}.ipynb".replace("-", "_")
            self.env.temp_data['generated_notebooks'][directive_key] = \
                notebook_unique_name
            self.options["path"] = notebook_unique_name

            # Copy the Notebook for RetroLite to find
            os.makedirs(notebooks_dir, exist_ok=True)
            with open(notebooks_dir / Path(notebook_unique_name), "w") as f:
                nbf.write(nb, f)

        app_path = f"{lite_app}{notebooks_path}"
        options = "&".join(
            [f"{key}={quote(value)}" for key, value in self.options.items()]
        )

        iframe_src = f'{prefix}/{app_path}{f"?{options}" if options else ""}'

        container_style = f'width: {width}; height: {height};'
        examples_div_id = uuid4()
        iframe_div_id = uuid4()

        outer_container = nodes.container()

        # Start the outer container with raw HTML
        examples_container_div = (
            f"<div class=\"examples_container\" id=\"{examples_div_id}\">"
        )
        start_examples_container = nodes.raw('', examples_container_div, format='html')
        outer_container += start_examples_container

        # Button with the onclick event
        button_html = (
            f"<button onclick=\"window.tryExamplesShowIframe('{examples_div_id}',"
            f"'{iframe_div_id}','{iframe_src}')\">"
            "Try it!</button>"
        )
        button_node = nodes.raw('', button_html, format='html')
        outer_container += example_node
        outer_container += button_node

        # End the examples container
        end_examples_container = nodes.raw('', "</div>", format='html')
        outer_container += end_examples_container

        # Iframe container (initially hidden)
        iframe_container_div = (
            f"<div id=\"{iframe_div_id}\" "
            f"class=\"try_examples_iframe_container hidden\" "
            f"style=\"{container_style}\"></div>"
        )
        iframe_container = nodes.raw('', iframe_container_div, format='html')
        outer_container += iframe_container

        # Return the outer container node
        return [outer_container]


def copy_assets(app, exception):
    """Copy CSS and JS assets."""
    if exception is None:
        copy_asset(str(HERE / "sphinx_try_examples.css"), str(Path(app.outdir) / "_static"))
        copy_asset(str(HERE / "sphinx_try_examples.js"), str(Path(app.outdir) / "_static"))


def setup(app):
    app.add_directive("try_examples", TryExamplesDirective)
    app.connect('build-finished', copy_assets)

    app.add_css_file("https://fonts.googleapis.com/css?family=Vibur")
    app.add_css_file("sphinx_try_examples.css")
    app.add_js_file("sphinx_try_examples.js")
