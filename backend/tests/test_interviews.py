# 面试模块测试


def test_create_interview(client):
    """测试创建面试记录"""
    # 先创建项目
    project = client.post(
        "/api/v1/projects",
        json={"name": "Test Project"}
    ).json()

    # 创建面试
    response = client.post(
        f"/api/v1/projects/{project['id']}/interviews",
        json={
            "company": "字节跳动",
            "position": "后端工程师",
            "interview_date": "2024-01-20",
            "status": "completed",
            "result": "offer",
            "overall_feedback": "项目经验丰富"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["company"] == "字节跳动"
    assert data["result"] == "offer"


def test_get_interviews(client):
    """测试获取面试列表"""
    # 先创建项目和面试
    project = client.post(
        "/api/v1/projects",
        json={"name": "Test Project"}
    ).json()

    client.post(
        f"/api/v1/projects/{project['id']}/interviews",
        json={"company": "阿里巴巴", "position": "后端"}
    )

    # 获取列表
    response = client.get(f"/api/v1/projects/{project['id']}/interviews")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_add_question(client):
    """测试添加面试问题"""
    # 先创建项目和面试
    project = client.post(
        "/api/v1/projects",
        json={"name": "Test Project"}
    ).json()

    interview = client.post(
        f"/api/v1/projects/{project['id']}/interviews",
        json={"company": "腾讯"}
    ).json()

    # 添加问题
    response = client.post(
        f"/api/v1/interviews/{interview['id']}/questions",
        json={
            "question": "Redis的持久化机制有哪些？",
            "user_answer": "RDB和AOF",
            "category": "Redis",
            "difficulty": "medium",
            "rating": 4
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == "Redis的持久化机制有哪些？"
    assert data["rating"] == 4


def test_get_stats(client):
    """测试获取面试统计"""
    # 先创建项目
    project = client.post(
        "/api/v1/projects",
        json={"name": "Test Project"}
    ).json()

    # 获取统计
    response = client.get(f"/api/v1/projects/{project['id']}/interviews/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_interviews" in data
    assert "total_questions" in data


def test_delete_interview(client):
    """测试删除面试记录"""
    # 先创建
    project = client.post(
        "/api/v1/projects",
        json={"name": "Test Project"}
    ).json()

    interview = client.post(
        f"/api/v1/projects/{project['id']}/interviews",
        json={"company": "要删除"}
    ).json()

    # 删除
    response = client.delete(f"/api/v1/projects/{project['id']}/interviews/{interview['id']}")
    assert response.status_code == 200
