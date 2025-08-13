import pickle

from django.db.models import QuerySet

from commons.util import page, ImportQuerySet, import_check, rename
from tools.models import Tool, ToolFolder, ToolScope, ToolType


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
        rename(file)


def check_tool_folder():
    if not QuerySet(ToolFolder).filter(id='default').exists():
        ToolFolder(id='default', name='根目录', desc='default', user_id=None, workspace_id='default').save()


def import_():
    check_tool_folder()

    page(ImportQuerySet('function_lib'), 1, tool_import, "function_lib", "导入工具", check=import_check)
