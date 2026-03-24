# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： function_lib.py
    @date：2025/7/29 16:13
    @desc:
"""
import os
import shutil
from django.db.models import QuerySet

from function_lib.models.function import FunctionLib
from commons.util import page, save_batch_file


def function_lib_export(function_lib_list, source_name, current_page):
    batch_list = [
        {
            'id': fl.id,
            'user': fl.user_id,
            'name': fl.name,
            'desc': fl.desc,
            'code': fl.code,
            'input_field_list': fl.input_field_list,
            'init_field_list': fl.init_field_list,
            'icon': fl.icon,
            'is_active': fl.is_active,
            'permission_type': fl.permission_type,
            'function_type': fl.function_type,
            'template_id': fl.template_id,
            'init_params': fl.init_params,
            'create_time': fl.create_time,
            'update_time': fl.update_time,
        }
        for fl in function_lib_list
    ]
    save_batch_file(batch_list, source_name, current_page)


def zip_pip_target():
    pip_target = os.environ.get('PIP_TARGET')
    if not pip_target or not os.path.isdir(pip_target):
        return
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
    os.makedirs(data_dir, exist_ok=True)
    zip_path = os.path.join(data_dir, 'python-packages')
    
    archive_path = shutil.make_archive(zip_path, 'zip', pip_target)
    return archive_path



def export():
    page(QuerySet(FunctionLib), 100, function_lib_export, "function_lib", "导出函数库")
    zip_pip_target()
