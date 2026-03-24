# coding=utf-8
"""
    @project: MaxKB-v1-to-v2-migrator
    @Author：虎虎
    @file： application.py
    @date：2025/7/28 14:33
    @desc:
"""
from application.models import Application, WorkFlowVersion, Chat, ChatRecord, ApplicationDatasetMapping
from application.models.api_key_model import ApplicationApiKey, ApplicationAccessToken, ApplicationPublicAccessClient
from django.db.models import QuerySet

from commons.util import page, save_batch_file


def application_export(application_list, source_name, current_page):
    batch_list = [
        {
            'id': a.id,
            'name': a.name,
            'desc': a.desc,
            'prologue': a.prologue,
            'dialogue_number': a.dialogue_number,
            'user': a.user_id,
            'model': a.model_id,
            'dataset_setting': a.dataset_setting,
            'model_setting': a.model_setting,
            'model_params_setting': a.model_params_setting,
            'tts_model_params_setting': a.tts_model_params_setting,
            'problem_optimization': a.problem_optimization,
            'icon': a.icon,
            'work_flow': a.work_flow,
            'type': a.type,
            'problem_optimization_prompt': a.problem_optimization_prompt,
            'tts_model': a.tts_model_id,
            'stt_model_id': a.stt_model_id,
            'tts_model_enable': a.tts_model_enable,
            'stt_model_enable': a.stt_model_enable,
            'tts_type': a.tts_type,
            'tts_autoplay': a.tts_autoplay,
            'stt_autosend': a.stt_autosend,
            'clean_time': a.clean_time,
            'file_upload_enable': a.file_upload_enable,
            'file_upload_setting': a.file_upload_setting,
            'create_time': a.create_time,
            'update_time': a.update_time,
        }
        for a in application_list
    ]
    save_batch_file(batch_list, source_name, current_page)


def application_workflow_version_export(workflow_version_list, source_name, current_page):
    batch_list = [
        {
            'id': v.id,
            'application': v.application_id,
            'name': v.name,
            'publish_user_id': v.publish_user_id,
            'publish_user_name': v.publish_user_name,
            'work_flow': v.work_flow,
            'create_time': v.create_time,
            'update_time': v.update_time,
        }
        for v in workflow_version_list
    ]
    save_batch_file(batch_list, source_name, current_page)


def application_api_key_export(application_api_key_list, source_name, current_page):
    batch_list = [
        {
            'id': k.id,
            'secret_key': k.secret_key,
            'user': k.user_id,
            'application': k.application_id,
            'is_active': k.is_active,
            'allow_cross_domain': k.allow_cross_domain,
            'cross_domain_list': k.cross_domain_list,
            'create_time': k.create_time,
            'update_time': k.update_time,
        }
        for k in application_api_key_list
    ]
    save_batch_file(batch_list, source_name, current_page)


def application_access_token_export(application_access_token_list, source_name, current_page):
    batch_list = [
        {
            'application': t.application_id,
            'access_token': t.access_token,
            'is_active': t.is_active,
            'access_num': t.access_num,
            'white_active': t.white_active,
            'white_list': t.white_list,
            'show_source': t.show_source,
            'language': t.language,
            'create_time': t.create_time,
            'update_time': t.update_time,
        }
        for t in application_access_token_list
    ]
    save_batch_file(batch_list, source_name, current_page)


def application_public_access_client_export(application_public_access_client_list, source_name, current_page):
    batch_list = [
        {
            'id': c.id,
            'client_id': c.client_id,
            'application': c.application_id,
            'access_num': c.access_num,
            'intraday_access_num': c.intraday_access_num,
            'create_time': c.create_time,
            'update_time': c.update_time,
        }
        for c in application_public_access_client_list
    ]
    save_batch_file(batch_list, source_name, current_page)


def chat_export(chat_list, source_name, current_page):
    batch_list = [
        {
            'id': c.id,
            'application': c.application_id,
            'abstract': c.abstract,
            'asker': c.asker,
            'client_id': c.client_id,
            'is_deleted': c.is_deleted,
            'create_time': c.create_time,
            'update_time': c.update_time,
        }
        for c in chat_list
    ]
    save_batch_file(batch_list, source_name, current_page)


def chat_record_export(chat_record_list, source_name, current_page):
    batch_list = [
        {
            'id': r.id,
            'chat': r.chat_id,
            'vote_status': r.vote_status,
            'problem_text': r.problem_text,
            'answer_text': r.answer_text,
            'answer_text_list': r.answer_text_list,
            'message_tokens': r.message_tokens,
            'answer_tokens': r.answer_tokens,
            'const': r.const,
            'details': r.details,
            'improve_paragraph_id_list': r.improve_paragraph_id_list,
            'run_time': r.run_time,
            'index': r.index,
            'create_time': r.create_time,
            'update_time': r.update_time,
        }
        for r in chat_record_list
    ]
    save_batch_file(batch_list, source_name, current_page)


def application_dataset_mapping_export(application_dataset_mapping_list, source_name, current_page):
    batch_list = [
        {
            'id': m.id,
            'application': m.application_id,
            'dataset': m.dataset_id,
            'create_time': m.create_time,
            'update_time': m.update_time,
        }
        for m in application_dataset_mapping_list
    ]
    save_batch_file(batch_list, source_name, current_page)


def export():
    page(QuerySet(Application), 100, application_export, "application", "导出应用")
    page(QuerySet(WorkFlowVersion), 100, application_workflow_version_export, "application_version",
         "导出应用工作流历史版本")
    page(QuerySet(ApplicationApiKey), 100, application_api_key_export, "application_api_key", "导出应用Apikey")
    page(QuerySet(ApplicationAccessToken), 100, application_access_token_export, "application_access_token",
         "导出应用访问限制配置",
         primary_key="application_id")
    page(QuerySet(ApplicationPublicAccessClient), 100, application_public_access_client_export,
         "application_public_access_client",
         "导出应用客户端信息")
    page(QuerySet(Chat), 500, chat_export, "chat", "导出对话日志")
    page(QuerySet(ChatRecord), 1000, chat_record_export, "chat_record", "导出对话日志记录")
    page(QuerySet(ApplicationDatasetMapping), 100, application_dataset_mapping_export, "application_dataset_mapping",
         "导出应用与知识库的关联关系")
