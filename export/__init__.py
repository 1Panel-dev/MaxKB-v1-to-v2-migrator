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
    from .setting_export import export as setting_export
    from .function_lib import export as function_export
    from commons.util import zip_folder
    from commons.util import contains_xpack
    from commons.util import base_version

    # 只能导出 v1.10.10-lts (build at 2025-08-21T13:49, commit: 4c878b0)
    version = os.environ.get('MAXKB_VERSION', '')
    if base_version(version) != 'v1.10.10-lts':
        print(f"当前版本 {version} 不是 v1.10.10-lts 版本，不能导出数据！")
        return

    _export()
    knowledge_export()
    function_export()
    setting_export()

    if contains_xpack():
        from xpack.serializers.license_serializers import LicenseSerializers
        from smartdoc.urls import xpack_cache
        LicenseSerializers().refresh()
        if xpack_cache.set('XPACK_LICENSE_IS_VALID', False, None):
            from .xpack_export import export as xpack_export
            xpack_export()

    zip_folder()