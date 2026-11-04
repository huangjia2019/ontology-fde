# 书中测试数字与当前仓库的关系

书中“53 项自动化测试”是出版时的业务验收基线。仓库后续增加了交付检查和回归测试，当前数量由运行结果给出。

## 53 + 3 是历史口径

53 项基线测试覆盖业务事实、本体、规则、动作边界、异常输入、身份权限、规则生命周期、状态转换、审计、补偿与交接。随书交付又增加了三项检查：

| 额外检查 | 检查内容 |
|---|---|
| `CheckpointTests.test_checkpoint_artifact_paths_use_english_names` | 十站工件采用稳定的英文文件路径；文件内容可以是中文 |
| `CheckpointTests.test_checkpoint_cli_emits_book_ready_card` | 命令行能输出随书检查卡 |
| `WebTests.test_index_and_static_assets_load_without_cdn` | 工作台及静态资源不依赖外部 CDN |

因此，当时完整测试集为 53 + 3 = 56 项。后续修复会增加回归测试，当前总数以命令末尾的 `Ran ... tests` 为准。

```bash
python3 tools/verify.py
```

`verify.py` 依次检查读者链接与截图、出版基线、单元及集成测试、策略样例与事故回放、完整示例、十站检查卡和退出资料。

## 36 个业务样例与 2 个事故回放

```bash
python3 run.py evaluate --output artifacts/evaluation-report.json
```

输出分别列出：

- `core`：36 个核心策略样例，比较判断结果与规则命中；
- `incident_replays`：2 个事故回放，分别输入缺失渠道和大写 `B2B`，预期均命中 R5 并转人工；
- `document_to_rule`：规则草稿的结构、字段语义、运行样例、来源依据四类校验，五类样例，以及未编译草稿被拒绝执行的检查。

这 36 + 2 项是数据驱动的策略回放，与自动化测试方法数量不是同一统计口径。它们直接调用策略层。事实装配、写入、幂等与失败补偿由 `tests/test_engine.py`、`tests/test_release_guards.py` 等测试覆盖。

## 组合验证范围

先运行全部测试，再看业务样例评估。各站的 `checkpoint N --check` 补查文件与配置。第 9 站还安排了一次付款指令创建失败的演练，确认记录中能看到失败、补偿状态和财务待办。

完整运行入口见[首页](../README.md)。这些检查验收的是本地参考实现；企业上线还要补充接口、权限、并发、故障恢复和人工接手等集成验收。
