# Brain drafts: hackathon product

Drafts of second-brain entries for the Bidirectional Integrity product, written from ARCH-002 and
Figure 4 only. None is recorded yet. Each file has the front matter `brain.py new` would write,
except `author`, which is the placeholder `<handle>`.

| Kind | Title | Path |
|---|---|---|
| concept | Determination | [concepts/determination.md](concepts/determination.md) |
| concept | Improper payment | [concepts/improper-payment.md](concepts/improper-payment.md) |
| concept | Improper denial | [concepts/improper-denial.md](concepts/improper-denial.md) |
| concept | DOL (U.S. Department of Labor) | [concepts/dol-u-s-department-of-labor.md](concepts/dol-u-s-department-of-labor.md) |
| concept | BAM (Benefit Accuracy Measurement) | [concepts/bam-benefit-accuracy-measurement.md](concepts/bam-benefit-accuracy-measurement.md) |
| concept | Appeal-board decision | [concepts/appeal-board-decision.md](concepts/appeal-board-decision.md) |
| entity | Amazon S3 | [entities/amazon-s3.md](entities/amazon-s3.md) |
| entity | Amazon Textract | [entities/amazon-textract.md](entities/amazon-textract.md) |
| entity | Amazon OpenSearch Serverless | [entities/amazon-opensearch-serverless.md](entities/amazon-opensearch-serverless.md) |
| entity | Amazon Bedrock | [entities/amazon-bedrock.md](entities/amazon-bedrock.md) |
| entity | Bedrock Knowledge Bases | [entities/bedrock-knowledge-bases.md](entities/bedrock-knowledge-bases.md) |
| entity | Amazon DynamoDB | [entities/amazon-dynamodb.md](entities/amazon-dynamodb.md) |
| entity | AWS Step Functions | [entities/aws-step-functions.md](entities/aws-step-functions.md) |
| entity | Bedrock Guardrails | [entities/bedrock-guardrails.md](entities/bedrock-guardrails.md) |
| entity | AWS CloudTrail | [entities/aws-cloudtrail.md](entities/aws-cloudtrail.md) |
| entity | AWS IAM | [entities/aws-iam.md](entities/aws-iam.md) |
| entity | Amazon VPC | [entities/amazon-vpc.md](entities/amazon-vpc.md) |
| entity | AWS KMS | [entities/aws-kms.md](entities/aws-kms.md) |
| entity | AWS PrivateLink | [entities/aws-privatelink.md](entities/aws-privatelink.md) |
| entity | Amazon Cognito | [entities/amazon-cognito.md](entities/amazon-cognito.md) |
| entity | Case Synthesis agent | [entities/case-synthesis-agent.md](entities/case-synthesis-agent.md) |
| entity | Statutory Application agent | [entities/statutory-application-agent.md](entities/statutory-application-agent.md) |
| entity | Bidirectional Flagging agent | [entities/bidirectional-flagging-agent.md](entities/bidirectional-flagging-agent.md) |
| entity | Notice Drafting agent | [entities/notice-drafting-agent.md](entities/notice-drafting-agent.md) |
| concept | The model reports; code decides | [concepts/the-model-reports-code-decides.md](concepts/the-model-reports-code-decides.md) |
| concept | The examiner decides, always | [concepts/the-examiner-decides-always.md](concepts/the-examiner-decides-always.md) |
| concept | Bidirectional flagging: both error directions | [concepts/bidirectional-flagging-both-error-directions.md](concepts/bidirectional-flagging-both-error-directions.md) |
| concept | Measured accuracy loop against the always-affirmed baseline | [concepts/measured-accuracy-loop-against-the-always-affirmed-baseline.md](concepts/measured-accuracy-loop-against-the-always-affirmed-baseline.md) |

## Recording

Run every command from the control repository root, with `IDEA_REALIZATION_ROOT` set to that root,
after the developer is registered in `docs/systems.yaml` (the author is that developer's handle,
from their git email). Then commit the new entry files together with `brain/index.md`, which
`brain.py new` regenerates on each call.

`--body -` reads standard input as the whole body, so the input must be the body only: each command
below strips the front matter with `sed '1,/^---$/d'` (deletes line 1 through the closing `---`).
`brain.py new` writes its own front matter, sets `created` and `updated` to the day it runs, and
derives the same id from the title. Every `--links` id must already exist, so record in this order:

```bash
export IDEA_REALIZATION_ROOT="$(pwd)"
DRAFTS=<path to this export>/owner-files/brain-drafts
```

1. `determination`

   ```bash
   sed '1,/^---$/d' "$DRAFTS/concepts/determination.md" | uv run plugins/idea-realization/scripts/brain.py new concept --title "Determination" --body - --tags glossary,unemployment-insurance --sources "ARCH-002,Figure 4"
   ```

2. `improper-payment`

   ```bash
   sed '1,/^---$/d' "$DRAFTS/concepts/improper-payment.md" | uv run plugins/idea-realization/scripts/brain.py new concept --title "Improper payment" --body - --tags glossary,unemployment-insurance --sources "ARCH-002,Figure 4"
   ```

3. `improper-denial`

   ```bash
   sed '1,/^---$/d' "$DRAFTS/concepts/improper-denial.md" | uv run plugins/idea-realization/scripts/brain.py new concept --title "Improper denial" --body - --tags glossary,unemployment-insurance --links improper-payment --sources "ARCH-002,Figure 4"
   ```

4. `dol-u-s-department-of-labor`

   ```bash
   sed '1,/^---$/d' "$DRAFTS/concepts/dol-u-s-department-of-labor.md" | uv run plugins/idea-realization/scripts/brain.py new concept --title "DOL (U.S. Department of Labor)" --body - --tags glossary,unemployment-insurance --sources "ARCH-002,Figure 4"
   ```

5. `bam-benefit-accuracy-measurement`

   ```bash
   sed '1,/^---$/d' "$DRAFTS/concepts/bam-benefit-accuracy-measurement.md" | uv run plugins/idea-realization/scripts/brain.py new concept --title "BAM (Benefit Accuracy Measurement)" --body - --tags glossary,unemployment-insurance --links dol-u-s-department-of-labor,improper-denial --sources "ARCH-002,Figure 4"
   ```

6. `appeal-board-decision`

   ```bash
   sed '1,/^---$/d' "$DRAFTS/concepts/appeal-board-decision.md" | uv run plugins/idea-realization/scripts/brain.py new concept --title "Appeal-board decision" --body - --tags glossary,unemployment-insurance --links dol-u-s-department-of-labor --sources "ARCH-002,Figure 4"
   ```

7. `amazon-s3`

   ```bash
   sed '1,/^---$/d' "$DRAFTS/entities/amazon-s3.md" | uv run plugins/idea-realization/scripts/brain.py new entity --title "Amazon S3" --body - --tags aws,data-layer --sources "ARCH-002,Figure 4"
   ```

8. `amazon-textract`

   ```bash
   sed '1,/^---$/d' "$DRAFTS/entities/amazon-textract.md" | uv run plugins/idea-realization/scripts/brain.py new entity --title "Amazon Textract" --body - --tags aws,data-layer --sources "ARCH-002,Figure 4"
   ```

9. `amazon-opensearch-serverless`

   ```bash
   sed '1,/^---$/d' "$DRAFTS/entities/amazon-opensearch-serverless.md" | uv run plugins/idea-realization/scripts/brain.py new entity --title "Amazon OpenSearch Serverless" --body - --tags aws,data-layer --sources "ARCH-002,Figure 4"
   ```

10. `amazon-bedrock`

   ```bash
   sed '1,/^---$/d' "$DRAFTS/entities/amazon-bedrock.md" | uv run plugins/idea-realization/scripts/brain.py new entity --title "Amazon Bedrock" --body - --tags aws,reasoning-core --sources "ARCH-002,Figure 4"
   ```

11. `bedrock-knowledge-bases`

   ```bash
   sed '1,/^---$/d' "$DRAFTS/entities/bedrock-knowledge-bases.md" | uv run plugins/idea-realization/scripts/brain.py new entity --title "Bedrock Knowledge Bases" --body - --tags aws,data-layer --links amazon-opensearch-serverless,amazon-bedrock --sources "ARCH-002,Figure 4"
   ```

12. `amazon-dynamodb`

   ```bash
   sed '1,/^---$/d' "$DRAFTS/entities/amazon-dynamodb.md" | uv run plugins/idea-realization/scripts/brain.py new entity --title "Amazon DynamoDB" --body - --tags aws,data-layer --sources "ARCH-002,Figure 4"
   ```

13. `aws-step-functions`

   ```bash
   sed '1,/^---$/d' "$DRAFTS/entities/aws-step-functions.md" | uv run plugins/idea-realization/scripts/brain.py new entity --title "AWS Step Functions" --body - --tags aws,reasoning-core --sources "ARCH-002,Figure 4"
   ```

14. `bedrock-guardrails`

   ```bash
   sed '1,/^---$/d' "$DRAFTS/entities/bedrock-guardrails.md" | uv run plugins/idea-realization/scripts/brain.py new entity --title "Bedrock Guardrails" --body - --tags aws,governance --links amazon-bedrock --sources "ARCH-002,Figure 4"
   ```

15. `aws-cloudtrail`

   ```bash
   sed '1,/^---$/d' "$DRAFTS/entities/aws-cloudtrail.md" | uv run plugins/idea-realization/scripts/brain.py new entity --title "AWS CloudTrail" --body - --tags aws,governance --sources "ARCH-002,Figure 4"
   ```

16. `aws-iam`

   ```bash
   sed '1,/^---$/d' "$DRAFTS/entities/aws-iam.md" | uv run plugins/idea-realization/scripts/brain.py new entity --title "AWS IAM" --body - --tags aws,governance --sources "ARCH-002,Figure 4"
   ```

17. `amazon-vpc`

   ```bash
   sed '1,/^---$/d' "$DRAFTS/entities/amazon-vpc.md" | uv run plugins/idea-realization/scripts/brain.py new entity --title "Amazon VPC" --body - --tags aws,governance --sources "ARCH-002,Figure 4"
   ```

18. `aws-kms`

   ```bash
   sed '1,/^---$/d' "$DRAFTS/entities/aws-kms.md" | uv run plugins/idea-realization/scripts/brain.py new entity --title "AWS KMS" --body - --tags aws,governance --links amazon-vpc --sources "ARCH-002,Figure 4"
   ```

19. `aws-privatelink`

   ```bash
   sed '1,/^---$/d' "$DRAFTS/entities/aws-privatelink.md" | uv run plugins/idea-realization/scripts/brain.py new entity --title "AWS PrivateLink" --body - --tags aws,governance --sources "ARCH-002,Figure 4"
   ```

20. `amazon-cognito`

   ```bash
   sed '1,/^---$/d' "$DRAFTS/entities/amazon-cognito.md" | uv run plugins/idea-realization/scripts/brain.py new entity --title "Amazon Cognito" --body - --tags aws,governance --links aws-privatelink --sources "ARCH-002,Figure 4"
   ```

21. `case-synthesis-agent`

   ```bash
   sed '1,/^---$/d' "$DRAFTS/entities/case-synthesis-agent.md" | uv run plugins/idea-realization/scripts/brain.py new entity --title "Case Synthesis agent" --body - --tags agent,reasoning-core --links amazon-bedrock,bedrock-guardrails --sources "ARCH-002,Figure 4"
   ```

22. `statutory-application-agent`

   ```bash
   sed '1,/^---$/d' "$DRAFTS/entities/statutory-application-agent.md" | uv run plugins/idea-realization/scripts/brain.py new entity --title "Statutory Application agent" --body - --tags agent,reasoning-core --links amazon-bedrock,bedrock-guardrails,bedrock-knowledge-bases --sources "ARCH-002,Figure 4"
   ```

23. `bidirectional-flagging-agent`

   ```bash
   sed '1,/^---$/d' "$DRAFTS/entities/bidirectional-flagging-agent.md" | uv run plugins/idea-realization/scripts/brain.py new entity --title "Bidirectional Flagging agent" --body - --tags agent,reasoning-core --links amazon-bedrock,bedrock-guardrails,improper-payment,improper-denial --sources "ARCH-002,Figure 4"
   ```

24. `notice-drafting-agent`

   ```bash
   sed '1,/^---$/d' "$DRAFTS/entities/notice-drafting-agent.md" | uv run plugins/idea-realization/scripts/brain.py new entity --title "Notice Drafting agent" --body - --tags agent,reasoning-core --links amazon-bedrock,bedrock-guardrails --sources "ARCH-002,Figure 4"
   ```

25. `the-model-reports-code-decides`

   ```bash
   sed '1,/^---$/d' "$DRAFTS/concepts/the-model-reports-code-decides.md" | uv run plugins/idea-realization/scripts/brain.py new concept --title "The model reports; code decides" --body - --tags principle,reasoning-core --links aws-step-functions,case-synthesis-agent,statutory-application-agent,bidirectional-flagging-agent,notice-drafting-agent --sources "ARCH-002,Figure 4"
   ```

26. `the-examiner-decides-always`

   ```bash
   sed '1,/^---$/d' "$DRAFTS/concepts/the-examiner-decides-always.md" | uv run plugins/idea-realization/scripts/brain.py new concept --title "The examiner decides, always" --body - --tags principle,human-decision --links determination,the-model-reports-code-decides --sources "ARCH-002,Figure 4"
   ```

27. `bidirectional-flagging-both-error-directions`

   ```bash
   sed '1,/^---$/d' "$DRAFTS/concepts/bidirectional-flagging-both-error-directions.md" | uv run plugins/idea-realization/scripts/brain.py new concept --title "Bidirectional flagging: both error directions" --body - --tags principle,reasoning-core --links bidirectional-flagging-agent,improper-payment,improper-denial --sources "ARCH-002,Figure 4"
   ```

28. `measured-accuracy-loop-against-the-always-affirmed-baseline`

   ```bash
   sed '1,/^---$/d' "$DRAFTS/concepts/measured-accuracy-loop-against-the-always-affirmed-baseline.md" | uv run plugins/idea-realization/scripts/brain.py new concept --title "Measured accuracy loop against the always-affirmed baseline" --body - --tags principle,human-decision,validation --links appeal-board-decision,bam-benefit-accuracy-measurement,dol-u-s-department-of-labor --sources "ARCH-002,Figure 4"
   ```

Finish with `uv run plugins/idea-realization/scripts/brain.py check`, then commit.
