from setuptools import setup

VERSION = '0.8.0'

setup(
    name='django-react',
    version=VERSION,
    packages=['django_react'],
    package_data={
        'django_react': [
            'render_server.js',
            'renderer.js',
            'package.json',
            'templates/django_react/*.html',
        ]
    },
    install_requires=[
        'django',
        'django-node == 2.2.1',
        'django-webpack == 2.0.2',
        'requests >= 2.5.1',
    ],
    description='Render and bundle React components from a Django application',
    long_description='Documentation at https://github.com/markfinger/django-react',
    author='Mark Finger',
    author_email='markfinger@gmail.com',
    url='https://github.com/markfinger/django-react',
)