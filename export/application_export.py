# coding=utf-8
"""
    @project: MaxKB-v1-to-v2-migrator
    @Author：虎虎
    @file： application.py
    @date：2025/7/28 14:33
    @desc:
"""
from django.db.models import QuerySet
from rest_framework import serializers

from application.models import Application, WorkFlowVersion, Chat, ChatRecord, ApplicationDatasetMapping
from application.models.api_key_model import ApplicationApiKey, ApplicationAccessToken, ApplicationPublicAccessClient
from .util import page, save_batch_file


class ApplicationModel(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = "__all__"


class ApplicationVersionModel(serializers.ModelSerializer):
    class Meta:
        model = WorkFlowVersion
        fields = "__all__"


class ApplicationApiKeyModel(serializers.ModelSerializer):
    class Meta:
        model = ApplicationApiKey
        fields = "__all__"


class ApplicationAccessTokenModel(serializers.ModelSerializer):
    class Meta:
        model = ApplicationAccessToken
        fields = "__all__"


class ApplicationPublicAccessClientModel(serializers.ModelSerializer):
    class Meta:
        model = ApplicationPublicAccessClient
        fields = "__all__"


class ChatModel(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = "__all__"


class ChatRecordModel(serializers.ModelSerializer):
    class Meta:
        model = ChatRecord
        fields = "__all__"


class ApplicationDatasetMappingModel(serializers.ModelSerializer):
    class Meta:
        model = ApplicationDatasetMapping
        fields = "__all__"


def application_export(application_list, source_name, current_page):
    batch_list = [ApplicationModel(application).data for application in application_list]
    save_batch_file(batch_list, source_name, current_page)


def application_workflow_version_export(workflow_version_list, source_name, current_page):
    batch_list = [ApplicationVersionModel(version).data for version in workflow_version_list]
    save_batch_file(batch_list, source_name, current_page)


def application_api_key_export(application_api_key_list, source_name, current_page):
    batch_list = [ApplicationApiKeyModel(application_api_key).data for application_api_key in application_api_key_list]
    save_batch_file(batch_list, source_name, current_page)


def application_access_token_export(application_access_token_list, source_name, current_page):
    batch_list = [ApplicationAccessTokenModel(application_access_token).data for application_access_token in
                  application_access_token_list]
    save_batch_file(batch_list, source_name, current_page)


def application_public_access_client_export(application_public_access_client_list, source_name, current_page):
    batch_list = [ApplicationPublicAccessClientModel(application_public_access_client).data for
                  application_public_access_client in
                  application_public_access_client_list]
    save_batch_file(batch_list, source_name, current_page)


def chat_export(chat_list, source_name, current_page):
    batch_list = [ChatModel(chat).data for chat in chat_list]
    save_batch_file(batch_list, source_name, current_page)


def chat_record_export(chat_record_list, source_name, current_page):
    batch_list = [ChatRecordModel(chat_record).data for chat_record in chat_record_list]
    save_batch_file(batch_list, source_name, current_page)


def application_dataset_mapping_export(application_dataset_mapping_list, source_name, current_page):
    batch_list = [ApplicationDatasetMappingModel(application_dataset_mapping) for application_dataset_mapping in
                  application_dataset_mapping_list]
    save_batch_file(batch_list, source_name, current_page)


def export():
    page(QuerySet(Application), 50, application_export, "application", "导出应用")
    page(QuerySet(WorkFlowVersion), 50, application_workflow_version_export, "application_version",
         "导出应用工作流历史版本")
    page(QuerySet(ApplicationApiKey), 50, application_api_key_export, "application_api_key", "导出应用Apikey")
    page(QuerySet(ApplicationAccessToken), 50, application_access_token_export, "application_access_token",
         "导出应用访问限制配置",
         primary_key="application_id")
    page(QuerySet(ApplicationPublicAccessClient), 50, application_public_access_client_export,
         "application_public_access_client",
         "导出应用客户端信息")
    page(QuerySet(Chat), 50, chat_export, "chat", "导出对话日志")
    page(QuerySet(ChatRecord), 50, chat_record_export, "chat_record", "导出对话日志记录")
    page(QuerySet(ApplicationDatasetMapping), 50, application_dataset_mapping_export, "application_dataset_mapping",
         "导出应用与知识库的关联关系")
