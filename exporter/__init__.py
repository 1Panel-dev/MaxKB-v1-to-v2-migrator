# coding=utf-8
"""
    @project: MaxKB-v1-to-v2-migrator
    @Author：虎虎
    @file： __init__.py
    @date：2025/7/28 14:34
    @desc:
"""
import os
import sys
import time
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartdoc.settings')
django.setup()


def _timed(label, fn):
    t0 = time.time()
    fn()
    print(f"[{label}] 耗时: {time.time() - t0:.1f}s")


def export():
    from .application_export import export as _export
    from .knowledge_export import export as knowledge_export
    from .setting_export import export as setting_export
    from .function_lib import export as function_export
    from commons.util import zip_folder
    from commons.util import contains_xpack
    from commons.util import ver_tuple

    # 只能导出 v1.10.10-lts (build at 2025-08-21T13:49, commit: 4c878b0) 及以上版本的数据
    version = os.environ.get('MAXKB_VERSION', '')
    if ver_tuple(version) < ver_tuple('v1.10.10-lts'):
        print(f"当前版本 {version} 不是 v1.10.10-lts 及以上版本，不能导出数据！")
        sys.exit(1)

    export_start = time.time()

    _timed("导出应用", _export)
    _timed("导出知识库", knowledge_export)
    _timed("导出函数库", function_export)
    _timed("导出系统设置", setting_export)

    if contains_xpack():
        from xpack.serializers.license_serializers import LicenseSerializers
        from smartdoc.urls import xpack_cache
        LicenseSerializers().refresh()
        if xpack_cache.get('XPACK_LICENSE_IS_VALID'):
            from .xpack_export import export as xpack_export
            _timed("导出 xpack", xpack_export)

    print(f"\n导出总耗时: {time.time() - export_start:.1f}s")

    print("\n正在打包迁移数据...")
    t0 = time.time()
    zip_folder()
    print(f"迁移数据打包完成，耗时: {time.time() - t0:.1f}s")
