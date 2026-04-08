import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# ---------- STYLE ----------
st.markdown("""
<style>
.main {
    background-color: #0E1117;
}
h1, h2, h3 {
    color: #00C6FF;
}
</style>
""", unsafe_allow_html=True)

st.title("🧑‍💼 Smart Resume Shortlisting System")

# ---------- SESSION ----------
if "data" not in st.session_state:
    st.session_state.data = []

# ---------- NAVIGATION ----------
page = st.radio(
    "Navigation",
    ["➕ Add Candidate", "📊 Analysis"],
    horizontal=True
)

st.markdown("---")

# =============================
# ➕ ADD CANDIDATE
# =============================
if page == "➕ Add Candidate":

    st.header("Add Candidate Details")

    with st.form("form"):
        name = st.text_input("Full Name")

        col1, col2 = st.columns(2)

        with col1:
            experience = st.slider("Experience (years)", 0, 15)
            projects = st.slider("Projects", 0, 20)

        with col2:
            score = st.slider("Codolio Score", 0, 100)
            communication = st.slider("Communication", 0, 10)

        salary = st.number_input("Salary (Lakhs ₹)", min_value=1)

        submit = st.form_submit_button("Add Candidate")

        if submit and name:
            st.session_state.data.append({
                "name": name,
                "experience": experience,
                "projects": projects,
                "score": score,
                "communication": communication,
                "salary": salary
            })
            st.success(f"{name} added!")

    if len(st.session_state.data) > 0:
        st.subheader("📋 Candidate List")
        st.dataframe(pd.DataFrame(st.session_state.data))


# =============================
# 📊 ANALYSIS
# =============================
elif page == "📊 Analysis":

    st.header("Candidate Analysis")

    if len(st.session_state.data) == 0:
        st.warning("Add candidates first.")
    else:
        df = pd.DataFrame(st.session_state.data)

        col1, col2 = st.columns(2)

        with col1:
            budget = st.number_input("Budget (Lakhs ₹)", min_value=1, value=50)

        with col2:
            max_hires = st.number_input("Max Hires", min_value=1, value=3)

        candidates = st.session_state.data

        # ---------- MERGE SORT ----------
        def merge_sort(arr):
            if len(arr) <= 1:
                return arr
            mid = len(arr)//2
            left = merge_sort(arr[:mid])
            right = merge_sort(arr[mid:])
            return merge(left, right)

        def merge(left, right):
            result = []
            i = j = 0
            while i < len(left) and j < len(right):
                if left[i]['score'] > right[j]['score']:
                    result.append(left[i]); i += 1
                else:
                    result.append(right[j]); j += 1
            result += left[i:]
            result += right[j:]
            return result

        # ---------- GREEDY ----------
        def greedy_selection(candidates, k):
            return sorted(
                candidates,
                key=lambda x: x['score']/x['salary'],
                reverse=True
            )[:k]

        # ---------- KNAPSACK ----------
        def knapsack(candidates, budget):
            n = len(candidates)
            dp = [[0]*(budget+1) for _ in range(n+1)]

            for i in range(1, n+1):
                sal = candidates[i-1]['salary']
                score = candidates[i-1]['score']

                for b in range(budget+1):
                    if sal <= b:
                        dp[i][b] = max(score + dp[i-1][b-sal], dp[i-1][b])
                    else:
                        dp[i][b] = dp[i-1][b]

            res = []
            b = budget
            for i in range(n, 0, -1):
                if dp[i][b] != dp[i-1][b]:
                    res.append(candidates[i-1])
                    b -= candidates[i-1]['salary']

            return res[::-1], dp[n][budget]

        # ---------- GRAPH ----------
        st.subheader("📊 Candidate Scores")
        fig, ax = plt.subplots()
        ax.bar(df['name'], df['score'], color="#00C6FF")
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # ---------- RESULTS ----------
        greedy_res = greedy_selection(candidates, max_hires)
        dp_res, dp_score = knapsack(candidates, budget)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🟢 Greedy")
            st.dataframe(pd.DataFrame(greedy_res))

        with col2:
            st.subheader("🔵 Optimal (DP)")
            st.dataframe(pd.DataFrame(dp_res))
            st.success(f"Total Score: {dp_score}")

        # ---------- COMPARISON ----------
        greedy_score = sum([c['score'] for c in greedy_res])

        st.subheader("📈 Comparison")
        fig2, ax2 = plt.subplots()
        ax2.bar(["Greedy", "DP"], [greedy_score, dp_score],
                color=["green", "blue"])
        st.pyplot(fig2)
