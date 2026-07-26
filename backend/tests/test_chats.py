# 聊天模块测试


def test_create_chat(client):
    """测试创建聊天"""
    # 先创建项目
    project = client.post(
        "/api/v1/projects",
        json={"name": "Test Project"}
    ).json()

    # 创建聊天
    response = client.post(
        f"/api/v1/projects/{project['id']}/chats",
        json={"title": "测试聊天", "model": "gpt-4"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "测试聊天"
    assert data["model"] == "gpt-4"


def test_get_chats(client):
    """测试获取聊天列表"""
    # 先创建项目和聊天
    project = client.post(
        "/api/v1/projects",
        json={"name": "Test Project"}
    ).json()

    client.post(
        f"/api/v1/projects/{project['id']}/chats",
        json={"title": "聊天1"}
    )

    # 获取列表
    response = client.get(f"/api/v1/projects/{project['id']}/chats")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_send_message(client):
    """测试发送消息"""
    # 先创建项目和聊天
    project = client.post(
        "/api/v1/projects",
        json={"name": "Test Project"}
    ).json()

    chat = client.post(
        f"/api/v1/projects/{project['id']}/chats",
        json={"title": "测试聊天"}
    ).json()

    # 发送消息
    response = client.post(
        f"/api/v1/chats/{chat['id']}/messages",
        json={"content": "你好"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "assistant"
    assert "收到你的消息" in data["content"]


def test_get_messages(client):
    """测试获取消息列表"""
    # 先创建项目、聊天、发送消息
    project = client.post(
        "/api/v1/projects",
        json={"name": "Test Project"}
    ).json()

    chat = client.post(
        f"/api/v1/projects/{project['id']}/chats",
        json={"title": "测试聊天"}
    ).json()

    client.post(
        f"/api/v1/chats/{chat['id']}/messages",
        json={"content": "你好"}
    )

    # 获取消息
    response = client.get(f"/api/v1/chats/{chat['id']}/messages")
    assert response.status_code == 200
    assert response.json()["total"] >= 1


def test_delete_chat(client):
    """测试删除聊天"""
    # 先创建
    project = client.post(
        "/api/v1/projects",
        json={"name": "Test Project"}
    ).json()

    chat = client.post(
        f"/api/v1/projects/{project['id']}/chats",
        json={"title": "要删除的聊天"}
    ).json()

    # 删除
    response = client.delete(f"/api/v1/projects/{project['id']}/chats/{chat['id']}")
    assert response.status_code == 200
