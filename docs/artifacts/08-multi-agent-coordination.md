# 第 8 站：退款助手同意，风控要求复核

`YF-R-0610` 申请 280 元，证据、履约和发票条件允许退款助手提出批准建议。但风控发现同一设备短时间内出现多次售后申请，给出 `review`。最终应该保留两个意见，并按约定转人工处理。

## 委托要引用业务对象

接待助手如果只发送“请退 280 元”，退款助手还需要猜测订单、商品和证据属于哪笔申请。任务信封把这次委托和具体对象绑定，同时限定允许的动作。即使接收方知道创建付款指令的方法，也不能因此超出委托范围。

完整[任务信封样例](08-task-envelope-YF-R-0610.json)记录：

| 字段 | 本次含义 |
|---|---|
| `envelope_id` | `ENV-T-0610`，识别这次委托 |
| `correlation_id` | `CORR-YF-R-0610`，关联业务过程 |
| `sender`、`recipient` | 从接待助手委托给退款助手 |
| `object_refs` | 指向工单、客户、订单、订单项和退款申请 |
| `allowed_actions`、`forbidden_actions` | 本次可以做什么，不可以做什么 |
| `context_scope`、`expires_at` | 可以使用哪些对象，委托何时过期 |

样例时间固定，用于可复现实验。运行时默认采用申请发生时间；需要测试过期行为时，可通过 `--processing-at` 指定更晚的带时区时间。

## 裁决后不要丢掉分歧

[Agent 登记表](../../config/identity/agent_registry.yaml)列出三个角色及其关系，[冲突策略](../../config/policies/conflict_resolution.yaml)规定这条次序：

```text
RiskAgent:block > RiskAgent:review > RefundAgent:approve
```

退款助手回答的是商品、发票和金额是否满足一般条件，风控回答的是这次交易是否需要额外审查。两份意见依据不同，不能靠投票取多数。冲突策略将风险复核作为自动批准的限制条件。当前程序以确定性逻辑生成候选意见并裁决，不调用独立模型服务。

```bash
python3 run.py run YF-R-0610 --mode write \
  --audit artifacts/ch08-decision-records.jsonl
python3 run.py checkpoint 8 --check
```

运行后，申请由 `pending_review` 变成 `pending_human`，创建审批材料 HAP-0610，没有付款指令。结果中的 `agent_candidates` 保留两个意见，`conflict_resolution` 记录哪项意见被采用、哪项被覆盖，以及裁决策略 `POL-AGENT-CONFLICT-001`。

保留被覆盖的意见有实际用途：人工复核时可以看到，一般退款条件已通过，待处理的是设备关联风险。若只保存最后一句“转人工”，接手人就要重新查询前面已经核对过的材料。

JSONL 文件会追加本次结果，不会保存或恢复整套业务状态。多轮练习可换文件名留档。

## 优先级从哪里来

本项目约定风险复核优先于自动批准，是因为一般条件满足并不能排除异常交易。若换成合同争议，裁决还可能需要法务意见，不能照搬这个排序。应由业务负责人确定各类意见的适用范围，再写入冲突策略和测试。

[下一站：评估与复盘](09-evaluation-audit-and-incident-replay.md) · [返回十站目录](../book-map.md)。
