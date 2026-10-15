"""aws/iam/*.json: every policy parses, and the owner's rulings of 2026-10-14 hold in them."""

from __future__ import annotations

import fnmatch
import json
from pathlib import Path
from typing import Any

import pytest

IAM = Path(__file__).resolve().parent.parent / "aws" / "iam"
BOUNDARY = "arn:aws:iam::REPLACE_WITH_SANDBOX_ACCOUNT_ID:policy/app-permissions-boundary"
US_PROFILES = "arn:aws:bedrock:*:*:inference-profile/us.*"
APP_ROLES = "arn:aws:iam::*:role/app/*"

#: Condition keys, and the actions the AWS Service Authorization Reference lists them for
#: (docs.aws.amazon.com/service-authorization/latest/reference/list_iam.html, list_bedrock.html,
#: list_kms.html; read 2026-10-14). A key on any other action is never in the request context.
#: iam:PermissionsBoundary is the boundary in the request for CreateRole/CreateUser/Put*Boundary,
#: and the boundary already attached to the role or user for the other actions.
CONDITION_KEY_ACTIONS: dict[str, set[str]] = {
    "iam:PermissionsBoundary": {
        "iam:AttachRolePolicy", "iam:AttachUserPolicy", "iam:CreateRole", "iam:CreateUser",
        "iam:DeleteRole", "iam:DeleteRolePermissionsBoundary", "iam:DeleteRolePolicy",
        "iam:DeleteUserPermissionsBoundary", "iam:DeleteUserPolicy", "iam:DetachRolePolicy",
        "iam:DetachUserPolicy", "iam:GetRole", "iam:PutRolePermissionsBoundary",
        "iam:PutRolePolicy", "iam:PutUserPermissionsBoundary", "iam:PutUserPolicy",
        "iam:UpdateAssumeRolePolicy", "iam:UpdateRole", "iam:UpdateRoleDescription"},
    "iam:PassedToService": {"iam:PassRole"},
    "bedrock:InferenceProfileArn": {"bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"},
    "kms:ViaService": {"kms:Decrypt"},
    "kms:ResourceAliases": {"kms:Decrypt"},
}


def policy(name: str) -> dict[str, dict[str, Any]]:
    doc = json.loads((IAM / name).read_text(encoding="utf-8"))
    assert doc["Version"] == "2012-10-17"
    sids = [s["Sid"] for s in doc["Statement"]]
    assert len(sids) == len(set(sids)), "statement ids must be unique"
    return {s["Sid"]: s for s in doc["Statement"]}


def actions(statement: dict[str, Any]) -> list[str]:
    value: str | list[str] = statement.get("Action", [])
    return [value] if isinstance(value, str) else value


def arn_like(value: str, pattern: str) -> bool:
    """ArnLike: each of the six colon-separated parts is matched on its own, with * and ?."""
    value_parts, pattern_parts = value.split(":", 5), pattern.split(":", 5)
    return len(value_parts) == len(pattern_parts) == 6 and all(
        fnmatch.fnmatchcase(v, p) for v, p in zip(value_parts, pattern_parts, strict=True))


def conditions_match(condition: dict[str, dict[str, Any]], context: dict[str, str]) -> bool:
    """Evaluate a Condition block against a request context of single-valued keys, with the
    missing-key rules of the IAM user guide ("Condition operators"): a missing key does not
    match a positive operator, matches a negated one, and Null tests presence."""
    for operator, keys in condition.items():
        for key, wanted in keys.items():
            values = [wanted] if isinstance(wanted, str) else list(wanted)
            present = key in context
            if operator == "Null":
                if (values[0] == "true") == present:
                    return False
                continue
            negated = "Not" in operator
            if not present:
                if not negated:
                    return False
                continue
            actual = context[key]
            if operator in ("StringEquals", "StringNotEquals"):
                hit = actual in values
            elif operator in ("StringLike", "StringNotLike"):
                hit = any(fnmatch.fnmatchcase(actual, v) for v in values)
            elif operator in ("ArnLike", "ArnNotLike", "ArnEquals", "ArnNotEquals"):
                hit = any(arn_like(actual, v) for v in values)
            else:
                raise AssertionError(f"operator {operator} not modelled")
            if hit == negated:
                return False
    return True


def statement_covers(statement: dict[str, Any], action: str) -> bool:
    if "NotAction" in statement:
        excluded = statement["NotAction"]
        excluded = [excluded] if isinstance(excluded, str) else excluded
        return not any(fnmatch.fnmatchcase(action, a) for a in excluded)
    return any(fnmatch.fnmatchcase(action, a) for a in actions(statement))


def statement_names(statement: dict[str, Any], resource: str) -> bool:
    key = "NotResource" if "NotResource" in statement else "Resource"
    patterns = statement[key]
    patterns = [patterns] if isinstance(patterns, str) else patterns
    hit = any(p == "*" or arn_like(resource, p) for p in patterns)
    return hit != (key == "NotResource")


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


def test_region_deny_exempts_only_us_inference_profile_routing() -> None:
    for name in ("deploy-policy.json", "app-permissions-boundary.json"):
        statement = policy(name)["DenyOtherRegionsExceptUSInferenceProfileRouting"]
        assert statement["Condition"] == {
            "StringNotEquals": {"aws:RequestedRegion": "REPLACE_WITH_SANDBOX_REGION"},
            "ArnNotLike": {"bedrock:InferenceProfileArn": US_PROFILES},
        }


def test_inference_profiles_are_an_allow_list_of_us_profiles() -> None:
    for name in ("deploy-policy.json", "app-permissions-boundary.json"):
        doc = policy(name)
        statement = doc["DenyInferenceProfilesOutsideTheUS"]
        assert statement["Effect"] == "Deny"
        assert statement["Condition"] == {
            "Null": {"bedrock:InferenceProfileArn": "false"},
            "ArnNotLike": {"bedrock:InferenceProfileArn": US_PROFILES},
        }
        # An allow-list, not a block-list: no statement names a non-US profile prefix.
        text = json.dumps(list(doc.values()))
        for prefix in ("global.", "eu.", "apac.", "jp.", "au.", "ca."):
            assert f"inference-profile/{prefix}" not in text, (name, prefix)


SANDBOX = "REPLACE_WITH_SANDBOX_REGION"


def profile_arn(region: str, profile: str) -> str:
    return f"arn:aws:bedrock:{region}:111122223333:inference-profile/{profile}"


@pytest.mark.parametrize("name", ["deploy-policy.json", "app-permissions-boundary.json"])
@pytest.mark.parametrize(("region", "profile_key", "denied"), [
    # A direct call to a foundation model, with no profile, is denied even in the sandbox region.
    (SANDBOX, None, True),
    # Any call outside the sandbox region without a profile key: denied.
    ("eu-west-1", None, True),
    # A US profile routing to another US region: allowed.
    ("us-west-2", profile_arn(SANDBOX, "us.anthropic.claude-sonnet-5"), False),
    (SANDBOX, profile_arn(SANDBOX, "us.anthropic.claude-opus-5-5"), False),
    # Every other profile prefix is denied, in or out of the sandbox region.
    ("eu-west-1", profile_arn(SANDBOX, "global.anthropic.claude-sonnet-5"), True),
    (SANDBOX, profile_arn(SANDBOX, "global.anthropic.claude-sonnet-5"), True),
    ("eu-central-1", profile_arn(SANDBOX, "eu.anthropic.claude-sonnet-5"), True),
    (SANDBOX, profile_arn(SANDBOX, "eu.anthropic.claude-sonnet-5"), True),
    ("ap-southeast-2", profile_arn(SANDBOX, "apac.anthropic.claude-sonnet-5"), True),
    (SANDBOX, profile_arn(SANDBOX, "apac.anthropic.claude-sonnet-5"), True),
    (SANDBOX, profile_arn(SANDBOX, "ca.anthropic.claude-sonnet-5"), True),
    # A profile whose id merely contains "us." is not a US profile.
    (SANDBOX, profile_arn(SANDBOX, "eu.us.anthropic.claude-sonnet-5"), True),
])
def test_model_invocation_is_denied_unless_routed_through_a_us_profile(
        name: str, region: str, profile_key: str | None, denied: bool) -> None:
    """The foundation-model evaluation AWS makes for each call (and, through a profile, for each
    destination region), with the profile key set only when the call goes through a profile."""
    context = {"aws:RequestedRegion": region}
    if profile_key is not None:
        context["bedrock:InferenceProfileArn"] = profile_key
    model = f"arn:aws:bedrock:{region}::foundation-model/anthropic.claude-sonnet-5"
    denies = [sid for sid, s in policy(name).items()
              if s["Effect"] == "Deny" and statement_covers(s, "bedrock:InvokeModel")
              and statement_names(s, model)
              and conditions_match(s.get("Condition", {}), context)]
    assert bool(denies) is denied, denies


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


@pytest.mark.parametrize("name", sorted(p.name for p in IAM.glob("*.json")))
def test_condition_keys_are_used_only_on_actions_that_support_them(name: str) -> None:
    """A statement that lists its actions conditions only on keys those actions carry. A
    NotAction statement (the region denies) is exempt: it relies on the key being absent."""
    for sid, statement in policy(name).items():
        if "NotAction" in statement:
            continue
        for operator, keys in statement.get("Condition", {}).items():
            for key in keys:
                if key.startswith("aws:"):
                    continue  # global keys
                supported = CONDITION_KEY_ACTIONS.get(key)
                assert supported is not None, f"{name} {sid}: add {key} to CONDITION_KEY_ACTIONS"
                unsupported = set(actions(statement)) - supported
                assert not unsupported, f"{name} {sid}: {key} is never set for {unsupported}"


def test_role_policy_changes_are_limited_to_app_roles_that_carry_the_boundary() -> None:
    deploy = policy("deploy-policy.json")
    role_policy_actions = {"iam:PutRolePolicy", "iam:DeleteRolePolicy", "iam:AttachRolePolicy",
                           "iam:DetachRolePolicy"}
    granting = [s for s in deploy.values() if s["Effect"] == "Allow"
                and role_policy_actions & set(actions(s))]
    assert granting, "the deploy role must be able to give its /app/ roles their policies"
    for statement in granting:
        assert statement["Resource"] == APP_ROLES
    # Outside /app/ every IAM change is denied, whatever the boundary.
    outside = deploy["DenyEveryIamChangeOutsideAppRoles"]
    assert outside["NotResource"] == APP_ROLES
    assert {"iam:Put*", "iam:Attach*", "iam:Detach*", "iam:Delete*"} <= set(actions(outside))


@pytest.mark.parametrize(("action", "boundary", "denied"), [
    ("iam:CreateRole", BOUNDARY, False),
    ("iam:CreateRole", None, True),
    ("iam:CreateRole", "arn:aws:iam::REPLACE_WITH_SANDBOX_ACCOUNT_ID:policy/other", True),
    ("iam:PutRolePermissionsBoundary", BOUNDARY, False),
    ("iam:PutRolePermissionsBoundary", "arn:aws:iam::aws:policy/AdministratorAccess", True),
    ("iam:AttachRolePolicy", BOUNDARY, False),
    ("iam:AttachRolePolicy", None, True),
    ("iam:PutRolePolicy", None, True),
    ("iam:DeleteRolePermissionsBoundary", BOUNDARY, True),
    ("iam:DeleteRolePermissionsBoundary", None, True),
])
def test_app_role_changes_on_an_app_role(action: str, boundary: str | None, denied: bool) -> None:
    """Evaluate the deploy policy's denies for an action on an /app/ role, with the boundary the
    request carries (CreateRole, PutRolePermissionsBoundary) or the role already has."""
    context = {} if boundary is None else {"iam:PermissionsBoundary": boundary}
    denies = [sid for sid, s in policy("deploy-policy.json").items()
              if s["Effect"] == "Deny" and statement_covers(s, action)
              and statement_names(s, "arn:aws:iam::111122223333:role/app/ClaimsStack-Role-1A2B")
              and conditions_match(s.get("Condition", {}), context)]
    assert bool(denies) is denied, denies


def test_read_role_decrypts_only_the_sandbox_tenant_keys() -> None:
    allow = policy("read-sandbox-data-policy.json")[
        "SandboxOnlyDecryptTenantDataThroughS3AndDynamoDB"]
    assert actions(allow) == ["kms:Decrypt"]
    assert allow["Resource"] == "arn:aws:kms:*:REPLACE_WITH_SANDBOX_ACCOUNT_ID:key/*"
    condition = allow["Condition"]
    assert condition["StringEquals"] == {"aws:ResourceAccount": "REPLACE_WITH_SANDBOX_ACCOUNT_ID"}
    assert condition["ForAnyValue:StringLike"] == {
        "kms:ResourceAliases": "alias/REPLACE_WITH_PRODUCT_NAME-tenant-*"}
    assert condition["StringLike"] == {
        "kms:ViaService": ["s3.*.amazonaws.com", "dynamodb.*.amazonaws.com"]}


def test_foundation_models_are_invoked_only_through_a_profile() -> None:
    for name in ("deploy-policy.json", "app-permissions-boundary.json"):
        statement = policy(name)["DenyDirectFoundationModelInvocation"]
        assert statement["Effect"] == "Deny"
        assert statement["Resource"] == "arn:aws:bedrock:*::foundation-model/*"
        assert statement["Condition"] == {"Null": {"bedrock:InferenceProfileArn": "true"}}
