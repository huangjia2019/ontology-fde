# 第 3 站：给退款助手登记身份

退款助手以 `agent.cs.refund.001` 执行。它不冒充客服主管，记录中的 `as_itself` 表示以自身身份行动。身份由[refund_agent.yaml](../../config/identity/refund_agent.yaml)描述。

## IART：身份、行动能力、关系与生命周期

| 维度 | 在这里指什么 | 配置中查看什么 |
|---|---|---|
| Identity：身份 | 它是谁，以谁的名义行动 | `technical_id`、`representation`、业务与技术负责人 |
| Agency：行动能力 | 可以读、建议、调用和写什么 | `read`、`draft`、`call`、`write`、`forbidden` |
| Relationship：关系 | 服务谁，受谁监督，和谁协作 | `users`、`supervisors`、`data_sources`、`peer_agents` |
| Temporality：生命周期 | 哪个版本，何时扩大或收回权限 | `promotion_gate`、`rollback_on`、`retirement_conditions` |

配置中的业务责任岗位是客服运营负责人，技术责任岗位是客户平台工程团队。前者确认退款政策和自动化范围，后者维护程序、连接器与运行故障。两者分开后，遇到“合同客户是否可以自动批准”和“ERP 查询超时”，就能找到不同的处理人。

## 从人工决策到条件自动化

身份配置保留了一组晋级条件：36 个策略样例和 2 个事故回放通过，决策记录覆盖符合要求，拒绝未授权主体的测试通过，并得到业务负责人批准。越权、无法解释的写入或证据来源缺失，触发收回权限的讨论与处理。

晋级条件用于决定何时扩大自动执行范围。例如，能够正确生成建议，并不说明付款失败补偿已经可靠；开放写入前，还要验证执行路径。配置中的晋级、回退字段记录这些管理要求，本地程序未接入企业审批或账号管理系统。

```bash
python3 run.py identity
python3 run.py run YF-R-0500 --mode write --actor agent.marketing.unknown
python3 run.py checkpoint 3 --check
```

未知主体的结果应包含 `G-ACTOR`，前后状态都为 `pending_review`，不创建付款指令。请技术与安全负责人核对身份、契约允许主体、权限策略中的 `agent_id` 是否一致。

这里通过命令参数传入身份，便于演练拒绝行为。真实环境必须从可信认证结果取得身份，不能把用户输入的字符串当作认证证明。[第 7 站](07-identity-and-permissions.md)继续检查一次动作是否获准。

[返回十站目录](../book-map.md)。
