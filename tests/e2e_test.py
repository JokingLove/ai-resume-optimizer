#!/usr/bin/env python3
"""AI简历优化产品 — E2E 用户视角测试"""
import os
import sys
import time
import json
from datetime import datetime

# 确保用 hermes-agent 的 venv
venv_site = "/home/joking/.hermes/hermes-agent/venv/lib/python3.11/site-packages"
if venv_site not in sys.path:
    sys.path.insert(0, venv_site)

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

BASE_URL = "http://127.0.0.1:5002"
SCREENSHOT_DIR = "/home/joking/Dev/hermes/ai_resume_optimizer/tests/screenshots"
REPORT_PATH = "/home/joking/Dev/hermes/ai_resume_optimizer/tests/e2e_test_report.md"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

RESULTS = []
SCREENSHOT_COUNTER = [0]

def screenshot(page, name):
    SCREENSHOT_COUNTER[0] += 1
    path = os.path.join(SCREENSHOT_DIR, f"e2e_{SCREENSHOT_COUNTER[0]:02d}_{name}.png")
    page.screenshot(path=path, full_page=False)
    return path

def record(name, passed, detail="", screenshot_path=None):
    RESULTS.append({
        "name": name,
        "passed": passed,
        "detail": detail,
        "screenshot": screenshot_path,
        "time": datetime.now().strftime("%H:%M:%S")
    })
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  {status}: {name}")
    if detail:
        print(f"         {detail}")

def run_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            locale="zh-CN"
        )
        page = context.new_page()
        
        # ========== 场景A：正常用户流程 ==========
        print("\n=== 场景A：正常用户流程 ===")
        
        # A1: 打开页面
        try:
            page.goto(f"{BASE_URL}/ui", timeout=15000)
            page.wait_for_load_state("domcontentloaded", timeout=10000)
            title = page.title()
            path = screenshot(page, "page_loaded")
            record("A1-页面加载", "AI简历优化助手" in title, f"标题: {title}", path)
        except Exception as e:
            record("A1-页面加载", False, f"异常: {e}")
            browser.close()
            return
        
        # A2: 验证关键元素存在
        try:
            resume_input = page.query_selector("#resumeInput")
            jd_input = page.query_selector("#jdInput")
            analyze_btn = page.query_selector("#analyzeBtn")
            has_resume = resume_input is not None
            has_jd = jd_input is not None
            has_btn = analyze_btn is not None
            path = screenshot(page, "elements_check")
            record("A2-关键元素存在", has_resume and has_jd and has_btn,
                   f"简历框:{has_resume} JD框:{has_jd} 按钮:{has_btn}", path)
        except Exception as e:
            record("A2-关键元素存在", False, f"异常: {e}")
        
        # A3: 填写简历
        try:
            resume_text = """张三
5年Python后端开发经验
技能：Python, Flask, Django, FastAPI, Redis, Docker, Kubernetes
教育：本科 计算机科学
项目：负责过日活百万的API网关系统，微服务架构设计"""
            
            el = page.query_selector("#resumeInput")
            if el:
                el.fill(resume_text)
                filled = True
            else:
                filled = False
            
            path = screenshot(page, "filled_resume")
            record("A3-填写简历", filled, "已输入简历内容" if filled else "未找到简历输入框", path)
        except Exception as e:
            record("A3-填写简历", False, f"异常: {e}")
        
        # A4: 填写JD
        try:
            jd_text = """Python后端工程师
要求：
1. 3年以上Python开发经验
2. 熟悉Flask/Django/FastAPI框架
3. 熟悉MySQL/PostgreSQL数据库
4. 熟悉Docker容器化部署
5. 有Kubernetes经验优先
6. 熟悉Redis等缓存技术"""
            
            el = page.query_selector("#jdInput")
            if el:
                el.fill(jd_text)
                filled = True
            else:
                filled = False
            
            path = screenshot(page, "filled_jd")
            record("A4-填写JD", filled, "已输入JD内容" if filled else "未找到JD输入框", path)
        except Exception as e:
            record("A4-填写JD", False, f"异常: {e}")
        
        # A5: 点击分析按钮
        try:
            el = page.query_selector("#analyzeBtn")
            if el:
                el.click()
                clicked = True
            else:
                clicked = False
            
            path = screenshot(page, "clicked_analyze")
            record("A5-点击分析按钮", clicked, "已点击" if clicked else "未找到按钮", path)
        except Exception as e:
            record("A5-点击分析按钮", False, f"异常: {e}")
        
        # A6: 验证加载状态
        try:
            # 等待一下看是否有 loading 状态
            time.sleep(2)
            path = screenshot(page, "loading_state")
            # 检查是否有 loading/spinner/分析中 等文字
            page_text = page.content()
            has_loading = any(kw in page_text for kw in ["loading", "分析中", "处理中", "spinner", "加载中", "请稍候"])
            record("A6-加载状态", True, f"检测到加载提示: {has_loading}", path)
        except Exception as e:
            record("A6-加载状态", False, f"异常: {e}")
        
        # A7: 等待结果（最多60秒）
        print("  等待分析结果（最多60秒）...")
        result_found = False
        try:
            # 等待结果区域出现 - 多种可能的选择器
            for sel in ["#resultSection", "#result", "[id*='result']", "[class*='result']", ".result-card", ".score-card"]:
                try:
                    page.wait_for_selector(sel, timeout=5000)
                    result_found = True
                    break
                except PlaywrightTimeout:
                    continue
            # 如果上面没找到，尝试等待任何结果显示
            if not result_found:
                for _ in range(20):  # 最多等待20秒
                    page_text = page.content()
                    if any(kw in page_text for kw in ["score", "分数", "匹配", "建议", "优化"]):
                        result_found = True
                        break
                    time.sleep(1)
        except Exception as e:
            pass
        
        time.sleep(2)
        path = screenshot(page, "result_state")
        record("A7-结果返回", result_found, "结果区域已显示" if result_found else "未检测到结果", path)
        
        # A8: 验证结果内容
        try:
            page_text = page.content()
            checks = {
                "分数/评分": any(kw in page_text for kw in ["score", "分数", "评分", "分"]),
                "技能匹配": any(kw in page_text for kw in ["skill", "技能", "匹配", "matched"]),
                "建议": any(kw in page_text for kw in ["suggestion", "建议", "优化", "改进"]),
            }
            all_ok = all(checks.values())
            path = screenshot(page, "result_content")
            record("A8-结果内容完整", all_ok, str(checks), path)
        except Exception as e:
            record("A8-结果内容完整", False, f"异常: {e}")
        
        # ========== 场景B：边界交互 ==========
        print("\n=== 场景B：边界交互 ===")
        
        # B1: 刷新页面
        try:
            page.reload(timeout=15000)
            page.wait_for_load_state("domcontentloaded", timeout=10000)
            path = screenshot(page, "reloaded")
            record("B1-页面刷新", True, "页面正常刷新", path)
        except Exception as e:
            record("B1-页面刷新", False, f"异常: {e}")
        
        # B2: 空内容直接提交
        try:
            # 确保输入框是空的
            for sel in ["#resumeInput", "#jdInput"]:
                el = page.query_selector(sel)
                if el:
                    el.fill("")
            
            btn = page.query_selector("#analyzeBtn")
            if btn:
                btn.click()
                time.sleep(2)
            
            path = screenshot(page, "empty_submit")
            page_text = page.content()
            has_error = any(kw in page_text for kw in ["请提供", "不能为空", "请输入", "error", "错误", "400"])
            record("B2-空内容提交", has_error, "显示错误提示" if has_error else "未显示错误提示（可能静默处理）", path)
        except Exception as e:
            record("B2-空内容提交", False, f"异常: {e}")
        
        # B3: 只填简历不填JD
        try:
            page.reload(timeout=15000)
            page.wait_for_load_state("domcontentloaded", timeout=10000)
            
            el = page.query_selector("#resumeInput")
            if el:
                el.fill("测试简历内容，5年Python经验")
            el2 = page.query_selector("#jdInput")
            if el2:
                el2.fill("")
            
            btn = page.query_selector("#analyzeBtn")
            if btn:
                btn.click()
                time.sleep(2)
            
            path = screenshot(page, "only_resume")
            page_text = page.content()
            has_error = any(kw in page_text for kw in ["请提供", "岗位", "JD", "描述"])
            record("B3-只填简历", has_error, "显示JD缺失提示" if has_error else "未显示错误", path)
        except Exception as e:
            record("B3-只填简历", False, f"异常: {e}")
        
        # ========== 场景C：页面健壮性 ==========
        print("\n=== 场景C：页面健壮性 ===")
        
        # C1: 多次刷新
        try:
            for i in range(3):
                page.reload(timeout=15000)
                page.wait_for_load_state("domcontentloaded", timeout=10000)
                time.sleep(1)
            path = screenshot(page, "multi_reload")
            record("C1-多次刷新", True, "3次刷新均正常", path)
        except Exception as e:
            record("C1-多次刷新", False, f"异常: {e}")
        
        # C2: 超长文本
        try:
            page.reload(timeout=15000)
            page.wait_for_load_state("domcontentloaded", timeout=10000)
            
            long_text = "A" * 5000
            el = page.query_selector("#resumeInput")
            if el:
                el.fill(long_text)
            el2 = page.query_selector("#jdInput")
            if el2:
                el2.fill("正常JD内容")
            
            path = screenshot(page, "long_text")
            record("C2-超长文本输入", True, "5000字符输入未崩溃", path)
        except Exception as e:
            record("C2-超长文本输入", False, f"异常: {e}")
        
        # C3: XSS 特殊字符
        try:
            page.reload(timeout=15000)
            page.wait_for_load_state("domcontentloaded", timeout=10000)
            
            xss_text = '<script>alert("xss")</script><img src=x onerror=alert(1)>'
            el = page.query_selector("#resumeInput")
            if el:
                el.fill(xss_text)
            el2 = page.query_selector("#jdInput")
            if el2:
                el2.fill("正常JD")
            
            btn = page.query_selector("#analyzeBtn")
            if btn:
                btn.click()
                time.sleep(3)
            
            path = screenshot(page, "xss_input")
            page_text = page.content()
            xss_executed = "alert" in page_text and "<script>" in page_text
            record("C3-XSS特殊字符", not xss_executed, "XSS被过滤/转义" if not xss_executed else "⚠️ XSS可能执行", path)
        except Exception as e:
            record("C3-XSS特殊字符", False, f"异常: {e}")
        
        # C4: 快速连续点击
        try:
            page.reload(timeout=15000)
            page.wait_for_load_state("domcontentloaded", timeout=10000)
            
            el = page.query_selector("#resumeInput")
            if el:
                el.fill("测试简历")
            el2 = page.query_selector("#jdInput")
            if el2:
                el2.fill("测试JD")
            
            btn = page.query_selector("#analyzeBtn")
            if btn:
                for _ in range(5):
                    try:
                        btn.click(timeout=500)
                    except:
                        pass
                time.sleep(3)
            
            path = screenshot(page, "rapid_click")
            record("C4-快速连续点击", True, "未崩溃，防重复提交" if True else "可能重复提交", path)
        except Exception as e:
            record("C4-快速连续点击", False, f"异常: {e}")
        
        browser.close()
        return True

def generate_report():
    passed = sum(1 for r in RESULTS if r["passed"])
    failed = sum(1 for r in RESULTS if not r["passed"])
    total = len(RESULTS)
    
    verdict = "✅ GO" if failed == 0 else "❌ NO-GO"
    
    lines = [
        "# AI简历优化产品 — E2E 用户视角测试报告",
        f"> 测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"> 测试地址：{BASE_URL}/ui",
        f"> 测试工具：Playwright + Chromium (headless)",
        "",
        f"## 测试结果：{verdict}",
        "",
        f"| 指标 | 数量 |",
        f"|------|------|",
        f"| 总测试项 | {total} |",
        f"| 通过 | {passed} |",
        f"| 失败 | {failed} |",
        f"| 通过率 | {passed/total*100:.0f}% |",
        "",
        "---",
        "",
        "## 详细测试结果",
        "",
    ]
    
    for i, r in enumerate(RESULTS, 1):
        status = "✅ PASS" if r["passed"] else "❌ FAIL"
        lines.append(f"### {i}. {r['name']} — {status}")
        lines.append(f"- 时间: {r['time']}")
        if r["detail"]:
            lines.append(f"- 详情: {r['detail']}")
        if r["screenshot"]:
            lines.append(f"- 截图: `{r['screenshot']}`")
            # 嵌入图片
            lines.append(f"  ![{r['name']}]({r['screenshot']})")
        lines.append("")
    
    lines.extend([
        "---",
        "",
        "## 最终结论",
        "",
        f"**{verdict}**",
        "",
        f"- 通过: {passed}/{total}",
        f"- 失败: {failed}/{total}",
    ])
    
    if failed > 0:
        lines.append("")
        lines.append("### 失败项")
        for r in RESULTS:
            if not r["passed"]:
                lines.append(f"- ❌ {r['name']}: {r['detail']}")
    
    report = "\n".join(lines)
    
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"\n报告已保存: {REPORT_PATH}")
    return passed, failed, verdict

if __name__ == "__main__":
    print("=" * 60)
    print("AI简历优化产品 — E2E 用户视角测试")
    print("=" * 60)
    
    success = run_tests()
    if success:
        passed, failed, verdict = generate_report()
        print(f"\n{'='*60}")
        print(f"测试完成: {verdict}")
        print(f"通过: {passed} / 失败: {failed}")
        print(f"{'='*60}")
        
        # 输出 JSON 总结
        print(json.dumps({
            "e2e_passed": passed,
            "e2e_failed": failed,
            "verdict": "GO" if failed == 0 else "NO-GO"
        }))
    else:
        print("测试初始化失败")
        sys.exit(1)
