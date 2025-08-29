import pickle
from functools import reduce

from django.db.models import QuerySet

from commons.util import import_page, ImportQuerySet, import_check, rename, to_workspace_user_resource_permission
from system_manage.models import WorkspaceUserResourcePermission
from tools.models import Tool, ToolFolder, ToolScope, ToolType
from users.models import User


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
                                                      permission_list=['MANAGE'] if
                                                      str(user_model.id) == tool.get('id') else ['VIEW']) for user_model
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

    import_page(ImportQuerySet('function_lib'), 1, tool_import, "function_lib", "导入工具", check=import_check)


def check_tool_empty():
    return not QuerySet(Tool).filter(tool_type=ToolType.CUSTOM).exists()