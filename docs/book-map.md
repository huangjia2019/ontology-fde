# 云帆退款项目：本体、规则与执行

一笔 347 元的退款转人工，一笔 500 元的退款自动批准。金额较小的那笔为什么没有通过？它的发票状态无法确认。按云帆的 R2 规则，已开票订单需先由财务处理冲红，再自动创建付款指令，因此发票状态也要核实。

这条判断可以沿代码追溯：`repository.py` 的 `get_case()` 在 ERP 查不到发票时将 `invoice_status` 记为 `unknown`，`policy.py` 命中 `G-INVOICE-UNKNOWN`，`engine.py` 创建人工审批材料 HAP-0311。`source_map.yaml` 记录了同一对应关系，供人核对；当前程序没有读取这份映射文件。

## 观察事实、建议与实际变更

按[首页](../README.md#快速启动)准备 Python 环境，在仓库根目录执行：

```bash
python3 run.py inspect YF-R-0311
python3 run.py run YF-R-0311 --mode draft
```

`inspect` 返回申请、订单、客户等事实及来源引用。`source_refs` 记录 ERP 查询条件 `order_id=O-9938` 和结果 `observation: not_found`，组装后的业务事实中 `invoice_status` 为 `unknown`。

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

Draft 保持申请为 `pending_review`；Write 创建人工审批材料 HAP-0311，将申请改为 `pending_human`。结果中的 `decision_record.outcome` 为 `queued_for_human`。

## 十站目录

| 站点 | 业务问题 | 对应实现 |
|---|---|---|
| [1. 确定业务范围](artifacts/01-ontology-positioning-card.md) | 哪些退款可以自动处理，哪些事实仍要人工确认？ | [347 元退款经过](artifacts/01-field-walkthrough.md)与[系统诊断](artifacts/01-six-question-diagnostic.md) |
| [2. 审视原有方案](artifacts/02-historical-audit.md) | 给人建议的助手增加写权限后，会新增什么风险？ | 原有做法、故障原因与执行检查的对应关系 |
| [3. 登记执行主体](artifacts/03-identity-acceptance.md) | 谁发起这次动作，谁负责这个 Agent？ | 身份登记、责任归属与生命周期 |
| [4. 建立最小本体](artifacts/04-minimum-ontology.md) | 如何确认退款、订单和商品属于同一笔业务？ | 对象引用、字段来源与状态机 |
| [5. 限定业务动作](artifacts/05-action-contract.md) | 500 元、500.01 元以及重复提交应如何处理？ | 动作契约、幂等和付款失败补偿 |
| [6. 整理判断依据](artifacts/06-rule-assets.md) | “签收超过 24 小时”怎样变成可执行规则？ | 时间字段、规则适用范围、测试与审核 |
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

如果把 `get_case()` 中查不到发票时返回的 `unknown` 错写成 `none`，策略会把这笔申请当作已确认未开票，自动批准并创建模拟付款指令 PI-0311。发票结果的含义需要财务与 ERP 负责人确认，再落实到代码和来源映射约定中；只修改 `source_map.yaml`，当前程序的结果不会改变。

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

`checkpoint 4 --check` 确认五份文件存在、对象目录声明了 `RefundRequest`、状态机包含批准后转待付款的转换。客户、订单和订单项是否一致，由[关系错误测试](../tests/test_release_guards.py)验证。`verify.py` 还会检查 Draft 是否修改状态、重复请求是否再建付款指令，范围见[测试说明](release-baseline.md)。

配置与代码的分工、进程内状态的保存方式见[架构说明](architecture.md)。分析自己的业务时，可参照[FDE 现场练习](fde-playbook.md)和[案例分析记录](learning-log.md)。
