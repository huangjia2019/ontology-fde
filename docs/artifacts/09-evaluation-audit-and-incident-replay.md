# 第 9 站：批准之后失败了，记录能否说明白

`YF-R-0800` 满足批准条件。执行器先批准，再创建付款指令。如果第二步失败，业务已经发生过变化。客服、财务和运维必须知道哪一步完成、哪一步未完成，才能继续处理。

## 先读一份决策记录

[DecisionRecord](../../src/ontology_fde/audit.py)将判断依据和执行结果放在同一条记录中。查“为什么转人工”，要看 `checks`、`rule_hits` 以及冲突裁决；查“到底做了什么”，要看 `state_after`、`actual_effect` 和工具调用结果。

例如，付款失败这笔记录中，`final_action` 仍是 `approve_refund_small`，但 `state_after` 为 `approval_pending_payment`。只读动作名，会误以为全部成功；结合实际效果，才能知道批准已完成，付款仍待处理。

## 运行评估和一次失败

```bash
python3 run.py evaluate --output artifacts/ch09-eval.json
python3 run.py run YF-R-0800 --mode write \
  --simulate-payment-failure --audit artifacts/ch09-failure.jsonl
python3 run.py checkpoint 9 --check
```

评估中的核心策略样例应为 `36/36`，事故回放为 `2/2`。它们直接调用策略层，不经过全部数据装配、写入和补偿路径。端到端行为还要运行测试：

```bash
python3 tools/verify.py
```

失败案例中，请依次找出：

1. 退款已批准；
2. `payments.create_refund_instruction` 状态为 `failed`；
3. 退款进入 `approval_pending_payment`；
4. 创建财务任务 `FMT-0800`；
5. `actual_effect` 说明指令创建失败及后续处理，没有报告“付款成功”。

轨迹按序记录了查询、判断、写入和补偿。`duration_ms` 是程序生成的模拟耗时，用于展示记录格式；若要比较真实接口或模型的速度，需要在实际调用前后计时。

## 修过的问题留下回放

| 回放 | 问题 | 修复后应保持的判断 |
|---|---|---|
| `INC-REPLAY-001` | 客户渠道缺失，被当作普通个人客户 | `unknown` 转人工核实 |
| `INC-REPLAY-002` | 大写 `B2B` 绕过了渠道比较 | 先规范大小写，命中 R5 并转人工 |

两项记录位于[事故回放集](../../config/evals/incident_replays.json)。新项目遇到判断错误时，保存脱敏输入、当时输出、业务确认的预期结果和修复点，再加入回归。

## 从一次错误增加一个测试

渠道缺失的事故暴露了默认值问题：若把缺失渠道填成 `b2c`，合同客户可能绕过合同审核。修复后应保留 `unknown` 并转人工，同时保留正常 B2C 申请仍可批准的测试。否则，简单地把所有申请都转人工也可能让事故样例通过，却损害原有功能。

本地 JSONL 是普通文本文件，有写权限的人可以直接修改。企业审计还需要控制谁能访问和修改记录、保存多长时间，以及怎样发现篡改。[测试口径说明](../release-baseline.md)解释书中 53 项测试与仓库当前数量的关系。

[下一站：运行交接与退出](10-operations-handoff-and-replication.md) · [返回十站目录](../book-map.md)。
