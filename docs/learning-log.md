# 案例分析：业务条件、授权与执行结果

记录案例时，保留命令、关键输入、实际结果和原因，就能在修改配置或代码后重新比较。

## 发票未知为何转人工

```bash
python3 run.py run YF-R-0311 --mode write
```

申请金额为 347 元，但 ERP 返回 `not_found`。`repository.py` 的 `get_case()` 将发票状态记为 `unknown`，策略命中 `G-INVOICE-UNKNOWN`，执行后创建人工审批材料，状态为 `pending_human`。

这次决策记录的 `checks` 中，只有 `invoice_status_known_safe` 为 false，其余检查均通过。要继续办理，需要财务补充发票状态及来源，审批人员据此决定是否批准；若核实期间其他事实有变化，也要重新检查。本地示例到生成审批材料为止，人工续办需接入实际审批流程。

## 相同业务为何因执行者不同而被拒绝

```bash
python3 run.py run YF-R-0500 --mode write
python3 run.py run YF-R-0500 --mode write --actor agent.marketing.unknown
```

每次运行都会重新读取样例文件，因此第二条命令处理的仍是待审核申请。第一次由退款 Agent 批准并创建模拟付款指令，第二次由未登记的营销 Agent 发起，命中 `G-ACTOR`。这样可以比较主体不同、业务条件相同的两次结果。

| 比较项 | 退款 Agent | 未登记营销 Agent |
|---|---|---|
| 申请金额 | 500 元 | 500 元 |
| 业务条件 | 全部满足 | 全部满足 |
| 动作主体检查 | 通过 | 不通过 |
| 实际效果 | 批准并创建付款指令 | 无业务写入 |

“这笔申请符合政策”与“当前调用者有权批准”需要分别验证。

## 动作名称为何不能代表完成结果

```bash
python3 run.py run YF-R-0800 --mode write --simulate-payment-failure
```

批准动作执行后，付款指令创建失败。记录仍保留 `final_action: approve_refund_small`，但 `state_after` 是 `approval_pending_payment`，并生成财务任务 FMT-0800。批准记录保留，待处理的是付款故障。查看 `final_action`、`state_after` 和 `actual_effect`，可以判断退款进行到了哪一步。

分析新故障时，判断错误先查 `policy.py` 和策略样例；权限未拦住先查契约允许的主体、权限配置及 `G-ACTOR` 测试；批准后执行失败则查 `engine.py` 的补偿分支和付款失败测试。

## 保存比较结果

```bash
python3 run.py run YF-R-0800 --mode write --simulate-payment-failure \
  --audit artifacts/payment-failure.jsonl
```

JSONL 追加保存本次决策。相同命令重复运行时，`decision_id`、`trace_id` 和时间戳都相同：计数从头开始，处理时间默认取申请时间，轨迹编号由相同输入计算。记录中没有运行批次字段，因此每轮实验应使用不同的文件名，并另外记下代码和配置版本。

[十站目录](book-map.md) · [FDE 现场练习](fde-playbook.md)
