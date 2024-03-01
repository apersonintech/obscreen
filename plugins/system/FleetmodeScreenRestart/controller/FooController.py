from flask import Flask, jsonify
from src.interface.ObController import ObController


class FooController(ObController):

    def register(self):
        self._app.add_url_rule('/foo', 'foo', self.foo, methods=['GET'])
        self._app.add_url_rule('/foo_html', 'foo_html', self.foo_html, methods=['GET'])

    def foo(self):
        return jsonify({'foo': True})

    def foo_html(self):
        return self.plugin().render_view(
            '@foo_html.jinja.html',
            page_name="FOO"
        )


