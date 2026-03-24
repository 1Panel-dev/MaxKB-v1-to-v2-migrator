# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： model_export.py
    @date：2025/7/29 16:12
    @desc:
"""

from django.db.models import QuerySet
from commons.util import page, save_batch_file

from xpack.models import ApplicationSetting, Platform, PlatformUser, PlatformSource, SystemApiKey, AuthConfig, \
    SystemParams


def application_setting_export(application_setting_list, source_name, current_page):
    batch_list = [
        {
            'application': s.application_id,
            'show_history': s.show_history,
            'draggable': s.draggable,
            'show_guide': s.show_guide,
            'avatar': s.avatar,
            'float_icon': s.float_icon,
            'authentication': s.authentication,
            'authentication_value': s.authentication_value,
            'disclaimer': s.disclaimer,
            'disclaimer_value': s.disclaimer_value,
            'custom_theme': s.custom_theme,
            'user_avatar': s.user_avatar,
            'float_location': s.float_location,
            'show_avatar': s.show_avatar,
            'show_user_avatar': s.show_user_avatar,
            'create_time': s.create_time,
            'update_time': s.update_time,
        }
        for s in application_setting_list
    ]
    save_batch_file(batch_list, source_name, current_page)


def platform_export(platform_list, source_name, current_page):
    batch_list = [
        {
            'id': p.id,
            'application_id': p.application_id,
            'type': p.type,
            'config': p.config,
            'is_active': p.is_active,
            'create_time': p.create_time,
            'update_time': p.update_time,
        }
        for p in platform_list
    ]
    save_batch_file(batch_list, source_name, current_page)


def platform_user_export(platform_user_list, source_name, current_page):
    batch_list = [
        {
            'id': u.id,
            'user': u.user_id,
            'create_time': u.create_time,
            'update_time': u.update_time,
        }
        for u in platform_user_list
    ]
    save_batch_file(batch_list, source_name, current_page)


def platform_source_export(platform_source_list, source_name, current_page):
    batch_list = [
        {
            'id': ps.id,
            'platform': ps.platform,
            'config': ps.config,
            'is_active': ps.is_active,
            'is_valid': ps.is_valid,
            'create_time': ps.create_time,
            'update_time': ps.update_time,
        }
        for ps in platform_source_list
    ]
    save_batch_file(batch_list, source_name, current_page)


def system_api_key_export(system_api_key_list, source_name, current_page):
    batch_list = [
        {
            'id': k.id,
            'secret_key': k.secret_key,
            'user': k.user_id,
            'is_active': k.is_active,
            'allow_cross_domain': k.allow_cross_domain,
            'cross_domain_list': k.cross_domain_list,
            'create_time': k.create_time,
            'update_time': k.update_time,
        }
        for k in system_api_key_list
    ]
    save_batch_file(batch_list, source_name, current_page)


def auth_config_export(auth_config_list, source_name, current_page):
    batch_list = [
        {
            'id': ac.id,
            'auth_type': ac.auth_type,
            'config_data': ac.config_data,
            'is_active': ac.is_active,
        }
        for ac in auth_config_list
    ]
    save_batch_file(batch_list, source_name, current_page)


def system_params_export(system_params_list, source_name, current_page):
    batch_list = [
        {
            'id': sp.id,
            'param_key': sp.param_key,
            'param_value': sp.param_value,
        }
        for sp in system_params_list
    ]
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
