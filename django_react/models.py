import os
import hashlib
import json
from django.utils.safestring import mark_safe
from django_webpack.models import WebpackBundle
import exceptions
import react


class ReactComponent(WebpackBundle):
    props = None
    serialised_props = None
    loaders = (
        {'loader': 'jsx', 'test': '.jsx$'},
    )
    paths_to_loaders = (os.path.abspath(os.path.join(os.path.dirname(__file__), 'node_modules')),)
    react_variable = 'window.React'
    externals = {
        # Rather than bundling React, we rely on a browser global
        'react': react_variable,
        'react/addons': react_variable
    }

    def __init__(self, **kwargs):
        self.props = kwargs

    def render_to_string(self):
        rendered = react.render_to_string(
            path_to_source=self.get_path_to_source(),
            serialised_props=self.get_serialised_props(),
        )
        return self.render_container(content=rendered)

    def render_to_static_markup(self):
        rendered = react.render_to_static_markup(
            path_to_source=self.get_path_to_source(),
            serialised_props=self.get_serialised_props(),
        )
        return self.render_container(content=rendered)

    def render_js(self):
        rendered = '\n'.join((
            self.render_props(),
            self.render_bundle(),
            self.render_init(),
        ))
        return mark_safe(rendered)

    def render_container(self, content=None):
        if content is None:
            content = ''
        rendered = '<div id="{container_id}" class="{container_class_name}">{content}</div>'.format(
            container_id=self.get_container_id(),
            container_class_name=self.get_container_class_name(),
            content=content,
        )
        return mark_safe(rendered)

    def render_props(self):
        rendered = '<script>{props_variable} = {serialised_props};</script>'.format(
            props_variable=self.get_props_variable(),
            serialised_props=self.get_serialised_props(),
        )
        return mark_safe(rendered)

    def render_init(self):
        props_check = ''
        if self.has_props():
            props_check = '''
                if (!window.{props_variable}) {{
                    throw new Error('Cannot find props `{props_variable}` for component `{exported_variable}`');
                }}
            '''.format(
                props_variable=self.get_props_variable(),
                exported_variable=self.get_library(),
            )
        rendered = '''
            <script>
                if (!window.{exported_variable}) {{
                    throw new Error('Cannot find component `{exported_variable}`');
                }}
                {props_check}
                (function(React, component, props, container_id) {{
                    var react_element = React.createElement(component, props);
                    var mount_container = document.getElementById(container_id);
                    if (!mount_container) {{
                        throw new Error('Cannot find the container element `#' + container_id + '` for component `{exported_variable}`');
                    }}
                    React.render(react_element, mount_container);
                }})({react_variable}, {exported_variable}, window.{props_variable}, '{container_id}');
            </script>
        '''.format(
            react_variable=self.get_react_variable(),
            exported_variable=self.get_library(),
            props_variable=self.get_props_variable(),
            container_id=self.get_container_id(),
            props_check=props_check,
        )
        return mark_safe(rendered)

    def get_props(self):
        return self.props

    def has_props(self):
        if self.get_props():
            return True
        return False

    def get_component_name(self):
        return self.__class__.__name__

    def get_library(self):
        if self.library:
            return self.library
        return self.get_component_name()

    def get_react_variable(self):
        return self.react_variable

    def get_component_id(self):
        return unicode(id(self))

    def get_container_id(self):
        return 'reactComponentContainer-{component_id}'.format(
            component_id=self.get_component_id()
        )

    def get_container_class_name(self):
        return 'reactComponentContainer reactComponentContainer--{component_name}'.format(
            component_name=self.get_component_name()
        )

    def get_serialised_props(self):
        if not self.serialised_props:
            # Django will silently ignore json's exceptions, so we need to
            # intercept them and raise our own class of exception
            try:
                self.serialised_props = json.dumps(self.get_props())
            except (TypeError, AttributeError) as e:
                raise exceptions.PropSerialisationError(e.__class__.__name__, *e.args)
        return self.serialised_props

    def get_serialised_props_hash(self):
        serialised_props = self.get_serialised_props()
        md5 = hashlib.md5()
        md5.update(serialised_props)
        return md5.hexdigest()

    def get_props_variable(self):
        return '__propsFor{component_name}_{serialised_props_hash}__'.format(
            component_name=self.get_component_name(),
            serialised_props_hash=self.get_serialised_props_hash(),
        )