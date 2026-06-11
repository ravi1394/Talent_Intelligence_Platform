import streamlit as st
import json
import heapq
import pandas as pd

st.set_page_config(page_title="Talent Intelligence Platform")

st.title("Talent Intelligence Platform")
st.write("Redrob AI Candidate Ranking Demo")

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

    profile = candidate.get("profile", {})
    skills = candidate.get("skills", [])
    history = candidate.get("career_history", [])
    signals = candidate.get("redrob_signals", {})

    exp = profile.get("years_of_experience", 0)

    if 5 <= exp <= 9:
        score += 10
    elif 4 <= exp <= 12:
        score += 7

    title = profile.get("current_title", "").lower()

    if any(t in title for t in HIGH_VALUE_TITLES):
        score += 15

    for s in skills:
        skill = s.get("name", "").lower()
        if skill in HIGH_VALUE_SKILLS:
            score += 2

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

    for job in history:
        text = (
            job.get("title", "") + " " +
            job.get("description", "")
        ).lower()

        for kw in keywords:
            if kw in text:
                score += 5

    score += signals.get("recruiter_response_rate", 0) * 10
    score += signals.get("interview_completion_rate", 0) * 5

    if signals.get("open_to_work_flag", False):
        score += 5

    score += min(signals.get("github_activity_score", 0), 100) / 10

    return score


uploaded_file = st.file_uploader(
    "Upload Candidate File",
    type=["jsonl"]
)

if uploaded_file:

    st.success("File uploaded successfully")

    top_candidates = []
    TOP_K = 100

    for line in uploaded_file:
        candidate = json.loads(line.decode("utf-8"))

        score = score_candidate(candidate)

        entry = (
            score,
            candidate["candidate_id"]
        )

        if len(top_candidates) < TOP_K:
            heapq.heappush(top_candidates, entry)
        else:
            heapq.heappushpop(top_candidates, entry)

    top_candidates.sort(reverse=True)

    results = []

    for rank, (score, cid) in enumerate(top_candidates, start=1):
        results.append({
            "rank": rank,
            "candidate_id": cid,
            "score": round(score, 2)
        })

    df = pd.DataFrame(results)

    st.subheader("Top Ranked Candidates")
    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Ranked CSV",
        data=csv,
        file_name="ranked_candidates.csv",
        mime="text/csv"
    )