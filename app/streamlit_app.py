import streamlit as st
import json
import heapq
import pandas as pd

st.set_page_config(page_title="Talent Intelligence Platform")

st.title("Talent Intelligence Platform")
st.write("Redrob AI Candidate Ranking Demo")

# ==========================
# JD Matching Signals
# ==========================

HIGH_VALUE_SKILLS = {
    "python",
    "faiss",
    "pinecone",
    "qdrant",
    "milvus",
    "weaviate",
    "elasticsearch",
    "opensearch",
    "retrieval",
    "ranking",
    "recommendation",
    "machine learning",
    "information retrieval",
    "embeddings",
    "semantic search"
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


# ==========================
# Candidate Scoring Function
# ==========================

def score_candidate(candidate):

    score = 0

    profile = candidate.get("profile", {})
    skills = candidate.get("skills", [])
    history = candidate.get("career_history", [])
    signals = candidate.get("redrob_signals", {})

    # Experience
    exp = profile.get("years_of_experience", 0)

    if 5 <= exp <= 9:
        score += 10
    elif 4 <= exp <= 12:
        score += 7

    # Current title
    title = profile.get("current_title", "").lower()

    if any(t in title for t in HIGH_VALUE_TITLES):
        score += 15

    # Skills
    for skill_obj in skills:

        skill = skill_obj.get("name", "").lower()

        if skill in HIGH_VALUE_SKILLS:
            score += 2

    # Career history keywords
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
            job.get("title", "") +
            " " +
            job.get("description", "")
        ).lower()

        for kw in keywords:

            if kw in text:
                score += 5

    # Behavioral signals
    score += signals.get("recruiter_response_rate", 0) * 10
    score += signals.get("interview_completion_rate", 0) * 5

    if signals.get("open_to_work_flag", False):
        score += 5

    score += min(
        signals.get("github_activity_score", 0),
        100
    ) / 10

    return score


# ==========================
# File Upload
# ==========================

uploaded_file = st.file_uploader(
    "Upload Candidate File (.jsonl)",
    type=["jsonl"]
)

# ==========================
# Ranking Pipeline
# ==========================

if uploaded_file:

    st.success("File uploaded successfully")

    TOP_K = 100
    top_candidates = []

    try:

        raw = uploaded_file.getvalue()

        # Try UTF-8 first
        try:
            content = raw.decode("utf-8")

        except UnicodeDecodeError:

            # Fallback to UTF-16
            content = raw.decode("utf-16")

        total_candidates = 0

        for line in content.splitlines():

            if not line.strip():
                continue

            candidate = json.loads(line)

            total_candidates += 1

            score = score_candidate(candidate)

            entry = (
                score,
                candidate["candidate_id"]
            )

            if len(top_candidates) < TOP_K:

                heapq.heappush(
                    top_candidates,
                    entry
                )

            else:

                heapq.heappushpop(
                    top_candidates,
                    entry
                )

        # Sort highest score first
        top_candidates.sort(reverse=True)

        # Create results table
        results = []

        for rank, (score, cid) in enumerate(
            top_candidates,
            start=1
        ):

            results.append({
                "rank": rank,
                "candidate_id": cid,
                "score": round(score, 2)
            })

        df = pd.DataFrame(results)

        st.write(
            f"Processed {total_candidates:,} candidates"
        )

        st.subheader("Top Ranked Candidates")

        st.dataframe(
            df,
            use_container_width=True
        )

        csv = df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="Download Ranked CSV",
            data=csv,
            file_name="ranked_candidates.csv",
            mime="text/csv"
        )

    except Exception as e:

        st.error(
            f"Error processing file: {str(e)}"
        )