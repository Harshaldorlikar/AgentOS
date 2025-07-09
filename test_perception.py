from tools.perception_controller import PerceptionController
import json

snapshot = PerceptionController.get_perception_snapshot()

# Print a readable view of what the agent sees
print(json.dumps(snapshot, indent=2, ensure_ascii=False))
