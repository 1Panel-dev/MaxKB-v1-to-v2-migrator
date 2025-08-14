# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： __init__.py.py
    @date：2025/7/28 16:33
    @desc:
"""
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maxkb.settings')
django.setup()


def app_import():
    from commons.util import un_zip
    from .application_import import import_ as application_import
    from .setting_import import import_ as setting_import
    from .file_import import import_ as file_import
    from .knowledge_import import import_ as knowledge_import
    from .tool_import import import_ as tool_import

    un_zip()
    file_import()
    setting_import()
    application_import()
    knowledge_import()
    tool_import()
    from .xpack_import import import_ as xpack_import
    xpack_import()
