# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： model_export.py
    @date：2025/7/29 16:12
    @desc:
"""

from django.db.models import QuerySet
from rest_framework import serializers
from commons.util import page, save_batch_file

from xpack.models import ApplicationSetting, Platform, PlatformUser, PlatformSource, SystemApiKey, AuthConfig, \
    SystemParams


class ApplicationSettingModel(serializers.ModelSerializer):
    class Meta:
        model = ApplicationSetting
        fields = "__all__"


class PlatformModel(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = "__all__"


class PlatformUserModel(serializers.ModelSerializer):
    class Meta:
        model = PlatformUser
        fields = "__all__"


class PlatformSourceModel(serializers.ModelSerializer):
    class Meta:
        model = PlatformSource
        fields = "__all__"


class SystemApiKeyModel(serializers.ModelSerializer):
    class Meta:
        model = SystemApiKey
        fields = "__all__"


class AuthConfigModel(serializers.ModelSerializer):
    class Meta:
        model = AuthConfig
        fields = "__all__"


class SystemParamsModel(serializers.ModelSerializer):
    class Meta:
        model = SystemParams
        fields = "__all__"


def application_setting_export(application_setting_list, source_name, current_page):
    batch_list = ApplicationSettingModel(list(application_setting_list), many=True).data
    save_batch_file(batch_list, source_name, current_page)


def platform_export(platform_list, source_name, current_page):
    batch_list = PlatformModel(list(platform_list), many=True).data
    save_batch_file(batch_list, source_name, current_page)


def platform_user_export(platform_user_list, source_name, current_page):
    batch_list = PlatformUserModel(list(platform_user_list), many=True).data
    save_batch_file(batch_list, source_name, current_page)


def platform_source_export(platform_source_list, source_name, current_page):
    batch_list = PlatformSourceModel(list(platform_source_list), many=True).data
    save_batch_file(batch_list, source_name, current_page)


def system_api_key_export(system_api_key_list, source_name, current_page):
    batch_list = SystemApiKeyModel(list(system_api_key_list), many=True).data
    save_batch_file(batch_list, source_name, current_page)


def auth_config_export(auth_config_list, source_name, current_page):
    batch_list = AuthConfigModel(list(auth_config_list), many=True).data
    save_batch_file(batch_list, source_name, current_page)


def system_params_export(system_params_list, source_name, current_page):
    batch_list = SystemParamsModel(list(system_params_list), many=True).data
    save_batch_file(batch_list, source_name, current_page)


def export():
    page(QuerySet(ApplicationSetting), 100, application_setting_export, "application_setting", "导出应用设置",
         primary_key="application_id")
    page(QuerySet(Platform), 100, platform_export, "platform", "导出三方平台")
    page(QuerySet(PlatformUser), 100, platform_user_export, "platform_user", "导出三方平台用户")
    page(QuerySet(PlatformSource), 100, platform_source_export, "platform_source", "导出认证三方平台")
    page(QuerySet(SystemApiKey), 100, system_api_key_export, "system_api_key", "导出系统api密钥")
    page(QuerySet(AuthConfig), 100, auth_config_export, "auth_config", "导出认证配置")
    page(QuerySet(SystemParams), 100, system_params_export, "system_params", "导出系统参数")
