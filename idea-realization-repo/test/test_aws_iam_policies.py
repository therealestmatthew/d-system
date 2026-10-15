"""aws/iam/*.json: every policy parses, and the owner's rulings of 2026-10-14 hold in them."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

IAM = Path(__file__).resolve().parent.parent / "aws" / "iam"
BOUNDARY = "arn:aws:iam::REPLACE_WITH_SANDBOX_ACCOUNT_ID:policy/app-permissions-boundary"


def policy(name: str) -> dict[str, dict[str, Any]]:
    doc = json.loads((IAM / name).read_text(encoding="utf-8"))
    assert doc["Version"] == "2012-10-17"
    sids = [s["Sid"] for s in doc["Statement"]]
    assert len(sids) == len(set(sids)), "statement ids must be unique"
    return {s["Sid"]: s for s in doc["Statement"]}


def actions(statement: dict[str, Any]) -> list[str]:
    value: str | list[str] = statement.get("Action", [])
    return [value] if isinstance(value, str) else value


@pytest.mark.parametrize("name", sorted(p.name for p in IAM.glob("*.json")))
def test_every_policy_parses_and_fits_the_managed_policy_size(name: str) -> None:
    policy(name)
    assert len("".join((IAM / name).read_text(encoding="utf-8").split())) <= 6144


def test_app_roles_are_created_only_under_the_boundary() -> None:
    deploy = policy("deploy-policy.json")
    allow = deploy["AllowChangingAppRolesOnlyUnderTheBoundary"]
    assert "iam:CreateRole" in actions(allow)
    assert allow["Resource"] == "arn:aws:iam::*:role/app/*"
    assert allow["Condition"] == {"StringEquals": {"iam:PermissionsBoundary": BOUNDARY}}
    deny = deploy["DenyAppRoleChangesWithoutTheBoundary"]
    assert set(actions(allow)) == set(actions(deny))
    assert deny["Condition"] == {"StringNotEquals": {"iam:PermissionsBoundary": BOUNDARY}}
    removing = deploy["DenyRemovingOrChangingTheBoundary"]
    assert "iam:DeleteRolePermissionsBoundary" in actions(removing)
    outside = deploy["DenyEveryIamChangeOutsideAppRoles"]
    assert outside["NotResource"] == "arn:aws:iam::*:role/app/*"
    assert "iam:Create*" in actions(outside)


def test_pass_role_is_limited_to_app_roles_and_named_services() -> None:
    deploy = policy("deploy-policy.json")
    passing = deploy["AllowPassingAppRolesToTheProductsServices"]
    assert passing["Resource"] == "arn:aws:iam::*:role/app/*"
    services = passing["Condition"]["StringEquals"]["iam:PassedToService"]
    assert {"states.amazonaws.com", "bedrock.amazonaws.com",
            "amplify.amazonaws.com"} <= set(services)


def test_region_deny_exempts_only_inference_profile_routing() -> None:
    for name, sid in (("deploy-policy.json", "DenyOtherRegionsExceptInferenceProfileRouting"),
                      ("app-permissions-boundary.json",
                       "DenyOtherRegionsExceptInferenceProfileRouting")):
        statement = policy(name)[sid]
        assert statement["Condition"]["Null"] == {"bedrock:InferenceProfileArn": "true"}
        assert "aws:RequestedRegion" in statement["Condition"]["StringNotEquals"]
        global_deny = json.dumps(policy(name)["DenyGlobalInferenceProfiles"])
        assert "inference-profile/global.*" in global_deny


def test_cloudtrail_deny_names_only_the_baseline_trail() -> None:
    trail = policy("deploy-policy.json")["DenyTurningOffTheBaselineTrail"]
    assert trail["Resource"] == "arn:aws:cloudtrail:*:*:trail/REPLACE_WITH_BASELINE_TRAIL_NAME"


def test_deploy_role_cannot_bypass_object_lock_but_keeps_key_administration() -> None:
    deploy = policy("deploy-policy.json")
    assert actions(deploy["DenyBypassingObjectLockRetention"]) == ["s3:BypassGovernanceRetention"]
    denied = {a for s in deploy.values() if s["Effect"] == "Deny" for a in actions(s)}
    assert not {"kms:PutKeyPolicy", "kms:ScheduleKeyDeletion", "kms:*"} & denied


def test_read_role_decrypts_only_through_s3_and_dynamodb() -> None:
    guard = policy("read-only-guard-policy.json")
    assert "kms:Decrypt" not in actions(guard["DenySecretAndCredentialReads"])
    via = guard["DenyDecryptExceptThroughS3AndDynamoDB"]["Condition"]["StringNotLike"]
    data = policy("read-sandbox-data-policy.json")
    allow = data["SandboxOnlyDecryptTenantDataThroughS3AndDynamoDB"]["Condition"]["StringLike"]
    assert via == allow
    assert actions(data["SandboxOnlyReadTextractResults"]) == ["textract:Get*", "textract:List*"]
