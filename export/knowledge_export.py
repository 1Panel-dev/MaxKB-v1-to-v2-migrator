# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： knowledge_export.py
    @date：2025/7/29 14:45
    @desc:
"""
from django.db.models import QuerySet
from rest_framework import serializers

from dataset.models import DataSet, Document, Paragraph, Problem, ProblemParagraphMapping, Image, File
from embedding.models import Embedding
from commons.util import page, save_batch_file


class KnowledgeModel(serializers.ModelSerializer):
    class Meta:
        model = DataSet
        fields = "__all__"


class DocumentModel(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = "__all__"


class ParagraphModel(serializers.ModelSerializer):
    class Meta:
        model = Paragraph
        fields = "__all__"


class ProblemModel(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = "__all__"


class ProblemParagraphMappingModel(serializers.ModelSerializer):
    class Meta:
        model = ProblemParagraphMapping
        fields = "__all__"


class ImageModel(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"


class FileModel(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = "__all__"


class EmbeddingModel(serializers.ModelSerializer):
    class Meta:
        model = Embedding
        fields = "__all__"


def knowledge_export(knowledge_list, source_name, current_page):
    batch_data = [KnowledgeModel(knowledge).data for knowledge in knowledge_list]
    save_batch_file(batch_data, source_name, current_page)


def document_export(document_list, source_name, current_page):
    batch_data = [DocumentModel(document).data for document in document_list]
    save_batch_file(batch_data, source_name, current_page)


def paragraph_export(paragraph_list, source_name, current_page):
    batch_data = [ParagraphModel(paragraph).data for paragraph in paragraph_list]
    save_batch_file(batch_data, source_name, current_page)


def problem_export(problem_list, source_name, current_page):
    batch_data = [ProblemModel(problem).data for problem in problem_list]
    save_batch_file(batch_data, source_name, current_page)


def problem_paragraph_mapping_export(problem_paragraph_mapping_list, source_name, current_page):
    batch_data = [ProblemParagraphMappingModel(problem_paragraph_mapping).data for problem_paragraph_mapping in
                  problem_paragraph_mapping_list]
    save_batch_file(batch_data, source_name, current_page)


def image_export(image_list, source_name, current_page):
    batch_data = [ImageModel(image).data for image in
                  image_list]
    save_batch_file(batch_data, source_name, current_page)


def file_export(file_list, source_name, current_page):
    batch_data = [{**FileModel(file).data, 'content': file.get_byte().tobytes()} for file in
                  file_list]
    save_batch_file(batch_data, source_name, current_page)


def embedding_export(embedding_list, source_name, current_page):
    batch_data = [EmbeddingModel(embedding).data for embedding in embedding_list]
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
