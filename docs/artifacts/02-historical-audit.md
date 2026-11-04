# 第 2 站：从建议到执行，原有方案缺了什么

过去，客服看完助手的建议，再自己登录系统批准退款。现在希望 Agent 直接执行，就需要规定它可以批准哪些申请、使用哪个身份，以及出错后由谁处理。

人工原先会核对订单、检查批准条件，再使用自己的账号执行。给 Agent 接上写接口后，这些检查必须有明确的实现位置，包括订单是否属于申请人、金额是否超过上限、发票是否已经开具。

| 风险编号 | 容易沿用的做法 | 在退款项目中会发生什么 | 要补的材料与验收 |
|---|---|---|---|
| HM-01 | 把给人看的建议直接当执行指令 | 一份未获批准的建议改变了业务状态 | [第 5 站](05-action-contract.md)：分开 Read、Draft、Write，验证前两者不写业务对象 |
| HM-02 | 只记录接口返回成功 | 查不到为什么批准，是否真的形成付款指令 | [动作契约](../../config/actions/)与[第 9 站决策记录](09-evaluation-audit-and-incident-replay.md)：核对前后状态和实际效果 |
| HM-03 | 复用客服主管账号 | 审计只能看到主管操作，分不清是谁发起 | [第 3 站身份](03-identity-acceptance.md)与[第 7 站权限](07-identity-and-permissions.md)：未登记主体必须被拒绝 |
| HM-04 | 换一个版本就扩大自动化范围 | 权限扩大了，业务条件和责任没有重审 | 身份配置的晋级条件、[事故回放](../../config/evals/incident_replays.json)与[第 10 站交接](10-operations-handoff-and-replication.md) |

## 在参考程序中核对

```bash
python3 run.py summary
python3 run.py run YF-R-0500 --mode draft
python3 run.py run YF-R-0500 --mode write --actor agent.marketing.unknown
python3 run.py checkpoint 2 --check
```

Draft 命令应返回批准建议，退款仍为 `pending_review`。随后用未知主体执行同一笔申请，即使业务条件满足，也会因主体未获授权而拒绝，命中 `G-ACTOR`。检查卡只确认文档包含四个风险编号，实际行为要看运行结果和测试。

身份认证确认“请求是谁发出的”，动作授权检查“这个主体能否调用批准动作”，业务条件检查“这笔申请能否自动批准”。例如，已登录的营销助手不应批准退款；退款助手虽然获得授权，也不能自动批准超额申请。本地命令只接收一个身份字符串，用它演示后两种检查；验证真实调用者还需要接入认证服务。

[返回十站目录](../book-map.md)。
