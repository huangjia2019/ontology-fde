# 企业本体论：人人都是 FDE

<a href="https://u.jd.com/5gaL3hM"><img src="docs/assets/book-cover.jpg" alt="《企业本体论：人人都是FDE》书封面，黄佳著" width="360"></a>

[京东购书：《企业本体论：人人都是FDE》](https://u.jd.com/5gaL3hM)

[快速启动](#快速启动) · [随书十站目录](docs/book-map.md) · [FDE 现场练习](docs/fde-playbook.md) · [版本记录](CHANGELOG.md)

## 从一笔退款理解企业本体

客户申请退还 347 元，低于公司规定的 500 元自动审批上限。客服 Agent 查了订单和发票，ERP 返回 `not_found`。此时能批准退款吗？

还缺一项判断依据：没有查到发票，可能是尚未开票，也可能是记录没有同步。程序把这次查询结果记为 `unknown`，转交人工核实。另一笔 500 元的申请，因为发票、风控和证据等条件全部满足，反而可以自动批准。

这个差别需要落实到系统中。订单与退款申请要通过编号关联，发票状态要有明确来源，批准动作要检查前提，执行记录要保留判断依据。**企业本体定义这些业务对象、关系、状态和动作的含义，使人、Agent 与业务程序能够使用同一套定义。**

本仓库提供书中“云帆退款项目”的可运行实现。可以查看一笔申请如何从原始记录得到处理建议，怎样通过授权与规则检查，再观察付款失败时状态如何变化。

FDE（Forward-Deployed Engineer，前沿部署工程师）参与的正是这类工作：和财务确认“查不到”的处理办法，与系统负责人确定字段来源，把约定实现为规则和测试，并安排异常发生后的接手流程。

## 快速启动

Python 3.11+，仅使用标准库。本地样例数据，离线运行。

```bash
git clone https://github.com/huangjia2019/ontology-fde.git
cd ontology-fde
python3 run.py serve --port 8000
```

访问 http://127.0.0.1:8000 。

Windows 使用 `py -3 run.py serve --port 8000`。下文命令中的 `python3` 也可替换为 `py -3`。

## 业务事实与执行结果

工作台包含业务对象、退款处理、决策记录、测试与评估四个视图，默认申请为“遥控器单” `YF-R-0311`。

![业务对象及来源](docs/assets/screenshots/01-ontology-workbench.png)

这笔申请金额为 347 元。ERP 查询返回 `not_found`，发票状态为 `unknown`，执行后转人工审核，不生成付款指令。业务经过见[遥控器单](docs/artifacts/01-field-walkthrough.md)。

Read 返回业务事实。Draft 返回处理建议，申请仍处于 `pending_review`。Write 会重新读取事实、核验权限并执行动作：这笔申请转为 `pending_human`，同时创建人工审批材料。

### 五笔退款申请

| 短名 | 申请编号 | 金额 | 执行结果 |
|---|---|---:|---|
| 遥控器单 | YF-R-0311 | 347 元 | 发票状态未知，转人工 |
| 刚好五百 | YF-R-0500 | 500 元 | 全部条件满足，批准并生成模拟付款指令 |
| 多出一分 | YF-R-0501 | 500.01 元 | 超过自动批准上限，转人工 |
| 小额黑名单 | YF-R-0312 | 199 元 | 风控条件不通过，转人工 |
| 合同优先 | YF-R-0415 | 480 元 | 企业合同客户，转人工核实合同 |

自动批准要求金额不超过 500 元，且其他条件全部满足。`approved` 表示申请已批准，付款指令 `created` 不代表资金到账。

![500.01 元申请进入人工审批](docs/assets/screenshots/02-action-console.png)

## 本体怎样进入程序

前四站从退款业务推导对象和状态，第 5 至 8 站实现动作、规则、授权与协作，最后两站处理故障验证和运行移交。各站包含业务分析、配置说明与运行示例，见[随书目录](docs/book-map.md)。

| 站点 | 内容 |
|---|---|
| [1. 确定业务范围](docs/artifacts/01-ontology-positioning-card.md) | 业务目标、对象、来源与自动化范围 |
| [2. 审视原有方案](docs/artifacts/02-historical-audit.md) | 从辅助建议到执行操作的风险审计 |
| [3. 登记执行主体](docs/artifacts/03-identity-acceptance.md) | Agent 身份、归属与生命周期 |
| [4. 建立最小本体](docs/artifacts/04-minimum-ontology.md) | 对象、关系、状态与来源映射 |
| [5. 限定业务动作](docs/artifacts/05-action-contract.md) | 动作契约、幂等与补偿 |
| [6. 整理判断依据](docs/artifacts/06-rule-assets.md) | 规则来源、适用范围与草稿审核 |
| [7. 验证权限](docs/artifacts/07-identity-and-permissions.md) | 身份登记、授权配置与拒绝测试 |
| [8. 处理协作分歧](docs/artifacts/08-multi-agent-coordination.md) | 任务委托、冲突裁决与人工交接 |
| [9. 评估和复盘](docs/artifacts/09-evaluation-audit-and-incident-replay.md) | 决策记录、策略评估与事故回放 |
| [10. 交还组织](docs/artifacts/10-operations-handoff-and-replication.md) | 运行维护、移交与退出检查 |

例如，第 4 站的检查会核对本体文件、来源映射和样例关系：

```bash
python3 run.py checkpoint 4 --check
```

协作冲突与故障补偿：

```bash
# 风控否决自动批准，转人工复核
python3 run.py run YF-R-0610 --mode write

# 模拟付款指令创建失败
python3 run.py run YF-R-0800 --mode write --simulate-payment-failure
```

付款指令创建失败后，申请进入 `approval_pending_payment`，生成财务处理任务。

![协作分歧与决策记录](docs/assets/screenshots/03-audit-trace.png)

## 命令行与源码

```bash
python3 run.py inspect YF-R-0311
python3 run.py run YF-R-0311 --mode draft
python3 run.py run YF-R-0500 --mode write --audit artifacts/my-first-decision.jsonl
```

CLI 每次调用重新加载样例。Web 状态保留在服务进程中，重置或重启后恢复初始数据。`--audit` 追加 JSONL 决策记录，不持久化业务状态。

| 模块 | 入口 |
|---|---|
| 跨系统对象与来源 | [repository.py](src/ontology_fde/repository.py) |
| 退款规则 | [policy.py](src/ontology_fde/policy.py) |
| 授权、执行、幂等与补偿 | [engine.py](src/ontology_fde/engine.py) |
| 决策记录 | [audit.py](src/ontology_fde/audit.py) |
| 对象与动作定义 | [本体配置](config/ontology/)与[动作契约](config/actions/) |
| 测试与评估 | [测试](tests/)与[评估样例](config/evals/) |

`.yaml` 配置使用 JSON 兼容格式。规则由配置与 Python 代码共同实现，见[架构说明](docs/architecture.md)。

## 测试与评估

```bash
python3 tools/verify.py
```

检查范围：文档与截图、单元及集成测试、36 个策略样例、2 个事故回放、十站检查卡及退出准备项。失败返回非零退出码。

策略评估检查“给定这些事实，应作何决定”；引擎测试检查“决定执行以后，状态、付款指令和审计记录是否正确”。两者共同覆盖业务判断和执行行为。测试分组见[测试口径](docs/release-baseline.md)。

![策略评估与规则发布条件](docs/assets/screenshots/04-evaluation-dashboard.png)

导出评估报告：

```bash
python3 run.py evaluate --output artifacts/evaluation-report.json
```

## 问题反馈

请在 [Issues](https://github.com/huangjia2019/ontology-fde/issues) 提供环境、复现命令及预期与实际结果，勿上传密钥或客户数据。
