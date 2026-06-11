import json

target = "CAND_0039754"   # top candidate from your output

with open("data/candidates.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        c = json.loads(line)
        if c["candidate_id"] == target:
            print("\nPROFILE")
            print(c["profile"])

            print("\nSKILLS")
            print(c["skills"][:10])

            print("\nCAREER")
            print(c["career_history"][:3])

            print("\nSIGNALS")
            print(c["redrob_signals"])

            break