# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： user_import.py
    @date：2025/8/12 10:26
    @desc:
"""
import json
import pickle

import uuid_utils.compat as uuid

from application.models import ApplicationAccessToken
from common.constants.permission_constants import RoleConstants
from commons.util import import_page, ImportQuerySet, import_check, rename
from knowledge.models import File, FileSourceType
from maxkb.const import CONFIG
from role_setting.models import UserRoleRelation
from users.models import User
from xpack.models import PlatformUser, SystemApiKey, PlatformSource, SystemParams
from xpack.models.application_setting import ApplicationSetting
from xpack.models.platform import Platform
from system_manage.models import Log


def convert_image_path(image_path):
    """转换图片路径，将旧路径格式转换为新路径格式"""
    if image_path and image_path.startswith('/api/image/'):
        return './oss/file/' + image_path[len('/api/image/'):], image_path[len('./oss/file/'):]
    return image_path, None


def to_v2_application_setting(application_setting):
    avatar_value, avatar_id = convert_image_path(application_setting.get('avatar'))
    float_icon_value, float_icon_id = convert_image_path(application_setting.get('float_icon'))
    user_avatar_value, user_avatar_id = convert_image_path(application_setting.get('user_avatar'))

    application_setting_obj = ApplicationSetting(
        application_id=application_setting.get('application'),
        show_history=application_setting.get('show_history'),
        draggable=application_setting.get('draggable'),
        show_guide=application_setting.get('show_guide'),
        avatar=avatar_value,
        float_icon=float_icon_value,
        disclaimer=application_setting.get('disclaimer'),
        disclaimer_value=application_setting.get('disclaimer_value'),
        custom_theme=application_setting.get('custom_theme'),
        float_location=application_setting.get('float_location'),
        show_avatar=application_setting.get('show_avatar'),
        user_avatar=user_avatar_value,
        show_user_avatar=application_setting.get('show_user_avatar'),
        create_time=application_setting.get('create_time'),
        update_time=application_setting.get('update_time')
    )
    if application_setting.get('authentication'):
        application_setting['authentication_value'] = {
            "type": "password",
            "password_value": application_setting.get('authentication_value').get('value')
        }

    ApplicationAccessToken.objects.filter(
        application_id=application_setting.get('application')
    ).update(authentication=application_setting.get('authentication'),
             authentication_value=application_setting.get('authentication_value', {}))
    # 还需要更新图片的source_type和source_id  先判断是不是有图片id 这块图片id可能是多个 需要先提取出来
    image_ids = []
    if avatar_id:
        image_ids.append(avatar_id)
    if float_icon_id:
        image_ids.append(float_icon_id)
    if user_avatar_id:
        image_ids.append(user_avatar_id)

    if image_ids and len(image_ids) > 0:
        File.objects.filter(id__in=image_ids).update(
            source_type=FileSourceType.APPLICATION,
            source_id=application_setting.get('application')
        )
    return application_setting_obj


def application_setting_import(application_setting_list, source_name, current_page):
    for application_setting in application_setting_list:
        application_setting_list = pickle.loads(application_setting.read_bytes())
        application_setting_model_list = [
            to_v2_application_setting(application_setting) for application_setting in
            application_setting_list]
        # 删除数据
        ApplicationSetting.objects.filter(
            application_id__in=[s.application_id for s in application_setting_model_list]).delete()
        # 插入数据
        ApplicationSetting.objects.bulk_create(application_setting_model_list)
        # 修改标识
        rename(application_setting)


def to_v2_platform(platform):
    if platform.get('type') == 'feishu':
        platform['type'] = 'lark'
    platform_obj = Platform(
        id=platform.get('id'),
        application_id=platform.get('application_id'),
        type=platform.get('type'),
        config=platform.get('config'),
        is_active=platform.get('is_active'),
        create_time=platform.get('create_time'),
        update_time=platform.get('update_time')
    )
    return platform_obj


def platform_import(platform_list, source_name, current_page):
    for platform in platform_list:
        platform_list = pickle.loads(platform.read_bytes())
        platform_model_list = [to_v2_platform(platform) for platform in
                               platform_list]
        # 删除数据
        Platform.objects.filter(id__in=[s.id for s in platform_model_list]).delete()
        # 插入数据
        Platform.objects.bulk_create(platform_model_list)
        # 修改标识
        rename(platform)


def to_v2_platform_user(platform_user):
    platform_user_obj = PlatformUser(
        id=platform_user.get('id'),
        user_id=platform_user.get('user'),
        create_time=platform_user.get('create_time'),
        update_time=platform_user.get('update_time')
    )
    return platform_user_obj


def platform_user_import(platform_user_list, source_name, current_page):
    for platform_user in platform_user_list:
        platform_user_list = pickle.loads(platform_user.read_bytes())
        platform_user_model_list = [to_v2_platform_user(platform_user) for platform_user in
                                    platform_user_list]
        # 删除数据
        PlatformUser.objects.filter(id__in=[s.id for s in platform_user_model_list]).delete()
        # 插入数据
        PlatformUser.objects.bulk_create(platform_user_model_list)
        # 修改标识
        rename(platform_user)


def to_v2_system_api_key(system_api_key):
    system_api_key_obj = SystemApiKey(
        id=system_api_key.get('id'),
        secret_key=system_api_key.get('secret_key'),
        is_active=system_api_key.get('is_active'),
        allow_cross_domain=system_api_key.get('allow_cross_domain'),
        cross_domain_list=system_api_key.get('cross_domain_list'),
        user_id=system_api_key.get('user'),
        create_time=system_api_key.get('create_time'),
        update_time=system_api_key.get('update_time'),
    )
    return system_api_key_obj


def system_api_key_import(system_api_key_list, source_name, current_page):
    for system_api_key in system_api_key_list:
        system_api_key_list = pickle.loads(system_api_key.read_bytes())
        system_api_key_model_list = [to_v2_system_api_key(system_api_key) for system_api_key in
                                     system_api_key_list]
        # 删除数据
        SystemApiKey.objects.filter(id__in=[s.id for s in system_api_key_model_list]).delete()
        # 插入数据
        SystemApiKey.objects.bulk_create(system_api_key_model_list)
        # 修改标识
        rename(system_api_key)


def to_v2_system_params(system_params):
    if system_params.get('param_key') in ['icon', 'loginLogo', 'loginImage']:
        # 处理图标路径
        system_params['param_value'], _ = convert_image_path(system_params.get('param_value'))
    if system_params.get('param_key') == 'slogan' and system_params.get('param_value') == '欢迎使用 MaxKB 智能知识库':
        system_params['param_value'] = '强大易用的企业级智能体平台'
    if system_params.get('param_key') == 'userManualUrl' and system_params.get(
            'param_value') == 'https://maxkb.cn/docs/':
        system_params['param_value'] = 'https://maxkb.cn/docs/v2/'
    system_params_obj = SystemParams(
        id=system_params.get('id'),
        param_key=system_params.get('param_key'),
        param_value=system_params.get('param_value'),
    )
    return system_params_obj


def system_params_import(system_params_list, source_name, current_page):
    for system_params in system_params_list:
        system_params_list = pickle.loads(system_params.read_bytes())
        system_params_model_list = [to_v2_system_params(system_params) for system_params in
                                    system_params_list]
        # 删除数据
        SystemParams.objects.all().delete()
        # 插入数据
        SystemParams.objects.bulk_create(system_params_model_list)
        # 修改标识
        rename(system_params)


def update_redirect_urls(config_data):
    """
    更新配置中的重定向URL路径
    """
    admin_api_path = f'{CONFIG.get_admin_path()}/api/'

    if config_data:
        redirect_keys = ['redirectUrl', 'callback_url']
        for key in redirect_keys:
            if key in config_data and isinstance(config_data[key], str):
                if config_data[key].endswith('/feishu'):
                    config_data[key] = config_data[key].replace('/feishu', '/lark')
                config_data[key] = config_data[key].replace('/api/', admin_api_path)
    return config_data


def to_v2_auth_config(auth_config):
    config_data = auth_config.get('config_data', {})
    # 更新重定向URL路径
    config_data = update_redirect_urls(config_data)
    auth_config_obj = PlatformSource(
        id=auth_config.get('id'),
        auth_type=auth_config.get('auth_type'),
        type='SSO',
        config=config_data,
        is_active=auth_config.get('is_active'),
        is_valid=auth_config.get('is_valid', True)
    )
    return auth_config_obj


def auth_config_import(auth_config_list, source_name, current_page):
    for auth_config in auth_config_list:
        auth_config_list = pickle.loads(auth_config.read_bytes())
        auth_config_model_list = [to_v2_auth_config(auth_config) for auth_config in
                                  auth_config_list]
        # 删除数据
        PlatformSource.objects.filter(auth_type__in=[s.auth_type for s in auth_config_model_list]).delete()
        # 插入数据
        PlatformSource.objects.bulk_create(auth_config_model_list)
        # 修改标识
        rename(auth_config)


def to_v2_platform_source(platform_source):
    config_data = platform_source.get('config', {})
    # 更新重定向URL路径
    config_data = update_redirect_urls(config_data)
    id = uuid.uuid7()
    platform_source_obj = PlatformSource(
        id=id,
        auth_type=platform_source.get('platform'),
        type='SCAN',
        config=config_data,
        is_active=platform_source.get('is_active'),
        is_valid=platform_source.get('is_valid', True),
        create_time=platform_source.get('create_time'),
        update_time=platform_source.get('update_time'),
    )
    return platform_source_obj


def platform_source_import(platform_source_list, source_name, current_page):
    for platform_source in platform_source_list:
        platform_source_list = pickle.loads(platform_source.read_bytes())
        platform_source_model_list = [to_v2_platform_source(platform_source) for platform_source in
                                      platform_source_list]
        # 删除数据
        PlatformSource.objects.filter(auth_type__in=[s.auth_type for s in platform_source_model_list]).delete()
        # 插入数据
        PlatformSource.objects.bulk_create(platform_source_model_list)
        # 修改标识
        rename(platform_source)


def import_user_relation():
    user_list = User.objects.all()
    user_role_relations = []

    # 判断用户，如果是默认的admin需要加管理员权限，其他加普通用户权限
    for user in user_list:
        if str(user.id) == 'f0dd8f71-e4ee-11ee-8c84-a8a1595801ab':
            roles_to_assign = [
                RoleConstants.ADMIN.name,
                RoleConstants.USER.name,
                RoleConstants.WORKSPACE_MANAGE.name
            ]
        else:
            roles_to_assign = [RoleConstants.USER.name]

        for role_id in roles_to_assign:
            workspace_id = 'default'
            if str(user.id) == 'f0dd8f71-e4ee-11ee-8c84-a8a1595801ab' and role_id == RoleConstants.ADMIN.name:
                workspace_id = 'None'
            user_role_relations.append(UserRoleRelation(
                id=uuid.uuid7(),
                user_id=user.id,
                role_id=role_id,
                workspace_id=workspace_id
            ))
    if user_role_relations:
        UserRoleRelation.objects.bulk_create(user_role_relations, ignore_conflicts=True)

def to_v2_log(log):
    log_obj = Log(
        id=log.get('id'),
        user=log.get('user'),
        workspace_id='default',
        menu=log.get('menu'),
        operate=log.get('operate'),
        operation_object=log.get('operation_object'),
        status=log.get('status'),
        ip_address=log.get('ip_address'),
        details=log.get('details'),
        create_time=log.get('create_time'),
        update_time=log.get('update_time'),
    )
    return log_obj


def log_import(log_list, source_name, current_page):
    for log in log_list:
        log_list = pickle.loads(log.read_bytes())
        log_model_list = [to_v2_log(log) for log in
                          log_list]
        # 插入数据
        Log.objects.bulk_create(log_model_list)
        # 修改标识
        rename(log)


def import_():
    import_page(ImportQuerySet('application_setting'), 1, application_setting_import, "application_setting", "导入应用设置",
         check=import_check)
    import_page(ImportQuerySet('platform'), 1, platform_import, "platform", "导入三方平台", check=import_check)
    import_page(ImportQuerySet('auth_config'), 1, auth_config_import, "auth_config", "导入认证配置", check=import_check)
    import_page(ImportQuerySet('platform_source'), 1, platform_source_import, "platform_source", "导出三方平台认证",
         check=import_check)
    import_page(ImportQuerySet('platform_user'), 1, platform_user_import, "platform_user", "导入三方平台用户",
         check=import_check)
    import_page(ImportQuerySet('system_api_key'), 1, system_api_key_import, "system_api_key", "导入系统api密钥",
         check=import_check)
    import_page(ImportQuerySet('system_params'), 1, system_params_import, "system_params", "导入系统参数", check=import_check)
    import_user_relation()
    import_page(ImportQuerySet('log'), 1, log_import, "log", "导入操作日志", check=import_check)
