import streamlit as st
import random
import json
import os
from datetime import datetime
import math
from PIL import Image, ImageDraw
from streamlit_image_coordinates import streamlit_image_coordinates
from supabase import create_client
supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)
if "user" not in st.session_state:
    st.session_state.user = None
def login_screen():
    st.title("🎯 THE PRACTICE BOARD")
    st.subheader("🔐 Player Login")

    login_tab, signup_tab = st.tabs(["Log In", "Create Account"])

    with login_tab:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("🔐 Log In", key="login_button"):
            try:
                response = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                st.session_state.user = response.user
                st.session_state.access_token = response.session.access_token
                st.rerun()
            except Exception:
                st.error("Email or password is incorrect.")

    with signup_tab:
        signup_email = st.text_input("Email", key="signup_email")
        signup_password = st.text_input("Password", type="password", key="signup_password")        	
        if st.button("🎯 Create Account", key="signup_button"):
            try:
                response = supabase.auth.sign_up({
                    "email": signup_email,
                    "password": signup_password
                })
                st.success("Account created! Check your email to confirm your account, then log in.")
            except Exception as e:
                st.error(f"Could not create account: {e}")



st.set_page_config(
    page_title="The Practice Board",
    page_icon="🎯",
    layout="wide"
)
if st.session_state.user is None:
    login_screen()
    st.stop()
# ---------------- STYLE ----------------

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

# ---------------- DATA ----------------

RESULTS_FILE = "practice_results.json"

def load_results():
    if os.path.exists(RESULTS_FILE):
        try:
            with open(RESULTS_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_results(results):
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)

if "results" not in st.session_state:
    st.session_state.results = load_results()

if "session" not in st.session_state:
    st.session_state.session = None

# ---------------- HEADER ----------------

st.title("🎯 THE PRACTICE BOARD")
st.caption("SMART DARTS PRACTICE GENERATOR • VERSION 4.0")
st.divider()

tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 Practice",
    "📊 Results",
    "📈 Progress",
    "🎯 Scorer"
])

# =========================================================
# PRACTICE TAB
# =========================================================

with tab1:

    st.subheader("👤 Player Setup")

    col1, col2, col3 = st.columns(3)

    with col1:
        player = st.text_input(
            "Player name",
            value=""
        )

    with col2:
        current_average = st.number_input(
            "Current 3-dart average",
            min_value=10,
            max_value=130,
            value=None
        )

    with col3:
        target_average = st.number_input(
            "Target average",
            min_value=20,
            max_value=130,
            value=None
        )

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
            [
                "Easy",
                "Normal",
                "Hard",
                "Pressure"
            ],
            index=1
        )

        maths = st.checkbox(
            "Include 501 maths training",
            value=True
        )

    # ---------------- DRILLS ----------------

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

    if st.button("🎯 GENERATE MY PRACTICE SESSION"):

        if focus == "Smart / All-Round":

            # Adapt the session using previous results
            player_results = [
                r for r in st.session_state.results
                if r["player"].lower() == player.lower()
            ]

            if player_results:

                recent = player_results[-5:]

                avg_checkout = sum(
                    r["checkout_percent"] for r in recent
                ) / len(recent)

                avg_scoring = sum(
                    r["average"] for r in recent
                ) / len(recent)

                if avg_checkout < 25:
                    categories = [
                        "Doubles",
                        "Checkouts",
                        "Scoring",
                        "501 Match Practice"
                    ]

                elif avg_scoring < current_average:
                    categories = [
                        "Scoring",
                        "Scoring",
                        "Checkouts",
                        "501 Match Practice"
                    ]

                else:
                    categories = [
                        "Scoring",
                        "Doubles",
                        "Checkouts",
                        "501 Match Practice"
                    ]

            else:
                categories = [
                    "Scoring",
                    "Doubles",
                    "Checkouts",
                    "501 Match Practice"
                ]

        else:
            categories = [focus]

        warmup = 5 if practice_time <= 45 else 10
        remaining = practice_time - warmup

        # Make sure short sessions still fit the chosen time.
        if len(categories) > remaining:
            categories = categories[:remaining]

        block_time = max(
            1,
            remaining // len(categories)
        )

        generated_drills = []

        for category in categories:
            generated_drills.append({
                "category": category,
                "drill": random.choice(drills[category])
            })

        st.session_state.session = {
            "player": player,
            "time": practice_time,
            "warmup": warmup,
            "block_time": block_time,
            "drills": generated_drills,
            "difficulty": difficulty,
            "maths": maths,
            "current_average": current_average,
            "target_average": target_average
        }

    # ---------------- DISPLAY SESSION ----------------

    if st.session_state.session:

        session = st.session_state.session

        st.divider()

        st.header(
            f"🔥 {session['player']}'s "
            f"{session['time']}-Minute Session"
        )

        gap = (
            session["target_average"]
            - session["current_average"]
        )

        if gap > 0:
            st.info(
                f"Current average: "
                f"{session['current_average']}  •  "
                f"Target: {session['target_average']}  •  "
                f"Gap to target: {gap}"
            )

        st.subheader(
            f"🔥 {session['warmup']} min — Warm Up"
        )

        st.write(
            "Throw relaxed darts at the big 20 segment, "
            "then move through 20 → 19 → 18. "
            "Don't chase scores yet — concentrate on "
            "rhythm and grouping."
        )

        for item in session["drills"]:

            st.subheader(
                f"🎯 {session['block_time']} min — "
                f"{item['category']}"
            )

            st.write(item["drill"])

            if session["difficulty"] == "Pressure":
                st.warning(
                    "🔥 PRESSURE RULE: Fail the target "
                    "and repeat the drill before moving on."
                )

        if session["maths"]:

            st.divider()
            st.subheader("🧠 501 Maths Challenge")

            remaining_score = random.randint(201, 401)

            visit = random.choice([
                41, 45, 60, 81, 85, 95,
                100, 121, 125, 134, 140
            ])

            st.write(
                f"You have **{remaining_score}** remaining "
                f"and score **{visit}**."
            )

            st.write(
                "Work out your new remaining score "
                "WITHOUT using a calculator."
            )

            with st.expander("Show answer"):
                st.success(
                    f"{remaining_score} − {visit} = "
                    f"**{remaining_score - visit} remaining**"
                )

        st.divider()

        st.success(
            f"🎯 Session ready, {session['player']}. "
            f"Get on the oche!"
        )

        st.caption(
            "When you're finished, open the Results tab "
            "and log how you played."
        )

# =========================================================
# RESULTS TAB
# =========================================================

with tab2:

    st.header("📊 Log Your Practice Results")

    st.write(
        "Finished your session? Record the numbers below. "
        "The Practice Board will use them to track your "
        "improvement."
    )

    result_player = st.text_input(
        "Player",
        value="",
        key="result_player"
    )

    col1, col2 = st.columns(2)

    with col1:

        result_average = st.number_input(
            "3-dart average",
            min_value=0.0,
            max_value=150.0,
            value=0.0,
            step=0.1
        )

        first9 = st.number_input(
            "First 9 average",
            min_value=0.0,
            max_value=180.0,
            value=0.0,
            step=0.1
        )

        checkout_attempts = st.number_input(
            "Checkout attempts",
            min_value=0,
            value=0,
            step=1
        )

        checkout_hits = st.number_input(
            "Checkouts hit",
            min_value=0,
            value=0,
            step=1
        )

    with col2:

        scores_100 = st.number_input(
            "100+ scores",
            min_value=0,
            value=0,
            step=1
        )

        scores_140 = st.number_input(
            "140+ scores",
            min_value=0,
            value=0,
            step=1
        )

        scores_180 = st.number_input(
            "180s",
            min_value=0,
            value=0,
            step=1
        )

        session_focus = st.selectbox(
            "Session focus",
            [
                "All-Round",
                "Scoring",
                "Doubles",
                "Checkouts",
                "501 Match Practice"
            ]
        )

    notes = st.text_area(
        "Session notes",
        placeholder=(
            "What felt good? What went wrong? "
            "Anything you want to work on next time?"
        )
    )

    if checkout_attempts > 0:
        checkout_percent = (
            checkout_hits / checkout_attempts
        ) * 100
    else:
        checkout_percent = 0

    st.metric(
        "Calculated checkout %",
        f"{checkout_percent:.1f}%"
    )

    if st.button("💾 SAVE PRACTICE RESULT"):

        if checkout_hits > checkout_attempts:
            st.error(
                "Checkouts hit can't be higher than "
                "checkout attempts."
            )

        else:

            new_result = {
                "date": datetime.now().strftime(
                    "%d/%m/%Y %H:%M"
                ),
                "player": result_player.strip() or "Player",
                "average": result_average,
                "first9": first9,
                "checkout_attempts": checkout_attempts,
                "checkout_hits": checkout_hits,
                "checkout_percent": checkout_percent,
                "scores_100": scores_100,
                "scores_140": scores_140,
                "scores_180": scores_180,
                "focus": session_focus,
                "notes": notes
            }

            st.session_state.results.append(new_result)

            save_results(st.session_state.results)

            st.success(
                "🎯 Result saved! Your progress has been updated."
            )

# =========================================================
# PROGRESS TAB
# =========================================================

with tab3:

    st.header("📈 Player Progress")

    if not st.session_state.results:

        st.info(
            "No practice results yet. Complete a session "
            "and save your first result."
        )

    else:

        players = sorted(
            set(
                r["player"]
                for r in st.session_state.results
            )
        )

        selected_player = st.selectbox(
            "View player",
            players
        )

        player_results = [
            r for r in st.session_state.results
            if r["player"] == selected_player
        ]

        latest = player_results[-1]

        best_average = max(
            r["average"] for r in player_results
        )

        best_first9 = max(
            r["first9"] for r in player_results
        )

        total_180s = sum(
            r["scores_180"] for r in player_results
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Latest Average",
                f"{latest['average']:.1f}"
            )

        with col2:
            st.metric(
                "Personal Best",
                f"{best_average:.1f}"
            )

        with col3:
            st.metric(
                "Best First 9",
                f"{best_first9:.1f}"
            )

        with col4:
            st.metric(
                "Total 180s",
                total_180s
            )

        st.divider()

        st.subheader("📈 Average Progress")

        average_chart = {
            str(i + 1): r["average"]
            for i, r in enumerate(player_results)
        }

        st.line_chart(average_chart)

        st.subheader("🎯 Checkout % Progress")

        checkout_chart = {
            str(i + 1): r["checkout_percent"]
            for i, r in enumerate(player_results)
        }

        st.line_chart(checkout_chart)

        # ---------------- ANALYSIS ----------------

        st.divider()
        st.subheader("🧠 Practice Board Analysis")

        recent = player_results[-5:]

        recent_average = sum(
            r["average"] for r in recent
        ) / len(recent)

        recent_first9 = sum(
            r["first9"] for r in recent
        ) / len(recent)

        recent_checkout = sum(
            r["checkout_percent"] for r in recent
        ) / len(recent)

        if len(player_results) >= 2:

            previous_average = player_results[-2]["average"]

            difference = (
                latest["average"]
                - previous_average
            )

            if difference > 0:
                st.success(
                    f"📈 Your average improved by "
                    f"{difference:.1f} points compared "
                    f"with your previous session."
                )

            elif difference < 0:
                st.info(
                    f"Your average was "
                    f"{abs(difference):.1f} points lower "
                    f"than your previous session. "
                    f"One session isn't a trend — keep going."
                )

        if recent_checkout < 20:

            st.warning(
                "🎯 Current weakness: DOUBLES. "
                "Your recent checkout percentage is below 20%. "
                "Your next Smart session will prioritise "
                "doubles and checkout practice."
            )

        elif recent_checkout < 30:

            st.info(
                "🎯 Checkout improvement opportunity: "
                "add extra doubles work to your next session."
            )

        elif recent_first9 > recent_average + 10:

            st.warning(
                "⚡ You are starting legs strongly but your "
                "average is dropping later. Focus on maintaining "
                "scoring rhythm throughout the leg."
            )

        else:

            st.success(
                "🔥 Your numbers are looking balanced. "
                "Keep using Smart / All-Round sessions."
            )

        st.write(
            f"**Recent 5-session average:** "
            f"{recent_average:.1f}"
        )

        st.write(
            f"**Recent checkout rate:** "
            f"{recent_checkout:.1f}%"
        )

        # ---------------- HISTORY ----------------

        st.divider()
        st.subheader("🗓️ Session History")

        for result in reversed(player_results):

            with st.expander(
                f"{result['date']} • "
                f"Avg {result['average']:.1f} • "
                f"{result['focus']}"
            ):

                st.write(
                    f"**First 9:** {result['first9']:.1f}"
                )

                st.write(
                    f"**Checkout:** "
                    f"{result['checkout_hits']} / "
                    f"{result['checkout_attempts']} "
                    f"({result['checkout_percent']:.1f}%)"
                )

                st.write(
                    f"**100+:** {result['scores_100']}  |  "
                    f"**140+:** {result['scores_140']}  |  "
                    f"**180s:** {result['scores_180']}"
                )

                if result["notes"]:
                    st.write(
                        f"**Notes:** {result['notes']}"
                    )



ORDER = [20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5]
CHECKOUTS = {
    170:"T20 T20 Bull",167:"T20 T19 Bull",164:"T20 T18 Bull",161:"T20 T17 Bull",
    160:"T20 T20 D20",158:"T20 T20 D19",157:"T20 T19 D20",156:"T20 T20 D18",
    155:"T20 T19 D19",154:"T20 T18 D20",153:"T20 T19 D18",152:"T20 T20 D16",
    151:"T20 T17 D20",150:"T20 T18 D18",149:"T20 T19 D16",148:"T20 T16 D20",
    147:"T20 T17 D18",146:"T20 T18 D16",145:"T20 T15 D20",144:"T20 T20 D12",
    143:"T20 T17 D16",142:"T20 T14 D20",141:"T20 T19 D12",140:"T20 T20 D10",
    138:"T20 T18 D12",137:"T20 T19 D10",136:"T20 T20 D8",135:"Bull T15 D20",
    134:"T20 T14 D16",133:"T20 T19 D8",132:"Bull Bull D16",131:"T20 T13 D16",
    130:"T20 T20 D5",129:"T19 T16 D12",128:"T18 T18 D10",127:"T20 T17 D8",
    126:"T19 T19 D6",125:"Bull T17 D12",124:"T20 T16 D8",123:"T19 T16 D9",
    122:"T18 T18 D7",121:"T20 T11 D14",120:"T20 20 D20",119:"T19 T12 D13",
    118:"T20 18 D20",117:"T20 17 D20",116:"T20 16 D20",115:"T20 15 D20",
    114:"T20 14 D20",113:"T20 13 D20",112:"T20 12 D20",111:"T20 19 D16",
    110:"T20 18 D16",109:"T20 17 D16",108:"T20 16 D16",107:"T19 18 D16",
    106:"T20 14 D16",105:"T20 13 D16",104:"T18 18 D16",103:"T19 14 D16",
    102:"T20 10 D16",101:"T17 18 D16",100:"T20 D20",99:"T19 10 D16",
    98:"T20 D19",97:"T19 D20",96:"T20 D18",95:"T19 D19",94:"T18 D20",
    93:"T19 D18",92:"T20 D16",91:"T17 D20",90:"T18 D18",89:"T19 D16",
    88:"T16 D20",87:"T17 D18",86:"T18 D16",85:"T15 D20",84:"T20 D12",
    83:"T17 D16",82:"Bull D16",81:"T19 D12",80:"T20 D10",79:"T19 D11",
    78:"T18 D12",77:"T19 D10",76:"T20 D8",75:"T17 D12",74:"T14 D16",
    73:"T19 D8",72:"T16 D12",71:"T13 D16",70:"T18 D8",69:"T19 D6",
    68:"T20 D4",67:"T17 D8",66:"T10 D18",65:"T19 D4",64:"T16 D8",
    63:"T13 D12",62:"T10 D16",61:"T15 D8",60:"20 D20",59:"19 D20",
    58:"18 D20",57:"17 D20",56:"16 D20",55:"15 D20",54:"14 D20",
    53:"13 D20",52:"12 D20",51:"11 D20",50:"Bull",49:"17 D16",
    48:"16 D16",47:"15 D16",46:"14 D16",45:"13 D16",44:"12 D16",
    43:"11 D16",42:"10 D16",41:"9 D16",40:"D20",38:"D19",36:"D18",
    34:"D17",32:"D16",30:"D15",28:"D14",26:"D13",24:"D12",22:"D11",
    20:"D10",18:"D9",16:"D8",14:"D7",12:"D6",10:"D5",8:"D4",6:"D3",4:"D2",2:"D1"
}

def board_image(size=650):
    img = Image.new("RGB", (size, size), "#111111")
    d = ImageDraw.Draw(img)
    c = size / 2
    radii = [0.045, 0.09, 0.49, 0.54, 0.78, 0.84]
    rr = [x * size/2 for x in radii]
    colors = ["#d9d9d9", "#222222"]
    red, green = "#c62828", "#16834b"

    # outer background
    d.ellipse((c-rr[5], c-rr[5], c+rr[5], c+rr[5]), fill="#222222")
    for i, num in enumerate(ORDER):
        a0 = math.radians(i*18 - 99)
        a1 = math.radians((i+1)*18 - 99)
        fill = colors[i % 2]
        ring = red if i % 2 == 0 else green
        # Paint from the outside inward so each annular scoring ring stays visible.
        d.pieslice((c-rr[5],c-rr[5],c+rr[5],c+rr[5]), math.degrees(a0), math.degrees(a1), fill=ring)  # double
        d.pieslice((c-rr[4],c-rr[4],c+rr[4],c+rr[4]), math.degrees(a0), math.degrees(a1), fill=fill)  # outer single
        d.pieslice((c-rr[3],c-rr[3],c+rr[3],c+rr[3]), math.degrees(a0), math.degrees(a1), fill=ring)  # treble
        d.pieslice((c-rr[2],c-rr[2],c+rr[2],c+rr[2]), math.degrees(a0), math.degrees(a1), fill=fill)  # inner single
    d.ellipse((c-rr[1],c-rr[1],c+rr[1],c+rr[1]), fill=green)
    d.ellipse((c-rr[0],c-rr[0],c+rr[0],c+rr[0]), fill=red)

    # number ring
    for i, num in enumerate(ORDER):
        ang = math.radians(i*18 - 90)
        x = c + math.cos(ang) * size*0.445
        y = c + math.sin(ang) * size*0.445
        txt = str(num)
        box = d.textbbox((0,0), txt)
        w, h = box[2]-box[0], box[3]-box[1]
        d.text((x-w/2,y-h/2), txt, fill="white")
    return img

def hit_from_xy(x, y, size=650):
    c = size/2
    dx, dy = x-c, y-c
    r = math.hypot(dx,dy)/(size/2)
    if r > .84:
        return ("MISS", 0, False)
    if r <= .045:
        return ("BULL", 50, True)
    if r <= .09:
        return ("25", 25, False)

    # 20 is centred at -90 degrees
    angle = (math.degrees(math.atan2(dy,dx)) + 90 + 9) % 360
    idx = int(angle // 18) % 20
    n = ORDER[idx]

    if .49 < r <= .54:
        return (f"T{n}", n*3, False)
    if .78 < r <= .84:
        return (f"D{n}", n*2, True)
    return (str(n), n, False)

def init_game():
    start = st.session_state.get("start_score", 501)
    mode = st.session_state.get("mode", "1 Player")
    p1 = st.session_state.get("p1_name", "Player 1") or "Player 1"
    p2 = "Bot" if mode == "Vs Bot" else (st.session_state.get("p2_name", "Player 2") or "Player 2")
    st.session_state.game = {
        "scores":[start,start],
        "start":start,
        "names":[p1,p2],
        "turn":0,
        "visit_start":start,
        "visit":[],
        "history":[],
        "darts":[0,0],
        "scored":[0,0],
        "legs":[0,0],
        "winner":None
    }

def ensure_game():
    if "game" not in st.session_state:
        init_game()

def add_dart(label, value, is_double=False, bot=False):
    g=st.session_state.game
    if g["winner"] is not None:
        return
    p=g["turn"]
    before=g["scores"][p]
    after=before-value
    bust = after < 0 or after == 1 or (after == 0 and not is_double)

    record={"player":p,"label":label,"value":value,"double":is_double,"before":before,"bust":bust}
    g["history"].append(record)
    g["visit"].append(record)
    g["darts"][p]+=1

    if bust:
	
        g["scores"][p]=g["visit_start"]
        finish_visit(bot=bot)
        return

    g["scores"][p]=after
    g["scored"][p]+=value

    if after == 0:
        g["winner"]=p
        g["legs"][p]+=1
        return

    if len(g["visit"]) >= 3:
        finish_visit(bot=bot)

def finish_visit(bot=False):
    g=st.session_state.game
    if g["winner"] is not None:
        return
    g["visit"]=[]
    if st.session_state.mode == "1 Player":
        g["visit_start"]=g["scores"][0]
    else:
        g["turn"]=1-g["turn"]
        g["visit_start"]=g["scores"][g["turn"]]

def undo():
    g=st.session_state.game
    if not g["history"]:
        return
    last=g["history"].pop()
    p=last["player"]
    g["winner"]=None
    g["turn"]=p
    g["scores"][p]=last["before"]
    g["darts"][p]=max(0,g["darts"][p]-1)
    if not last["bust"]:
        g["scored"][p]=max(0,g["scored"][p]-last["value"])
    # rebuild current visit from trailing records for same player, max 2
    trailing=[]
    for r in reversed(g["history"]):
        if r["player"] != p or r["bust"]:
            break
        trailing.append(r)
        if len(trailing)==2:
            break
    g["visit"]=list(reversed(trailing))
    g["visit_start"]=g["scores"][p] + sum(r["value"] for r in g["visit"])

def bot_visit():
    g=st.session_state.game
    if st.session_state.mode != "Vs Bot" or g["turn"] != 1 or g["winner"] is not None:
        return
    target={
        "Beginner — ~35 avg":35,
        "Pub Player — ~50 avg":50,
        "Club Player — ~60 avg":60,
        "League Player — ~70 avg":70,
        "Advanced — ~80 avg":80,
        "Pro — ~95 avg":95
    }[st.session_state.bot_level]
    # realistic-ish dart values around target average
    for _ in range(3):
        if g["turn"] != 1 or g["winner"] is not None:
            break
        rem=g["scores"][1]
        # try a double when on an even finish <=40
        if rem <= 40 and rem % 2 == 0:
            chance=min(.65,max(.10,(target-25)/100))
            if random.random() < chance:
                add_dart(f"D{rem//2}", rem, True, bot=True)
            else:
                add_dart("MISS",0,False,bot=True)
        elif rem == 50:
            add_dart("BULL",50,True,bot=True) if random.random()<.25 else add_dart("25",25,False,bot=True)
        else:
            per_dart=target/3
            pool=[0,1,5,20,20,20,19,18,40,45,57,60]
            weights=[2,1,1,8,8,8,4,3,2,2,2,max(1,int(target/12))]
            val=random.choices(pool,weights=weights,k=1)[0]
            # don't intentionally bust
            if val >= rem-1:
                val=random.choice([0,5,20])
            label={60:"T20",57:"T19",45:"T15",40:"D20"}.get(val,str(val) if val else "MISS")
            add_dart(label,val,label.startswith("D"),bot=True)



with tab4:
    st.title("🎯 THE PRACTICE BOARD — SCORER TEST")
    st.caption("Interactive scorer prototype • 1 Player • 2 Players • Vs Bot")

    with st.sidebar:
        st.header("⚙️ Match Setup")
        mode=st.selectbox("Game mode",["1 Player","2 Players","Vs Bot"],key="mode")
        start_score=st.selectbox("Starting score",[501,301],key="start_score")
        p1=st.text_input("Player 1","",key="p1_name")
        if mode=="2 Players":
            st.text_input("Player 2","Player 2",key="p2_name")
        if mode=="Vs Bot":
            st.selectbox("Bot difficulty",[
                "Beginner — ~35 avg",
                "Pub Player — ~50 avg",
                "Club Player — ~60 avg",
                "League Player — ~70 avg",
                "Advanced — ~80 avg",
                "Pro — ~95 avg"
            ],index=3,key="bot_level")
        st.selectbox("Match",["Best of 1","Best of 3","Best of 5","Best of 7"],key="match_len")
        if st.button("🔄 Start / Reset Match"):
            init_game()
            st.rerun()

    ensure_game()
    g=st.session_state.game

    # Sync displayed names without wiping scores
    g["names"][0]=st.session_state.p1_name or "Player 1"
    if mode=="2 Players":
        g["names"][1]=st.session_state.p2_name or "Player 2"
    elif mode=="Vs Bot":
        g["names"][1]=f"Bot ({st.session_state.bot_level})"

    cols=st.columns(2 if mode!="1 Player" else 1)
    for i in range(2 if mode!="1 Player" else 1):
        with cols[i]:
            marker="🎯 " if g["turn"]==i and g["winner"] is None else ""
            st.subheader(f"{marker}{g['names'][i]}")
            st.metric("Remaining",g["scores"][i])
            avg=(g["scored"][i]/g["darts"][i]*3) if g["darts"][i] else 0
            st.caption(f"3-dart avg: {avg:.1f} • Darts: {g['darts'][i]} • Legs: {g['legs'][i]}")
            route=CHECKOUTS.get(g["scores"][i])
            if route:
                st.success(f"Checkout: {route}")

    if g["winner"] is not None:
        st.success(f"🏆 {g['names'][g['winner']]} wins the leg!")

    st.divider()
    left,right=st.columns([1.35,1])

    with left:
        st.subheader("🎯 Tap the dartboard")
        img=board_image()
        click=streamlit_image_coordinates(img,key="dartboard")
        if click:
            sig=(click["x"],click["y"])
            if st.session_state.get("last_click") != sig and g["winner"] is None:
                st.session_state.last_click=sig
                label,value,is_double=hit_from_xy(click["x"],click["y"])
                add_dart(label,value,is_double)
                st.rerun()

    with right:
        st.subheader("Current Visit")
        if g["visit"]:
            for n,dart in enumerate(g["visit"],1):
                st.write(f"**Dart {n}:** {dart['label']} ({dart['value']})")
        else:
            st.write("No darts entered yet.")

        c1,c2=st.columns(2)
        with c1:
            if st.button("❌ MISS / 0"):
                add_dart("MISS",0,False)
                st.rerun()
        with c2:
            if st.button("↩️ UNDO LAST DART"):
                undo()
                st.rerun()

        st.caption("Wrong segment? Tap **Undo Last Dart**, then tap the correct segment. This edits the current visit without restarting the leg.")

        if mode=="Vs Bot" and g["turn"]==1 and g["winner"] is None:
            if st.button("🤖 BOT THROW"):
                bot_visit()
                st.rerun()

        st.divider()
        st.subheader("Visit / Throw History")
        if not g["history"]:
            st.caption("No darts yet.")
        else:
            for item in reversed(g["history"][-12:]):
                who=g["names"][item["player"]]
                bust=" • BUST" if item["bust"] else ""
                st.write(f"{who}: **{item['label']}** ({item['value']}){bust}")

    st.info("🧪 This is the scorer test version. Your main V3 Practice Board file has not been changed.")

with tab4:
    st.header("🎯 Match Scorer")

st.divider()
st.caption(
    "THE PRACTICE BOARD • SMART TRAINING • V4.0"
)
