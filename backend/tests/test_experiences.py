# 经验管理模块测试


def test_create_experience(client):
    """测试创建经验"""
    # 先创建项目
    project = client.post(
        "/api/v1/projects",
        json={"name": "Test Project"}
    ).json()

    # 创建经验
    response = client.post(
        f"/api/v1/projects/{project['id']}/experiences",
        json={
            "title": "Docker部署问题",
            "type": "bug",
            "content": "Docker容器内无法写入文件",
            "solution": "将用户加入docker group",
            "tags": ["docker", "permissions"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Docker部署问题"
    assert data["type"] == "bug"


def test_get_experiences(client):
    """测试获取经验列表"""
    # 先创建项目和经验
    project = client.post(
        "/api/v1/projects",
        json={"name": "Test Project"}
    ).json()

    client.post(
        f"/api/v1/projects/{project['id']}/experiences",
        json={"title": "经验1", "type": "bug", "content": "内容"}
    )

    # 获取列表
    response = client.get(f"/api/v1/projects/{project['id']}/experiences")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_experience(client):
    """测试获取单个经验"""
    # 先创建
    project = client.post(
        "/api/v1/projects",
        json={"name": "Test Project"}
    ).json()

    exp = client.post(
        f"/api/v1/projects/{project['id']}/experiences",
        json={"title": "测试经验", "type": "lesson", "content": "内容"}
    ).json()

    # 获取
    response = client.get(f"/api/v1/projects/{project['id']}/experiences/{exp['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == "测试经验"


def test_update_experience(client):
    """测试更新经验"""
    # 先创建
    project = client.post(
        "/api/v1/projects",
        json={"name": "Test Project"}
    ).json()

    exp = client.post(
        f"/api/v1/projects/{project['id']}/experiences",
        json={"title": "旧标题", "type": "note", "content": "内容"}
    ).json()

    # 更新
    response = client.put(
        f"/api/v1/projects/{project['id']}/experiences/{exp['id']}",
        json={"title": "新标题"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "新标题"


def test_delete_experience(client):
    """测试删除经验"""
    # 先创建
    project = client.post(
        "/api/v1/projects",
        json={"name": "Test Project"}
    ).json()

    exp = client.post(
        f"/api/v1/projects/{project['id']}/experiences",
        json={"title": "要删除", "type": "note", "content": "内容"}
    ).json()

    # 删除
    response = client.delete(f"/api/v1/projects/{project['id']}/experiences/{exp['id']}")
    assert response.status_code == 200
