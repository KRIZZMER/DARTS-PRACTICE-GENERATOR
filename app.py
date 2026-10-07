import streamlit as st
import random

st.set_page_config(
    page_title="The Practice Board",
    page_icon="🎯",
    layout="wide"
)

# ---------- STYLE ----------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0b0b0b, #181818);
}
h1, h2, h3 {
    font-family: Arial, sans-serif;
}
div.stButton > button {
    width: 100%;
    height: 3.5rem;
    font-size: 18px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.title("🎯 THE PRACTICE BOARD")
st.caption("SMART DARTS PRACTICE GENERATOR • VERSION 2.0")

st.divider()

# ---------- PLAYER ----------
st.subheader("👤 Player Setup")

col1, col2, col3 = st.columns(3)

with col1:
    player = st.text_input("Player name", value="Kriss")

with col2:
    current_average = st.number_input(
        "Current 3-dart average",
        min_value=10,
        max_value=130,
        value=67
    )

with col3:
    target_average = st.number_input(
        "Target average",
        min_value=20,
        max_value=130,
        value=80
    )

# ---------- SESSION ----------
st.subheader("🎯 Build Today's Session")

col1, col2 = st.columns(2)

with col1:
    practice_time = st.select_slider(
        "Practice time",
        options=[15, 30, 45, 60, 75, 90, 120],
        value=45
    )

    focus = st.selectbox(
        "Main focus",
        [
            "Smart / All-Round",
            "Scoring",
            "Doubles",
            "Checkouts",
            "501 Match Practice"
        ]
    )

with col2:
    difficulty = st.selectbox(
        "Difficulty",
        ["Easy", "Normal", "Hard", "Pressure"]
    )

    maths = st.checkbox(
        "Include 501 maths training",
        value=True
    )

# ---------- DRILLS ----------
drills = {

    "Scoring": [
        "T20 Power Scoring — 10 visits at T20. Record every 100+, 140+ and 180.",
        "Treble Switching — alternate T20 → T19 → T18 every dart for 10 visits.",
        "60 Challenge — score at least 60 every visit. Reset the streak whenever you score below 60.",
        "Treble Ladder — hit T20, T19, T18, T17 and T16. Count how many darts it takes."
    ],

    "Doubles": [
        "D16 Route — hit D16 → D8 → D4 twice.",
        "Around the Board — hit D1 through D20. Record total darts used.",
        "Pressure Doubles — choose 5 doubles. You have 3 darts to hit each one.",
        "Favourite Finish — 20 darts each at D20, D16 and D10. Record hits."
    ],

    "Checkouts": [
        "Checkout Ladder — start at 41. Finish it within 3 darts to move up one.",
        "61–80 Challenge — attempt 10 randomly generated finishes between 61 and 80.",
        "81–100 Challenge — attempt 10 randomly generated finishes between 81 and 100.",
        "Pressure Checkout — you get ONE visit at each checkout. Miss it and move on."
    ],

    "501 Match Practice": [
        "Play one 501 leg and record your darts taken and checkout attempts.",
        "Play Best of 3 legs. Treat every leg as if you're playing a league match.",
        "Race to 3 legs — record your average after every leg.",
        "Pressure 501 — you must reach a finish within 15 darts."
    ]
}

# ---------- GENERATOR ----------
if st.button("🎯 GENERATE MY PRACTICE SESSION"):

    st.divider()

    st.header(f"🔥 {player}'s {practice_time}-Minute Session")

    gap = target_average - current_average

    if gap > 10:
        st.info(
            f"Current average: {current_average}  •  "
            f"Target: {target_average}  •  "
            f"Gap to target: {gap}"
        )

    warmup = 5 if practice_time <= 45 else 10
    remaining = practice_time - warmup

    st.subheader(f"🔥 {warmup} min — Warm Up")
    st.write(
        "Throw relaxed darts at the big 20 segment, then move through "
        "20 → 19 → 18. Don't chase scores yet — concentrate on rhythm and grouping."
    )

    if focus == "Smart / All-Round":

        categories = [
            "Scoring",
            "Doubles",
            "Checkouts",
            "501 Match Practice"
        ]

    else:
        categories = [focus]

    block_time = max(5, remaining // len(categories))

    for category in categories:

        st.subheader(f"🎯 {block_time} min — {category}")

        st.write(random.choice(drills[category]))

        if difficulty == "Pressure":
            st.warning(
                "🔥 PRESSURE RULE: Fail the target and repeat the drill before moving on."
            )

    # ---------- MATHS ----------
    if maths:

        st.divider()

        st.subheader("🧠 501 Maths Challenge")

        remaining_score = random.randint(201, 401)

        visit = random.choice([
            41, 45, 60, 81, 85, 95,
            100, 121, 125, 134, 140
        ])

        st.write(
            f"You have **{remaining_score}** remaining and score **{visit}**."
        )

        st.write("Work out your new remaining score WITHOUT using a calculator.")

        with st.expander("Show answer"):
            st.success(
                f"{remaining_score} − {visit} = "
                f"**{remaining_score - visit} remaining**"
            )

    # ---------- FINISH ----------
    st.divider()

    st.success(
        f"🎯 Session ready, {player}. Get on the oche!"
    )

    st.caption(
        "Quality beats quantity — keep the throw relaxed and record your results."
    )

st.divider()
st.caption("THE PRACTICE BOARD • SMART TRAINING • V2.0")
