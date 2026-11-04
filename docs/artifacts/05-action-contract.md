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

金额上限从契约的 `threshold_cny` 读取。其他判断由[退款策略](../../src/ontology_fde/policy.py)和[执行引擎](../../src/ontology_fde/engine.py)实现。修改契约中的自然语言描述不会自动改变这些判断。

超过金额上限仍然需要继续处理业务，因此另有[人工审批契约](../../config/actions/request_human_refund_approval.yaml)。它允许创建审批材料，但不能自动批准，也不能创建付款指令。[补证契约](../../config/actions/request_missing_evidence.yaml)则生成补证请求。

契约中声明的 `role:cs_supervisor` 表示外部人工审批角色。CLI 不提供真人认证，传入这个字符串不能获得主管权限。

## 建议与执行的区别

```bash
python3 run.py run YF-R-0500 --mode read
python3 run.py run YF-R-0500 --mode draft
```

Read 返回事实。Draft 会给出批准建议，但退款仍为 `pending_review`，也没有付款指令。Write 会重新读取事实并核验条件，然后执行操作。三个模式用于不同的权限和交互需要，不要求先后调用。

CLI 每条命令启动独立进程，使用初始样例。要观察连续操作，可以在同一个 Web 服务进程中运行，或阅读[执行器测试](../../tests/test_engine.py)。

## 批准后为什么还需要补偿

```bash
python3 run.py run YF-R-0800 --mode write --simulate-payment-failure
```

这笔申请的审批条件全部通过，程序先完成批准，随后创建付款指令 PI-0800 失败。记录中的 `outcome` 为 `compensated`，退款进入 `approval_pending_payment`，同时生成财务任务 FMT-0800。

这里不能把申请退回“尚未审批”，因为审批确实发生过；也不能标记“已退款”，因为付款尚未完成。财务任务保存失败原因与关联对象，供后续核查和继续处理。它是这次失败的补偿结果，不是任意 Agent 都能调用的第四种业务动作。

## 相同请求重试会怎样

网络超时可能让调用方重复提交同一个请求。引擎使用 `intent_id` 标识这次操作意图：在同一引擎实例中，用相同身份重放同一个意图，会返回原决策记录，附上 `idempotent_replay: true`，不再创建一笔付款指令。其他身份不能取用这份结果。

这项检查解决的是同一实例内的重复请求。跨进程运行需要把幂等记录与业务写入持久化，并处理并发；本地每次重启 CLI 都会重新加载样例。

```bash
python3 run.py checkpoint 5 --check
```

[下一站：规则如何形成](06-rule-assets.md) · [返回十站目录](../book-map.md)。
