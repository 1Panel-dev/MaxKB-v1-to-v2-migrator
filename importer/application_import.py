# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application_import.py
    @date：2025/8/11 18:24
    @desc:
"""
import datetime
import json
import pickle
import re

from application.models import Application, ApplicationFolder, ApplicationVersion, ApplicationApiKey, \
    ApplicationAccessToken, ApplicationChatUserStats, Chat, ChatRecord
from application.serializers.application import ApplicationOperateSerializer
from django.db.models import QuerySet

from common.db.search import native_update
from knowledge.models import File

from commons.util import import_page, ImportQuerySet, import_check, rename, to_workspace_user_resource_permission, \
    preserve_time_fields
from system_manage.models import WorkspaceUserResourcePermission


def to_v2_node(node):
    node_type = node.get('type')
    if node_type == 'search-dataset-node':
        node['type'] = 'search-knowledge-node'
        node_data = node.get('properties').get('node_data')
        node_data['knowledge_id_list'] = node_data.pop('dataset_id_list')
        node_data['knowledge_setting'] = node_data.pop('dataset_setting')
        node_data['show_knowledge'] = False

    elif node_type == 'function-node':
        node['type'] = 'tool-node'

    elif node_type == 'function-lib-node':
        node['type'] = 'tool-lib-node'
        node_data = node.get('properties').get('node_data')
        node_data['tool_lib_id'] = node_data.pop('function_lib_id')
    elif node_type == 'application-node':
        node_data = node.get('properties').get('node_data')
        node_data['icon'] = get_v2_icon(node_data['icon'])
    elif node_type == 'reranker-node':
        node_data = node.get('properties').get('node_data')
        node_data['show_knowledge'] = False
    return node


def get_v2_icon(icon):
    if icon == '/ui/favicon.ico':
        return "./favicon.ico"
    elif icon.startswith('/api/image/'):
        return icon.replace("/api/image/", './oss/file/')
    elif icon.startswith('/api/file/'):
        return icon.replace("/api/file/", './oss/file/')
    return icon


def to_v2_workflow(workflow):
    nodes = workflow.get('nodes')
    if nodes is not None:
        nodes = [to_v2_node(node) for node in nodes]
        return {**workflow, 'nodes': nodes}
    return workflow


def to_v2_icon(icon, application_id):
    if icon == '/ui/favicon.ico':
        return "./favicon.ico"
    elif icon.startswith('/api/image/'):
        QuerySet(File).filter(id=icon.replace("/api/image/", '')).update(source_type='APPLICATION',
                                                                         source_id=application_id)
        return icon.replace("/api/image/", './oss/file/')
    elif icon.startswith('/api/file/'):
        QuerySet(File).filter(id=icon.replace("/api/file/", '')).update(source_type='APPLICATION',
                                                                        source_id=application_id)
        return icon.replace("/api/file/", './oss/file/')
    return icon


def to_v2_application(application):
    return Application(id=application.get('id'),
                       workspace_id='default',
                       folder_id='default',
                       is_publish=True if application.get('type') == 'SIMPLE' else False,
                       name=application.get('name'),
                       desc=application.get('desc'),
                       prologue=application.get('prologue'),
                       dialogue_number=application.get('dialogue_number'),
                       user_id=application.get('user'),
                       model_id=application.get('model'),
                       knowledge_setting=application.get('dataset_setting'),
                       model_setting=application.get('model_setting'),
                       model_params_setting=application.get('model_params_setting'),
                       tts_model_params_setting=application.get('tts_model_params_setting'),
                       problem_optimization=application.get('problem_optimization'),
                       icon=to_v2_icon(application.get('icon'), application.get('id')),
                       work_flow=to_v2_workflow(application.get('work_flow')),
                       type=application.get('type'),
                       problem_optimization_prompt=application.get('problem_optimization_prompt'),
                       tts_model_id=application.get('tts_model'),
                       stt_model_id=application.get('stt_model_id'),
                       tts_model_enable=application.get('tts_model_enable'),
                       stt_model_enable=application.get('stt_model_enable'),
                       tts_type=application.get('tts_type'),
                       tts_autoplay=application.get('tts_autoplay'),
                       stt_autosend=application.get('stt_autosend'),
                       clean_time=application.get('clean_time'),
                       publish_time=application.get('create_time'),
                       file_upload_enable=application.get('file_upload_enable'),
                       file_upload_setting=application.get('file_upload_setting'),
                       create_time=application.get('create_time'),
                       update_time=application.get('update_time'))


def application_import(file_list, source_name, current_page):
    for file in file_list:
        application_list = pickle.loads(file.read_bytes())
        application_model_list = [to_v2_application(app) for app in application_list]
        # 删除数据
        QuerySet(Application).filter(id__in=[app.id for app in application_model_list]).delete()
        # 插入应用配置
        QuerySet(Application).bulk_create(application_model_list)
        simple_app_version_list = [to_v2_simple_application_version(app) for app in application_model_list if
                                   app.type == 'SIMPLE']
        # 删除数据
        QuerySet(ApplicationVersion).filter(
            id__in=[simple_app_version.id for simple_app_version in simple_app_version_list])
        # 插入简易版本发布信息
        QuerySet(ApplicationVersion).bulk_create(simple_app_version_list)

        for application_model in application_model_list:
            # 删除授权相关数据
            QuerySet(WorkspaceUserResourcePermission).filter(
                target=application_model.id,
                user_id=application_model.user_id
            ).delete()

        # 插入授权数据
        application_permission_list = [
            to_workspace_user_resource_permission(application_model.user_id, 'APPLICATION', application_model.id) for
            application_model in application_model_list]
        QuerySet(WorkspaceUserResourcePermission).bulk_create(application_permission_list)
        rename(file)


def to_v2_simple_application_version(application):
    application_version = ApplicationVersion(work_flow=application.work_flow, application=application,
                                             name=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                             publish_user_id=application.user.id,
                                             publish_user_name=application.user.username,
                                             workspace_id='default')
    ApplicationOperateSerializer.reset_application_version(application_version, application)
    return application_version


def to_v2_application_version(application_version, application_dict):
    application = application_dict.get(application_version.get('application'))
    if application is None:
        return None
    application_model_version = ApplicationVersion(id=application_version.get('id')
                                                   , application_id=application_version.get('application'),
                                                   name=application_version.get('name'),
                                                   publish_user_id=application_version.get('publish_user_id'),
                                                   publish_user_name=application_version.get('publish_user_name'),
                                                   work_flow=application_version.get('work_flow'),
                                                   )
    ApplicationOperateSerializer.reset_application_version(application_model_version, application)
    return application_model_version


def application_version_import(file_list, source_name, current_page):
    for file in file_list:
        application_version_list = pickle.loads(file.read_bytes())
        # 查询到对应的应用
        application_list = QuerySet(Application).filter(
            id__in=list(
                set([application_version.get('application') for application_version in application_version_list])))
        # 根据id分组
        application_dict = {app.id: app for app in application_list}
        # 转换为v2的application_version
        app_version_list = [a_v for a_v in [to_v2_application_version(app_version, application_dict) for app_version in
                                            application_version_list] if a_v is not None]
        # 删除数据
        QuerySet(ApplicationVersion).filter(id__in=[app_version.id for app_version in app_version_list]).delete()
        # 插入数据
        QuerySet(ApplicationVersion).bulk_create(app_version_list)
        rename(file)


def to_v2_application_api_key(application_api_key):
    return ApplicationApiKey(
        id=application_api_key.get('id'),
        secret_key=application_api_key.get('secret_key'),
        user_id=application_api_key.get('user'),
        application_id=application_api_key.get('application'),
        is_active=application_api_key.get('is_active'),
        allow_cross_domain=application_api_key.get('allow_cross_domain'),
        cross_domain_list=application_api_key.get('cross_domain_list'),
        workspace_id='default'
    )


def application_api_key_import(file_list, source_name, current_page):
    for file in file_list:
        application_api_key_list = pickle.loads(file.read_bytes())
        application_api_key_model_list = [to_v2_application_api_key(application_api_key) for application_api_key in
                                          application_api_key_list]
        QuerySet(ApplicationApiKey).filter(id__in=[a.id for a in application_api_key_model_list]).delete()

        QuerySet(ApplicationApiKey).bulk_create(application_api_key_model_list)
        rename(file)


def to_v2_application_access_token(application_access_token):
    return ApplicationAccessToken(
        application_id=application_access_token.get('application'),
        access_token=application_access_token.get('access_token'),
        is_active=application_access_token.get('is_active'),
        access_num=application_access_token.get('access_num'),
        white_active=application_access_token.get('white_active'),
        white_list=application_access_token.get('white_list'),
        show_source=application_access_token.get('show_source'),
        show_exec=False,
        authentication=False,
        authentication_value={},
        language=application_access_token.get('language')
    )


def application_access_token_import(file_list, source_name, current_page):
    for file in file_list:
        application_access_token_list = pickle.loads(file.read_bytes())
        application_access_token_model_list = [to_v2_application_access_token(application_access_token) for
                                               application_access_token in application_access_token_list]
        # 删除
        QuerySet(ApplicationAccessToken).filter(
            application_id__in=[application_access_token_model.application_id for application_access_token_model in
                                application_access_token_model_list]).delete()
        # 插入数据
        QuerySet(ApplicationAccessToken).bulk_create(application_access_token_model_list)
        rename(file)


def to_v2_application_chat_user_stats(application_public_access_client):
    return ApplicationChatUserStats(
        id=application_public_access_client.get('id'),
        chat_user_id=application_public_access_client.get('client_id'),
        chat_user_type="ANONYMOUS_USER",
        application_id=application_public_access_client.get('application'),
        access_num=application_public_access_client.get('access_num'),
        intraday_access_num=application_public_access_client.get('intraday_access_num')
    )


def application_public_access_client_import(file_list, source_name, current_page):
    for file in file_list:
        application_public_access_client_list = pickle.loads(file.read_bytes())
        application_chat_user_stats_model_list = [
            to_v2_application_chat_user_stats(application_public_access_client) for application_public_access_client in
            application_public_access_client_list]
        QuerySet(ApplicationChatUserStats).filter(
            id__in=[application_chat_user_stats_model.id for application_chat_user_stats_model in
                    application_chat_user_stats_model_list]).delete()
        QuerySet(ApplicationChatUserStats).bulk_create(application_chat_user_stats_model_list)
        rename(file)


def to_v2_asker(asker):
    if isinstance(asker, dict):
        return {**asker, 'username': asker.get('user_name')}
    return {'username': str(asker)}


def to_v2_chat(chat):
    return Chat(id=chat.get('id'),
                application_id=chat.get('application'),
                abstract=chat.get('abstract'),
                chat_user_id=chat.get('client_id'),
                chat_user_type='ANONYMOUS_USER',
                asker=to_v2_asker(chat.get('asker')),
                is_deleted=chat.get('is_deleted'),
                meta={},
                star_num=0,
                trample_num=0,
                chat_record_count=0,
                mark_sum=0,
                create_time=chat.get('create_time'),
                update_time=chat.get('update_time'))


@preserve_time_fields(Chat, "create_time", "update_time")
def application_chat_import(file_list, source_name, current_page):
    for file in file_list:
        chat_list = pickle.loads(file.read_bytes())
        chat_model_list = [to_v2_chat(chat) for chat in chat_list]
        QuerySet(Chat).filter(id__in=[chat_model.id for chat_model in chat_model_list]).delete()
        QuerySet(Chat).bulk_create(chat_model_list)
        rename(file)


uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'


def reset_to_v2_str(v1_data_str: str):
    result = v1_data_str.replace("search-dataset-node", 'search-knowledge-node')
    result = result.replace("function-node", "tool-node")
    result = result.replace("function-lib-node", "tool-lib-node")
    result = re.sub(rf'/api/file/({uuid_pattern})', r'./oss/file/\1', result)
    result = re.sub(rf'/api/image/({uuid_pattern})', r'./oss/file/\1', result)
    return result


def reset_application_chat_record_details(details: dict):
    details_str = json.dumps(details)
    result = reset_to_v2_str(details_str)
    return json.loads(result)


def reset_application_chat_record_answer_text_list(answer_text_list):
    answer_text_list_str = json.dumps(answer_text_list)
    result = re.sub(rf'/api/file/({uuid_pattern})', r'./oss/file/\1', answer_text_list_str)
    result = re.sub(rf'/api/image/({uuid_pattern})', r'./oss/file/\1', result)
    return json.loads(result)


def reset_application_chat_record_answer_text(answer_text):
    result = re.sub(rf'/api/file/({uuid_pattern})', r'./oss/file/\1', answer_text)
    result = re.sub(rf'/api/image/({uuid_pattern})', r'./oss/file/\1', result)
    return result[0:40960]


def update_chat_chat_record_count(file_list, source_name, current_page):
    sql = """
   update application_chat
    set chat_record_count=(select count("id") from application_chat_record where chat_id = application_chat.id),
        star_num         =(select count("id")
                       from application_chat_record
                       where chat_id = application_chat.id and vote_status = '0'),
        mark_sum         =(select count("id")
                       from application_chat_record
                       where chat_id = application_chat.id and vote_status = '1')

    """
    for file in file_list:
        chat_list = pickle.loads(file.read_bytes())
        native_update(QuerySet(Chat).filter(id__in=[c.get('id') for c in chat_list]), sql)


def to_v2_chat_record(chat_record):
    return ChatRecord(
        id=chat_record.get('id'),
        chat_id=chat_record.get('chat'),
        vote_status=chat_record.get('vote_status'),
        problem_text=chat_record.get('problem_text'),
        answer_text=reset_application_chat_record_answer_text(chat_record.get('answer_text', '') or ''),
        answer_text_list=reset_application_chat_record_answer_text_list(chat_record.get('answer_text_list')),
        message_tokens=chat_record.get('message_tokens'),
        answer_tokens=chat_record.get('answer_tokens'),
        const=chat_record.get('const'),
        details=reset_application_chat_record_details(chat_record.get('details')),
        improve_paragraph_id_list=chat_record.get('improve_paragraph_id_list'),
        run_time=chat_record.get('run_time'),
        index=chat_record.get('index'),
        create_time=chat_record.get('create_time'),
        update_time=chat_record.get('update_time')
    )


@preserve_time_fields(ChatRecord, "create_time", "update_time")
def application_chat_record_import(file_list, source_name, current_page):
    for file in file_list:
        chat_record_list = pickle.loads(file.read_bytes())
        chat_record_model_list = [to_v2_chat_record(chat_record) for chat_record in chat_record_list]
        QuerySet(ChatRecord).filter(
            id__in=[chat_record_model.id for chat_record_model in chat_record_model_list]).delete()
        QuerySet(ChatRecord).bulk_create(chat_record_model_list)
        rename(file)


def check_application_folder():
    if not QuerySet(ApplicationFolder).filter(id='default').exists():
        ApplicationFolder(id='default', name='根目录', desc='default', user_id=None, workspace_id='default').save()


def update_application_publish(file_list, source_name, current_page):
    sql = """
    update application
    set is_publish = EXISTS(select 1 from application_version where application_id = application.id)
    """
    for file in file_list:
        application_list = pickle.loads(file.read_bytes())
        native_update(QuerySet(Application).filter(id__in=[a.get('id') for a in application_list]), sql)


def import_():
    check_application_folder()
    import_page(ImportQuerySet('application'), 1, application_import, "application", "导入应用", check=import_check)
    import_page(ImportQuerySet('application_version'), 1, application_version_import, 'application_version',
                "导入应用版本",
                check=import_check)
    import_page(ImportQuerySet('application'), 1, update_application_publish, 'application',
                "修改应用发布状态",
                check=lambda source_name, current_page: True)
    import_page(ImportQuerySet('application_api_key'), 1, application_api_key_import, 'application_api_key',
                "导入应用api key",
                check=import_check)
    import_page(ImportQuerySet('application_access_token'), 1, application_access_token_import,
                'application_access_token',
                "导入应用访问限制配置",
                check=import_check)
    import_page(ImportQuerySet('application_public_access_client'), 1, application_public_access_client_import,
                'application_public_access_client',
                "导入应用客户端信息",
                check=import_check)
    import_page(ImportQuerySet('chat'), 1, application_chat_import,
                'chat',
                "导入对话日志",
                check=import_check)
    import_page(ImportQuerySet('chat_record'), 1, application_chat_record_import,
                'chat_record',
                "导入对话日志记录",
                check=import_check)
    import_page(ImportQuerySet('chat'), 1, update_chat_chat_record_count,
                'chat',
                "处理对话日志数据",
                check=lambda source_name, current_page: True)


def check_application_empty():
    return not QuerySet(Application).exists()
