# 第 5 站：把退款条件落实到动作契约

`YF-R-0500` 与 `YF-R-0501` 的其他审批条件都满足，金额分别为 500 元和 500.01 元。公司规定自动批准金额不得超过 500 元，因此这两笔申请走不同的处理路径。

```bash
python3 run.py run YF-R-0500 --mode write
python3 run.py run YF-R-0501 --mode write
```

| 样例 | 执行动作 | 执行后的状态 | 新增记录 |
|---|---|---|---|
| 500 元，其他条件通过 | `approve_refund_small` | `approved` | 模拟付款指令 PI-0500 |
| 500.01 元 | `request_human_refund_approval` | `pending_human` | 人工审批材料 HAP-0501 |
| 证据不完整或未核验通过 | `request_missing_evidence` | 保持原状态 | 补充证据请求草稿 |

## 契约如何约束一次批准

动作契约描述某个操作的输入、允许的执行主体、业务前提以及预期效果。[小额批准契约](../../config/actions/approve_refund_small.yaml)将这些要求放在同一份定义里。

以 500 元那笔申请为例，执行时需要核对退款编号、客户、订单和订单项。随后检查金额上限、签收状态、发票、风险、证据、渠道及退款频率。全部通过后，才修改申请状态并生成付款指令。

```text
approve_refund_small
  输入：退款、客户、订单、订单项、金额、证据引用
  主体：获准调用此动作的 Agent
  条件：待审核 + 金额 ≤ 500 元 + 其他业务条件全部满足
  效果：退款申请获批 + 创建付款指令 + 记录决策
  失败：保留已发生的审批，登记待付款状态和财务任务
```

金额上限从契约的 `threshold_cny` 读取。其他判断由[退款策略](../../src/ontology_fde/policy.py)和[执行引擎](../../src/ontology_fde/engine.py)实现。调整条件时要找到实际读取的字段或执行的代码，再补充相应测试；只修改描述文字，程序仍会按原条件判断。

超过金额上限仍然需要继续处理业务，因此另有[人工审批契约](../../config/actions/request_human_refund_approval.yaml)。它将申请转为待人工审核并创建审批材料。核实条件、获得人工批准后，才应进入付款流程；本地示例尚未提供这段人工续办接口。[补证契约](../../config/actions/request_missing_evidence.yaml)则生成补证请求草稿。

契约中声明的 `role:cs_supervisor` 表示外部人工审批角色。CLI 的执行器仅接受已登记的退款 Agent，传入这个角色名会被拒绝。实际主管审批需要另外接入真人认证和审批服务。

## 建议与执行的区别

```bash
python3 run.py run YF-R-0500 --mode read
python3 run.py run YF-R-0500 --mode draft
```

Read 返回事实。Draft 会给出批准建议，但退款仍为 `pending_review`，也没有付款指令。需要查看建议时用 Draft，需要执行时用 Write；即使直接调用 Write，它也会先读取事实、核验授权与业务条件，再执行操作。

CLI 的修改保存在当次运行的内存中，退出后释放；下一条命令重新读取样例文件。要观察批准后的状态，可以在 Web 工作台执行后再查询，或阅读[执行器测试](../../tests/test_engine.py)。

## 批准后为什么还需要补偿

```bash
python3 run.py run YF-R-0800 --mode write --simulate-payment-failure
```

这笔申请的审批条件全部通过，程序先完成批准，随后创建付款指令 PI-0800 失败。记录中的 `outcome` 为 `compensated`，退款进入 `approval_pending_payment`，同时生成财务任务 FMT-0800。

审批已经完成，因此保留批准记录，并把当前进度记为“已批准，待付款”。财务人员据此知道应处理付款故障，而非重新审批。财务任务保存失败原因与关联对象，由执行器在这次故障后创建，供后续核查和继续处理。

## 相同请求重试会怎样

网络超时可能让调用方重复提交同一个请求。引擎使用 `intent_id` 标识这次操作意图：在同一引擎实例中，用相同身份重放同一个意图，会返回原决策记录，附上 `idempotent_replay: true`，避免重复创建付款指令。返回旧结果前也会检查身份，防止未授权调用者凭意图编号取得别人的执行记录。

幂等记录也保存在内存中，进程退出后会消失。若要在服务重启后识别旧请求，必须把幂等记录与业务结果一起保存，并处理多个请求同时到达的情况。

```bash
python3 run.py checkpoint 5 --check
```

[下一站：规则如何形成](06-rule-assets.md) · [返回十站目录](../book-map.md)。
