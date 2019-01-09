from jinja2 import Environment, PackageLoader, select_autoescape
from nameko.extensions import DependencyProvider

class TemplateRenderer:

  def __init__(self, package_name, package_dir):
    self.template_env = Environment(
      loader=PackageLoader(package_name, package_dir),
      autoescape=select_autoescape(['html'])
    )

  def render_home(self, messages):
    template = self.template_env.get_template('home.html')
    return template.render(messages=messages)


class Jinja2(DependencyProvider):
  def setup(self): # creates TemplateRenderer instance
    self.template_renderer = TemplateRenderer('temp_messenger', 'templates')

  # Injects template to worker
  def get_dependency(self, worker_ctx):
    return self.template_renderer
