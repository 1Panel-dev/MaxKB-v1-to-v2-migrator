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
from models_provider.models import Model
from system_manage.models import SystemSetting
from users.models import User


def to_v2_user(user):
    return User(id=user.get('id'),
                email=user.get('email'),
                phone=user.get('phone'),
                nick_name=user.get('nick_name'),
                username=user.get('username'),
                password=user.get('password'),
                role=user.get('role'),
                source=user.get('source'),
                is_active=user.get('is_active'),
                language=user.get('language'),
                create_time=user.get('create_time'),
                update_time=user.get('update_time'))


def to_v2_model(model):
    return Model(id=model.get('id'),
                 name=model.get('name'),
                 status=model.get('status'),
                 model_type=model.get('model_type'),
                 model_name=model.get('model_name'),
                 user_id=model.get('user'),
                 provider=model.get('provider'),
                 credential=model.get('credential'),
                 meta=model.get('meta'),
                 model_params_form=model.get('model_params_form'),
                 workspace_id='default')


def to_v2_system_setting_model(system_setting):
    return SystemSetting(type=system_setting.get('type'),
                         meta=system_setting.get('meta'),
                         create_time=system_setting.get('create_time'),
                         update_time=system_setting.get('update_time'))


def user_import(file_list, source_name, current_page):
    for file in file_list:
        user_list = pickle.loads(file.read_bytes())
        user_model_list = [to_v2_user(user) for user in user_list]
        # 删除数据
        QuerySet(User).filter(id_in=[u.id for u in user_model_list]).delete()
        # 插入数据
        QuerySet(User).bulk_create(user_model_list)
        # 修改标识
        rename(file)


def model_import(file_list, source_name, current_page):
    for file in file_list:
        model_list = pickle.loads(file.read_bytes())
        model_model_list = [to_v2_model(model) for model in model_list]
        # 删除数据
        QuerySet(SystemSetting).filter(id_in=[m.id for m in model_model_list]).delete()
        # 插入数据
        QuerySet(Model).bulk_create(model_model_list)
        # 修改标识
        rename(file)


def system_setting_import(file_list, source_name, current_page):
    for file in file_list:
        system_setting_list = pickle.loads(file.read_bytes())
        system_setting_model_list = [to_v2_system_setting_model(system_setting) for system_setting in
                                     system_setting_list]
        # 删除数据
        QuerySet(SystemSetting).filter(type_in=[s.type for s in system_setting_model_list]).delete()
        # 插入数据
        QuerySet(SystemSetting).bulk_create(system_setting_model_list)
        # 修改标识
        rename(file)


def import_():
    page(ImportQuerySet('system_setting'), 1, system_setting_import, "system_setting", "导入系统设置",
         check=import_check)
    page(ImportQuerySet('user'), 1, user_import, "user", "导入用户", check=import_check)
    page(ImportQuerySet('model'), 1, model_import, "model", "导入模型", check=import_check)
