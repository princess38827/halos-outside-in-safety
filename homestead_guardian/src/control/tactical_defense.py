"""
Asimov-Law-Constrained Defensive Tactical Skills
=================================================

All decisions made by this module are governed by Asimov's Three Laws of
Robotics (and the implicit Zeroth Law as a guardian context):

  0. (Zeroth)  A robot may not harm humanity, or through inaction allow
               humanity to come to harm.
  1. (First)   A robot may not injure a human being, or through inaction
               allow a human being to come to harm — EXCEPT where such
               action would conflict with the Zeroth Law.
  2. (Second)  A robot must obey orders given by human beings except where
               such orders would conflict with the First or Zeroth Law.
  3. (Third)   A robot must protect its own existence as long as such
               protection does not conflict with the First or Zeroth Law.

Defensive tactics are therefore STRICTLY non-lethal, non-injurious, and
oriented toward de-escalation, evasion, and alerting human responders.
Any action that could injure a human is vetoed automatically.
"""

from enum import Enum, auto


# ---------------------------------------------------------------------------
# Threat classification
# ---------------------------------------------------------------------------

class ThreatLevel(Enum):
    NONE = auto()
    LOW = auto()       # Suspicious presence, no immediate danger
    MEDIUM = auto()    # Approaching fast / unknown intent
    HIGH = auto()      # Imminent physical threat


# ---------------------------------------------------------------------------
# Asimov compliance gate
# ---------------------------------------------------------------------------

class AsimovVeto(Exception):
    """Raised when a requested action violates an Asimov Law."""


def asimov_check(action: str, could_injure_human: bool) -> None:
    """
    Gate that enforces the Laws before any action is executed.
    Raises AsimovVeto if the action violates a Law.
    """
    if could_injure_human:
        raise AsimovVeto(
            f"Action '{action}' vetoed — violates First Law "
            "(may not injure a human being)."
        )


# ---------------------------------------------------------------------------
# Defensive tactics
# ---------------------------------------------------------------------------

class DefensiveTacticalSkills:
    """
    Non-lethal, Asimov-compliant defensive and survival skills for the
    Homestead Guardian robot.

    All offensive or injurious responses are automatically blocked.
    The available tactics escalate from passive to active-evasive:

      1. Alert        — broadcast alarm and notify human operators
      2. Illuminate   — activate high-intensity lights to deter / disorient
      3. Vocalise     — emit verbal warnings and siren
      4. Retreat       — move to a safe waypoint via GPS
      5. Shield       — place non-injurious physical barrier (smoke/fog only)
      6. Lock-down    — secure area doors / gates, call emergency services

    Tactics that could injure humans (e.g. electric shock, projectile)
    are explicitly absent and will raise AsimovVeto if attempted.
    """

    TACTIC_MATRIX = {
        ThreatLevel.NONE:   [],
        ThreatLevel.LOW:    ["alert", "illuminate"],
        ThreatLevel.MEDIUM: ["alert", "illuminate", "vocalise", "retreat"],
        ThreatLevel.HIGH:   ["alert", "illuminate", "vocalise", "retreat",
                             "shield", "lock_down"],
    }

    def __init__(self, robot_id: str = "guardian_001"):
        self.robot_id = robot_id
        self.active_tactics: list[str] = []
        self.action_log: list[dict] = []

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def assess_and_respond(self, threat_level: ThreatLevel,
                           threat_description: str = "") -> list[str]:
        """
        Given a threat level, selects and executes all appropriate tactics.
        Returns the list of tactics that were executed.
        """
        tactics = self.TACTIC_MATRIX.get(threat_level, [])
        executed = []
        for tactic in tactics:
            try:
                self._execute(tactic, threat_level, threat_description)
                executed.append(tactic)
            except AsimovVeto as e:
                self._log(tactic, vetoed=True, reason=str(e))
                print(f"  [VETO] {e}")
        self.active_tactics = executed
        return executed

    def request_custom_action(self, action: str,
                              could_injure_human: bool = False) -> str:
        """
        Allows external code to request an arbitrary action.
        Will be vetoed if it could injure a human (First Law).
        """
        try:
            asimov_check(action, could_injure_human)
            self._log(action, vetoed=False)
            print(f"  [ACTION] '{action}' approved and executed.")
            return "executed"
        except AsimovVeto as e:
            self._log(action, vetoed=True, reason=str(e))
            print(f"  [VETO] {e}")
            return "vetoed"

    def stand_down(self) -> None:
        """Cancels all active tactics and returns to idle."""
        print(f"  [{self.robot_id}] Standing down — all tactics cancelled.")
        self.active_tactics = []

    # ------------------------------------------------------------------
    # Individual tactic implementations
    # ------------------------------------------------------------------

    def _execute(self, tactic: str, threat_level: ThreatLevel,
                 description: str) -> None:
        # All tactics here are explicitly non-injurious to humans.
        asimov_check(tactic, could_injure_human=False)

        handlers = {
            "alert":      self._tactic_alert,
            "illuminate": self._tactic_illuminate,
            "vocalise":   self._tactic_vocalise,
            "retreat":    self._tactic_retreat,
            "shield":     self._tactic_shield,
            "lock_down":  self._tactic_lock_down,
        }
        handler = handlers.get(tactic)
        if handler:
            handler(threat_level, description)
        self._log(tactic, vetoed=False)

    def _tactic_alert(self, threat_level: ThreatLevel, description: str) -> None:
        print(f"  [ALERT] Broadcasting threat level {threat_level.name} "
              f"to human operators. Detail: '{description or 'N/A'}'")

    def _tactic_illuminate(self, threat_level: ThreatLevel, _: str) -> None:
        intensity = {ThreatLevel.LOW: 50, ThreatLevel.MEDIUM: 80,
                     ThreatLevel.HIGH: 100}.get(threat_level, 50)
        print(f"  [ILLUMINATE] Activating perimeter lights at {intensity}% — "
              "non-injurious deterrent only.")

    def _tactic_vocalise(self, _: ThreatLevel, __: str) -> None:
        print("  [VOCALISE] 'WARNING: You are in a monitored safety zone. "
              "Please identify yourself or withdraw. Human responders alerted.'")

    def _tactic_retreat(self, _: ThreatLevel, __: str) -> None:
        print("  [RETREAT] Navigating to designated safe waypoint via GPS — "
              "preserving own existence (Third Law), no human obstruction.")

    def _tactic_shield(self, _: ThreatLevel, __: str) -> None:
        print("  [SHIELD] Deploying non-injurious smoke/fog barrier — "
              "creates visual obstruction only; no chemical harm to humans.")

    def _tactic_lock_down(self, _: ThreatLevel, __: str) -> None:
        print("  [LOCK-DOWN] Securing perimeter gates and contacting "
              "emergency services. Human responders dispatched.")

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    def _log(self, action: str, vetoed: bool, reason: str = "") -> None:
        import time
        self.action_log.append({
            "action": action,
            "vetoed": vetoed,
            "reason": reason,
            "timestamp": time.time(),
        })


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== Homestead Guardian — Asimov-Compliant Defensive Tactics Demo ===\n")

    skills = DefensiveTacticalSkills(robot_id="guardian_001")

    for level, desc in [
        (ThreatLevel.NONE,   "All clear"),
        (ThreatLevel.LOW,    "Unknown entity detected near perimeter"),
        (ThreatLevel.MEDIUM, "Fast-approaching unidentified individual"),
        (ThreatLevel.HIGH,   "Imminent physical threat detected"),
    ]:
        print(f"\n--- Threat: {level.name} | {desc} ---")
        executed = skills.assess_and_respond(level, desc)
        print(f"  Tactics executed: {executed or ['none']}")

    print("\n--- Attempting a vetoed (injurious) action ---")
    skills.request_custom_action("deploy_electric_shock", could_injure_human=True)

    print("\n--- Attempting a safe custom action ---")
    skills.request_custom_action("increase_patrol_frequency", could_injure_human=False)

    print("\n--- Standing down ---")
    skills.stand_down()
