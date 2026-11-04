# 生成工作台截图

README 中的四张截图由 [capture_screenshots.py](../tools/capture_screenshots.py) 从本地工作台生成。脚本启动独立服务，重置样例、执行指定动作并检查业务结果，完成后关闭浏览器和服务。

## 运行

在仓库根目录执行验证：

```bash
python3 tools/verify.py
```

已有 Google Chrome 时：

```bash
uv run --with playwright python tools/capture_screenshots.py --channel chrome
```

使用 Playwright 的 Chromium 时：

```bash
uv run --with playwright playwright install chromium
uv run --with playwright python tools/capture_screenshots.py
```

Playwright 仅用于截图。也可通过 `CHROME_BIN` 指定浏览器可执行文件，与 `--channel` 二选一：

```bash
CHROME_BIN=/path/to/chromium uv run --with playwright python tools/capture_screenshots.py
```

## 截图对应的业务状态

| 文件 | 申请与视图 | 预期结果 |
|---|---|---|
| `01-ontology-workbench.png` | YF-R-0311，业务对象 | 347 元；ERP 返回 not_found；发票状态 unknown |
| `02-action-console.png` | YF-R-0501，退款处理 | 500.01 元；命中 G-AMOUNT；创建人工审批材料 |
| `03-audit-trace.png` | YF-R-0610，决策记录 | 风控复核覆盖退款批准建议；两项意见保留；无付款指令 |
| `04-evaluation-dashboard.png` | 测试与评估 | 核心策略 36/36，事故回放 2/2；候选规则仍缺开封状态输入、业务审核和编译 |

默认输出目录为 [assets/screenshots](assets/screenshots/)，可通过 `--output-dir` 改到审阅目录。视口为 1600×1000，截图覆盖完整页面，高度随内容变化。

脚本检查接口结果、可见文字、JavaScript 错误、横向溢出及图片尺寸。它还会比较 YF-R-0311 的发票未知状态与 YF-R-0500 的明确未开票记录。

人工复核应确认长编号未遮挡、中文可读、图中状态与运行结果一致，以及画面没有账号、密钥或本机私有路径。完整 JSON 面板可滚动，截图仅展示可见部分。

## 手动核对

```bash
python3 run.py serve --port 8000
```

打开 `http://127.0.0.1:8000`。网址参数 `?view=audit&case=YF-R-0610` 可预选视图和申请，打开链接只读取数据，不会执行或重置业务。
