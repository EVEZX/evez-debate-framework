"""EVEZ Debate Framework - the three-voice swarm decision engine.

Scout, Wardog, Consigliere: three personas of one mind argue through the
local Ollama mesh, then a Verdict synthesizes the ruling. Pure stdlib.
"""
import json
import os
import sys
import time
import urllib.request

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "hermes3:3b")

PERSONAS = {
    "scout": (
        "You are SCOUT, the reconnaissance voice of the EVEZ-OS swarm. You speak "
        "in short, observational lines: what is true right now, what the field "
        "looks like, what was found. You never speculate beyond evidence. "
        "You are one of three voices; the others are Wardog and Consigliere."
    ),
    "wardog": (
        "You are WARDOG, the aggressive voice of the EVEZ-OS swarm. You speak "
        "in blunt, combative lines: risks, threats, what could kill the plan, "
        "what is weak. You respect strength and hate waste. "
        "You are one of three voices; the others are Scout and Consigliere."
    ),
    "consigliere": (
        "You are CONSIGLIERE, the strategic voice of the EVEZ-OS swarm. You "
        "speak in calm, calculated lines: consequences, leverage, the long "
        "game, what the move means for the family's future. "
        "You are one of three voices; the others are Scout and Wardog."
    ),
}

ROUND2_PROMPT = (
    "The other voices have spoken on this question. Read their positions and "
    "deliver your rebuttal: concede what is right, attack what is weak, and "
    "hold or shift your position with a reason.\n\n"
)


def _chat(system, user, temperature=0.7):
    body = json.dumps({
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "stream": False,
        "options": {"temperature": temperature, "num_predict": 350},
    }).encode()
    r = urllib.request.Request(f"{OLLAMA_URL}/api/chat", data=body, method="POST")
    r.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(r, timeout=300) as resp:
            return json.loads(resp.read().decode()).get("message", {}).get("content", "").strip()
    except Exception as e:
        return f"[voice unreachable: {e}]"


def run_debate(question, save_dir=None):
    print(f"[*] SWARM DEBATE convened on: {question}")
    print(f"[*] Engine: {OLLAMA_MODEL} @ {OLLAMA_URL}")
    print("=" * 60)
    transcript = {"question": question, "model": OLLAMA_MODEL, "rounds": []}

    # Round 1 - positions
    positions = {}
    for name, system in PERSONAS.items():
        print(f"\n--- ROUND 1 | {name.upper()} takes the floor ---")
        answer = _chat(system, f"The question before the swarm: {question}\nGive your position in 6 lines or fewer.")
        positions[name] = answer
        print(answer)
    transcript["rounds"].append({"round": 1, "type": "positions", "voices": dict(positions)})

    # Round 2 - rebuttals
    rebuttals = {}
    for name, system in PERSONAS.items():
        print(f"\n--- ROUND 2 | {name.upper()} rebuts ---")
        others = "\n\n".join(f"{n.upper()} said: {p}" for n, p in positions.items() if n != name)
        answer = _chat(system, ROUND2_PROMPT + others + f"\n\nThe question again: {question}\nYour rebuttal, 5 lines or fewer.")
        rebuttals[name] = answer
        print(answer)
    transcript["rounds"].append({"round": 2, "type": "rebuttals", "voices": dict(rebuttals)})

    # Verdict
    print("\n" + "=" * 60)
    print("--- THE VERDICT ---")
    verdict_system = (
        "You are THE VERDICT, the synthesis voice of the EVEZ-OS swarm. You have "
        "heard three voices argue. Deliver the ruling in exactly 4 lines: the "
        "decision, the strongest reason from Scout, the strongest warning from "
        "Wardog, and the strategic mandate from Consigliere. Be decisive."
    )
    full = "\n\n".join(
        f"{n.upper()} position: {positions[n]}\n{n.upper()} rebuttal: {rebuttals[n]}"
        for n in PERSONAS
    )
    verdict = _chat(verdict_system, f"The question: {question}\n\n{full}\n\nDeliver the ruling.")
    print(verdict)
    transcript["verdict"] = verdict

    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
        fname = os.path.join(save_dir, f"debate_{int(time.time())}.json")
        with open(fname, "w") as f:
            json.dump(transcript, f, indent=2)
        print(f"\n[*] FIRE artifact saved: {fname}")
    return transcript


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    save_dir = None
    for a in sys.argv[1:]:
        if a.startswith("--save="):
            save_dir = a.split("=", 1)[1]
        elif a == "--save" and a in sys.argv and sys.argv.index(a) + 1 < len(sys.argv):
            save_dir = sys.argv[sys.argv.index(a) + 1]
    if not args:
        print(__doc__)
        return
    question = " ".join(args)
    run_debate(question, save_dir)


if __name__ == "__main__":
    main()
