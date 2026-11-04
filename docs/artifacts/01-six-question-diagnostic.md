# 第 1 站：检查退款方案中的业务定义

接入客服知识库和退款 API 后，还要检查订单是否属于申请人、退款是否符合财务政策，以及付款失败后怎样继续处理。这些判断分别涉及身份、对象、动作、规则、权限和失败处理。

| 检查项 | 云帆项目中的具体定义 | 定义与实现 |
|---|---|---|
| 执行主体 | `agent.cs.refund.001` 以自身身份执行，不借用主管账号 | [身份配置](../../config/identity/refund_agent.yaml) |
| 处理对象 | 申请关联客户、订单和订单项，三者必须一致 | [对象定义](../../config/ontology/)、[关联检查](../../src/ontology_fde/repository.py) |
| 业务动作 | 批准、转人工或补证，均有对应前提与效果 | [动作契约](../../config/actions/) |
| 判断依据 | ERP 查无记录记为发票未知，交财务核实是否开票 | [get_case()](../../src/ontology_fde/repository.py)与[退款策略](../../src/ontology_fde/policy.py) |
| 授权范围 | 自动批准限额 500 元，禁止修改申请金额 | [权限配置](../../config/policies/permissions.yaml) |
| 失败处理 | 付款指令失败进入待付款状态，生成财务任务 | [执行引擎](../../src/ontology_fde/engine.py) |

## 核对身份与业务事实

```bash
python3 run.py summary
python3 run.py identity
```

`summary` 返回来源和对象概况，`identity` 返回身份及能力范围。运行 `python3 run.py inspect YF-R-0311` 可以进一步核对这笔申请的对象引用和来源记录。

如果申请、订单和商品的引用关系错了，查 `repository.py` 的 `get_case()`。如果发票未知仍被批准，查 `get_case()` 是否返回 `unknown`，以及 `policy.py` 的 `G-INVOICE-UNKNOWN` 分支。如果未授权主体能执行，查契约的 `actor.allowed`、权限配置和执行前的主体检查。

[下一站：审视原有方案](02-historical-audit.md) · [返回十站目录](../book-map.md)。
