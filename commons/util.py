# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： common.py
    @date：2025/7/28 14:53
    @desc:
"""
import os
import zipfile
from math import ceil, floor
from pathlib import Path

from tqdm import tqdm
import pickle
import shutil

from migrate import BASE_DIR, APP_DIR

source_dir_size = 1000


class ImportQuerySet:

    def __init__(self, source_name: str):
        directory_path = Path(f"{BASE_DIR}/data/{source_name}/")
        self.file_list = [f for f in directory_path.rglob('*') if f.is_file()]

    def count(self):
        return len(self.file_list)

    def order_by(self, k):
        self.file_list.sort(key=lambda f: int(f.stem))
        return self

    def all(self):
        return self

    def __getitem__(self, item):
        return self.file_list[item.start:item.stop]


def _check(source_name, current_page):
    """

    @param source_name:
    @param current_page:
    @return:
    """
    dir_path = get_dir_path(source_name, current_page)
    base_path = f"{dir_path}/{current_page}.pickle"
    return not os.path.exists(base_path)


def import_check(source_name, current_page):
    dir_path = get_dir_path(source_name, current_page)
    base_path = f"{dir_path}/{current_page}.pickle_done"
    return not os.path.exists(base_path)


def page(query_set, page_size, handler, source_name, desc, primary_key="id", check=_check):
    """

    @param primary_key: 主键
    @param desc:        任务描述
    @param query_set:   查询query_set
    @param page_size:   每次查询大小
    @param handler:     数据处理器
    @param source_name: 资源名称
    @param check:       校验是否已经导出
    @return:
    """

    query = query_set.order_by(primary_key)
    count = query_set.count()
    with tqdm(range(count), desc=desc,
              bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}] {postfix}") as pbar:
        for i in range(0, ceil(count / page_size)):
            offset = i * page_size
            if check(source_name, i + 1):
                data_list = query.all()[offset: offset + page_size]
                handler(data_list, source_name, i + 1)
                pbar.refresh()
            pbar.update(page_size if offset + page_size <= count else count - offset)


def get_dir_path(source_name, current_page):
    dir_path = f"{BASE_DIR}/data/{source_name}/{ceil(current_page / 1000)}/"
    return dir_path


def save_batch_file(data_list, source_name, current_page):
    dir_path = get_dir_path(source_name, current_page)
    base_path = f"{dir_path}/{current_page}.pickle"
    os.makedirs(dir_path, exist_ok=True)
    with open(base_path, 'wb') as f:
        # 使用pickle的dump方法将对象序列化并写入文件
        pickle.dump(data_list, f)


def rename(file):
    new_name = f"{file.name}_done"
    new_path = file.with_name(new_name)
    file.rename(new_path)


def zip_folder():
    folder_path = f"{BASE_DIR}/data/"
    zip_name = f"{BASE_DIR}/migrate"
    if os.path.exists(zip_name + '.zip'):
        return
    shutil.make_archive(zip_name, 'zip', folder_path)


def un_zip():
    zip_name = Path(f"{BASE_DIR}/migrate.zip")
    extract_dir = Path(f"{BASE_DIR}/data/")
    if os.path.exists(extract_dir):
        return
    extract_dir.mkdir(exist_ok=True)
    with zipfile.ZipFile(zip_name, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)


def contains_xpack():
    dir_path = Path(f"{APP_DIR}/")
    for source in dir_path.iterdir():
        if source.is_dir() and source.name.startswith("xpack"):
            return True
    return False
