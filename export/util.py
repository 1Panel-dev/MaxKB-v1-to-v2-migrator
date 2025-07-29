# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： common.py
    @date：2025/7/28 14:53
    @desc:
"""
import os
from math import ceil
from tqdm import tqdm
import pickle
import shutil

from migrate import BASE_DIR


def page(query_set, page_size, handler, desc, primary_key="id"):
    """

    @param primary_key: 主键
    @param desc: 任务描述
    @param query_set: 查询query_set
    @param page_size: 每次查询大小
    @param handler:   数据处理器
    @return:
    """

    query = query_set.order_by(primary_key)
    count = query_set.count()
    with tqdm(range(count), desc=desc,
              bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}] {postfix}") as pbar:
        for i in range(0, ceil(count / page_size)):
            offset = i * page_size
            data_list = query.all()[offset: offset + page_size]
            handler(data_list, i + 1)
            pbar.update(len(data_list))


def save_batch_file(data_list, source_name, current_page):
    dir_path = f"{BASE_DIR}/data/{source_name}/"
    base_path = f"{dir_path}/{current_page}.pickle"
    os.makedirs(dir_path, exist_ok=True)
    with open(base_path, 'wb') as f:
        # 使用pickle的dump方法将对象序列化并写入文件
        pickle.dump(data_list, f)


def zip_folder():
    folder_path = f"{BASE_DIR}/data/"
    zip_name = f"{BASE_DIR}/migrate"
    shutil.make_archive(zip_name, 'zip', folder_path)
