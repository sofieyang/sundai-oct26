import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict

# Add project root to path so we can import agents
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.marketing_agency import build_marketing_pipeline

logger = logging.getLogger(__name__)


def run_pipeline(brief: str) -> Dict[str, Any]:
    pipeline = build_marketing_pipeline()

    # Prepare inputs and defaults
    inputs = {"brief": brief}
    defaults = {
        "brand": "Acme Bio",
        "region": "US",
        "objective": "Generate HCP awareness",
    }

    print("\n=== Launching Marketing Agency Pipeline ===")
    print("Brief:\n" + brief)
    print("Defaults:\n" + json.dumps(defaults, indent=2))

    result = pipeline.run({
        "inputs": inputs,
        "pipeline": {
            "defaults": defaults,
        }
    })

    print("Pipeline run completed.")
    print("Result:")
    print(json.dumps(result, indent=2))
    logger.info("=== Pipeline Completed ===")
    logger.info(json.dumps(result, indent=2))


    print("\n=== Pipeline Completed ===")
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    demo_brief = (
        "Launch campaign for NewThera in moderate-to-severe condition X. Primary audience: HCPs.\n"
        "Key value props: rapid onset, favorable safety. Avoid overpromising; include safety."
    )
    run_pipeline(demo_brief)


