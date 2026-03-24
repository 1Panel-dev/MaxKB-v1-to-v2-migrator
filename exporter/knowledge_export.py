# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： knowledge_export.py
    @date：2025/7/29 14:45
    @desc:
"""
from dataset.models import DataSet, Document, Paragraph, Problem, ProblemParagraphMapping, Image, File
from django.db.models import QuerySet
from embedding.models import Embedding

from commons.util import page, save_batch_file


def knowledge_export(knowledge_list, source_name, current_page):
    batch_data = [
        {
            'id': k.id,
            'name': k.name,
            'desc': k.desc,
            'user': k.user_id,
            'type': k.type,
            'embedding_mode': k.embedding_mode_id,
            'meta': k.meta,
            'create_time': k.create_time,
            'update_time': k.update_time,
        }
        for k in knowledge_list
    ]
    save_batch_file(batch_data, source_name, current_page)


def document_export(document_list, source_name, current_page):
    batch_data = [
        {
            'id': d.id,
            'dataset': d.dataset_id,
            'name': d.name,
            'char_length': d.char_length,
            'status': d.status,
            'status_meta': d.status_meta,
            'is_active': d.is_active,
            'type': d.type,
            'hit_handling_method': d.hit_handling_method,
            'directly_return_similarity': d.directly_return_similarity,
            'meta': d.meta,
            'create_time': d.create_time,
            'update_time': d.update_time,
        }
        for d in document_list
    ]
    save_batch_file(batch_data, source_name, current_page)


def paragraph_export(paragraph_list, source_name, current_page):
    batch_data = [
        {
            'id': p.id,
            'document': p.document_id,
            'dataset': p.dataset_id,
            'content': p.content,
            'title': p.title,
            'status': p.status,
            'status_meta': p.status_meta,
            'hit_num': p.hit_num,
            'is_active': p.is_active,
            'create_time': p.create_time,
            'update_time': p.update_time,
        }
        for p in paragraph_list
    ]
    save_batch_file(batch_data, source_name, current_page)


def problem_export(problem_list, source_name, current_page):
    batch_data = [
        {
            'id': prob.id,
            'dataset': prob.dataset_id,
            'content': prob.content,
            'hit_num': prob.hit_num,
            'create_time': prob.create_time,
            'update_time': prob.update_time,
        }
        for prob in problem_list
    ]
    save_batch_file(batch_data, source_name, current_page)


def problem_paragraph_mapping_export(problem_paragraph_mapping_list, source_name, current_page):
    batch_data = [
        {
            'id': m.id,
            'dataset': m.dataset_id,
            'document': m.document_id,
            'problem': m.problem_id,
            'paragraph': m.paragraph_id,
            'create_time': m.create_time,
            'update_time': m.update_time,
        }
        for m in problem_paragraph_mapping_list
    ]
    save_batch_file(batch_data, source_name, current_page)


def image_export(image_list, source_name, current_page):
    batch_data = []
    for image in image_list:
        try:
            batch_data.append({
                'id': image.id,
                'image_name': image.image_name,
                'image_data': image.image,
                'create_time': image.create_time,
                'update_time': image.update_time,
            })
        except Exception:
            pass
    save_batch_file(batch_data, source_name, current_page)


def file_export(file_list, source_name, current_page):
    batch_data = []
    for file in file_list:
        try:
            batch_data.append({
                'id': file.id,
                'file_name': file.file_name,
                'loid': file.loid,
                'meta': file.meta,
                'content': file.get_byte(),
                'create_time': file.create_time,
                'update_time': file.update_time,
            })
        except Exception:
            pass
    save_batch_file(batch_data, source_name, current_page)


def embedding_export(embedding_list, source_name, current_page):
    batch_data = [
        {
            'id': e.id,
            'source_id': e.source_id,
            'source_type': e.source_type,
            'is_active': e.is_active,
            'dataset': e.dataset_id,
            'document': e.document_id,
            'paragraph': e.paragraph_id,
            'embedding': e.embedding,
            'search_vector': e.search_vector,
            'meta': e.meta,
        }
        for e in embedding_list
    ]
    save_batch_file(batch_data, source_name, current_page)


def export():
    page(QuerySet(DataSet), 100, knowledge_export, "knowledge", "导出知识库")
    page(QuerySet(Document), 100, document_export, "document", "导出文档")
    page(QuerySet(Paragraph), 100, paragraph_export, "paragraph", "导出段落")
    page(QuerySet(Problem), 100, problem_export, "problem", "导出问题")
    page(QuerySet(ProblemParagraphMapping), 100, problem_paragraph_mapping_export, "problem_paragraph_mapping",
         "导出问题段落关联关系")
    page(QuerySet(File), 10, file_export, "file", "导出文件")
    page(QuerySet(Image), 10, image_export, "image", "导出图片")
    page(QuerySet(Embedding), 100, embedding_export, "embedding", "导出向量")
