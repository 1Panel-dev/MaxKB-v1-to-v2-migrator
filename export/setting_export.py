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


def model_export(model_list, source_name, current_page):
    name_count = {}
    batch_list = []

    for model in model_list:
        model_data = ModelModel(model).data

        original_name = model_data['name']
        count = name_count.get(original_name, 0)
        if count > 0:
            model_data['name'] = f"{original_name}{count}"
        name_count[original_name] = count + 1

        batch_list.append(model_data)

        batch_list.append(model_data)
    save_batch_file(batch_list, source_name, current_page)


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
