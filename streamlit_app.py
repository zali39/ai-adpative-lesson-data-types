# Adaptive AI-Powered Python Data Types Lesson (Streamlit Prototype)

import streamlit as st
import random
import datetime
import pandas as pd
import sqlite3
from urllib.parse import urlencode

# --- Persistent User Storage ---
conn = sqlite3.connect(":memory:")
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS progress (
    timestamp TEXT, question TEXT, selected TEXT, correct TEXT,
    result TEXT, confidence INTEGER, level INTEGER
)''')
conn.commit()

# --- Session State ---
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'question_num' not in st.session_state:
    st.session_state.question_num = 0
if 'adaptive_level' not in st.session_state:
    st.session_state.adaptive_level = 1
if 'results' not in st.session_state:
    st.session_state.results = []
if 'user' not in st.session_state:
    st.session_state.user = st.text_input("Enter your name or student ID")

if not st.session_state.user:
    st.stop()

# --- Question Bank by Difficulty Level ---
questions = {
    1: [
        {"q": "What type is the result of: 5 + 2.0?", "a": ["int", "float", "str", "bool"], "c": "float"},
        {"q": "Which data type is immutable?", "a": ["list", "dict", "tuple", "set"], "c": "tuple"},
    ],
    2: [
        {"q": "What will type('True') return?", "a": ["str", "bool", "int", "NoneType"], "c": "str"},
        {"q": "Which operation modifies a list in-place?", "a": ["append()", "+", "*", "sorted()"], "c": "append()"},
    ],
    3: [
        {"q": "What is the output of: type({1: 'a', 2: 'b'})?", "a": ["dict", "list", "tuple", "set"], "c": "dict"},
        {"q": "What type is returned by: set([1,2,2,3])?", "a": ["list", "tuple", "set", "dict"], "c": "set"},
    ]
}

st.title("🔁 Adaptive Python Data Types Lesson")

st.markdown("""
This interactive lesson adjusts to your learning level. Answer each question and receive feedback instantly. Let's get started!

📺 [Watch Introduction Video](https://example.com/python-data-types-intro)
""")

# --- Ask Question ---
current_level = st.session_state.adaptive_level
question_set = questions.get(current_level, questions[1])
question = random.choice(question_set)
st.write(f"**Q{st.session_state.question_num + 1}: {question['q']}**")

answer = st.radio("Choose one:", question['a'])
confidence = st.slider("How confident are you in your answer?", 0, 100, 50)

if st.button("Submit"):
    correct = answer == question['c']
    feedback = "✅ Correct!" if correct else f"❌ Incorrect. The correct answer was: {question['c']}"
    if correct:
        st.session_state.score += 1
        st.session_state.adaptive_level = min(3, st.session_state.adaptive_level + 1)
    else:
        st.session_state.adaptive_level = max(1, st.session_state.adaptive_level - 1)

    result_record = {
        "Timestamp": datetime.datetime.now().isoformat(),
        "Question": question['q'],
        "Selected": answer,
        "Correct": question['c'],
        "Result": "Correct" if correct else "Incorrect",
        "Confidence": confidence,
        "Level": current_level
    }

    st.session_state.results.append(result_record)

    # Save to SQLite database
    c.execute('''INSERT INTO progress VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (result_record["Timestamp"], result_record["Question"], result_record["Selected"],
               result_record["Correct"], result_record["Result"], result_record["Confidence"], result_record["Level"]))
    conn.commit()

    st.session_state.question_num += 1
    st.success(feedback) if correct else st.error(feedback)
    st.rerun()

# --- Progress ---
st.markdown(f"### Progress: {st.session_state.score} / {st.session_state.question_num}")

# --- Export Results ---
if st.session_state.results:
    df = pd.DataFrame(st.session_state.results)
    st.download_button("Download Results as CSV", df.to_csv(index=False), "results.csv")

    # --- Simulated LMS Grade Sync (Brightspace via LTI) ---
    st.markdown("#### 📤 LMS Integration Preview")
    lti_data = {
        'user': st.session_state.user,
        'score': st.session_state.score,
        'total': st.session_state.question_num,
        'correct_pct': round((st.session_state.score / st.session_state.question_num) * 100, 1) if st.session_state.question_num else 0
    }
    st.code("https://lms.example.com/lti/submit?" + urlencode(lti_data))

# --- Instructor Dashboard ---
if st.checkbox("📊 Show Instructor Dashboard"):
    df_all = pd.read_sql_query("SELECT * FROM progress", conn)
    st.dataframe(df_all)
    if not df_all.empty:
        avg_confidence = df_all['confidence'].mean()
        correct_pct = df_all[df_all['result'] == 'Correct'].shape[0] / df_all.shape[0] * 100
        st.metric("Average Confidence", f"{avg_confidence:.1f}%")
        st.metric("Correct Answer Rate", f"{correct_pct:.1f}%")
