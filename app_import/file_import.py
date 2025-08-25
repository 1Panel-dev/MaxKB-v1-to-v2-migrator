# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： user_import.py
    @date：2025/8/12 10:26
    @desc:
"""
import pickle

from django.db.models import QuerySet

from commons.util import page, ImportQuerySet, import_check, rename
from knowledge.models import File
from system_manage.models import SystemSetting


def to_v2_file(file):
    content = file.get('content')
    file_obj = File(id=file.get('id'),
                    file_name=file.get('file_name'),
                    loid=file.get('loid'),
                    meta=file.get('meta'),
                    source_type='SYSTEM',
                    source_id='SYSTEM',
                    create_time=file.get('create_time'),
                    update_time=file.get('update_time'))
    file_obj._content = content
    return file_obj


def image_to_v2_file(file):
    content = file.get('image_data')
    file_obj = File(id=file.get('id'),
                    file_name=file.get('image_name'),
                    meta={},
                    source_type='SYSTEM',
                    source_id='SYSTEM',
                    create_time=file.get('create_time'),
                    update_time=file.get('update_time'))
    file_obj._content = content
    return file_obj


def file_import(file_list, source_name, current_page):
    for file in file_list:
        file_list = pickle.loads(file.read_bytes())
        file_model_list = [to_v2_file(file) for file in
                           file_list]
        # 删除数据
        QuerySet(File).filter(id__in=[s.id for s in file_model_list]).delete()
        # 插入数据
        for item in file_model_list:
            item.save(item._content if hasattr(item, '_content') else None)
        # 修改标识
        rename(file)


def image_import(file_list, source_name, current_page):
    for image in file_list:
        file_list = pickle.loads(image.read_bytes())
        file_model_list = [image_to_v2_file(file) for file in
                           file_list]
        # 删除数据
        QuerySet(File).filter(id__in=[s.id for s in file_model_list]).delete()
        # 插入数据
        for item in file_model_list:
            item.save(item._content if hasattr(item, '_content') else None)
        # 修改标识
        rename(image)


def import_():
    page(ImportQuerySet('file'), 1, file_import, "file", "导入文件",
         check=import_check)
    page(ImportQuerySet('image'), 1, image_import, "image", "导入图片", check=import_check)

def check_file_empty():
    return not QuerySet(File).exists()