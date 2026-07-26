# 知识库模块测试

import io


def test_upload_document(client):
    """测试上传文档"""
    # 先创建项目
    project = client.post(
        "/api/v1/projects",
        json={"name": "Test Project"}
    ).json()

    # 上传文件
    file_content = b"This is a test document content."
    response = client.post(
        f"/api/v1/projects/{project['id']}/knowledge",
        files={"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.txt"
    assert data["file_type"] == "txt"


def test_get_documents(client):
    """测试获取文档列表"""
    # 先创建项目和上传文档
    project = client.post(
        "/api/v1/projects",
        json={"name": "Test Project"}
    ).json()

    client.post(
        f"/api/v1/projects/{project['id']}/knowledge",
        files={"file": ("test.txt", io.BytesIO(b"content"), "text/plain")}
    )

    # 获取列表
    response = client.get(f"/api/v1/projects/{project['id']}/knowledge")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_search_knowledge(client):
    """测试知识检索"""
    # 先创建项目
    project = client.post(
        "/api/v1/projects",
        json={"name": "Test Project"}
    ).json()

    # 搜索（即使没有文档也应该返回空结果）
    response = client.post(
        f"/api/v1/projects/{project['id']}/knowledge/search",
        json={"query": "Redis", "top_k": 5}
    )
    assert response.status_code == 200
    assert "results" in response.json()


def test_delete_document(client):
    """测试删除文档"""
    # 先创建项目和上传文档
    project = client.post(
        "/api/v1/projects",
        json={"name": "Test Project"}
    ).json()

    doc = client.post(
        f"/api/v1/projects/{project['id']}/knowledge",
        files={"file": ("test.txt", io.BytesIO(b"content"), "text/plain")}
    ).json()

    # 删除
    response = client.delete(f"/api/v1/projects/{project['id']}/knowledge/{doc['id']}")
    assert response.status_code == 200
