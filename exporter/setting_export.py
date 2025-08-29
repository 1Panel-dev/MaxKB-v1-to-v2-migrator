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
import zipfile

from django.db.models import QuerySet
from rest_framework import serializers

from common.util.rsa_util import rsa_long_decrypt
from setting.models import Model, SystemSetting, TeamMemberPermission, TeamMember
from setting.models.log_management import Log
from users.models import User
from commons.util import page, save_batch_file


class LogModel(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = "__all__"


class ModelModel(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = "__all__"


class SystemSettingModel(serializers.ModelSerializer):
    class Meta:
        model = SystemSetting
        fields = "__all__"


class TeamMemberPermissionModel(serializers.ModelSerializer):
    class Meta:
        model = TeamMemberPermission
        fields = "__all__"


class UserModel(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


def log_export(log_list, source_name, current_page):
    batch_list = [LogModel(log).data for log in log_list]
    save_batch_file(batch_list, source_name, current_page)


model_name_count_global = {}
local_model_cache = []


def model_export(model_list, source_name, current_page):
    global model_name_count_global
    batch_list = []

    for model in model_list:
        model_data = ModelModel(model).data

        original_name = model_data['name']
        count = model_name_count_global.get(original_name, 0)
        if count > 0:
            model_data['name'] = f"{original_name}{count}"
        model_name_count_global[original_name] = count + 1
        if model_data['provider'] == 'model_local_provider' and model_data.get('credential') and model_data[
            'id'] != '42f63a3d-427e-11ef-b3ec-a8a1595801ab':
            credential = json.loads(rsa_long_decrypt(model_data.get('credential')))
            local_model_cache.append(credential.get('model_name'))
        batch_list.append(model_data)
    save_batch_file(batch_list, source_name, current_page)


from migrate import BASE_DIR


def zip_local_models():
    unique_paths = set(path for path in local_model_cache if path)
    for path in unique_paths:
        zip_folder(path)


# 打包本地模型到一个zip
def zip_folder(folder_path: str, output_dir: str = f"{BASE_DIR}/data/local_model"):
    """
    根据给定的绝对路径压缩目录
    :param folder_path: 模型的完整路径
    :param output_dir: 压缩包存放目录
    """
    # 如果路径不存在，尝试替换最后一级目录为 models--xxx
    if not os.path.exists(folder_path):
        base_dir = os.path.dirname(folder_path)
        folder_name = os.path.basename(os.path.normpath(folder_path))
        alt_name = f"models--{folder_name}"
        alt_path = os.path.join(base_dir, alt_name)

        if os.path.exists(alt_path):
            print(f"⚠️ 路径不存在，已自动修正为: {alt_path}")
            folder_path = alt_path
        else:
            print(f"❌ 目录不存在: {folder_path} 或 {alt_path}")
            return

    if not os.path.isdir(folder_path):
        print(f"⚠️ 路径不是目录: {folder_path}")
        return

    if not os.access(folder_path, os.R_OK | os.X_OK):
        print(f"🚫 没有权限访问目录: {folder_path}")
        return

    os.makedirs(output_dir, exist_ok=True)

    folder_name = os.path.basename(os.path.normpath(folder_path))
    zip_file_path = os.path.join(output_dir, f"{folder_name}.zip")

    print(f"✅ 开始压缩: {folder_path} -> {zip_file_path}")

    try:
        with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, start=folder_path)
                    zipf.write(file_path, arcname=arcname)

        print(f"🎉 压缩完成: {zip_file_path}\n")

    except PermissionError as e:
        print(f"🚫 文件权限不足，压缩失败: {e}")


def system_setting_export(system_setting_list, source_name, current_page):
    batch_list = [SystemSettingModel(system_setting).data for system_setting in system_setting_list]
    save_batch_file(batch_list, source_name, current_page)


def reset_team_member_permission_model(team_member_permission, team_member_dict):
    team_member = team_member_dict.get(team_member_permission.member_id)
    if team_member is not None:
        return {**TeamMemberPermissionModel(team_member_permission).data,
                'user_id': team_member.user_id,
                'team_id': team_member.team_id}
    return TeamMemberPermissionModel(team_member_permission).data


def team_member_permission_export(team_member_permission_list, source_name, current_page):
    team_member_dict = {team_member.id: team_member for team_member in QuerySet(TeamMember).filter(
        id__in=[team_member_permission.member_id for team_member_permission in team_member_permission_list])}
    batch_list = [reset_team_member_permission_model(team_member_permission, team_member_dict) for
                  team_member_permission in
                  team_member_permission_list]
    save_batch_file(batch_list, source_name, current_page)


def user_export(user_list, source_name, current_page):
    nick_name_count = {}

    batch_list = []
    for user in user_list:
        user_data = UserModel(user).data

        # 如果 nick_name 不存在，则使用 username 填充
        if not user_data.get('nick_name'):
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


def export():
    page(QuerySet(Log), 100, log_export, "log", "导出操作日志")
    page(QuerySet(Model), 100, model_export, "model", "导出模型")
    page(QuerySet(SystemSetting), 100, system_setting_export, "system_setting", "导出系统设置", primary_key="type")
    page(QuerySet(TeamMemberPermission), 100, team_member_permission_export, "team_member_permission",
         "导出团队授权数据")
    page(QuerySet(User), 100, user_export, "user", "导出用户数据")
    zip_local_models()
