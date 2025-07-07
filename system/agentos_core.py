# system/agentos_core.py

import subprocess
import pyautogui
import time
from agents.supervisor import SupervisorAgent

class AgentOSCore:
    def __init__(self):
        self.supervisor = SupervisorAgent()

    def request_action(self, agent, action_type, target=None, reason=""):
        decision = self.supervisor.approve_action(agent, action_type, target or "", reason)
        if not decision:
            print(f"[AgentOSCore] Supervisor blocked {action_type}")
            return False

        print(f"[AgentOSCore] Executing {action_type} for {agent}")

        if action_type == "open_browser":
            return self._open_browser(target)

        if action_type == "type_text":
            return self._type_text(target)

        if action_type == "move_mouse":
            return self._move_mouse(*target)

        if action_type == "click_mouse":
            return self._click_mouse()

        print(f"[AgentOSCore] Unknown action: {action_type}")
        return False

    def _open_browser(self, url):
        try:
            subprocess.Popen(["start", "chrome", url], shell=True)
            return True
        except Exception as e:
            print(f"[AgentOSCore] Failed to open browser: {e}")
            return False

    def _type_text(self, text):
        pyautogui.write(text, interval=0.04)
        return True

    def _move_mouse(self, x, y):
        pyautogui.moveTo(x, y, duration=0.3)
        return True

    def _click_mouse(self):
        pyautogui.click()
        return True
