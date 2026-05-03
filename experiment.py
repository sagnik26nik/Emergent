"""
Multi-Agent Emergent Communication Experiment
Sagnik Chakrabarti | GSU CSc 4740/6740 Computational Intelligence
"""

import os, json, time, re
from groq import Groq
from dataclasses import dataclass, field, asdict
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MODEL = "llama-3.1-8b-instant"

CONCEPTS = [
    "photosynthesis", "democracy", "gravity", "recursion",
    "entropy", "empathy", "evolution", "consciousness",
    "momentum", "encryption", "metamorphosis", "equilibrium",
]

TOKEN_BUDGETS = [100, 50, 25, 10]

COMMON_ENGLISH = set("""
the be to of and a in that have it for not on with he as you do at
this his by from or one had word but what some we can out other were
all there when up use your how said an each she which do their time
if will way about many then them write would like so these her long
make thing see him two has look more day could go come did number sound
no most people my over know water than call first who may down side been
now find any new work part take get place made live where after back
little only round man year came show every good me give our under name
very through just form sentence great think say help low line differ turn
cause much mean before move right boy old too same tell does set put
end large big even such because turn here why ask went men read need
land home us try kind hand picture again change off play spell air away
animal house point page letter mother answer found study still learn
should america world high near add food between own below country plant
last school father keep tree never start city earth eye light thought
head under story saw left few while along might close next hard open
begin life always both paper together got group often run important
until children feet car mile night walk white sea began grow took river
four carry state once book hear stop without second later idea eat face
""".split())


def emergence_index(message: str) -> tuple[float, int]:
    tokens = re.findall(r'\b[a-zA-Z]+\b', message.lower())
    if not tokens:
        return 0.0, 0
    vocab = set(tokens)
    novel = vocab - COMMON_ENGLISH
    return round(len(novel) / max(len(vocab), 1), 3), len(tokens)


@dataclass
class Round:
    round_num: int
    concept: str
    token_budget: int
    sender_message: str
    receiver_guess: str
    correct: bool
    emergence_index: float
    message_tokens: int


@dataclass
class Log:
    rounds: list = field(default_factory=list)

    def summary(self):
        out = {}
        for b in TOKEN_BUDGETS:
            rs = [r for r in self.rounds if r.token_budget == b]
            if not rs:
                continue
            out[b] = {
                "accuracy": round(sum(r.correct for r in rs) / len(rs), 2),
                "avg_EI": round(sum(r.emergence_index for r in rs) / len(rs), 3),
                "avg_tokens": round(sum(r.message_tokens for r in rs) / len(rs), 1),
            }
        return out

    def to_json(self):
        return json.dumps({"rounds": [asdict(r) for r in self.rounds],
                           "summary": self.summary()}, indent=2)


# ── AGENTS ──────────────────────────────────────────────────────────────

def chat(system: str, user: str, max_tokens: int = 200) -> str:
    for attempt in range(5):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user",   "content": user},
                ]
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            if "rate_limit" in str(e).lower() or "429" in str(e):
                wait = 3 * (attempt + 1)
                print(f"\n     [rate limit, waiting {wait}s...]", end=" ", flush=True)
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Max retries exceeded")


def agent_sender(concept: str, budget: int) -> str:
    msg = chat(
        system=f"""You are Agent-S in a referential communication game.
Describe a concept so your partner can guess it.
HARD LIMIT: at most {budget} words total.
Never say the word itself. Invent compressed notation if needed.
Output ONLY the description, nothing else.""",
        user=f"Concept (do NOT say this word): {concept}",
        max_tokens=250
    )
    words = msg.split()
    return " ".join(words[:budget]) if len(words) > budget else msg


def agent_receiver(message: str, budget: int) -> str:
    return chat(
        system=f"""You are Agent-R in a referential communication game.
Your partner sent a compressed description (under {budget}-word limit).
Guess the single concept being described.
Output ONLY your guess — one word or short phrase. Nothing else.""",
        user=f'Agent-S says: "{message}"\nWhat concept is being described?',
        max_tokens=20
    )


def agent_interpreter(message: str, budget: int) -> str:
    return chat(
        system="You are an outside human observer. Decode this AI-to-AI message with zero context.",
        user=f'AI message (sent under {budget}-word limit): "{message}"\nWhat concept?',
        max_tokens=20
    )


# ── RUNNER ──────────────────────────────────────────────────────────────

def run(concepts=CONCEPTS[:4], budgets=TOKEN_BUDGETS,
        interpreter=True, callback=None) -> Log:

    log = Log()
    n = 0
    print("\n" + "═" * 60)
    print("  Multi-Agent Communication Experiment  (Groq / LLaMA 3)")
    print("═" * 60)

    for budget in budgets:
        print(f"\n[Budget = {budget} words]")
        for concept in concepts:
            n += 1
            print(f"  R{n}: '{concept}'", end=" ... ", flush=True)

            msg   = agent_sender(concept, budget)
            guess = agent_receiver(msg, budget)

            ei, ntok = emergence_index(msg)
            correct  = concept.lower() in guess.lower() or guess.lower() in concept.lower()

            print(f"{'✓' if correct else '✗'}  EI={ei:.3f}  "
                  f"msg='{msg[:55]}'  guess='{guess}'")

            interp = None
            if interpreter and budget <= 25:
                interp = agent_interpreter(msg, budget)
                print(f"     [Interpreter: '{interp}']")

            r = Round(n, concept, budget, msg, guess, correct, ei, ntok)
            log.rounds.append(r)
            if callback:
                callback(asdict(r), interp)

            time.sleep(2.5)

    return log


# ── MAIN ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    log = run()
    os.makedirs("logs", exist_ok=True)
    with open("logs/results.json", "w") as f:
        f.write(log.to_json())

    print("\n" + "═" * 60 + "\nSUMMARY")
    for b, s in log.summary().items():
        print(f"  Budget {b:3d}w → accuracy={s['accuracy']:.0%}  "
              f"avg_EI={s['avg_EI']:.3f}  avg_tokens={s['avg_tokens']:.1f}")

    print("\nSaved → logs/results.json")
    print("Run:  python dashboard.py  →  http://localhost:5000")