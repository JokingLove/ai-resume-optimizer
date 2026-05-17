#!/usr/bin/env python3
"""Quick verification that the /analyze endpoint works with realistic inputs."""
import json
import time
import requests

def test_analyze():
    url = "http://127.0.0.1:5002/analyze"
    payload = {
        "resume_text": """张三
        求职意向：Python后端开发工程师
        专业技能：Python, Django, Flask, RESTful API, MySQL, Redis
        工作经验：
        2021-2023 某科技公司 后端开发工程师
          - 负责电商平台订单系统的设计与开发，使用Django框架
          - 优化数据库查询，提升接口响应速度40%
          - 微服务改造，使用Docker容器化部署
        2020-2021 某互联网公司 Java开发工程师
          - 参与金融交易系统后端开发，使用Spring Boot
        教育背景：某大学 计算机科学与技术 本科 2016-2020
        """,
        "jd_text": """职位名称：高级Python后端开发工程师
        任职要求：
        1. 3年以上Python后端开发经验
        2. 精通Django或Flask框架
        3. 熟悉MySQL、PostgreSQL等关系型数据库
        4. 了解Redis、MongoDB等NoSQL数据库
        5. 有微服务架构设计经验
        6. 熟练使用Git进行版本控制
        7. 良好的问题分析和解决能力
        职责描述：
        - 负责公司核心业务系统的后端设计与开发
        - 参与技术方案评审和代码审查
        - 优化系统性能，提升并发处理能力
        - 编写技术文档和开发规范
        """
    }
    
    print("发送请求到 /analyze...")
    start = time.time()
    try:
        resp = requests.post(url, json=payload, timeout=120)
        elapsed = time.time() - start
        print(f"请求耗时: {elapsed:.1f}秒")
        print(f"状态码: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"成功: {data.get('success')}")
            print(f"匹配分数: {data.get('score')}")
            print(f"关键词匹配率: {data.get('keyword_match_rate')}%")
            print(f"匹配技能: {data.get('skills', {}).get('matched', [])}")
            print(f"缺失技能: {data.get('skills', {}).get('missing', [])}")
            suggestions = data.get('suggestions', [])
            print(f"建议数量: {len(suggestions)}")
            if suggestions:
                print(f"第一条建议: {suggestions[0].get('title') if isinstance(suggestions[0], dict) else suggestions[0]}")
            opt_resume = data.get('optimized_resume', '')
            print(f"优化后简历长度: {len(opt_resume)}字符")
            if len(opt_resume) > 200:
                print(f"优化后简历前200字符: {opt_resume[:200]}...")
            return True
        else:
            print(f"错误: {resp.text}")
            return False
    except requests.exceptions.Timeout:
        print("请求超时（>120秒）")
        return False
    except Exception as e:
        print(f"异常: {e}")
        return False

if __name__ == "__main__":
    success = test_analyze()
    if success:
        print("\n✅ 测试通过：/analyze 端点正常工作")
    else:
        print("\n❌ 测试失败：/analyze 端点仍有问题")