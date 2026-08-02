# RAG服务 - 文档解析、分块、向量嵌入、检索
# 流程: 文档 → 解析 → 分块 → 嵌入 → ChromaDB → 检索 → 组装上下文

import os
import uuid
from typing import List, Optional

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings

# ChromaDB 持久化目录
CHROMA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "chroma_data")
os.makedirs(CHROMA_DIR, exist_ok=True)

# 创建 ChromaDB 客户端（持久化）
_client = chromadb.PersistentClient(path=CHROMA_DIR)


def _get_collection(project_id: str):
    """获取项目的向量集合（每个项目一个集合）"""
    collection_name = f"project_{project_id[:8]}"
    return _client.get_or_create_collection(name=collection_name)


def embed_texts(texts: List[str]) -> List[List[float]]:
    """调用 Ollama embedding 模型生成向量"""
    import requests
    response = requests.post(
        f"{settings.OLLAMA_BASE_URL}/api/embed",
        json={"model": "nomic-embed-text", "input": texts},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["embeddings"]


def parse_document(file_path: str, file_type: str) -> str:
    """解析文档为纯文本"""
    ext = file_type.lower()

    if ext == "txt" or ext == "md":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    elif ext == "pdf":
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    elif ext == "docx":
        import docx
        doc = docx.Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)

    else:
        raise ValueError(f"不支持的文件类型: {file_type}")


def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    """将长文本分块"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return splitter.split_text(text)


def index_document(project_id: str, doc_id: str, file_path: str, file_type: str) -> int:
    """
    对文档进行索引：
    解析 → 分块 → 嵌入 → 存入ChromaDB
    返回分块数量
    """
    # 1. 解析文档
    text = parse_document(file_path, file_type)
    if not text.strip():
        return 0

    # 2. 分块
    chunks = chunk_text(text)

    # 3. 生成向量
    embeddings = embed_texts(chunks)

    # 4. 存入ChromaDB（每个块一个条目，metadata记录文档ID和块序号）
    collection = _get_collection(project_id)
    ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [
        {"doc_id": doc_id, "chunk_index": i, "content": chunks[i]}
        for i in range(len(chunks))
    ]
    collection.upsert(ids=ids, embeddings=embeddings, metadatas=metadatas)

    return len(chunks)


def delete_document_vectors(project_id: str, doc_id: str):
    """删除文档的向量（文档被删除时调用）"""
    try:
        collection = _get_collection(project_id)
        # 查询该文档的所有块ID
        result = collection.get(where={"doc_id": doc_id})
        if result and result["ids"]:
            collection.delete(ids=result["ids"])
    except Exception as e:
        print(f"删除向量失败: {e}")


def search_documents(project_id: str, query: str, top_k: int = 5) -> List[dict]:
    """
    语义检索：查询向量 → 返回Top-K结果
    """
    try:
        collection = _get_collection(project_id)
        # 生成查询向量
        query_embedding = embed_texts([query])[0]
        # 检索
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )
        # 组装结果
        items = []
        if results and results.get("metadatas"):
            for meta, distance in zip(results["metadatas"][0], results["distances"][0]):
                items.append({
                    "content": meta.get("content", ""),
                    "doc_id": meta.get("doc_id", ""),
                    "score": 1 - distance,  # 距离转相似度
                })
        return items
    except Exception as e:
        print(f"检索失败: {e}")
        return []


def build_rag_context(project_id: str, query: str, top_k: int = 5) -> str:
    """构建RAG上下文：检索相关内容并组装"""
    results = search_documents(project_id, query, top_k)
    if not results:
        return ""

    context_parts = []
    for i, r in enumerate(results, 1):
        context_parts.append(f"[资料{i}] {r['content']}")

    return "\n\n".join(context_parts)
