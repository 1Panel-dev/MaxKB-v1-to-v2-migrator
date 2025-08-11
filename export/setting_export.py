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

from setting.models import Model, SystemSetting, TeamMemberPermission
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
    batch_list = [ModelModel(model).data for model in model_list]
    save_batch_file(batch_list, source_name, current_page)


def system_setting_export(system_setting_list, source_name, current_page):
    batch_list = [SystemSettingModel(system_setting).data for system_setting in system_setting_list]
    save_batch_file(batch_list, source_name, current_page)


def team_member_permission_export(team_member_permission_list, source_name, current_page):
    batch_list = [TeamMemberPermissionModel(team_member_permission).data for team_member_permission in
                  team_member_permission_list]
    save_batch_file(batch_list, source_name, current_page)


def user_export(user_list, source_name, current_page):
    batch_list = [UserModel(user).data for user in user_list]
    save_batch_file(batch_list, source_name, current_page)


def export():
    page(QuerySet(Log), 100, log_export, "log", "导出操作日志")
    page(QuerySet(Model), 100, model_export, "model", "导出模型")
    page(QuerySet(SystemSetting), 100, system_setting_export, "system_setting", "导出系统设置", primary_key="type")
    page(QuerySet(TeamMemberPermission), 100, team_member_permission_export, "team_member_permission",
         "导出团队授权数据")
    page(QuerySet(User), 100, user_export, "user", "导出用户数据")
