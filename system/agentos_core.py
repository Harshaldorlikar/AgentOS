# system/agentos_core.py

from agents.supervisor import SupervisorAgent
from tools.runtime_controller import RuntimeController

class AgentOSCore:
    def __init__(self):
        self.supervisor = SupervisorAgent()

    def request_action(self, agent, action_type, target=None, reason="", data=None):
        # Ask supervisor for approval
        approved = self.supervisor.approve_action(agent, action_type, target or "", reason)
        if not approved:
            print(f"[AgentOSCore] ❌ Supervisor blocked {action_type}")
            return False

        print(f"[AgentOSCore] ✅ Executing {action_type} for {agent} → {target}")

        try:
            # === Apps & Browser ===
            if action_type == "open_app":
                RuntimeController.open_app(target, reason)

            elif action_type in ["browse", "open_browser"]:
                RuntimeController.browse(target, reason)

            # === Typing & Keyboard ===
            elif action_type == "type_text":
                RuntimeController.type_text(target, reason)

            elif action_type == "press_key":
                RuntimeController.press_key(target, reason)

            # === Mouse Clicks ===
            elif action_type in ["click", "click_mouse"]:
                if isinstance(target, str) and "," in target:
                    x, y = map(int, target.split(","))
                elif isinstance(target, (list, tuple)) and len(target) == 2:
                    x, y = target
                else:
                    raise ValueError("Invalid target for click. Expected 'x,y' string or [x, y] tuple.")

                print(f"[AgentOSCore] 🖱️ Clicking at coordinates: ({x},{y})")
                RuntimeController.click(x, y, reason)

            # === Screenshot ===
            elif action_type == "screenshot":
                RuntimeController.screenshot(target, reason)

            # === Posting (simulated) ===
            elif action_type == "post_tweet":
                print(f"[AgentOSCore] ✍️ Tweet posted: {data}")

            else:
                print(f"[AgentOSCore] ❌ Unknown action_type: {action_type}")
                return False

        except Exception as e:
            print(f"[AgentOSCore] ❌ Failed to execute {action_type}: {e}")
            return False

        return True
