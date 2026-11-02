"""Read the pilot policy from trusted consumer settings; serialize safe action inputs."""
import json
import os
import sys
from pathlib import Path

policy = json.loads(Path(sys.argv[1]).read_bytes())
expected = json.loads(Path(__file__).with_name("barista-policy.json").read_bytes())
# This bounded pilot exercises a known allowlist. Reject configuration drift, including disabled skills.
for key in expected:
    if policy.get(key) != expected[key]:
        sys.exit(f"Consumer {key} differs from reviewed Barista pilot policy")
bc = policy["BCQuality"]
with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as out:
    for key, values in {"layers":bc["enabledLayers"],"disabled":bc["disabledSkills"],
                        "allow":bc["knowledge"]["allow"],"deny":bc["knowledge"]["deny"]}.items():
        print(f"{key}={','.join(values)}", file=out)
    print("ref=" + policy["KnowledgeAdvisorPilot"]["marketplaceRef"], file=out)
