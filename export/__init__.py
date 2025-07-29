# coding=utf-8
"""
    @project: MaxKB-v1-to-v2-migrator
    @Author：虎虎
    @file： __init__.py
    @date：2025/7/28 14:34
    @desc:
"""
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartdoc.settings')
django.setup()


def export():
    from .application_export import export as _export
    from .knowledge_export import export as knowledge_export
    from .util import zip_folder
    _export()
    knowledge_export()
    zip_folder()
