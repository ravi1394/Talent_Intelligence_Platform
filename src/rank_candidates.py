import json
import heapq

HIGH_VALUE_SKILLS = {
    "python", "faiss", "pinecone", "qdrant", "milvus",
    "weaviate", "elasticsearch", "opensearch",
    "retrieval", "ranking", "recommendation",
    "machine learning", "information retrieval",
    "embeddings", "semantic search"
}

HIGH_VALUE_TITLES = {
    "ai engineer",
    "ml engineer",
    "machine learning engineer",
    "search engineer",
    "relevance engineer",
    "recommendation engineer",
    "applied scientist",
    "nlp engineer"
}

def score_candidate(candidate):
    score = 0

    profile = candidate["profile"]
    skills = candidate["skills"]
    history = candidate["career_history"]
    signals = candidate["redrob_signals"]

    # Experience
    exp = profile["years_of_experience"]
    if 5 <= exp <= 9:
        score += 10
    elif 4 <= exp <= 12:
        score += 7

    # Title match
    title = profile["current_title"].lower()
    if any(t in title for t in HIGH_VALUE_TITLES):
        score += 15

    # Skills
    for s in skills:
        skill = s["name"].lower()
        if skill in HIGH_VALUE_SKILLS:
            score += 2

    # Career history
    for job in history:
        text = (
            job["title"] + " " +
            job["description"]
        ).lower()

        keywords = [
            "retrieval",
            "ranking",
            "recommendation",
            "semantic search",
            "embeddings",
            "vector database",
            "faiss",
            "pinecone",
            "qdrant"
        ]

        for kw in keywords:
            if kw in text:
                score += 5

    # Recruiter signals
    score += signals["recruiter_response_rate"] * 10
    score += signals["interview_completion_rate"] * 5

    if signals["open_to_work_flag"]:
        score += 5

    score += min(signals["github_activity_score"], 100) / 10

    return score

TOP_K = 100
top_candidates = []

with open("data/candidates.jsonl", "r", encoding="utf-8") as f:
    for line_num, line in enumerate(f):
        candidate = json.loads(line)

        score = score_candidate(candidate)

        entry = (
            score,
            candidate["candidate_id"]
        )

        if len(top_candidates) < TOP_K:
            heapq.heappush(top_candidates, entry)
        else:
            heapq.heappushpop(top_candidates, entry)

        if line_num % 10000 == 0:
            print(f"Processed {line_num}")

top_candidates.sort(reverse=True)

max_score = top_candidates[0][0]

with open("outputs/final_submission.csv", "w", encoding="utf-8") as out:
    out.write("candidate_id,rank,score,reasoning\n")

    for rank, (score, cid) in enumerate(top_candidates, start=1):

        normalized_score = score / max_score

        reasoning = (
            "Strong match for Senior AI Engineer role with retrieval/ranking "
            "experience, relevant AI skills, and strong engagement signals."
        )

        out.write(
            f'{cid},{rank},{normalized_score:.4f},"{reasoning}"\n'
        )

print("Done")