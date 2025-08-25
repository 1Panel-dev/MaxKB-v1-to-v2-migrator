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

from django.db.models import QuerySet

from common.constants.permission_constants import ResourcePermission, ResourceAuthType
from common.utils.rsa_util import rsa_long_decrypt, rsa_long_encrypt
from commons.util import page, ImportQuerySet, import_check, rename
from models_provider.models import Model
from system_manage.models import SystemSetting, AuthTargetType, WorkspaceUserResourcePermission
from users.models import User


def to_v2_user(user):
    return User(id=user.get('id'),
                email=user.get('email'),
                phone=user.get('phone'),
                nick_name=user.get('nick_name'),
                username=user.get('username'),
                password=user.get('password'),
                role=user.get('role'),
                source=user.get('source'),
                is_active=user.get('is_active'),
                language=user.get('language'),
                create_time=user.get('create_time'),
                update_time=user.get('update_time'))


def to_v2_system_setting_model(system_setting):
    return SystemSetting(type=system_setting.get('type'),
                         meta=system_setting.get('meta'),
                         create_time=system_setting.get('create_time'),
                         update_time=system_setting.get('update_time'))


def user_import(file_list, source_name, current_page):
    for file in file_list:
        user_list = pickle.loads(file.read_bytes())
        user_model_list = [to_v2_user(user) for user in user_list]
        # 删除数据
        QuerySet(User).filter(id__in=[u.id for u in user_model_list]).delete()
        # 插入数据
        QuerySet(User).bulk_create(user_model_list)
        # 修改标识
        rename(file)


def update_qwen_model(model):
    """处理通义千问模型到阿里云百炼的转换"""
    if model.get('provider') == 'model_qwen_provider':
        model['provider'] = 'aliyun_bai_lian_model_provider'
        if model.get('credential') and model.get('model_type') == 'LLM':
            credential = json.loads(rsa_long_decrypt(model.get('credential')))
            model['credential'] = json.dumps({
                'api_base': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
                'api_key': credential.get('api_key'),
            })
            model['credential'] = rsa_long_encrypt(model['credential'])

    if model.get('provider') == 'model_local_provider' and model.get('credential'):
        credential = json.loads(rsa_long_decrypt(model.get('credential')))
        cache_path = None

        if model.get('model_type') == 'EMBEDDING':
            cache_path = credential.get('cache_folder')
        elif model.get('model_type') == 'RERANKER':
            cache_path = credential.get('cache_dir')

        if cache_path and cache_path.startswith('/opt/maxkb/'):
            cache_path = cache_path.replace('/opt/maxkb/', '/opt/maxkb-app/')

        if model.get('model_type') == 'EMBEDDING':
            model['credential'] = json.dumps({'cache_folder': cache_path})
        elif model.get('model_type') == 'RERANKER':
            model['credential'] = json.dumps({'cache_dir': cache_path})

        model['credential'] = rsa_long_encrypt(model['credential'])

    return model


def create_model_permissions(model, model_id):
    permissions_to_create = []
    creator_permission = WorkspaceUserResourcePermission(
        target=model_id,
        auth_target_type=AuthTargetType.MODEL,
        permission_list=[ResourcePermission.VIEW, ResourcePermission.MANAGE],
        workspace_id='default',
        user_id=model.get('user'),
        auth_type=ResourceAuthType.RESOURCE_PERMISSION_GROUP
    )
    permissions_to_create.append(creator_permission)

    if model.get('permission') == 'PUBLIC':
        users = User.objects.exclude(id=model.get('user')).values_list('id', flat=True)
        for user_id in users:
            public_permission = WorkspaceUserResourcePermission(
                target=model_id,
                auth_target_type=AuthTargetType.MODEL,
                permission_list=[ResourcePermission.VIEW],
                workspace_id='default',
                user_id=user_id,
                auth_type=ResourceAuthType.RESOURCE_PERMISSION_GROUP
            )
            permissions_to_create.append(public_permission)

    if permissions_to_create:
        WorkspaceUserResourcePermission.objects.bulk_create(permissions_to_create)


def to_v2_model(model):
    """
    模型迁移逻辑：
    1. 私有权限的工具只有创建者有"管理"权限，其他用户未授权；
    2. 公有权限的工具创建者有"管理"权限；其他所有工作空间用户有"查看"权限；
    3. "通义千问"模型迁移后变为"阿里云百炼"对应的模型；
    4. 本地模型迁移直接迁移。V2和V1目录一致
    """
    # 处理通义千问模型转换
    model = update_qwen_model(model)

    model_obj = Model(id=model.get('id'),
                      name=model.get('name'),
                      status=model.get('status'),
                      model_type=model.get('model_type'),
                      model_name=model.get('model_name'),
                      user_id=model.get('user'),
                      provider=model.get('provider'),
                      credential=model.get('credential'),
                      meta=model.get('meta'),
                      model_params_form=model.get('model_params_form'),
                      create_time=model.get('create_time'),
                      update_time=model.get('update_time'),
                      workspace_id='default')

    # 创建相应权限
    create_model_permissions(model, model_obj.id)

    return model_obj


def model_import(file_list, source_name, current_page):
    for file in file_list:
        model_list = pickle.loads(file.read_bytes())
        model_model_list = [to_v2_model(model) for model in model_list]
        # 删除数据
        QuerySet(Model).filter(id__in=[m.id for m in model_model_list]).delete()
        # 插入数据
        QuerySet(Model).bulk_create(model_model_list)
        # 修改标识
        rename(file)


def system_setting_import(file_list, source_name, current_page):
    for file in file_list:
        system_setting_list = pickle.loads(file.read_bytes())
        system_setting_model_list = [to_v2_system_setting_model(system_setting) for system_setting in
                                     system_setting_list]
        # 删除数据
        QuerySet(SystemSetting).filter(type__in=[s.type for s in system_setting_model_list]).delete()
        # 插入数据
        QuerySet(SystemSetting).bulk_create(system_setting_model_list)
        # 修改标识
        rename(file)


def reset_permission_list(operate):
    return ['VIEW' if o == 'USE' else 'MANAGE' for o in operate if ['USE', 'MANAGE'].__contains__(o)]


def to_v2_workspace_user_resource_permission(team_member_permission):
    user_id = team_member_permission.get('user_id')
    if user_id is None:
        return None
    return WorkspaceUserResourcePermission(id=team_member_permission.get('id'),
                                           workspace_id='default',
                                           user_id=team_member_permission.get('user_id'),
                                           auth_target_type='KNOWLEDGE' if team_member_permission.get(
                                               'auth_target_type') == 'DATASET' else 'APPLICATION',
                                           target=team_member_permission.get('target'),
                                           auth_type='RESOURCE_PERMISSION_GROUP',
                                           permission_list=reset_permission_list(
                                               team_member_permission.get('operate', [])))


def team_member_permission_import(file_list, source_name, current_page):
    for file in file_list:
        team_member_permission_list = pickle.loads(file.read_bytes())
        workspace_user_resource_permission_model_list = [i for i in [
            to_v2_workspace_user_resource_permission(team_member_permission) for team_member_permission in
            team_member_permission_list] if i is not None]
        # 删除数据
        QuerySet(WorkspaceUserResourcePermission).filter(
            id__in=[wur.id for wur in workspace_user_resource_permission_model_list]).delete()

        # 插入数据
        QuerySet(WorkspaceUserResourcePermission).bulk_create(workspace_user_resource_permission_model_list)
        # 修改标识
        rename(file)


def import_():
    page(ImportQuerySet('system_setting'), 1, system_setting_import, "system_setting", "导入系统设置",
         check=import_check)
    page(ImportQuerySet('user'), 1, user_import, "user", "导入用户", check=import_check)
    page(ImportQuerySet('model'), 1, model_import, "model", "导入模型", check=import_check)
    page(ImportQuerySet("team_member_permission"), 1, team_member_permission_import, 'team_member_permission',
         '导入授权', check=import_check)
