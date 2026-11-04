# 案例分析：业务条件、授权与执行结果

下面用三笔运行结果分析退款系统的判断。记录案例时，保留命令、关键输入、实际结果和原因，就能在修改配置后重新比较。

## 发票未知为何转人工

```bash
python3 run.py run YF-R-0311 --mode write
```

申请金额为 347 元，但 ERP 返回 `not_found`。来源映射将发票状态设为 `unknown`，策略命中 `G-INVOICE-UNKNOWN`，执行后创建人工审批材料，状态为 `pending_human`。

这次结果由发票状态决定。要继续办理，需要财务补充发票状态及来源，审批人员再核对其余条件。提高金额上限仍解决不了缺少发票事实的问题。本地示例到生成审批材料为止，人工续办需接入实际审批流程。

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

因此，“这笔申请符合政策”与“当前调用者有权批准”必须分别验证。不能因为模型找到了正确的处理方式，就授予它执行该动作的权限。

## 动作名称为何不能代表完成结果

```bash
python3 run.py run YF-R-0800 --mode write --simulate-payment-failure
```

批准动作执行后，付款指令创建失败。记录仍保留 `final_action: approve_refund_small`，但 `state_after` 是 `approval_pending_payment`，并生成财务任务 FMT-0800。判断完成情况需要同时查看动作、对象状态和实际效果。

分析新故障时，可以据此区分：判断本身错了，权限检查没有拦住，还是判断正确但执行未完成。三种问题需要修改的代码和补充的测试不同。

## 保存比较结果

```bash
python3 run.py run YF-R-0800 --mode write --simulate-payment-failure \
  --audit artifacts/payment-failure.jsonl
```

JSONL 保存本次决策，供事后比较；下一次运行的业务数据仍从样例文件读取。重复实验可使用不同文件名，并记录所用配置和版本。决策编号在每个引擎实例中从头编号，不同运行可能出现相同编号，因此比较时要结合文件、运行批次与 `trace_id` 确认是哪一次操作。

[十站目录](book-map.md) · [FDE 实践](fde-playbook.md)
