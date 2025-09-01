# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： __init__.py.py
    @date：2025/7/28 16:33
    @desc:
"""
import os
import sys

import django

from commons.util import contains_xpack
from django.core.cache import cache

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maxkb.settings')
django.setup()


def app_import():
    from commons.util import un_zip
    from .application_import import import_ as application_import, check_application_empty
    from .setting_import import import_ as setting_import
    from .file_import import import_ as file_import, check_file_empty
    from .knowledge_import import import_ as knowledge_import, check_knowledge_empty
    from .tool_import import import_ as tool_import, check_tool_empty
    from commons.util import base_version

    # 只能导入 v2.1.0
    version = os.environ.get('MAXKB_VERSION', '')
    if base_version(version) != 'v2.1.0':
        print(f"当前版本 {version} 不是 v2.1.0 版本，不能导入数据！")
        sys.exit(1)

    if contains_xpack():
        from xpack.serializers.license.license_serializers import LicenseSerializers
        from common.constants.cache_version import Cache_Version
        LicenseSerializers().refresh()
        version, get_key = Cache_Version.SYSTEM.value
        license_is_valid = cache.get(get_key('license_is_valid'), version=version)
        if not license_is_valid:
            print("当前版本没有授权，请导入 License 文件！")
            sys.exit(1)

    # 检查导入标记文件
    import_flag_file = os.path.join(os.path.dirname(__file__), '..', '.import_completed')

    # 如果没有导入标记，则检查是否是空环境
    if not os.path.exists(import_flag_file):
        if not check_knowledge_empty() or not check_file_empty() or not check_application_empty() or not check_tool_empty():
            print("当前数据库不是空环境，请确认后再导入数据！")
            sys.exit(1)
        print("首次导入检测通过，开始导入数据...")
    else:
        print("跳过空环境检查，直接导入数据...")

    print("正在解压迁移数据...")
    un_zip()
    print("迁移数据解压完成")

    # 创建导入完成标记文件
    with open(import_flag_file, 'w') as f:
        f.write(f"Import completed at {os.environ.get('MAXKB_VERSION', '')}")

    file_import()
    setting_import()
    application_import()
    knowledge_import()
    tool_import()
    if contains_xpack():
        from .xpack_import import import_ as xpack_import
        xpack_import()
    cache.clear()
