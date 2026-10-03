# EVEZ Debate Framework

The three-voice swarm decision engine. Scout, Wardog, and Consigliere — three personas of one mind — argue any question through the local Ollama mesh, then a Verdict synthesizes their positions into a ruling.

Never make a solo decision again.

## Install
```bash
pip install .
evez-debate "Should we do X?"
```

Requires a local Ollama daemon (default `http://127.0.0.1:11434`, model `hermes3:3b` — configurable via `OLLAMA_URL` / `OLLAMA_MODEL` env vars).

## How it works
1. **Round 1 — Positions**: each persona answers the question in its own voice.
   - **Scout** — reconnaissance, facts, what the field actually looks like
   - **Wardog** — aggression, risk, what could kill you
   - **Consigliere** — strategy, consequences, the long game
2. **Round 2 — Rebuttals**: each persona sees the others' positions and attacks/defends.
3. **Verdict**: a synthesis that must honor the strongest argument from each voice.

Transcripts are saved as FIRE-event artifacts (`debate_<timestamp>.json`) for the corpus.

## Mesh integration
```bash
evez-debate "question" --save /root/evez-corpus/debates/
```
The mesh's standing governance mode. Impress the future swarms: every major EVEZ-OS decision gets argued in triplicate.
