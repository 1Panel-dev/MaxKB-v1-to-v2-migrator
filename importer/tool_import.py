import os
import pickle
from functools import reduce
import shutil
import zipfile

from django.db.models import QuerySet
from system_manage.models import WorkspaceUserResourcePermission
from tools.models import Tool, ToolFolder, ToolScope, ToolType
from users.models import User

from commons.util import import_page, ImportQuerySet, import_check, rename, to_workspace_user_resource_permission


def extract_python_packages():
    """解压Python包到PIP_TARGET目录"""
    pip_target = os.environ.get('PIP_TARGET')
    if not pip_target:
        print("PIP_TARGET环境变量未设置，跳过Python包解压")
        return

    os.makedirs(pip_target, exist_ok=True)

    # 查找python-packages.zip文件
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
    zip_path = os.path.join(data_dir, 'python-packages.zip')

    if not os.path.exists(zip_path):
        print(f"Python包文件不存在: {zip_path}")
        return

    try:
        # 使用shutil.unpack_archive作为zipfile的替代方案
        shutil.unpack_archive(zip_path, pip_target)
        print(f"Python包已成功解压到: {pip_target}")
    except Exception as e:
        print(f"解压Python包时发生错误: {e}")


def to_v2_tool(instance):
    icon = (
        instance.get('icon')
        .replace('/ui/fx/', './tool/')
        .replace('/api/file/', './oss/file/')
        .replace('/ui/favicon.ico', '')
    )
    return Tool(
        id=instance.get('id'),
        user_id=instance.get('user'),
        name=instance.get('name'),
        desc=instance.get('desc'),
        code=instance.get('code'),
        input_field_list=instance.get('input_field_list'),
        init_field_list=instance.get('init_field_list'),
        icon=icon,
        is_active=instance.get('is_active'),
        scope=ToolScope.WORKSPACE,
        tool_type=ToolType.CUSTOM,
        template_id=instance.get('template_id'),
        folder_id='default',
        workspace_id='default',
        init_params=instance.get('init_params'),
        label=''
    )


def tool_import(file_list, source_name, current_page):
    for file in file_list:
        tool_list = pickle.loads(file.read_bytes())
        tool_model_list = [to_v2_tool(item) for item in tool_list if item.get('function_type') == 'PUBLIC']
        QuerySet(Tool).bulk_create(tool_model_list)

        # 删除授权相关数据
        QuerySet(WorkspaceUserResourcePermission).filter(
            target__in=[tool.get('id') for tool in tool_list]).delete()
        # 获取所有用户数据
        user_model_list = QuerySet(User).all()
        # 构建工具权限列表
        tool_permission_list = reduce(lambda x, y: [*x, *y], [
            [
                to_workspace_user_resource_permission(user_model.id, 'TOOL', tool.get('id'),
                                                      permission_list=(['MANAGE', 'VIEW'] if
                                                                       str(user_model.id) == str(tool.get('id')) else [
                                                          'VIEW'])) for user_model
                in
                user_model_list]
            if tool.get('permission_type') == 'PUBLIC' else [
                to_workspace_user_resource_permission(tool.get('user'), 'TOOL', tool.get('id'))]
            for
            tool in tool_list if tool.get('function_type') == 'PUBLIC'], [])
        # 插入授权数据
        QuerySet(WorkspaceUserResourcePermission).bulk_create(tool_permission_list)
        rename(file)


def check_tool_folder():
    if not QuerySet(ToolFolder).filter(id='default').exists():
        ToolFolder(id='default', name='根目录', desc='default', user_id=None, workspace_id='default').save()


def import_():
    check_tool_folder()

    # 解压Python包
    extract_python_packages()

    import_page(ImportQuerySet('function_lib'), 1, tool_import, "function_lib", "导入工具", check=import_check)


def check_tool_empty():
    return not QuerySet(Tool).filter(tool_type=ToolType.CUSTOM).exists()
