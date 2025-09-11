import pickle
import re
import uuid

from django.db import models
from django.db.models import QuerySet
from knowledge.models import KnowledgeFolder, Knowledge, KnowledgeType, KnowledgeScope, Document, Paragraph, \
    ProblemParagraphMapping, Problem, Embedding, File, FileSourceType
from system_manage.models import WorkspaceUserResourcePermission

from application.models import ApplicationKnowledgeMapping
from commons.util import import_page, ImportQuerySet, import_check, rename, to_workspace_user_resource_permission


def to_v2_knowledge(knowledge):
    return Knowledge(
        id=knowledge.get('id'),
        name=knowledge.get('name'),
        workspace_id='default',
        desc=knowledge.get('desc'),
        type=knowledge.get('type', KnowledgeType.BASE),
        user_id=knowledge.get('user'),
        scope=KnowledgeScope.WORKSPACE,
        folder_id='default',
        embedding_model_id=knowledge.get('embedding_mode'),
        meta=knowledge.get('meta', {}),
    )


def to_v2_document(instance):
    return Document(
        id=instance.get('id'),
        knowledge_id=instance.get('dataset'),
        name=instance.get('name'),
        char_length=instance.get('char_length'),
        status=instance.get('status'),
        status_meta=instance.get('status_meta'),
        is_active=instance.get('is_active'),
        type=instance.get('type'),
        hit_handling_method=instance.get('hit_handling_method'),
        directly_return_similarity=instance.get('directly_return_similarity'),
        meta={**instance.get('meta'), 'allow_download': True},
    )


def to_v2_problem(instance):
    return Problem(
        id=instance.get('id'),
        knowledge_id=instance.get('dataset'),
        content=instance.get('content'),
        hit_num=instance.get('hit_num'),
    )


def to_v2_problem_paragraph_mapping(instance):
    return ProblemParagraphMapping(
        id=instance.get('id'),
        knowledge_id=instance.get('dataset'),
        document_id=instance.get('document'),
        problem_id=instance.get('problem'),
        paragraph_id=instance.get('paragraph'),
    )


def to_v2_embedding(instance):
    return Embedding(
        id=instance.get('id'),
        source_id=instance.get('source_id'),
        source_type=instance.get('source_type'),
        is_active=instance.get('is_active'),
        knowledge_id=instance.get('dataset'),
        document_id=instance.get('document'),
        paragraph_id=instance.get('paragraph'),
        embedding=instance.get('embedding'),
        search_vector=instance.get('search_vector'),
        meta=instance.get('meta'),
    )


def knowledge_import(file_list, source_name, current_page):
    for file in file_list:
        knowledge_list = pickle.loads(file.read_bytes())
        knowledge_model_list = [to_v2_knowledge(item) for item in knowledge_list]
        QuerySet(Knowledge).bulk_create(knowledge_model_list)
        # 删除授权相关数据
        for knowledge_model in knowledge_model_list:
            QuerySet(WorkspaceUserResourcePermission).filter(
                target=knowledge_model.id, user_id=knowledge_model.user_id).delete()
        # 插入授权数据
        knowledge_permission_list = [
            to_workspace_user_resource_permission(knowledge_model.user_id, 'KNOWLEDGE', knowledge_model.id)
            for
            knowledge_model in knowledge_model_list]
        QuerySet(WorkspaceUserResourcePermission).bulk_create(knowledge_permission_list)
        rename(file)


def document_import(file_list, source_name, current_page):
    for file in file_list:
        document_list = pickle.loads(file.read_bytes())
        document_model_list = [to_v2_document(item) for item in document_list]
        QuerySet(Document).bulk_create(document_model_list)
        rename(file)


def problem_import(file_list, source_name, current_page):
    for file in file_list:
        problem_list = pickle.loads(file.read_bytes())
        problem_model_list = [to_v2_problem(item) for item in problem_list]
        QuerySet(Problem).bulk_create(problem_model_list)
        rename(file)


def extract_file_and_image_ids(content):
    # UUID 格式的正则表达式：8-4-4-4-12 个十六进制字符
    uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'

    # 提取 /api/file/ 后面的有效 UUID
    file_matches = re.findall(rf'/api/file/({uuid_pattern})', content, re.IGNORECASE)

    # 提取 /api/image/ 后面的有效 UUID
    image_matches = re.findall(rf'/api/image/({uuid_pattern})', content, re.IGNORECASE)

    # 验证提取的 UUID 是否有效
    valid_file_ids = []
    for match in file_matches:
        try:
            uuid.UUID(match)  # 验证 UUID 格式
            valid_file_ids.append(match)
        except ValueError:
            print(f"警告: 无效的文件 UUID: {match}")

    valid_image_ids = []
    for match in image_matches:
        try:
            uuid.UUID(match)  # 验证 UUID 格式
            valid_image_ids.append(match)
        except ValueError:
            print(f"警告: 无效的图片 UUID: {match}")

    return valid_file_ids, valid_image_ids


def paragraph_import(file_list, source_name, current_page):
    for file in file_list:
        paragraph_list = pickle.loads(file.read_bytes())

        QuerySet(Paragraph).filter(id__in=[p.get('id') for p in paragraph_list]).delete()
        # 按 document_id 分组并为每组分配递增的 position
        from collections import defaultdict
        document_paragraphs = defaultdict(list)

        for item in paragraph_list:
            document_paragraphs[item.get('document')].append(item)

        # 查询每个文档已有的最大 position
        document_ids = list(document_paragraphs.keys())
        existing_positions = {}

        for doc_id in document_ids:
            max_position = QuerySet(Paragraph).filter(document=doc_id).aggregate(
                max_pos=models.Max('position')
            )['max_pos']
            existing_positions[doc_id] = max_position or 0

        paragraph_model_list = []
        for document_id, paragraphs in document_paragraphs.items():
            start_position = existing_positions[document_id]

            for i, item in enumerate(paragraphs):
                content = item.get('content')
                file_ids, image_ids = extract_file_and_image_ids(content)
                # 更新File表
                for file_id in file_ids + image_ids:
                    QuerySet(File).filter(id=file_id).update(
                        source_id=item.get('document'),
                        source_type=FileSourceType.DOCUMENT
                    )

                content = (
                    content
                    .replace('/api/file/', './oss/file/')
                    .replace('/api/image/', './oss/file/')
                )

                paragraph = Paragraph(
                    id=item.get('id'),
                    document_id=item.get('document'),
                    knowledge_id=item.get('dataset'),
                    content=content,
                    title=item.get('title'),
                    status=item.get('status'),
                    status_meta=item.get('status_meta'),
                    hit_num=item.get('hit_num'),
                    is_active=item.get('is_active'),
                    position=start_position + i + 1  # 从已有最大值+1开始
                )
                paragraph_model_list.append(paragraph)

        QuerySet(Paragraph).bulk_create(paragraph_model_list)
        rename(file)


def problem_paragraph_mapping_import(file_list, source_name, current_page):
    for file in file_list:
        mapping_list = pickle.loads(file.read_bytes())
        problem_paragraph_model_list = [to_v2_problem_paragraph_mapping(item) for item in mapping_list]
        QuerySet(ProblemParagraphMapping).bulk_create(problem_paragraph_model_list)
        rename(file)


def embedding_import(file_list, source_name, current_page):
    for file in file_list:
        mapping_list = pickle.loads(file.read_bytes())
        embedding_model_list = [to_v2_embedding(item) for item in mapping_list]
        QuerySet(Embedding).bulk_create(embedding_model_list)
        rename(file)


def to_v2_application_knowledge_mapping(application_dataset_mapping):
    return ApplicationKnowledgeMapping(id=application_dataset_mapping.get('id'),
                                       application_id=application_dataset_mapping.get('application'),
                                       knowledge_id=application_dataset_mapping.get('dataset'))


def application_dataset_mapping_import(file_list, source_name, current_page):
    for file in file_list:
        application_dataset_mapping_list = pickle.loads(file.read_bytes())
        adm_model_list = [to_v2_application_knowledge_mapping(adm) for adm in application_dataset_mapping_list]
        QuerySet(ApplicationKnowledgeMapping).bulk_create(adm_model_list)
        rename(file)


def check_knowledge_folder():
    if not QuerySet(KnowledgeFolder).filter(id='default').exists():
        KnowledgeFolder(id='default', name='根目录', desc='default', user_id=None, workspace_id='default').save()


def import_():
    check_knowledge_folder()

    import_page(ImportQuerySet('knowledge'), 1, knowledge_import, "knowledge", "导入知识库", check=import_check)
    import_page(ImportQuerySet('document'), 1, document_import, "document", "导入文档", check=import_check)
    import_page(ImportQuerySet('paragraph'), 1, paragraph_import, "paragraph", "导入段落", check=import_check)
    import_page(ImportQuerySet('problem'), 1, problem_import, "problem", "导入问题", check=import_check)
    import_page(
        ImportQuerySet('problem_paragraph_mapping'), 1, problem_paragraph_mapping_import, "problem_paragraph_mapping",
        "导入问题段落关联关系", check=import_check
    )
    import_page(ImportQuerySet('embedding'), 1, embedding_import, "embedding", "导入向量", check=import_check)
    import_page(ImportQuerySet('application_dataset_mapping'), 1, application_dataset_mapping_import,
                "application_dataset_mapping",
                "导入应用和知识库的关联关系", check=import_check)


def check_knowledge_empty():
    return not QuerySet(Knowledge).exists()
