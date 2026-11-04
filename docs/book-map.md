# 云帆退款项目：本体、规则与执行

一笔 347 元的退款转人工，一笔 500 元的退款自动批准。金额较小的那笔为什么没有通过？它的发票状态无法确认。退款规则要求金额和其他业务条件同时满足，不能用“小额”代替对事实的核实。

这条判断可以沿代码追溯：ERP 查询结果进入来源映射，来源映射把 `not_found` 解释为 `unknown`，策略据此选择人工审批，执行引擎再创建审批材料。下面的十站围绕这笔业务，逐步解释本体如何影响程序。

## 观察事实、建议与实际变更

按[首页](../README.md#快速启动)准备 Python 环境，在仓库根目录执行：

```bash
python3 run.py inspect YF-R-0311
python3 run.py run YF-R-0311 --mode draft
```

`inspect` 返回申请、订单、客户等事实及来源引用。ERP 本次查询没有返回发票记录，程序保留这次观测，并将订单的 `invoice_status` 设为 `unknown`。

第二条命令生成建议。结果中 `draft` 的部分字段为：

```json
{
  "decision": "queue_human",
  "rule_hits": ["G-INVOICE-UNKNOWN"],
  "final_action": "request_human_refund_approval"
}
```

这时申请还是 `pending_review`。要实际建立人工审批任务，执行：

```bash
python3 run.py run YF-R-0311 --mode write
```

结果中的 `decision_record.state_after` 变为 `pending_human`，`outcome` 为 `queued_for_human`。Draft 表达处理意见，Write 执行相应业务动作，两者的状态变化不同。

## 十站目录

| 站点 | 业务问题 | 对应实现 |
|---|---|---|
| [1. 确定业务范围](artifacts/01-ontology-positioning-card.md) | 哪些退款可以自动处理，哪些事实仍要人工确认？ | [347 元退款经过](artifacts/01-field-walkthrough.md)与[系统诊断](artifacts/01-six-question-diagnostic.md) |
| [2. 审视原有方案](artifacts/02-historical-audit.md) | 给人建议的助手增加写权限后，会新增什么风险？ | 原有做法、故障原因与执行检查的对应关系 |
| [3. 登记执行主体](artifacts/03-identity-acceptance.md) | 谁发起这次动作，谁负责这个 Agent？ | 身份登记、责任归属与生命周期 |
| [4. 建立最小本体](artifacts/04-minimum-ontology.md) | 如何确认退款、订单和商品属于同一笔业务？ | 对象引用、字段来源与状态机 |
| [5. 限定业务动作](artifacts/05-action-contract.md) | 500 元、500.01 元以及重复提交应如何处理？ | 动作契约、幂等和付款失败补偿 |
| [6. 整理判断依据](artifacts/06-rule-assets.md) | “签收后 24 小时内”怎样变成可执行规则？ | 时间字段、规则适用范围、测试与审核 |
| [7. 验证权限](artifacts/07-identity-and-permissions.md) | 业务条件全部通过，陌生 Agent 能批准吗？ | 执行主体检查与业务条件检查 |
| [8. 处理协作分歧](artifacts/08-multi-agent-coordination.md) | 退款 Agent 同意，风控 Agent 要求复核，如何裁决？ | 任务委托、意见保留与冲突优先级 |
| [9. 评估和复盘](artifacts/09-evaluation-audit-and-incident-replay.md) | 申请已批准，付款指令创建失败，该怎样恢复？ | 决策记录、故障补偿与回归测试 |
| [10. 运行交接](artifacts/10-operations-handoff-and-replication.md) | 谁继续处理未完成的退款，怎样停用自动执行？ | 财务待办、规则维护与退出流程 |

## 一条规则如何决定需要建什么模型

“未开票或发票已冲红，才允许自动批准”要求程序取得发票状态。但退款申请本身没有这个事实，必须先通过 `RefundRequest.order_id` 找到订单，再按订单编号查询 ERP。

由此可以推导出模型中的关系和字段：

```text
退款申请 YF-R-0311
  └─ order_id: O-9938
       └─ ERP 发票查询: not_found
            └─ Order.invoice_status: unknown
                 └─ G-INVOICE-UNKNOWN
                      └─ 创建人工审批材料，等待财务核实
```

如果把 `not_found` 映射成 `none`，后面的规则即使完全按配置执行，也可能自动批准一笔事实不清的退款。来源映射本身就是业务设计的一部分。

详细定义见[第 4 站](artifacts/04-minimum-ontology.md)，动作前提见[第 5 站](artifacts/05-action-contract.md)。本地数据与规则均为教学样例，不连接真实财务系统。

## 按问题查实现

| 运行结果不符合预期时 | 检查内容 | 源码入口 |
|---|---|---|
| 订单或商品关联错了 | 申请中的引用编号、客户与订单项是否一致 | [repository.py](../src/ontology_fde/repository.py) 的 `get_case()` |
| 小额退款没有自动通过 | 发票、风险、渠道、证据等条件，以及 `rule_hits` | [policy.py](../src/ontology_fde/policy.py) 的 `evaluate()` |
| 条件通过却没有执行 | Actor、动作授权、当前状态与重复请求 | [engine.py](../src/ontology_fde/engine.py) 的 `run()` |
| 批准与付款结果不同 | `state_before`、`state_after`、`actual_effect` | [audit.py](../src/ontology_fde/audit.py) 的 `DecisionRecord` |
| 修改规则后旧案例失败 | 样例预期与实际决定的差异 | [evaluator.py](../src/ontology_fde/evaluator.py) |

```bash
python3 run.py checkpoint 4 --check
python3 tools/verify.py
```

`checkpoint 4 --check` 核对本体文件、字段和部分关系约束。`verify.py` 还会运行行为测试，例如 Draft 是否修改状态、相同请求是否重复生成付款指令。检查范围见[测试说明](release-baseline.md)。

配置与代码的分工、进程内状态的保存方式见[架构说明](architecture.md)。分析自己的业务时，可参照[退款项目练习](fde-playbook.md)和[案例分析记录](learning-log.md)。
