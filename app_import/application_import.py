# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application_import.py
    @date：2025/8/11 18:24
    @desc:
"""
import pickle

from django.db.models import QuerySet

from application.models import Application, ApplicationFolder
from commons.util import page, ImportQuerySet, import_check, rename


def to_v2_node(node):
    node_type = node.get('type')
    if node_type == 'search-dataset-node':
        node['type'] = 'search-knowledge-node'
        node_data = node.properties.get('node_data')
        node_data['knowledge_id_list'] = node_data.pop('dataset_id_list')
        node_data['knowledge_setting'] = node_data.pop('dataset_setting')
        node_data['show_knowledge'] = True

    elif node_type == 'function-node':
        node['type'] = 'tool-node'

    elif node_type == 'function-lib-node':
        node['type'] = 'tool-lib-node'
        node_data = node.properties.get('node_data')
        node_data['tool_lib_id'] = node_data.pop('function_lib_id')
    return node


def to_v2_workflow(workflow):
    nodes = workflow.get('nodes')
    nodes = [to_v2_node(node) for node in nodes]
    return {**workflow, 'nodes': nodes}


def to_v2_application(application):
    return Application(id=application.get('id'),
                       workspace_id='default',
                       folder_id='default',
                       is_publish=True,
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
                       icon=application.get('icon'),
                       work_flow=application.get('work_flow'),
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
        QuerySet(Application).bulk_create(application_model_list)
        rename(file)


def check_application_folder():
    if not QuerySet(ApplicationFolder).filter(id='default').exists():
        ApplicationFolder(id='default', name='根目录', desc='default', user_id=None, workspace_id='default').save()


def import_():
    check_application_folder()
    page(ImportQuerySet('application'), 1, application_import, "application", "导入应用", check=import_check)
