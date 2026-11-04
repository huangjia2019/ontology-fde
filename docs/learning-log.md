# 案例分析：业务条件、授权与执行结果

下面用三笔运行结果分析退款系统的判断。记录案例时，保留命令、关键输入、实际结果和原因，就能在修改配置后重新比较。

## 发票未知为何转人工

```bash
python3 run.py run YF-R-0311 --mode write
```

申请金额为 347 元，但 ERP 返回 `not_found`。来源映射将发票状态设为 `unknown`，策略命中 `G-INVOICE-UNKNOWN`，执行后创建人工审批材料，状态为 `pending_human`。

这次结果由发票状态决定。若要继续自动审批，需要取得能够确认发票状态的记录，再检查其余条件。仅提高金额上限不会改变这笔申请缺失发票事实的问题。

## 相同业务为何因执行者不同而被拒绝

```bash
python3 run.py run YF-R-0500 --mode write
python3 run.py run YF-R-0500 --mode write --actor agent.marketing.unknown
```

两次运行使用相同初始业务数据。第一次批准并创建模拟付款指令，第二次命中 `G-ACTOR`，状态仍为 `pending_review`。

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

JSONL 保存本次决策，不持久化业务状态。重复实验可使用不同文件名，并记录所用配置和版本。决策编号在引擎实例内顺序生成，跨进程比较时应结合文件、运行批次与 `trace_id`，不能仅凭相同编号认定是同一次操作。

[十站目录](book-map.md) · [FDE 实践](fde-playbook.md)
