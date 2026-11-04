from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .exit_drill import exit_drill_payload
from .paths import load_structured, project_root
from .repository import EnterpriseRepository


@dataclass(frozen=True, slots=True)
class CheckpointSpec:
    number: int
    title: str
    problem: str
    artifacts: tuple[str, ...]
    commands: tuple[str, ...]
    acceptance: tuple[str, ...]


CHECKPOINTS: dict[int, CheckpointSpec] = {
    1: CheckpointSpec(
        1,
        "项目定位：跟完一笔退款",
        "347 元退款的发票查询返回 not_found，为什么应转人工核实？",
        (
            "docs/artifacts/01-field-walkthrough.md",
            "docs/artifacts/01-ontology-positioning-card.md",
            "docs/artifacts/01-six-question-diagnostic.md",
        ),
        ("python3 run.py inspect YF-R-0311",),
        (
            "ERP 的 not_found 观测保留在来源记录中；发票状态映射为 unknown，转人工核实是否开票，再决定是否批准。",
        ),
    ),
    2: CheckpointSpec(
        2,
        "原有方案审计",
        "给人提建议的助手开始执行业务动作后，原有接口日志、共享账号和发布流程还缺哪些控制？",
        ("docs/artifacts/02-historical-audit.md",),
        ("python3 run.py summary",),
        (
            "第 2 站文档表格列出 HM-01 至 HM-04 的后续验收位置；本检查只确认四个编号均在文档中。行为验证需执行相应命令和测试。",
        ),
    ),
    3: CheckpointSpec(
        3,
        "IART 身份登记",
        "登记退款助手以谁的名义行动、由谁负责、与谁协作，以及权限何时扩大或收回。",
        (
            "config/identity/refund_agent.yaml",
            "docs/artifacts/03-identity-acceptance.md",
        ),
        ("python3 run.py identity",),
        (
            "身份配置声明技术身份 agent.cs.refund.001 和 representation: as_itself；IART 四部分、晋级条件、回退条件及数据来源均已登记。technical_id 与权限配置是否一致仍需人工核对。",
        ),
    ),
    4: CheckpointSpec(
        4,
        "最小本体 v0.1",
        "将各来源记录关联到同一笔退款，保留编号、字段来源、对象关系和允许的状态转换。",
        (
            "docs/artifacts/04-minimum-ontology.md",
            "config/ontology/objects.yaml",
            "config/ontology/relationships.yaml",
            "config/ontology/state_machines.yaml",
            "config/ontology/source_map.yaml",
        ),
        ("python3 run.py graph --refund-id YF-R-0311",),
        (
            "检查五个文件存在、对象配置包含 RefundRequest、状态机声明 approved 到 approval_pending_payment 的转换。来源映射和样例关系不在本检查范围内，需核对 get_case() 及对象关联测试。",
        ),
    ),
    5: CheckpointSpec(
        5,
        "动作契约与执行器",
        "比较 500 元与 500.01 元的申请，将接口调用限定为有前提、效果、审批门槛、重试和失败处理的业务动作。",
        (
            "docs/artifacts/05-action-contract.md",
            "config/actions/approve_refund_small.yaml",
            "config/actions/request_human_refund_approval.yaml",
            "config/actions/request_missing_evidence.yaml",
            "src/ontology_fde/engine.py",
        ),
        (
            "python3 run.py run YF-R-0500 --mode write",
            "python3 run.py run YF-R-0501 --mode write",
        ),
        (
            "其他条件通过时，500 元可批准并创建模拟付款指令；500.01 元转人工，等待人工批准后再进入付款流程。真实到账要以支付结果为依据。",
            "Read 和 Draft 不改变业务状态；Write 重新读取事实、检查授权与业务条件后执行动作。",
            "写入路径中的执行、拒绝与转人工结果均有 DecisionRecord，能核对前后状态和实际效果。",
        ),
    ),
    6: CheckpointSpec(
        6,
        "规则来源与草稿",
        "把签收超过 24 小时的政策绑定到申请时间、签收时间和商品状态，并验证时间边界与缺失数据。",
        (
            "docs/artifacts/06-rule-assets.md",
            "config/rules/refund_rules.yaml",
            "config/rules/drafts/opened_consumable_rule_draft.json",
            "config/evals/document_rule_cases.json",
        ),
        (
            "python3 run.py extract-rule "
            "--output artifacts/ch06-rule-draft.json",
            "python3 run.py run YF-R-0703 --mode draft",
        ),
        (
            "签收后恰好 24 小时不算超过，规则不触发；缺少经过时长返回 missing_data；B2B 返回 out_of_scope。采用草稿前，还需确定开封事实由谁提供、完成审核与编译，再接入执行程序。",
        ),
    ),
    7: CheckpointSpec(
        7,
        "身份与六维权限验收",
        "同一笔 500 元申请，已授权退款 Agent 可以批准，未登记 Agent 必须被拒绝。",
        (
            "docs/artifacts/07-identity-and-permissions.md",
            "config/identity/refund_agent.yaml",
            "config/policies/permissions.yaml",
        ),
        (
            "python3 run.py run YF-R-0500 --mode write --actor agent.marketing.unknown",
            "python3 tools/verify.py",
        ),
        (
            "运行未知主体命令，应触发 G-ACTOR，退款状态和付款对象均不改变。本地只核对身份字符串，不验证凭据；集成范围见 docs/artifacts/07-identity-and-permissions.md 的“哪些已经运行，哪些还需要集成”。",
        ),
    ),
    8: CheckpointSpec(
        8,
        "任务信封与冲突裁决",
        "280 元申请的一般退款条件通过，但风控要求复核。按冲突策略转人工，同时保留两项意见。",
        (
            "docs/artifacts/08-multi-agent-coordination.md",
            "docs/artifacts/08-task-envelope-YF-R-0610.json",
            "config/identity/agent_registry.yaml",
            "config/policies/conflict_resolution.yaml",
        ),
        (
            "python3 run.py run YF-R-0610 --mode write "
            "--audit artifacts/ch08-decision-records.jsonl",
        ),
        (
            "决策记录的 envelope_id 为 ENV-T-0610，与信封样例一致；RiskAgent:review 覆盖 RefundAgent:approve，两项意见均保留。退款进入 pending_human，创建人工审批材料；风险核实并获得人工批准之前，暂不创建付款指令。",
        ),
    ),
    9: CheckpointSpec(
        9,
        "决策记录与事故回放",
        "核对每次判断读了什么、依据何种权限、调用了哪些动作、实际改变了什么，再将发现的问题加入回归样例。",
        (
            "docs/artifacts/09-evaluation-audit-and-incident-replay.md",
            "config/evals/golden_set_v1.json",
            "config/evals/incident_replays.json",
            "src/ontology_fde/audit.py",
        ),
        (
            "python3 run.py evaluate --output artifacts/ch09-eval.json",
            "python3 run.py run YF-R-0800 --mode write "
            "--simulate-payment-failure --audit artifacts/ch09-failure.jsonl",
        ),
        (
            "36 个核心策略样例与 2 个事故回放通过，验证给定事实下的策略判断；执行器测试另行验证付款指令创建失败后的状态、失败记录和财务任务。",
        ),
    ),
    10: CheckpointSpec(
        10,
        "运行交接、场景复制与退出",
        "付款失败后如何找到财务任务、失败指令和决策记录？停用自动执行时，未完成退款由谁接手？",
        (
            "docs/artifacts/10-operations-handoff-and-replication.md",
            "docs/fde-playbook.md",
            "AGENTS.md",
            "Makefile",
            "src/ontology_fde/exit_drill.py",
        ),
        (
            "python3 tools/verify.py",
            "python3 run.py demo --output artifacts/demo",
            "python3 run.py evaluate",
            "python3 run.py exit-drill",
        ),
        (
            "核对 production_write: false 的声明、工作负载身份前缀、转人工契约、审计策略引用及文档中的操作名称。PASS 不表示已停用账号或移交业务；逐项判定条件见第 10 站文档。",
        ),
    ),
}


def checkpoint_payload(number: int, *, check: bool = False) -> dict[str, Any]:
    if number not in CHECKPOINTS:
        raise ValueError(f"Checkpoint must be between 1 and 10, got {number}")
    payload = asdict(CHECKPOINTS[number])
    if check:
        items = _check_required_paths(CHECKPOINTS[number].artifacts)
        items.extend(_check_semantics(number))
        payload["check"] = {
            "passed": all(item["passed"] for item in items),
            "items": items,
        }
    return payload


def _check_required_paths(paths: tuple[str, ...]) -> list[dict[str, Any]]:
    root = project_root()
    return [
        {
            "name": "required_path_exists",
            "target": path,
            "passed": (root / path).exists(),
        }
        for path in paths
    ]


def _item(name: str, passed: bool, actual: Any) -> dict[str, Any]:
    return {"name": name, "passed": bool(passed), "actual": actual}


def _check_semantics(number: int) -> list[dict[str, Any]]:
    try:
        if number == 1:
            source_map = load_structured("config/ontology/source_map.yaml")
            case = EnterpriseRepository().get_case("YF-R-0311")
            erp_observations = [
                ref for ref in case.source_refs if ref["system"] == "ERP"
            ]
            return [
                _item(
                    "source_map_declared",
                    bool(source_map),
                    source_map.get("schema_version"),
                ),
                _item(
                    "erp_negative_observation_preserved",
                    len(erp_observations) == 1
                    and erp_observations[0].get("observation") == "not_found",
                    erp_observations,
                ),
                _item(
                    "erp_no_result_remains_unknown",
                    case.invoice_status == "unknown",
                    case.invoice_status,
                ),
            ]
        if number == 2:
            text = (
                project_root() / "docs/artifacts/02-historical-audit.md"
            ).read_text(encoding="utf-8")
            risk_ids = [f"HM-0{index}" for index in range(1, 5)]
            return [
                _item(
                    "four_historical_risks_mapped",
                    all(value in text for value in risk_ids),
                    risk_ids,
                )
            ]
        if number == 3:
            identity = load_structured("config/identity/refund_agent.yaml")
            keys = {"identity", "agency", "relationship", "temporality"}
            temporality = identity["temporality"]
            promotion_gate = temporality.get("promotion_gate", {})
            required_gates = {
                "golden_replay == 36/36",
                "incident_replay == 2/2",
                "decision_record_coverage == 100%",
                "permission_denied_test == pass",
                "business_owner_approval == true",
            }
            required_rollbacks = {
                "guardrail_breach",
                "unexplained_write",
                "evidence_lineage_missing",
            }
            required_sources = {
                "CRM",
                "COMMERCE",
                "AFTER_SALES",
                "ERP",
                "SUPPORT",
                "RISK",
                "EVIDENCE",
                "PAYMENTS",
            }
            required_writes = {
                "HumanApprovalPacket:create",
                "EvidenceRequestDraft:create",
                "FinanceManualTask:create",
                "DecisionRecord:create",
            }
            return [
                _item("iart_complete", keys.issubset(identity), sorted(identity)),
                _item(
                    "acts_as_itself",
                    identity["identity"]["representation"] == "as_itself",
                    identity["identity"]["representation"],
                ),
                _item(
                    "promotion_gate_declared",
                    promotion_gate.get("from") == "L3-human-decision"
                    and promotion_gate.get("to") == "L4-conditional-auto"
                    and required_gates.issubset(set(promotion_gate.get("requires", []))),
                    promotion_gate,
                ),
                _item(
                    "rollback_conditions_declared",
                    required_rollbacks.issubset(
                        set(temporality.get("rollback_on", []))
                    ),
                    temporality.get("rollback_on", []),
                ),
                _item(
                    "eight_data_sources_declared",
                    required_sources.issubset(
                        set(identity["relationship"]["data_sources"])
                    ),
                    identity["relationship"]["data_sources"],
                ),
                _item(
                    "runtime_side_effects_declared",
                    required_writes.issubset(set(identity["agency"]["write"])),
                    identity["agency"]["write"],
                ),
            ]
        if number == 4:
            objects = load_structured("config/ontology/objects.yaml")
            states = load_structured("config/ontology/state_machines.yaml")
            object_names = [
                row["name"]
                for group in ("core_objects", "supporting_objects")
                for row in objects[group]
            ]
            refund_states = states["state_machines"]["RefundRequest"]["transitions"]
            return [
                _item(
                    "refund_request_declared",
                    "RefundRequest" in object_names,
                    object_names,
                ),
                _item(
                    "compensation_state_declared",
                    ["approved", "approval_pending_payment"] in refund_states,
                    refund_states,
                ),
            ]
        if number == 5:
            action = load_structured("config/actions/approve_refund_small.yaml")
            missing_evidence = load_structured(
                "config/actions/request_missing_evidence.yaml"
            )
            artifact_text = (
                project_root() / "docs/artifacts/05-action-contract.md"
            ).read_text(encoding="utf-8")
            success_rows = [
                line
                for line in artifact_text.splitlines()
                if "`approve_refund_small`" in line and "`approved`" in line
            ]
            return [
                _item(
                    "approval_threshold_is_500",
                    action["approval"]["threshold_cny"] == 500,
                    action["approval"]["threshold_cny"],
                ),
                _item(
                    "idempotency_declared",
                    bool(action.get("idempotency")),
                    action.get("idempotency"),
                ),
                _item(
                    "compensation_declared",
                    bool(action.get("compensation")),
                    action.get("compensation"),
                ),
                _item(
                    "third_contract_is_missing_evidence",
                    missing_evidence["action_id"] == "request_missing_evidence",
                    missing_evidence["action_id"],
                ),
                _item(
                    "success_state_is_approved",
                    bool(success_rows),
                    "approved" if success_rows else "missing",
                ),
            ]
        if number == 6:
            rules = load_structured("config/rules/refund_rules.yaml")
            draft = load_structured(
                "config/rules/drafts/opened_consumable_rule_draft.json"
            )
            cases = load_structured("config/evals/document_rule_cases.json")
            case_kinds = sorted({case["kind"] for case in cases["cases"]})
            return [
                _item(
                    "five_explicit_rules",
                    len(rules["rules"]) == 5,
                    len(rules["rules"]),
                ),
                _item(
                    "rule_is_still_draft",
                    draft["lifecycle"]["state"] == "draft",
                    draft["lifecycle"]["state"],
                ),
                _item(
                    "known_gap_declared",
                    bool(draft["missing_inputs"]),
                    draft["missing_inputs"],
                ),
                _item("five_rule_case_kinds", len(case_kinds) == 5, case_kinds),
            ]
        if number == 7:
            permissions = load_structured("config/policies/permissions.yaml")
            dimensions = set(permissions["dimensions"])
            expected = {
                "data",
                "tools",
                "actions",
                "conditions",
                "time",
                "environment",
            }
            return [
                _item(
                    "six_permission_dimensions",
                    dimensions == expected,
                    sorted(dimensions),
                ),
                _item(
                    "production_write_disabled",
                    permissions["dimensions"]["environment"]["production_write"]
                    is False,
                    permissions["dimensions"]["environment"],
                ),
            ]
        if number == 8:
            registry = load_structured("config/identity/agent_registry.yaml")
            policy = load_structured("config/policies/conflict_resolution.yaml")
            envelope = load_structured(
                "docs/artifacts/08-task-envelope-YF-R-0610.json"
            )
            refund_agent = next(
                row
                for row in registry["agents"]
                if row["agent_id"] == "agent.cs.refund.001"
            )
            required_side_effects = {
                "RefundRequest",
                "PaymentInstruction",
                "HumanApprovalPacket",
                "EvidenceRequestDraft",
                "FinanceManualTask",
                "DecisionRecord",
            }
            return [
                _item(
                    "three_agents_registered",
                    len(registry["agents"]) == 3,
                    len(registry["agents"]),
                ),
                _item(
                    "conflict_policy_bound",
                    policy["policy_id"] == "POL-AGENT-CONFLICT-001",
                    policy["policy_id"],
                ),
                _item(
                    "sample_envelope_scoped",
                    envelope["envelope_id"] == "ENV-T-0610"
                    and envelope["recipient"] == "agent.cs.refund.001",
                    {
                        "envelope_id": envelope["envelope_id"],
                        "recipient": envelope["recipient"],
                    },
                ),
                _item(
                    "registry_lists_runtime_side_effects",
                    required_side_effects.issubset(set(refund_agent["writes"])),
                    refund_agent["writes"],
                ),
            ]
        if number == 9:
            golden = load_structured("config/evals/golden_set_v1.json")
            incidents = load_structured("config/evals/incident_replays.json")
            return [
                _item(
                    "golden_set_has_36_cases",
                    len(golden["cases"]) == 36,
                    len(golden["cases"]),
                ),
                _item(
                    "incident_set_has_2_cases",
                    len(incidents["cases"]) == 2,
                    len(incidents["cases"]),
                ),
            ]
        if number == 10:
            text = (
                project_root()
                / "docs/artifacts/10-operations-handoff-and-replication.md"
            ).read_text(encoding="utf-8")
            required = [
                "Close `Write`",
                "Revoke credentials",
                "Return unfinished work to people",
                "Preserve audit evidence",
            ]
            drill = exit_drill_payload()
            return [
                _item(
                    "exit_drill_has_four_controls",
                    all(token in text for token in required),
                    required,
                ),
                _item(
                    "executable_exit_drill_passes",
                    drill["status"] == "PASS" and len(drill["steps"]) == 5,
                    drill,
                ),
            ]
    except (KeyError, OSError, TypeError, ValueError) as error:
        return [
            _item(
                "semantic_check_loads",
                False,
                f"{type(error).__name__}: {error}",
            )
        ]
    return []
