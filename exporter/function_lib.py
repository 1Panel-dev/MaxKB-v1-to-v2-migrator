# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： function_lib.py
    @date：2025/7/29 16:13
    @desc:
"""
import os
import zipfile
from django.db.models import QuerySet
from rest_framework import serializers

from function_lib.models.function import FunctionLib
from commons.util import page, save_batch_file


class FunctionLibModel(serializers.ModelSerializer):
    class Meta:
        model = FunctionLib
        fields = "__all__"


def function_lib_export(function_lib_list, source_name, current_page):
    batch_list = [FunctionLibModel(function_lib).data for function_lib in function_lib_list]
    save_batch_file(batch_list, source_name, current_page)


def zip_pip_target():
    pip_target = os.environ.get('PIP_TARGET')
    if not pip_target or not os.path.isdir(pip_target):
        return
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
    os.makedirs(data_dir, exist_ok=True)
    zip_path = os.path.join(data_dir, 'python-packages.zip')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(pip_target):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, pip_target)
                zipf.write(file_path, arcname)
    return zip_path



def export():
    page(QuerySet(FunctionLib), 100, function_lib_export, "function_lib", "导出函数库")
    zip_pip_target()
