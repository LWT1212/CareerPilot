# 项目模块测试


def test_create_project(client):
    """测试创建项目"""
    response = client.post(
        "/api/v1/projects",
        json={
            "name": "Test Project",
            "description": "测试项目",
            "icon": "🚀"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["description"] == "测试项目"
    assert data["status"] == "active"


def test_get_projects(client):
    """测试获取项目列表"""
    # 先创建一个项目
    client.post(
        "/api/v1/projects",
        json={"name": "Test Project"}
    )

    # 获取列表
    response = client.get("/api/v1/projects")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


def test_get_project(client):
    """测试获取单个项目"""
    # 先创建
    create_resp = client.post(
        "/api/v1/projects",
        json={"name": "Test Project"}
    )
    project_id = create_resp.json()["id"]

    # 获取
    response = client.get(f"/api/v1/projects/{project_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Project"


def test_update_project(client):
    """测试更新项目"""
    # 先创建
    create_resp = client.post(
        "/api/v1/projects",
        json={"name": "Old Name"}
    )
    project_id = create_resp.json()["id"]

    # 更新
    response = client.put(
        f"/api/v1/projects/{project_id}",
        json={"name": "New Name"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


def test_delete_project(client):
    """测试删除项目"""
    # 先创建
    create_resp = client.post(
        "/api/v1/projects",
        json={"name": "To Delete"}
    )
    project_id = create_resp.json()["id"]

    # 删除
    response = client.delete(f"/api/v1/projects/{project_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "删除成功"
