# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： function_lib.py
    @date：2025/7/29 16:13
    @desc:
"""
from django.db.models import QuerySet
from rest_framework import serializers

from function_lib.models.function import FunctionLib
from .util import page, save_batch_file


class FunctionLibModel(serializers.ModelSerializer):
    class Meta:
        model = FunctionLib
        fields = "__all__"


def function_lib_export(function_lib_list, current_page):
    batch_list = [FunctionLibModel(function_lib).data for function_lib in function_lib_list]
    save_batch_file(batch_list, 'function_lib', current_page)


def export():
    page(QuerySet(FunctionLib), 100, function_lib_export, "导出函数库")
