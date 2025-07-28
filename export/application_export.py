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

from application.models import Application, WorkFlowVersion
from export.util import page, save_batch_file

count = QuerySet(Application).count()


class ApplicationModel(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = "__all__"


def application_export(application_list, current_page):
    batch_list = [ApplicationModel(application).data for application in application_list]
    save_batch_file(batch_list, "application", current_page)


def application_workflow_version_export(workflow_version_list, current_page):
    pass


page(QuerySet(Application), 10, application_export, "导出应用")
