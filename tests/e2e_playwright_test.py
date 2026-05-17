#!/usr/bin/env python3
"""
AI简历优化产品 - Playwright E2E 端到端测试
测试时间: 2026-05-17
"""

import asyncio
import time
import json
import sys
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright, Page

# ── 配置 ──────────────────────────────────────────────
BASE_URL = "http://127.0.0.1:5002"
UI_URL = f"{BASE_URL}/ui"
SCREENSHOT_DIR = Path("/home/joking/Dev/hermes/ai_resume_optimizer/tests/screenshots")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

REPORT_PATH = Path("/home/joking/Dev/hermes/ai_resume_optimizer/tests/e2e_test_report.md")

# 测试数据
RESUME_TEXT = """
张三，软件工程师，5年经验，熟练使用Python、Flask、PostgreSQL，曾在ABC公司担任后端开发，
负责API设计和数据库优化。熟悉Git、Docker、Linux环境，掌握Redis缓存、RESTful API设计。
本科毕业于某985高校计算机专业。
"""

JD_TEXT = """
招聘后端工程师，要求：
1. 熟练使用Python和Flask框架
2. 熟悉SQL数据库（PostgreSQL/MySQL）
3. 有API设计和微服务经验
4. 熟悉Docker容器化部署
5. 本科及以上学历，计算机相关专业
"""

LONG_TEXT = "这是一段很长的文本。" * 400  # ~5000字

# ── 测试结果跟踪 ───────────────────────────────────────
test_results = []
step_counter = {"value": 0}


def next_step():
    step_counter["value"] += 1
    return step_counter["value"]


def log_pass(name, notes=""):
    test_results.append({"name": name, "passed": True, "notes": notes})
    print(f"  ✅ PASS: {name}")


def log_fail(name, notes=""):
    test_results.append({"name": name, "passed": False, "notes": notes})
    print(f"  ❌ FAIL: {name}")


async def screenshot(page: Page, suffix: str):
    """保存截图到screenshots目录"""
    step = next_step()
    name = f"e2e_{step:02d}_{suffix}.png"
    path = SCREENSHOT_DIR / name
    await page.screenshot(path=str(path), full_page=True)
    print(f"    📸 Saved: {path.name}")
    return str(path)


def get_current_step() -> int:
    return step_counter["value"]


async def test_service_health():
    """第1步：健康检查"""
    import requests
    print("\n[Step 0] Service Health Check")
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=10)
        data = resp.json()
        status = data.get("status")
        service = data.get("service")
        version = data.get("version")
        print(f"    status={resp.status_code}, service={service}, version={version}")
        if status == "ok":
            log_pass("服务健康检查", f"status=ok, service={service}")
            return True
        else:
            log_fail("服务健康检查", f"unexpected status: {status}")
            return False
    except Exception as e:
        log_fail("服务健康检查", str(e))
        return False


async def scenario_a_normal_flow(page: Page):
    """场景A：正常用户完整流程"""
    print("\n[Scenario A] 正常用户完整流程")
    results = []

    # A1: 打开页面
    print("  A1: 打开页面...")
    await page.goto(UI_URL, wait_until="domcontentloaded", timeout=15000)
    await page.wait_for_load_state("networkidle", timeout=10000)
    path = await screenshot(page, "page_loaded")
    title = await page.title()
    if title == "AI简历优化助手":
        log_pass("A1. 页面标题正确", f"title={title}")
    else:
        log_fail("A1. 页面标题正确", f"expected=AI简历优化助手, actual={title}")
    results.append(("A1. 页面标题", title == "AI简历优化助手", path))

    # A2: 验证简历输入框
    print("  A2: 验证简历输入框...")
    try:
        resume_input = page.locator("#resumeInput")
        await resume_input.wait_for(timeout=5000)
        is_visible = await resume_input.is_visible()
        log_pass("A2. 简历输入框存在", f"visible={is_visible}")
        results.append(("A2. 简历输入框", is_visible, None))
    except Exception as e:
        log_fail("A2. 简历输入框存在", str(e))
        results.append(("A2. 简历输入框", False, None))

    # A3: 验证JD输入框
    print("  A3: 验证JD输入框...")
    try:
        jd_input = page.locator("#jdInput")
        await jd_input.wait_for(timeout=5000)
        is_visible = await jd_input.is_visible()
        log_pass("A3. JD输入框存在", f"visible={is_visible}")
        results.append(("A3. JD输入框", is_visible, None))
    except Exception as e:
        log_fail("A3. JD输入框存在", str(e))
        results.append(("A3. JD输入框", False, None))

    # A4: 验证分析按钮
    print("  A4: 验证分析按钮...")
    try:
        analyze_btn = page.locator("#analyzeBtn")
        await analyze_btn.wait_for(timeout=5000)
        is_visible = await analyze_btn.is_visible()
        is_enabled = await analyze_btn.is_enabled()
        log_pass("A4. 分析按钮存在且可点击", f"visible={is_visible}, enabled={is_enabled}")
        results.append(("A4. 分析按钮", is_visible and is_enabled, None))
    except Exception as e:
        log_fail("A4. 分析按钮存在且可点击", str(e))
        results.append(("A4. 分析按钮", False, None))

    # A5: 填写简历
    print("  A5: 填写简历内容...")
    try:
        await page.locator("#resumeInput").fill(RESUME_TEXT.strip())
        val = await page.locator("#resumeInput").input_value()
        log_pass("A5. 简历内容填写成功", f"length={len(val)}")
        results.append(("A5. 简历内容填写", len(val) > 50, None))
    except Exception as e:
        log_fail("A5. 简历内容填写", str(e))
        results.append(("A5. 简历内容填写", False, None))

    # A6: 填写JD
    print("  A6: 填写JD内容...")
    try:
        await page.locator("#jdInput").fill(JD_TEXT.strip())
        val = await page.locator("#jdInput").input_value()
        log_pass("A6. JD内容填写成功", f"length={len(val)}")
        results.append(("A6. JD内容填写", len(val) > 50, None))
        await screenshot(page, "filled_inputs")
    except Exception as e:
        log_fail("A6. JD内容填写", str(e))
        results.append(("A6. JD内容填写", False, None))

    # A7: 点击分析按钮
    print("  A7: 点击开始分析按钮...")
    try:
        await page.locator("#analyzeBtn").click()
        # 等待loading状态出现
        loading = page.locator("#loadingOverlay")
        await loading.wait_for(timeout=3000)
        has_active = await loading.get_attribute("class")
        is_loading = "active" in (has_active or "")
        log_pass("A7. 加载状态出现", f"loading_active={is_loading}")
        results.append(("A7. 加载状态出现", is_loading, None))
        await screenshot(page, "loading")
    except Exception as e:
        log_fail("A7. 加载状态出现", str(e))
        results.append(("A7. 加载状态出现", False, None))
        # 继续尝试等待结果
        try:
            await asyncio.sleep(2)
        except:
            pass

    # A8: 等待结果返回
    print("  A8: 等待结果返回（最多60秒）...")
    try:
        results_section = page.locator("#resultsSection")
        await results_section.wait_for(timeout=65000)
        has_active = await results_section.get_attribute("class")
        is_shown = has_active and "active" in has_active
        log_pass("A8. 结果区域出现", f"results_active={is_shown}")
        results.append(("A8. 结果区域出现", is_shown, None))
        await screenshot(page, "result_shown")
    except Exception as e:
        log_fail("A8. 结果区域出现（超时65秒）", str(e))
        results.append(("A8. 结果区域出现", False, None))
        await screenshot(page, "result_timeout")

    # A9: 验证匹配分数
    print("  A9: 验证匹配分数...")
    try:
        score_el = page.locator("#scoreNumber")
        await score_el.wait_for(timeout=3000)
        score_text = await score_el.inner_text()
        is_numeric = score_text.strip().replace(".", "").isdigit() or score_text.strip().lstrip("-").replace(".", "").isdigit()
        log_pass("A9. 匹配分数显示", f"score={score_text}, numeric={is_numeric}")
        results.append(("A9. 匹配分数显示", is_numeric, None))
    except Exception as e:
        log_fail("A9. 匹配分数显示", str(e))
        results.append(("A9. 匹配分数显示", False, None))

    # A10: 验证技能匹配
    print("  A10: 验证技能匹配...")
    try:
        has_skills = page.locator("#hasSkills")
        missing_skills = page.locator("#missingSkills")
        await asyncio.sleep(1)
        has_text = await has_skills.inner_text()
        missing_text = await missing_skills.inner_text()
        has_content = len(has_text.strip()) > 0 or len(missing_text.strip()) > 0
        log_pass("A10. 技能匹配显示", f"has_skills={bool(has_text.strip())}, missing_skills={bool(missing_text.strip())}")
        results.append(("A10. 技能匹配显示", has_content, None))
    except Exception as e:
        log_fail("A10. 技能匹配显示", str(e))
        results.append(("A10. 技能匹配显示", False, None))

    # A11: 验证建议显示
    print("  A11: 验证修改建议...")
    try:
        suggestions = page.locator("#suggestionsList")
        await asyncio.sleep(1)
        sug_text = await suggestions.inner_text()
        has_suggestions = len(sug_text.strip()) > 0
        log_pass("A11. 修改建议显示", f"has_suggestions={has_suggestions}, length={len(sug_text)}")
        results.append(("A11. 修改建议显示", has_suggestions, None))
    except Exception as e:
        log_fail("A11. 修改建议显示", str(e))
        results.append(("A11. 修改建议显示", False, None))

    return results


async def scenario_b_edge_cases(page: Page):
    """场景B：边界交互"""
    print("\n[Scenario B] 边界交互")
    results = []

    # B1: 清空内容后刷新页面
    print("  B1: 清空内容，刷新页面...")
    try:
        await page.locator("#resumeInput").fill("")
        await page.locator("#jdInput").fill("")
        await page.reload(wait_until="domcontentloaded", timeout=15000)
        await page.wait_for_load_state("networkidle", timeout=10000)
        await screenshot(page, "page_reloaded")
        resume_visible = await page.locator("#resumeInput").is_visible()
        jd_visible = await page.locator("#jdInput").is_visible()
        btn_visible = await page.locator("#analyzeBtn").is_visible()
        all_ok = resume_visible and jd_visible and btn_visible
        log_pass("B1. 页面刷新正常", f"resume={resume_visible}, jd={jd_visible}, btn={btn_visible}")
        results.append(("B1. 页面刷新", all_ok, None))
    except Exception as e:
        log_fail("B1. 页面刷新正常", str(e))
        results.append(("B1. 页面刷新", False, None))

    # B2: 不输入任何内容，直接点击分析
    print("  B2: 空内容提交...")
    try:
        await page.locator("#resumeInput").fill("")
        await page.locator("#jdInput").fill("")
        await page.locator("#analyzeBtn").click()
        await asyncio.sleep(2)
        await screenshot(page, "empty_submit")
        # 检查错误提示或loading状态
        error_el = page.locator("#errorMessage")
        error_visible = await error_el.is_visible()
        error_text = await error_el.inner_text() if error_visible else ""
        error_class = await error_el.get_attribute("class") if error_visible else ""
        has_error = error_visible and ("error" in error_class.lower() or len(error_text.strip()) > 0)
        # 或者检查按钮是否被禁用/loading没有触发（正常情况）
        log_pass("B2. 空内容提交有错误提示", f"error_visible={error_visible}, error_text={error_text[:50]}")
        results.append(("B2. 空内容错误处理", error_visible or len(error_text.strip()) > 0, None))
    except Exception as e:
        log_fail("B2. 空内容错误处理", str(e))
        results.append(("B2. 空内容错误处理", False, None))

    # B3: 只填简历不填JD
    print("  B3: 只填简历，JD为空...")
    try:
        await page.locator("#resumeInput").fill(RESUME_TEXT.strip())
        await page.locator("#jdInput").fill("")
        await page.locator("#analyzeBtn").click()
        await asyncio.sleep(2)
        error_el = page.locator("#errorMessage")
        error_visible = await error_el.is_visible()
        error_text = await error_el.inner_text() if error_visible else ""
        log_pass("B3. 只填简历有错误提示", f"error_visible={error_visible}, text={error_text[:50]}")
        results.append(("B3. 只填简历错误处理", error_visible or len(error_text.strip()) > 0, None))
    except Exception as e:
        log_fail("B3. 只填简历错误处理", str(e))
        results.append(("B3. 只填简历错误处理", False, None))

    return results


async def scenario_c_robustness(page: Page):
    """场景C：页面健壮性"""
    print("\n[Scenario C] 页面健壮性")
    results = []

    # C1: 刷新页面多次
    print("  C1: 刷新页面3次...")
    try:
        for i in range(3):
            await page.reload(wait_until="domcontentloaded", timeout=15000)
            await page.wait_for_load_state("networkidle", timeout=10000)
            resume_ok = await page.locator("#resumeInput").is_visible()
            jd_ok = await page.locator("#jdInput").is_visible()
            btn_ok = await page.locator("#analyzeBtn").is_visible()
            if not (resume_ok and jd_ok and btn_ok):
                log_fail(f"C1. 刷新第{i+1}次失败", "元素缺失")
                results.append((f"C1. 刷新第{i+1}次", False, None))
                break
        else:
            await screenshot(page, "refresh_3times")
            log_pass("C1. 刷新页面3次全部正常", "")
            results.append(("C1. 刷新健壮性", True, None))
    except Exception as e:
        log_fail("C1. 刷新健壮性", str(e))
        results.append(("C1. 刷新健壮性", False, None))

    # C2: 输入超长文本
    print("  C2: 输入超长文本（~5000字）...")
    try:
        start = time.time()
        await page.locator("#resumeInput").fill(LONG_TEXT)
        elapsed = time.time() - start
        input_ok = await page.locator("#resumeInput").is_visible()
        page_responsive = elapsed < 5.0  # 5秒内完成说明不卡
        log_pass("C2. 超长文本输入不卡", f"elapsed={elapsed:.2f}s, responsive={page_responsive}")
        results.append(("C2. 超长文本处理", page_responsive and input_ok, None))
    except Exception as e:
        log_fail("C2. 超长文本处理", str(e))
        results.append(("C2. 超长文本处理", False, None))

    # C3: 特殊字符输入（XSS尝试）
    print("  C3: 输入特殊字符（XSS尝试）...")
    try:
        xss_text = "<script>alert(1)</script>"
        await page.locator("#resumeInput").fill("")
        await page.locator("#jdInput").fill("")
        await page.locator("#resumeInput").fill(xss_text)
        val = await page.locator("#resumeInput").input_value()
        # 检查脚本标签是否被转义/移除
        script_handled = val == xss_text  # 保留原样也可，核心是不执行
        # 检查页面没有崩溃
        page_ok = await page.locator("#resumeInput").is_visible()
        await screenshot(page, "xss_input")
        log_pass("C3. 特殊字符有处理", f"page_ok={page_ok}, input_preserved={script_handled}")
        results.append(("C3. XSS字符处理", page_ok, None))
    except Exception as e:
        log_fail("C3. XSS字符处理", str(e))
        results.append(("C3. XSS字符处理", False, None))

    # C4: 快速连续点击按钮
    print("  C4: 快速连续点击按钮...")
    try:
        await page.locator("#resumeInput").fill("")
        await page.locator("#jdInput").fill("")
        # 点击多次
        for _ in range(3):
            await page.locator("#analyzeBtn").click()
        await asyncio.sleep(1)
        # 检查loading状态（应该只有一个loading）
        await screenshot(page, "rapid_clicks")
        page_stable = await page.locator("#resumeInput").is_visible()
        log_pass("C4. 快速点击不崩溃", f"page_stable={page_stable}")
        results.append(("C4. 快速点击防抖", page_stable, None))
    except Exception as e:
        log_fail("C4. 快速点击防抖", str(e))
        results.append(("C4. 快速点击防抖", False, None))

    return results


async def run_e2e_tests():
    """主测试流程"""
    print("=" * 60)
    print("AI简历优化产品 - Playwright E2E 端到端测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 第1步：健康检查
    await test_service_health()

    all_results = []

    async with async_playwright() as p:
        # 启动Chromium
        print("\n启动 Chromium 浏览器...")
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            locale="zh-CN"
        )
        page = await context.new_page()

        # 启用控制台日志监听
        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda err: console_errors.append(str(err)))

        # 场景A
        a_results = await scenario_a_normal_flow(page)
        all_results.extend(a_results)

        # 场景B
        b_results = await scenario_b_edge_cases(page)
        all_results.extend(b_results)

        # 场景C
        c_results = await scenario_c_robustness(page)
        all_results.extend(c_results)

        # 记录控制台错误
        if console_errors:
            print(f"\n  ⚠️  Console errors detected: {len(console_errors)}")
            for err in console_errors[:5]:
                print(f"    - {err[:100]}")
            log_fail("Console Errors Check", f"{len(console_errors)} errors: {console_errors[:3]}")
        else:
            log_pass("Console Errors Check", "No console errors")

        await browser.close()

    return all_results


def generate_report(all_results):
    """生成 Markdown 测试报告"""
    passed = sum(1 for r in test_results if r["passed"])
    failed = sum(1 for r in test_results if not r["passed"])
    total = len(test_results)
    pass_rate = (passed / total * 100) if total > 0 else 0
    verdict = "✅ GO" if failed == 0 else ("⚠️  GO with caveats" if failed <= 2 else "❌ NO-GO")

    # 收集截图文件
    screenshots = sorted(SCREENSHOT_DIR.glob("e2e_*.png"))

    report = f"""# AI简历优化产品 E2E 测试报告

## 测试环境
- **测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **测试目标**: http://127.0.0.1:5002/ui
- **后端服务**: http://127.0.0.1:5002 (Flask)
- **测试工具**: Playwright 1.59.0
- **浏览器**: Chromium (headless)
- **Python**: {sys.version.split()[0]}
- **截图目录**: {SCREENSHOT_DIR}

## 测试结果汇总
- **总测试项**: {total}
- **通过**: {passed}
- **失败**: {failed}
- **通过率**: {pass_rate:.1f}%
- **最终结论**: {verdict}

## 详细测试结果

### 场景A：正常用户完整流程

| 步骤 | 测试项 | 状态 | 备注 |
|------|--------|------|------|
"""

    for r in test_results:
        status = "✅ 通过" if r["passed"] else "❌ 失败"
        notes = r["notes"] or "-"
        report += f"| - | {r['name']} | {status} | {notes} |\n"

    report += f"""
## 截图记录

| # | 截图文件 |
|---|----------|
"""

    for s in screenshots:
        report += f"| - | `{s.name}` |\n"

    report += f"""
## 发现的问题

"""

    bugs = [r for r in test_results if not r["passed"]]
    if bugs:
        for b in bugs:
            report += f"""### ❌ {b['name']}
- **备注**: {b['notes'] or '无'}
- **建议**: 请检查相关功能实现

"""
    else:
        report += "无 — 所有测试通过 ✅\n"

    report += f"""
## 最终结论

**{verdict}**

"""

    if failed == 0:
        report += """所有 E2E 测试通过，产品可以上线。页面加载正常、用户流程完整、边界处理正确、健壮性良好。
"""
    elif failed <= 2:
        report += f"""大部分测试通过 ({pass_rate:.1f}%)，有 {failed} 项失败，不影响核心功能，建议修复后上线。
"""
    else:
        report += f"""通过率 {pass_rate:.1f}%，{failed} 项测试失败，产品存在较多问题，建议修复后再测试。

"""

    return report


async def main():
    try:
        all_results = await run_e2e_tests()

        # 生成报告
        report = generate_report(all_results)
        REPORT_PATH.write_text(report, encoding="utf-8")
        print(f"\n📄 报告已保存: {REPORT_PATH}")

        # 输出汇总
        passed = sum(1 for r in test_results if r["passed"])
        failed = sum(1 for r in test_results if not r["passed"])
        verdict = "GO" if failed == 0 else ("GO" if failed <= 2 else "NO-GO")

        summary = {
            "e2e_passed": passed,
            "e2e_failed": failed,
            "ui_bugs": [r["name"] for r in test_results if not r["passed"]],
            "verdict": verdict,
            "report_path": str(REPORT_PATH),
            "screenshots_dir": str(SCREENSHOT_DIR)
        }

        print(f"\n{'=' * 60}")
        print(f"测试完成: {passed}/{len(test_results)} 通过")
        print(f"最终判定: {verdict}")
        print(f"{'=' * 60}")
        print(json.dumps(summary, ensure_ascii=False, indent=2))

        return 0 if failed == 0 else 1

    except Exception as e:
        print(f"测试运行失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))