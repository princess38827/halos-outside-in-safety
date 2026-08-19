"""
Sympathy Towards Humans
=======================

This module gives the Homestead Guardian the ability to detect human
emotional states and respond with appropriate sympathetic behaviours.

Design principles
-----------------
* Non-intrusive — the robot never overrides a human's autonomy or decision.
* Transparent   — every sympathetic action is logged and can be reviewed.
* Calibrated    — sympathy level scales continuously with detected distress;
                   the robot does not assume the worst.
* Asimov-safe   — all responses here are purely supportive; no physical
                   action is taken without human consent.
"""

from enum import Enum, auto


# ---------------------------------------------------------------------------
# Emotional state classification
# ---------------------------------------------------------------------------

class HumanEmotionalState(Enum):
    CONTENT      = auto()   # Calm, positive
    NEUTRAL      = auto()   # Baseline — no strong signal
    UNEASY       = auto()   # Mild discomfort or anxiety
    DISTRESSED   = auto()   # Clear signs of distress
    CRISIS       = auto()   # Acute emergency (injury, panic, medical)


# ---------------------------------------------------------------------------
# Sympathy response catalogue
# ---------------------------------------------------------------------------

SYMPATHY_RESPONSES = {
    HumanEmotionalState.CONTENT: {
        "verbal":   "I'm glad you're doing well. I'm here if you need anything.",
        "gesture":  "gentle_wave",
        "action":   None,
    },
    HumanEmotionalState.NEUTRAL: {
        "verbal":   "Hello. Is there anything I can help you with?",
        "gesture":  "attentive_stance",
        "action":   None,
    },
    HumanEmotionalState.UNEASY: {
        "verbal":   (
            "I notice you seem a little uneasy. "
            "I'm here with you — please let me know if I can help."
        ),
        "gesture":  "open_posture",
        "action":   "reduce_movement_speed",
    },
    HumanEmotionalState.DISTRESSED: {
        "verbal":   (
            "I can see you're having a hard time right now. "
            "You're not alone — I'm alerting a human caretaker to come assist you."
        ),
        "gesture":  "approach_slowly",
        "action":   "notify_caretaker",
    },
    HumanEmotionalState.CRISIS: {
        "verbal":   (
            "I'm here. Help is on the way — I've already contacted emergency services. "
            "Please stay calm; you are safe."
        ),
        "gesture":  "stay_close_non_contact",
        "action":   "call_emergency_services",
    },
}


# ---------------------------------------------------------------------------
# Sympathy engine
# ---------------------------------------------------------------------------

class SympathyEngine:
    """
    Detects a human's emotional state from sensor cues and produces
    calibrated sympathetic responses.

    In a real deployment the ``detect_state`` method would consume output
    from a facial-expression classifier, voice-tone analyser, or the
    AetheraAffectiveEngine.  Here a simple rule-based mapping over raw
    sensor cues is used for simulation.
    """

    def __init__(self, robot_id: str = "guardian_001"):
        self.robot_id = robot_id
        self.last_state: HumanEmotionalState = HumanEmotionalState.NEUTRAL
        self.interaction_log: list[dict] = []

    # ------------------------------------------------------------------
    # State detection
    # ------------------------------------------------------------------

    def detect_state(self, cues: dict) -> HumanEmotionalState:
        """
        Maps raw sensor cues to a HumanEmotionalState.

        Expected cue keys (all optional, defaults are neutral):
          - ``heart_rate``    (int, bpm)        — elevated = distress
          - ``voice_tone``    (str)              — "calm" | "shaky" | "crying" | "screaming"
          - ``facial_expr``   (str)              — "happy" | "neutral" | "sad" | "fearful" | "pained"
          - ``body_language`` (str)              — "relaxed" | "tense" | "collapsed"
          - ``self_report``   (str)              — free text override: "fine" | "uneasy" |
                                                   "distressed" | "crisis"
        """
        # Self-report takes highest priority
        sr = cues.get("self_report", "").lower()
        if sr == "crisis":
            return HumanEmotionalState.CRISIS
        if sr == "distressed":
            return HumanEmotionalState.DISTRESSED
        if sr == "uneasy":
            return HumanEmotionalState.UNEASY
        if sr == "fine":
            return HumanEmotionalState.CONTENT

        score = 0  # higher = more distress

        hr = cues.get("heart_rate", 70)
        if hr > 120:
            score += 3
        elif hr > 100:
            score += 2
        elif hr > 85:
            score += 1

        voice = cues.get("voice_tone", "calm")
        score += {"calm": 0, "shaky": 1, "crying": 2, "screaming": 3}.get(voice, 0)

        face = cues.get("facial_expr", "neutral")
        score += {"happy": -1, "neutral": 0, "sad": 1, "fearful": 2, "pained": 3}.get(face, 0)

        body = cues.get("body_language", "relaxed")
        score += {"relaxed": 0, "tense": 1, "collapsed": 3}.get(body, 0)

        if score <= -1:
            state = HumanEmotionalState.CONTENT
        elif score <= 1:
            state = HumanEmotionalState.NEUTRAL
        elif score <= 3:
            state = HumanEmotionalState.UNEASY
        elif score <= 6:
            state = HumanEmotionalState.DISTRESSED
        else:
            state = HumanEmotionalState.CRISIS

        self.last_state = state
        return state

    # ------------------------------------------------------------------
    # Response generation
    # ------------------------------------------------------------------

    def respond(self, state: HumanEmotionalState,
                human_id: str = "unknown") -> dict:
        """
        Generates and 'executes' a sympathetic response for the detected state.
        Returns the full response dict and appends to the interaction log.
        """
        response = SYMPATHY_RESPONSES[state].copy()
        response["state"] = state.name
        response["human_id"] = human_id

        self._execute_response(state, response)
        self._log(human_id, state, response)
        return response

    def perceive_and_respond(self, cues: dict,
                             human_id: str = "unknown") -> dict:
        """Convenience wrapper: detect state then respond in one call."""
        state = self.detect_state(cues)
        return self.respond(state, human_id)

    # ------------------------------------------------------------------
    # Action dispatch
    # ------------------------------------------------------------------

    def _execute_response(self, state: HumanEmotionalState,
                          response: dict) -> None:
        print(f"\n[{self.robot_id}] Detected human state: {state.name}")
        print(f"  Verbal  : \"{response['verbal']}\"")
        print(f"  Gesture : {response['gesture']}")
        if response["action"]:
            print(f"  Action  : {response['action']}")
            self._dispatch_action(response["action"])

    def _dispatch_action(self, action: str) -> None:
        handlers = {
            "reduce_movement_speed":    lambda: print("  >> Reducing locomotion speed for comfort."),
            "notify_caretaker":         lambda: print("  >> Sending alert to human caretaker."),
            "call_emergency_services":  lambda: print("  >> Contacting emergency services immediately."),
        }
        handler = handlers.get(action)
        if handler:
            handler()
        else:
            print(f"  >> Executing: {action}")

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    def _log(self, human_id: str, state: HumanEmotionalState,
             response: dict) -> None:
        import time
        self.interaction_log.append({
            "human_id": human_id,
            "state": state.name,
            "verbal": response["verbal"],
            "gesture": response["gesture"],
            "action": response["action"],
            "timestamp": time.time(),
        })


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== Homestead Guardian — Sympathy Engine Demo ===")

    engine = SympathyEngine(robot_id="guardian_001")

    scenarios = [
        ("alice",   {"heart_rate": 65,  "voice_tone": "calm",     "facial_expr": "happy",   "body_language": "relaxed"}),
        ("bob",     {"heart_rate": 75,  "voice_tone": "calm",     "facial_expr": "neutral",  "body_language": "relaxed"}),
        ("carol",   {"heart_rate": 95,  "voice_tone": "shaky",    "facial_expr": "sad",      "body_language": "tense"}),
        ("dave",    {"heart_rate": 115, "voice_tone": "crying",   "facial_expr": "fearful",  "body_language": "tense"}),
        ("eve",     {"heart_rate": 140, "voice_tone": "screaming","facial_expr": "pained",   "body_language": "collapsed"}),
        ("frank",   {"self_report": "distressed"}),
    ]

    for human_id, cues in scenarios:
        engine.perceive_and_respond(cues, human_id=human_id)

    print(f"\n--- Interaction log ({len(engine.interaction_log)} entries recorded) ---")
