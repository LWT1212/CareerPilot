# 文档管理模块测试


def test_get_documents(client):
    """测试获取文档列表"""
    # 先创建项目
    project = client.post(
        "/api/v1/projects",
        json={"name": "Test Project"}
    ).json()

    # 获取列表
    response = client.get(f"/api/v1/projects/{project['id']}/documents")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_generate_document(client):
    """测试AI生成文档"""
    # 先创建项目
    project = client.post(
        "/api/v1/projects",
        json={"name": "Test Project"}
    ).json()

    # 生成文档
    response = client.post(
        f"/api/v1/projects/{project['id']}/documents/readme/generate",
        json={"instruction": "生成README"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["doc_type"] == "readme"
    assert data["is_auto_generated"] == True


def test_get_document(client):
    """测试获取单个文档"""
    # 先创建项目和生成文档
    project = client.post(
        "/api/v1/projects",
        json={"name": "Test Project"}
    ).json()

    client.post(
        f"/api/v1/projects/{project['id']}/documents/readme/generate",
        json={"instruction": "生成README"}
    )

    # 获取文档
    response = client.get(f"/api/v1/projects/{project['id']}/documents/readme")
    assert response.status_code == 200
    assert response.json()["doc_type"] == "readme"


def test_update_document(client):
    """测试更新文档"""
    # 先创建项目和生成文档
    project = client.post(
        "/api/v1/projects",
        json={"name": "Test Project"}
    ).json()

    client.post(
        f"/api/v1/projects/{project['id']}/documents/readme/generate",
        json={"instruction": "生成README"}
    )

    # 更新文档
    response = client.put(
        f"/api/v1/projects/{project['id']}/documents/readme",
        json={
            "content": "# 新的README\n\n这是手动更新的内容",
            "change_reason": "手动更新"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == 2  # 版本号应该增加
    assert data["is_auto_generated"] == False  # 手动更新
