# system/agentos_core.py

from agents.supervisor import SupervisorAgent
from tools.runtime_controller import RuntimeController

class AgentOSCore:
    def __init__(self):
        self.supervisor = SupervisorAgent()

    def request_action(self, agent, action_type, target=None, reason="", data=None):
        # Ask supervisor for approval
        decision = self.supervisor.approve_action(agent, action_type, target or "", reason)
        if not decision:
            print(f"[AgentOSCore] ❌ Supervisor blocked {action_type}")
            return False

        print(f"[AgentOSCore] ✅ Executing {action_type} for {agent} → {target}")

        # Dispatch actions to RuntimeController
        try:
            if action_type == "open_app":
                RuntimeController.open_app(target, reason)

            elif action_type == "browse" or action_type == "open_browser":
                RuntimeController.browse(target, reason)

            elif action_type == "type_text":
                RuntimeController.type_text(target, reason)

            elif action_type == "click":
                if isinstance(target, str) and "," in target:
                    x, y = map(int, target.split(","))
                elif isinstance(target, (list, tuple)) and len(target) == 2:
                    x, y = target
                else:
                    raise ValueError("Invalid target for click. Expected 'x,y' string or [x, y] list.")
                RuntimeController.click(x, y, reason)

            elif action_type == "screenshot":
                RuntimeController.screenshot(target, reason)

            elif action_type == "post_tweet":
                # Simulated log for now
                print(f"[AgentOSCore] ✍️ Tweet posted: {data}")

            else:
                print(f"[AgentOSCore] ❌ Unknown action_type: {action_type}")
                return False

        except Exception as e:
            print(f"[AgentOSCore] ❌ Failed to execute {action_type}: {e}")
            return False

        return True
