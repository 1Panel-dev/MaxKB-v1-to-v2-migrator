# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application_import.py
    @date：2025/8/11 18:24
    @desc:
"""
import pickle

from commons.util import page, ImportQuerySet, import_check, rename


def application_import(file_list, source_name, current_page):
    for file in file_list:
        application_list = pickle.loads(file.read_bytes())
        print(application_list)
        rename(file)


def import_():
    page(ImportQuerySet('application'), 1, application_import, "application", "导入应用", check=import_check)
