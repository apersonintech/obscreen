from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2.loaders import split_template_path


class AliasFileSystemLoader(FileSystemLoader):

    def __init__(self, searchpath, encoding='utf-8', followlinks=False, alias_paths=None):
        super().__init__(searchpath, encoding=encoding, followlinks=followlinks)

        if alias_paths is None:
            alias_paths = {}
        self.alias_paths = alias_paths

    def get_source(self, environment, template):
        for alias, path in self.alias_paths.items():
            if template.startswith(alias):
                template = template.replace(alias, path, 1)
                break

        template = "/".join(split_template_path(template))

        return super().get_source(environment, template)

