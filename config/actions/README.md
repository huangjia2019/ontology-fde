# 退款动作契约

[仓库首页](../../README.md#本体怎样进入程序) · [十站目录](../../docs/book-map.md#十站目录) · [第 5 站：动作契约讲解](../../docs/artifacts/05-action-contract.md)

| 契约 | 业务动作 | 执行结果 |
|---|---|---|
| [approve_refund_small](approve_refund_small.yaml) | 批准不超过 500 元且其他条件满足的退款 | 申请变为 `approved`，创建模拟付款指令；付款指令创建失败时进入 `approval_pending_payment`，生成财务任务 |
| [request_human_refund_approval](request_human_refund_approval.yaml) | 提交人工审核 | 申请变为 `pending_human`，生成人工审批材料 |
| [request_missing_evidence](request_missing_evidence.yaml) | 请求补充证据 | 生成补证请求草稿，申请状态不变 |

业务判断见[退款策略](../../src/ontology_fde/policy.py)，动作执行、幂等与补偿见[执行引擎](../../src/ontology_fde/engine.py)，验证用例见[执行器测试](../../tests/test_engine.py)。契约字段与代码的分工见[第 5 站](../../docs/artifacts/05-action-contract.md#契约如何约束一次批准)。

相关站点：[权限验证](../../docs/artifacts/07-identity-and-permissions.md)、[协作分歧](../../docs/artifacts/08-multi-agent-coordination.md)、[事故回放](../../docs/artifacts/09-evaluation-audit-and-incident-replay.md)、[运行交接](../../docs/artifacts/10-operations-handoff-and-replication.md)。
