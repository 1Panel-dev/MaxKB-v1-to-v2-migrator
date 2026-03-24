# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： model_export.py
    @date：2025/7/29 16:12
    @desc:
"""
import json
import os
import shutil

from common.util.rsa_util import rsa_long_decrypt
from django.db.models import QuerySet
from setting.models import Model, SystemSetting, TeamMemberPermission, TeamMember
from setting.models.log_management import Log
from users.models import User

from commons.util import page, save_batch_file, get_model_dir_path


def log_export(log_list, source_name, current_page):
    batch_list = [
        {
            'id': log.id,
            'menu': log.menu,
            'operate': log.operate,
            'operation_object': log.operation_object,
            'user': log.user,
            'status': log.status,
            'ip_address': log.ip_address,
            'details': log.details,
            'create_time': log.create_time,
            'update_time': log.update_time,
        }
        for log in log_list
    ]
    save_batch_file(batch_list, source_name, current_page)


model_name_count_global = {}


def model_export(model_list, source_name, current_page):
    global model_name_count_global
    batch_list = []

    for model in model_list:
        model_data = {
            'id': model.id,
            'name': model.name,
            'status': model.status,
            'model_type': model.model_type,
            'model_name': model.model_name,
            'user': model.user_id,
            'provider': model.provider,
            'credential': model.credential,
            'meta': model.meta,
            'permission_type': model.permission_type,
            'model_params_form': model.model_params_form,
            'create_time': model.create_time,
            'update_time': model.update_time,
        }
        original_name = model_data['name']
        count = model_name_count_global.get(original_name, 0)
        if count > 0:
            model_data['name'] = f"{original_name}{count}"
        model_name_count_global[original_name] = count + 1
        batch_list.append(model_data)
    save_batch_file(batch_list, source_name, current_page)


def system_setting_export(system_setting_list, source_name, current_page):
    batch_list = [
        {
            'type': ss.type,
            'meta': ss.meta,
            'create_time': ss.create_time,
            'update_time': ss.update_time,
        }
        for ss in system_setting_list
    ]
    save_batch_file(batch_list, source_name, current_page)


def reset_team_member_permission_model(team_member_permission, team_member_dict):
    team_member = team_member_dict.get(team_member_permission.member_id)
    base = {
        'id': team_member_permission.id,
        'member': team_member_permission.member_id,
        'auth_target_type': team_member_permission.auth_target_type,
        'target': team_member_permission.target,
        'operate': team_member_permission.operate,
        'create_time': team_member_permission.create_time,
        'update_time': team_member_permission.update_time,
    }
    if team_member is not None:
        base['user_id'] = team_member.user_id
        base['team_id'] = team_member.team_id
    return base


def team_member_permission_export(team_member_permission_list, source_name, current_page):
    team_member_dict = {team_member.id: team_member for team_member in QuerySet(TeamMember).filter(
        id__in=[team_member_permission.member_id for team_member_permission in team_member_permission_list])}
    batch_list = [reset_team_member_permission_model(team_member_permission, team_member_dict) for
                  team_member_permission in
                  team_member_permission_list]
    save_batch_file(batch_list, source_name, current_page)


nick_name_count = {}


def user_export(user_list, source_name, current_page):
    global nick_name_count
    batch_list = []
    for user in user_list:
        user_data = {
            'id': user.id,
            'email': user.email,
            'phone': user.phone,
            'nick_name': user.nick_name,
            'username': user.username,
            'password': user.password,
            'role': user.role,
            'source': user.source,
            'is_active': user.is_active,
            'language': user.language,
            'create_time': user.create_time,
            'update_time': user.update_time,
        }
        # 如果 nick_name 不存在，则使用 username 填充
        if not user_data['nick_name']:
            user_data['nick_name'] = user_data['username']

        original_nick_name = user_data['nick_name']
        # 处理 nick_name 重复问题
        if original_nick_name in nick_name_count:
            nick_name_count[original_nick_name] += 1
            user_data['nick_name'] = f"{original_nick_name}{nick_name_count[original_nick_name]}"
        else:
            nick_name_count[original_nick_name] = 0

        batch_list.append(user_data)
    save_batch_file(batch_list, source_name, current_page)


def local_model_export(model_list, source_name, current_page):
    for model in model_list:
        model_path = model.model_name
        model_path = model_path[:-1] if 'model_path'.endswith('/') else model_path
        if not model.model_name.startswith("/"):
            credential = json.loads(rsa_long_decrypt(model.credential))
            cache_dir = credential.get('cache_dir') or credential.get('cache_folder')
            model_path = os.path.join(cache_dir, 'models--' + model.model_name.replace('/', '--'))
        if not os.path.exists(model_path):
            pass
        else:
            target_model = os.path.join(get_model_dir_path(source_name), os.path.basename(model_path))
            if not os.path.exists(target_model):
                shutil.copytree(model_path, target_model)


def export():
    page(QuerySet(Log), 100, log_export, "log", "导出操作日志")
    page(QuerySet(Model), 100, model_export, "model", "导出模型")
    page(QuerySet(SystemSetting), 100, system_setting_export, "system_setting", "导出系统设置", primary_key="type")
    page(QuerySet(TeamMemberPermission), 100, team_member_permission_export, "team_member_permission",
         "导出团队授权数据")
    page(QuerySet(User), 100, user_export, "user", "导出用户数据")
    page(QuerySet(Model)
         .exclude(model_name='/opt/maxkb/model/embedding/shibing624_text2vec-base-chinese')
         .filter(provider='model_local_provider'), 1, local_model_export, "local_model", "导出本地模型")
