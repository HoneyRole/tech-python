#!/usr/bin/env python

import subprocess
import os
import sys
import django

print('\n' + '-' * 80)
print('Running tests without django')
print('-' * 80)

subprocess.call(('nosetests', '--nocapture'))

print('\n' + '-' * 80)
print('Running tests with django')
print('-' * 80)

os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
if hasattr(django, 'setup'):  # Only compatible with Django >= 1.7
    django.setup()

# For Django 1.6, need to import after setting DJANGO_SETTINGS_MODULE.
from django.conf import settings
from django.test.utils import get_runner

TestRunner = get_runner(settings)
test_runner = TestRunner()
failures = test_runner.run_tests(['tests'])
sys.exit(bool(failures))