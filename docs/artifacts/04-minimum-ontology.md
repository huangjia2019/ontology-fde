# 第 4 站：从退款条件推导对象、关系和状态

退款申请里有金额，但批准退款还需要知道：退的是哪件商品，是否签收，发票是否处理完，客户是否有风险。建模从这些判断需要的事实开始。

例如，客户买了两件商品，只退其中一件。如果模型只关联到订单，程序就无法检查申请指向哪一件商品，也无法确定对应证据。于是退款申请需要引用订单项，而不只是订单。

## 为什么需要这些对象

[对象配置](../../config/ontology/objects.yaml)中的对象各自保存不同的事实：

| 批准退款前需要确认的事实 | 保存位置 | 为什么分开 |
|---|---|---|
| 谁提出申请，属于个人还是合同客户 | `Customer` | 同一客户可以有多笔订单，渠道会影响退款政策 |
| 这笔交易是否已签收，发票是什么状态 | `Order` | 履约和开票属于交易事实，不随退款意见改变 |
| 退的是哪个商品 | `OrderItem` | 一笔订单可能包含不同类别的商品 |
| 申请退多少，何时申请，处理到哪一步 | `RefundRequest` | 同一交易的售后处理有自己的时间和状态 |
| 哪次风险判断影响这次申请 | `RiskSignal` | 风控观测需要保留来源和时间 |
| 沟通、证据和处理记录是什么 | `Ticket`、`Evidence` | 处理意见要能追溯到工单与具体材料 |

付款指令是单独的 `PaymentInstruction` 对象。指令创建失败时，退款申请进入 `approval_pending_payment`（已批准，待付款），保留已经完成的审批，交财务核查付款故障。ERP 查不到发票时，不建立 `Invoice` 对象：订单的 `invoice_status` 记为 `unknown`，来源记录保留这次 `not_found` 查询。

## 用编号连接同一笔业务

“遥控器单”的退款编号是 `YF-R-0311`，关联订单 `O-9938`、订单项 `OI-9938-1` 和客户 `C-8831`。这些编号形成如下关系：

```text
RefundRequest YF-R-0311
  ├─ 申请人 ──> Customer C-8831
  ├─ 所属订单 ──> Order O-9938 ──客户──> C-8831
  ├─ 退款商品 ──> OrderItem OI-9938-1 ──所属订单──> O-9938
  └─ 支持证据 <── Evidence EV-0311-1
```

关系检查不只检查“编号存在”。如果申请的客户是 C-8831，关联订单却属于另一个客户，即使两个编号都有效，程序也必须拒绝把它们拼成同一笔业务。`get_case()` 会检查客户、订单和订单项之间的一致性，相关测试见[对象关联检查](../../tests/test_release_guards.py)。

```bash
python3 run.py inspect YF-R-0311
python3 run.py graph --refund-id YF-R-0311
```

不同系统还有各自的编号。售后系统的 `AS-RMA-250311` 对应本项目的 `YF-R-0311`，映射记录见[source_crosswalk.json](../../data/mock/source_crosswalk.json)。客户可能同名，仅凭姓名合并会把两个人的订单混在一起。因此，应使用经业务系统确认的编号映射来关联记录。

## 字段值还需要解释来源

发票状态来自 ERP，退款状态来自售后系统，商品和签收信息来自商城。字段的权威来源记录在[source_map.yaml](../../config/ontology/source_map.yaml)中，供人核对；程序不读取这份文件，取值逻辑写在[repository.py](../../src/ontology_fde/repository.py)的 `get_case()` 中。

对订单 `O-9938`，ERP 返回 `not_found`。记录可能尚未同步，也可能确实未开票，本次查询还无法区分。`get_case()` 将发票状态记为 `unknown`，等待财务核实；自动退款规则接受的状态是已确认未开票 `none` 或已冲红 `reversed`。

```text
ERP 没查到记录             财务确认未开票          发票已冲红
not_found                 none                   reversed
    ↓                       ↓                       ↓
invoice_status=unknown    invoice_status=none     invoice_status=reversed
    ↓                       └───────────┬───────────┘
转人工核实                           继续检查其他退款条件
```

如果在 `get_case()` 中把查不到填成 `none`（未开票），YF-R-0311 就会被自动批准，并创建付款指令 PI-0311。策略收到的已经是“已确认未开票”，无法知道 ERP 其实没查到。财务和 ERP 负责人需要先确认查询结果的含义，再让代码和来源说明保持一致；单独修改 `source_map.yaml` 不会改变运行结果。本地文件保存的是固定样例，接入真实 ERP 后还要检查查询时间，重新查询过期数据。

## 把不同业务结果分成不同状态

`approved` 表示申请获批，`paid_out` 表示已支付。两者之间还可能出现付款指令创建失败：

```text
pending_review ──批准──> approved
                            ├──付款成功──> paid_out
                            └──创建付款指令失败──> approval_pending_payment
```

本地批准分支在成功创建指令后停在 `approved`，创建失败则进入 `approval_pending_payment`。程序没有支付系统的回执，不会因此把本次申请改为 `paid_out`。[状态机](../../config/ontology/state_machines.yaml)不允许从 `pending_review` 直接跳到 `paid_out`，`transition()` 遇到非法跳转会报错。

业务人员说“退了”时，可能指审批通过，也可能指钱已到账。分别建模以后，客服可以回答具体进度，财务可以找到未完成的付款，程序也能拒绝不合法的状态跳转。

```bash
python3 run.py checkpoint 4 --check
```

检查卡只检查五个文件是否存在、对象是否声明，以及是否定义了批准后的失败补偿状态转换。它不核对来源映射或样例中的对象关系；对象关联是否正确，要运行前面的 `inspect` 命令并检查相关测试。

[下一站：动作契约](05-action-contract.md)。

[返回十站目录](../book-map.md)。
