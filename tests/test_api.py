import sys
import os
import json
import pytest
from unittest.mock import patch

# 将 code 目录添加到路径，以便导入 app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../code'))

from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    """测试健康检查端点"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'
    assert 'version' in data
    assert 'api_keys_count' in data

def test_analyze_normal(client):
    """测试正常分析请求"""
    mock_result = {
        "resume_info": {
            "skills": ["Python", "Flask"],
            "experience_years": 3,
            "education": ["本科"]
        },
        "jd_info": {
            "job_title": "后端工程师",
            "required_skills": ["Python", "SQL"],
            "preferred_skills": ["Docker"]
        },
        "match_result": {
            "score": 85,
            "keyword_match_rate": 75.0,
            "matched_skills": ["Python"],
            "missing_skills": ["SQL"],
            "suggestions": [
                {
                    "type": "keyword",
                    "priority": "high",
                    "title": "增加SQL",
                    "description": "内容",
                    "action": "行动"
                }
            ],
            "optimized_resume": "Optimized text"
        }
    }
    
    with patch('app.run_analysis', return_value=mock_result):
        payload = {
            "resume_text": "My resume content with Python and Flask",
            "jd_text": "Job seeking Python developer with SQL knowledge"
        }
        response = client.post('/analyze', json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['score'] == 85
        assert "Python" in data['skills']['matched']
        assert data['jd_summary']['job_title'] == "后端工程师"

def test_analyze_empty_input(client):
    """测试空输入"""
    # 空对象 {} → data 为 {} → resume_text.strip() 为 "" → "请提供简历内容"
    response = client.post('/analyze', json={})
    assert response.status_code == 400
    assert "请提供简历内容" in response.get_json()['error']

    # 空字符串 resume_text → "请提供简历内容"
    response = client.post('/analyze', json={"resume_text": "", "jd_text": "test"})
    assert response.status_code == 400
    assert "请提供简历内容" in response.get_json()['error']

    # 仅提供 jd_text → "请提供简历内容"
    response = client.post('/analyze', json={"jd_text": "test"})
    assert response.status_code == 400
    assert "请提供简历内容" in response.get_json()['error']

    # 仅提供 resume_text → "请提供岗位描述"
    response = client.post('/analyze', json={"resume_text": "test"})
    assert response.status_code == 400
    assert "请提供岗位描述" in response.get_json()['error']

def test_analyze_invalid_json(client):
    """测试无效JSON"""
    response = client.post('/analyze', data="not a json", content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    # get_json(silent=True) 对无效JSON返回 None → 触发 "请提供JSON数据"
    assert "请提供JSON数据" in data['error']

def test_analyze_runtime_error(client):
    """测试AI服务错误 (RuntimeError)"""
    with patch('app.run_analysis', side_effect=RuntimeError("LLM failed")):
        payload = {"resume_text": "test", "jd_text": "test"}
        response = client.post('/analyze', json=payload)
        assert response.status_code == 503
        assert "AI服务暂时不可用" in response.get_json()['error']

def test_analyze_unexpected_error(client):
    """测试未知错误 (Exception)"""
    with patch('app.run_analysis', side_effect=Exception("Unknown error")):
        payload = {"resume_text": "test", "jd_text": "test"}
        response = client.post('/analyze', json=payload)
        assert response.status_code == 500
        assert "分析失败" in response.get_json()['error']
