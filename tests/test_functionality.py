import datetime
import json
import os
import unittest
import shutil
from django.utils import timezone, six
import django_react
from django_react.render import render_component, RenderedComponent
from django_react.bundle import (
    get_webpack_config, get_var_from_path, get_component_config_filename, bundle_component
)
from django_react.exceptions import ComponentRenderingError, ComponentSourceFileNotFound, ComponentWasNotBundled
from django_webpack.compiler import WebpackBundle
from django_react.conf import settings
from .settings import STATIC_ROOT

NODE_MODULES = os.path.join(os.path.dirname(django_react.__file__), 'services', 'node_modules')

COMPONENT_ROOT = os.path.join(os.path.dirname(__file__), 'components')

HELLO_WORLD_COMPONENT_JS = os.path.join(COMPONENT_ROOT, 'HelloWorld.js')
HELLO_WORLD_COMPONENT_JSX = os.path.join(COMPONENT_ROOT, 'HelloWorld.jsx')
HELLO_WORLD_WRAPPER_COMPONENT = os.path.join(COMPONENT_ROOT, 'HelloWorldWrapper.jsx')
ERROR_THROWING_COMPONENT = os.path.join(COMPONENT_ROOT, 'ErrorThrowingComponent.jsx')
SYNTAX_ERROR_COMPONENT = os.path.join(COMPONENT_ROOT, 'SyntaxErrorComponent.jsx')
REACT_ADDONS_COMPONENT = os.path.join(COMPONENT_ROOT, 'ReactAddonsComponent.jsx')
STATIC_FILE_FINDER_COMPONENT = 'test_app/StaticFileFinderComponent.jsx'


class TestDjangoReact(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure we have a clean slate for the run
        if os.path.exists(STATIC_ROOT):
            shutil.rmtree(STATIC_ROOT)

    @classmethod
    def tearDownClass(cls):
        # Ensure we leave a clean slate after the run
        if os.path.exists(STATIC_ROOT):
            shutil.rmtree(STATIC_ROOT)

    def test_can_render_a_component_in_js(self):
        component = render_component(HELLO_WORLD_COMPONENT_JS, to_static_markup=True)
        self.assertEqual(str(component), '<span>Hello </span>')

    def test_can_generate_a_var_from_a_path(self):
        self.assertEqual(get_var_from_path('/foo/bar/woz.jsx'), 'bar__woz')
        self.assertEqual(get_var_from_path('/foo-bar/woz.jsx'), 'foo_bar__woz')
        self.assertEqual(get_var_from_path('/foo/ba +\\r/woz.jsx'), 'ba_r__woz')
        self.assertEqual(get_var_from_path('foo/test/one/two/bar/a'), 'bar__a')
        self.assertEqual(get_var_from_path('foo/test/one/two/bar/.a'), 'bar___a')

    "\nvar resolve = require('/Users/markfinger/Projects/django-react/django_react/services/node_modules/resolve');\n\nmodule.exports = {\n    context: '/Users/markfinger/Projects/django-react/tests/components',\n    entry: './HelloWorld.js',\n    output: {\n        path: '[bundle_dir]/react-components',\n        filename: 'components__HelloWorld-[hash].js',\n        libraryTarget: 'umd',\n        library: 'components__HelloWorld'\n    },\n    externals: [{\n      react: {\n        commonjs2: resolve.sync('react', {basedir: '/Users/markfinger/Projects/django-react/tests/components'}),\n        root: 'React'\n      },\n      'react/addons': {\n        commonjs2: resolve.sync('react/addons', {basedir: '/Users/markfinger/Projects/django-react/tests/components'}),\n        root: 'React'\n      }\n    }]\n};\n"
    "\nvar resolve = require('/Users/markfinger/Projects/django-react/django_react/services/node_modules/resolve');\n\nmodule.exports = {\n    context: '/Users/markfinger/Projects/django-react/tests/components',\n    entry: './HelloWorld.js',\n    output: {\n        path: '[bundle_dir]/react-components',\n        filename: 'components__HelloWorld-[hash].js',\n        libraryTarget: 'umd',\n        library: 'components__HelloWorld'\n    },\n    externals: [{\n      react: {\n        commonjs2: resolve.sync('react', {basedir: '/Users/markfinger/Projects/django-react/tests/components'}),\n        root: 'React'\n      },\n      'react/addons': {\n        commonjs2: resolve.sync('react/addons', {basedir: '/Users/markfinger/Projects/django-react/tests/components'}),\n        root: 'React'\n      }\n    }],\n    devtool: 'eval'\n};\n"
    def test_can_generate_a_webpack_config_for_a_js_component(self):
        _DEV_TOOL = settings.DEV_TOOL
        settings._unlock()
        settings.DEV_TOOL = True
        config = get_webpack_config(HELLO_WORLD_COMPONENT_JS)
        expected = \
"""
var resolve = require('%s');

module.exports = {
    context: '%s',
    entry: './HelloWorld.js',
    output: {
        path: '[bundle_dir]/react-components',
        filename: 'components__HelloWorld-[hash].js',
        libraryTarget: 'umd',
        library: 'components__HelloWorld'
    },
    externals: [{
      react: {
        commonjs2: resolve.sync('react', {basedir: '%s'}),
        root: 'React'
      },
      'react/addons': {
        commonjs2: resolve.sync('react/addons', {basedir: '%s'}),
        root: 'React'
      }
    }],
    devtool: 'eval'
};
""" % (
    os.path.join(NODE_MODULES, 'resolve'),
    COMPONENT_ROOT,
    COMPONENT_ROOT,
    COMPONENT_ROOT,
)
        self.assertEqual(config, expected)
        settings.DEV_TOOL = _DEV_TOOL
        settings._lock()
    "\nvar resolve = require('/Users/markfinger/Projects/django-react/django_react/services/node_modules/resolve');\n\nmodule.exports = {\n    context: '/Users/markfinger/Projects/django-react/tests/components',\n    entry: './HelloWorld.jsx',\n    output: {\n        path: '[bundle_dir]/react-components',\n        filename: 'components__HelloWorld-[hash].js',\n        libraryTarget: 'umd',\n        library: 'components__HelloWorld'\n    },\n    externals: [{\n      react: {\n        commonjs2: resolve.sync('react', {basedir: '/Users/markfinger/Projects/django-react/tests/components'}),\n        root: 'React'\n      },\n      'react/addons': {\n        commonjs2: resolve.sync('react/addons', {basedir: '/Users/markfinger/Projects/django-react/tests/components'}),\n        root: 'React'\n      }\n    }],\n    devtool: 'eval'\n,\n    module: {\n        loaders: [{\n            test: /\\.jsx$/,\n            exclude: /node_modules/,\n            loader: 'babel-loader'\n        }]\n    },\n    resolveLoader: {\n        root: '/Users/markfinger/Projects/django-react/django_react/services/node_modules'\n    }\n\n};\n"
    "\nvar resolve = require('/Users/markfinger/Projects/django-react/django_react/services/node_modules/resolve');\n\nmodule.exports = {\n    context: '/Users/markfinger/Projects/django-react/tests/components',\n    entry: './HelloWorld.jsx',\n    output: {\n        path: '[bundle_dir]/react-components',\n        filename: 'components__HelloWorld-[hash].js',\n        libraryTarget: 'umd',\n        library: 'components__HelloWorld'\n    },\n    externals: [{\n      react: {\n        commonjs2: resolve.sync('react', {basedir: '/Users/markfinger/Projects/django-react/tests/components'}),\n        root: 'React'\n      },\n      'react/addons': {\n        commonjs2: resolve.sync('react/addons', {basedir: '/Users/markfinger/Projects/django-react/tests/components'}),\n        root: 'React'\n      }\n    }],\n    devtool: 'eval',\n\n    module: {\n        loaders: [{\n            test: /\\.jsx$/,\n            exclude: /node_modules/,\n            loader: 'babel-loader'\n        }]\n    },\n    resolveLoader: {\n        root: '/Users/markfinger/Projects/django-react/django_react/services/node_modules'\n    }\n\n};\n"
    def test_can_generate_a_webpack_config_for_a_jsx_component(self):
        _DEV_TOOL = settings.DEV_TOOL
        settings._unlock()
        settings.DEV_TOOL = True

        config = get_webpack_config(HELLO_WORLD_COMPONENT_JSX, translate=True)
        expected = \
"""
var resolve = require('%s');

module.exports = {
    context: '%s',
    entry: './HelloWorld.jsx',
    output: {
        path: '[bundle_dir]/react-components',
        filename: 'components__HelloWorld-[hash].js',
        libraryTarget: 'umd',
        library: 'components__HelloWorld'
    },
    externals: [{
      react: {
        commonjs2: resolve.sync('react', {basedir: '%s'}),
        root: 'React'
      },
      'react/addons': {
        commonjs2: resolve.sync('react/addons', {basedir: '%s'}),
        root: 'React'
      }
    }],
    devtool: 'eval',
    module: {
        loaders: [{
            test: /\.jsx$/,
            exclude: /node_modules/,
            loader: 'babel-loader'
        }]
    },
    resolveLoader: {
        root: '%s'
    }

};
""" % (
    os.path.join(NODE_MODULES, 'resolve'),
    COMPONENT_ROOT,
    COMPONENT_ROOT,
    COMPONENT_ROOT,
    NODE_MODULES,
)
        self.assertEqual(config, expected)
        settings.DEV_TOOL = _DEV_TOOL
        settings._lock()

    def test_can_generate_and_create_a_config_file(self):
        filename = get_component_config_filename(HELLO_WORLD_COMPONENT_JS)
        with open(filename, 'r') as config_file:
            contents = config_file.read()
            self.assertEqual(contents, get_webpack_config(HELLO_WORLD_COMPONENT_JS))

        filename = get_component_config_filename(HELLO_WORLD_COMPONENT_JSX, translate=True)
        with open(filename, 'r') as config_file:
            contents = config_file.read()
            self.assertEqual(contents, get_webpack_config(HELLO_WORLD_COMPONENT_JSX, translate=True))

    def test_generated_config_files_are_cached(self):
        self.assertEqual(
            get_component_config_filename(HELLO_WORLD_COMPONENT_JS),
            get_component_config_filename(HELLO_WORLD_COMPONENT_JS),
        )
        self.assertEqual(
            get_component_config_filename(HELLO_WORLD_COMPONENT_JS, translate=True),
            get_component_config_filename(HELLO_WORLD_COMPONENT_JS, translate=True),
        )
        self.assertNotEqual(
            get_component_config_filename(HELLO_WORLD_COMPONENT_JS, translate=True),
            get_component_config_filename(HELLO_WORLD_COMPONENT_JS, translate=False),
        )
        self.assertNotEqual(
            get_component_config_filename(HELLO_WORLD_COMPONENT_JS),
            get_component_config_filename(HELLO_WORLD_COMPONENT_JSX),
        )
        self.assertNotEqual(
            get_component_config_filename(HELLO_WORLD_COMPONENT_JS, translate=True),
            get_component_config_filename(HELLO_WORLD_COMPONENT_JSX, translate=True),
        )
        self.assertNotEqual(
            get_component_config_filename(HELLO_WORLD_COMPONENT_JS, translate=True),
            get_component_config_filename(HELLO_WORLD_COMPONENT_JSX, translate=False),
        )
        self.assertNotEqual(
            get_component_config_filename(HELLO_WORLD_COMPONENT_JS, translate=False),
            get_component_config_filename(HELLO_WORLD_COMPONENT_JSX, translate=False),
        )

    def test_can_bundle_a_js_component(self):
        bundle = bundle_component(HELLO_WORLD_COMPONENT_JS)
        asset = bundle.get_assets()[0]
        self.assertTrue(os.path.exists(asset['path']))
        with open(asset['path'], 'r') as asset_file:
            contents = asset_file.read()
            self.assertIn('// __DJANGO_WEBPACK_BUNDLE_TEST__', contents)

    def test_can_bundle_a_jsx_component(self):
        bundle = bundle_component(HELLO_WORLD_COMPONENT_JSX, translate=True)
        asset = bundle.get_assets()[0]
        self.assertTrue(os.path.exists(asset['path']))
        with open(asset['path'], 'r') as asset_file:
            contents = asset_file.read()
            self.assertIn('// __DJANGO_WEBPACK_TRANSLATE_BUNDLE_TEST__', contents)

    def test_can_render_a_bundled_js_component(self):
        bundle = bundle_component(HELLO_WORLD_COMPONENT_JS)
        asset = bundle.get_assets()[0]
        component = render_component(asset['path'], to_static_markup=True)
        self.assertEqual(str(component), '<span>Hello </span>')

    def test_can_render_a_bundled_jsx_component(self):
        bundle = bundle_component(HELLO_WORLD_COMPONENT_JSX, translate=True)
        asset = bundle.get_assets()[0]
        component = render_component(asset['path'], to_static_markup=True)
        self.assertEqual(str(component), '<span>Hello </span>')

    def test_can_pass_props_when_rendering_a_bundled_js_component(self):
        bundle = bundle_component(HELLO_WORLD_COMPONENT_JS)
        asset = bundle.get_assets()[0]
        component = render_component(asset['path'], props={'name': 'world!'}, to_static_markup=True)
        self.assertEqual(str(component), '<span>Hello world!</span>')

    def test_can_pass_props_when_rendering_a_bundled_jsx_component(self):
        bundle = bundle_component(HELLO_WORLD_COMPONENT_JSX, translate=True)
        asset = bundle.get_assets()[0]
        component = render_component(asset['path'], props={'name': 'world!'}, to_static_markup=True)
        self.assertEqual(
            str(component),
            '<span>Hello world!</span>'
        )

    def test_can_render_a_component_in_jsx(self):
        component = render_component(HELLO_WORLD_COMPONENT_JSX, translate=True, to_static_markup=True)
        self.assertEqual(str(component), '<span>Hello </span>')

    def test_can_render_a_component_requiring_another_component(self):
        component = render_component(
            HELLO_WORLD_WRAPPER_COMPONENT,
            props={
                'name': 'world!',
                'numbers': [1, 2, 3, 4, 5],
            },
            translate=True,
            to_static_markup=True
        )
        self.assertEqual(str(component), '<div><span>Hello world!</span><span>10, 20, 30, 40, 50</span></div>')

    def test_can_render_a_component_to_a_string_with_props(self):
        component = render_component(
            HELLO_WORLD_COMPONENT_JSX,
            {'name': 'world!'},
            translate=True,
        )
        markup = str(component)
        self.assertNotEqual(markup, '<span>Hello world!</span>')
        self.assertIn('Hello ', markup)
        self.assertIn('world!', markup)

    def test_render_component_returns_a_rendered_component(self):
        component = render_component(
            HELLO_WORLD_COMPONENT_JSX,
            props={
                'name': 'world!'
            },
            translate=True,
            to_static_markup=True,
        )
        self.assertIsInstance(component, RenderedComponent)
        self.assertEqual(component.markup, '<span>Hello world!</span>')
        self.assertEqual(component.markup, str(component))
        if six.PY2:
            self.assertEqual(component.markup, unicode(component))

    def test_can_get_a_components_serialized_props(self):
        component = render_component(
            HELLO_WORLD_COMPONENT_JSX,
            props={
                'name': 'world!',
            },
            translate=True,
        )
        self.assertEqual(component.props, {'name': 'world!'})
        self.assertEqual(component.serialized_props, '{"name": "world!"}')
        self.assertEqual(component.render_props(), '{"name": "world!"}')

    def test_can_serialize_datetime_values_in_props(self):
        component = render_component(
            HELLO_WORLD_COMPONENT_JSX,
            props={
                'name': 'world!',
                'datetime': datetime.datetime(2015, 1, 2, 3, 4, 5, tzinfo=timezone.utc),
                'date': datetime.date(2015, 1, 2),
                'time': datetime.time(3, 4, 5),
            },
            translate=True,
        )
        deserialized = json.loads(component.serialized_props)
        self.assertEqual(
            deserialized,
            {
                'name': 'world!',
                'datetime': '2015-01-02T03:04:05Z',
                'date': '2015-01-02',
                'time': '03:04:05',
            }
        )

    def test_component_js_rendering_errors_raise_an_exception(self):
        self.assertRaises(ComponentRenderingError, render_component, ERROR_THROWING_COMPONENT)
        self.assertRaises(ComponentRenderingError, render_component, ERROR_THROWING_COMPONENT, to_static_markup=True)

    def test_components_with_syntax_errors_raise_exceptions(self):
        self.assertRaises(ComponentRenderingError, render_component, SYNTAX_ERROR_COMPONENT)
        self.assertRaises(ComponentRenderingError, render_component, SYNTAX_ERROR_COMPONENT, to_static_markup=True)

    def test_unserializable_props_raise_an_exception(self):
        self.assertRaises(
            TypeError,
            render_component,
            HELLO_WORLD_COMPONENT_JSX,
            props={'name': lambda: None}
        )
        self.assertRaises(
            TypeError,
            render_component,
            HELLO_WORLD_COMPONENT_JSX,
            props={'name': self}
        )

    def test_relative_paths_are_resolved_via_the_static_file_finder(self):
        component = render_component(STATIC_FILE_FINDER_COMPONENT, to_static_markup=True, translate=True)
        self.assertEqual(str(component), '<span>You found me.</span>')

    def test_missing_paths_throw_an_exception(self):
        self.assertRaises(ComponentSourceFileNotFound, render_component, '/path/to/nothing.jsx')
        # Ensure that relative paths are handled as well
        self.assertRaises(ComponentSourceFileNotFound, render_component, 'path/to/nothing.jsx')

    def test_rendered_components_which_are_bundled_have_access_to_their_bundle(self):
        bundled_component = render_component(HELLO_WORLD_COMPONENT_JS, to_static_markup=True)
        self.assertRaises(ComponentWasNotBundled, bundled_component.get_bundle)

        bundled_component = render_component(HELLO_WORLD_COMPONENT_JS, to_static_markup=True, bundle=True)
        self.assertIsInstance(bundled_component.get_bundle(), WebpackBundle)

        translated_component = render_component(HELLO_WORLD_COMPONENT_JS, to_static_markup=True, translate=True)
        self.assertIsInstance(translated_component.get_bundle(), WebpackBundle)

        watched_component = render_component(HELLO_WORLD_COMPONENT_JS, to_static_markup=True, watch_source=True)
        self.assertIsInstance(watched_component.get_bundle(), WebpackBundle)

    def test_bundled_components_can_get_access_to_their_variable(self):
        component = render_component(HELLO_WORLD_COMPONENT_JS, to_static_markup=True, bundle=True)
        self.assertEqual(component.get_var(), 'components__HelloWorld')

    def test_bundled_components_have_their_markup_wrapped_in_a_container(self):
        component = render_component(HELLO_WORLD_COMPONENT_JS, bundle=True)
        self.assertEqual(str(component), '<span id="reactComponent-components__HelloWorld">' + component.markup + '</span>')

    def test_bundled_components_can_render_mount_js(self):
        component = render_component(HELLO_WORLD_COMPONENT_JS, bundle=True)
        expected = \
"""
if (typeof React === 'undefined') throw new Error('Cannot find `React` global variable. Have you added a script element to this page which points to React?');
if (typeof components__HelloWorld === 'undefined') throw new Error('Cannot find component variable `components__HelloWorld`');
(function(React, component, containerId) {
  var props = null;
  var element = React.createElement(component, props);
  var container = document.getElementById(containerId);
  if (!container) throw new Error('Cannot find the container element `#reactComponent-components__HelloWorld` for component `components__HelloWorld`');
  React.render(element, container);
})(React, components__HelloWorld, 'reactComponent-components__HelloWorld');
"""
        self.assertEqual(component.render_mount_js(), expected)

    def test_bundled_components_can_render_mount_js_with_props(self):
        component = render_component(HELLO_WORLD_COMPONENT_JS, props={'name': 'world!'}, bundle=True)
        expected = \
"""
if (typeof React === 'undefined') throw new Error('Cannot find `React` global variable. Have you added a script element to this page which points to React?');
if (typeof components__HelloWorld === 'undefined') throw new Error('Cannot find component variable `components__HelloWorld`');
(function(React, component, containerId) {
  var props = {"name": "world!"};
  var element = React.createElement(component, props);
  var container = document.getElementById(containerId);
  if (!container) throw new Error('Cannot find the container element `#reactComponent-components__HelloWorld` for component `components__HelloWorld`');
  React.render(element, container);
})(React, components__HelloWorld, 'reactComponent-components__HelloWorld');
"""
        self.assertEqual(component.render_mount_js(), expected)

    def test_bundled_components_can_render_script_elements_with_the_bundle_and_mount_js(self):
        component = render_component(HELLO_WORLD_COMPONENT_JS, bundle=True)
        self.assertEqual(
            component.render_js(),
            '\n<script src="' + component.bundle.get_urls()[0] + '"></script>\n<script>\n' + component.render_mount_js() + '\n</script>\n',
        )

    def test_bundled_components_omit_react_and_react_addons(self):
        bundle = bundle_component(REACT_ADDONS_COMPONENT, translate=True)
        with open(bundle.get_assets()[0]['path'], 'r') as bundle_file:
            content = bundle_file.read()
        # A bit hacky, but seems to work
        self.assertNotIn('Facebook, Inc', content)