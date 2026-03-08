import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from streamlit_elements import elements, mui, nivo

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG (must be first)
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Personal Finance Planner", page_icon="💰", layout="wide")

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE DEFAULTS
# ══════════════════════════════════════════════════════════════════════════════
for k, v in {
    "name": "", "age": 30, "salary": 50000, "retirement_age": 60,
    "current_saved": 100000, "history": [], "history_dates": [],
    "chat_history": [], "grand_total": 0
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Portfolio data stored in session state
ASSETS = {
    "Fixed Deposit": {"rate": 6.5,  "color": "#8DA9B3", "risk": "Low"},
    "Bonds":         {"rate": 7.5,  "color": "#40E0D0", "risk": "Low-Moderate"},
    "Stocks":        {"rate": 12.0, "color": "#367588", "risk": "High"},
    "Mutual Funds":  {"rate": 10.0, "color": "#9BBBCC", "risk": "Moderate-High"},
    "ETFs":          {"rate": 9.0,  "color": "#AEC6CF", "risk": "Moderate"},
    "Gold":          {"rate": 8.0,  "color": "#C2B280", "risk": "Moderate"},
}
if "portfolio" not in st.session_state:
    st.session_state.portfolio = {a: {"amount": 0, "return": d["rate"], "color": d["color"]} for a, d in ASSETS.items()}
if "total_sip" not in st.session_state:
    st.session_state.total_sip = 0
if "weighted_return" not in st.session_state:
    st.session_state.weighted_return = 0.0

# ══════════════════════════════════════════════════════════════════════════════
# 3D THEME (unchanged)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* Paste your entire CSS theme here – it's unchanged */
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700;900&family=Raleway:wght@300;400;500;600;700&display=swap');
:root {
  --yankees:#1C2841; --yankees2:#141d31; --teal:#367588; --pewter:#8DA9B3;
  --pastel:#AEC6CF;  --columbia:#9BBBCC; --turquoise:#40E0D0;
  --pearl:#F0EAD6;   --vanilla:#F3E5AB;  --sand:#C2B280;  --cream:#FFFDD0;
  --walnut:#6B4226;  --mocha:#3D1C02;
}
html,body,[class*="css"]{font-family:'Raleway',sans-serif!important;color:var(--pearl)!important;}
.stApp{
  background:
    radial-gradient(ellipse at 18% 8%, rgba(54,117,136,.25) 0%,transparent 52%),
    radial-gradient(ellipse at 82% 92%,rgba(64,224,208,.12) 0%,transparent 48%),
    radial-gradient(ellipse at 50% 50%,rgba(28,40,65,.97)   0%,#141d31 100%);
  background-attachment:fixed;
}
.stApp::before{content:'';position:fixed;inset:0;pointer-events:none;z-index:0;
  background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.035'/%3E%3C/svg%3E");}
h1{font-family:'Cinzel',serif!important;font-weight:900!important;font-size:2.6rem!important;
   background:linear-gradient(135deg,var(--turquoise) 0%,var(--columbia) 45%,var(--vanilla) 100%)!important;
   -webkit-background-clip:text!important;-webkit-text-fill-color:transparent!important;
   letter-spacing:.04em!important;filter:drop-shadow(0 4px 14px rgba(64,224,208,.38));}
h2,h3{font-family:'Cinzel',serif!important;font-weight:700!important;color:var(--pastel)!important;letter-spacing:.03em!important;}
h4,h5,h6{font-family:'Raleway',sans-serif!important;font-weight:600!important;color:var(--columbia)!important;letter-spacing:.06em!important;}
.stMarkdown h5{color:var(--columbia)!important;font-size:.75rem!important;letter-spacing:.12em!important;
  font-weight:700!important;text-transform:uppercase!important;font-family:'Raleway',sans-serif!important;
  padding-bottom:6px!important;border-bottom:1px solid rgba(141,169,179,.25)!important;margin-bottom:14px!important;}
.stMarkdown p{color:var(--pearl)!important;} .stMarkdown strong{color:var(--vanilla)!important;}
.stTabs [data-baseweb="tab-list"]{background:linear-gradient(180deg,rgba(28,40,65,.92),rgba(20,29,49,.97))!important;
  border-radius:18px 18px 0 0!important;border:1px solid rgba(141,169,179,.22)!important;border-bottom:none!important;
  padding:6px 6px 0!important;gap:4px!important;box-shadow:0 -4px 18px rgba(0,0,0,.45),inset 0 1px 0 rgba(255,255,255,.06)!important;backdrop-filter:blur(14px);}
.stTabs [data-baseweb="tab"]{font-family:'Raleway',sans-serif!important;font-weight:600!important;font-size:.8rem!important;
  letter-spacing:.07em!important;text-transform:uppercase!important;color:var(--pewter)!important;
  background:transparent!important;border-radius:12px 12px 0 0!important;padding:10px 18px!important;
  border:1px solid transparent!important;transition:all .25s ease!important;}
.stTabs [data-baseweb="tab"]:hover{color:var(--turquoise)!important;background:rgba(64,224,208,.07)!important;
  transform:translateY(-2px);box-shadow:0 -4px 14px rgba(64,224,208,.15)!important;}
.stTabs [aria-selected="true"]{color:var(--cream)!important;
  background:linear-gradient(180deg,rgba(54,117,136,.48),rgba(28,40,65,.82))!important;
  border-color:rgba(141,169,179,.28) rgba(141,169,179,.28) transparent!important;
  box-shadow:0 -6px 22px rgba(64,224,208,.22),inset 0 1px 0 rgba(255,255,255,.14)!important;}
.stTabs [data-baseweb="tab-panel"]{background:linear-gradient(180deg,rgba(18,26,46,.98),rgba(28,40,65,.94))!important;
  border:1px solid rgba(141,169,179,.18)!important;border-top:none!important;
  border-radius:0 18px 18px 18px!important;padding:28px 24px!important;
  box-shadow:6px 14px 34px rgba(0,0,0,.65),inset 0 1px 0 rgba(255,255,255,.04)!important;backdrop-filter:blur(18px);}
[data-testid="stMetric"]{background:linear-gradient(145deg,rgba(54,117,136,.20),rgba(28,40,65,.88) 55%,rgba(18,26,46,.96))!important;
  border:1px solid rgba(141,169,179,.28)!important;border-radius:16px!important;padding:18px 20px!important;
  box-shadow:6px 7px 18px rgba(0,0,0,.52),-2px -2px 8px rgba(255,255,255,.04),inset 0 1px 0 rgba(255,255,255,.1),inset 0 -1px 0 rgba(0,0,0,.28)!important;
  transform:perspective(600px) rotateX(2.5deg);transition:all .3s cubic-bezier(.34,1.56,.64,1)!important;position:relative;overflow:hidden;}
[data-testid="stMetric"]::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,transparent,var(--turquoise),transparent);opacity:.55;}
[data-testid="stMetric"]:hover{transform:perspective(600px) rotateX(0deg) translateY(-5px) scale(1.025)!important;
  box-shadow:8px 18px 36px rgba(0,0,0,.62),0 0 26px rgba(64,224,208,.16),inset 0 1px 0 rgba(255,255,255,.14)!important;
  border-color:rgba(64,224,208,.38)!important;}
[data-testid="stMetricLabel"]{color:var(--pewter)!important;font-size:.7rem!important;font-weight:600!important;letter-spacing:.1em!important;text-transform:uppercase!important;}
[data-testid="stMetricValue"]{color:var(--vanilla)!important;font-family:'Cinzel',serif!important;font-weight:700!important;font-size:1.45rem!important;text-shadow:0 2px 10px rgba(0,0,0,.45)!important;}
[data-testid="stMetricDelta"]{color:var(--turquoise)!important;font-size:.76rem!important;}
[data-testid="stNumberInput"]>div,[data-testid="stTextInput"]>div,[data-testid="stTextareaInput"]>div{
  background:linear-gradient(145deg,rgba(18,26,46,.92),rgba(28,40,65,.82))!important;
  border:1px solid rgba(141,169,179,.28)!important;border-radius:12px!important;
  box-shadow:inset 3px 3px 9px rgba(0,0,0,.42),inset -1px -1px 4px rgba(255,255,255,.04),0 2px 5px rgba(0,0,0,.3)!important;transition:all .2s ease!important;}
[data-testid="stNumberInput"]>div:focus-within,[data-testid="stTextInput"]>div:focus-within,
[data-testid="stTextareaInput"]>div:focus-within{border-color:rgba(64,224,208,.48)!important;
  box-shadow:inset 3px 3px 9px rgba(0,0,0,.42),0 0 0 3px rgba(64,224,208,.1),0 0 18px rgba(64,224,208,.14)!important;}
input[type="number"],input[type="text"],textarea{color:var(--cream)!important;background:transparent!important;
  font-family:'Raleway',sans-serif!important;font-weight:500!important;}
[data-testid="stSlider"]>div>div>div{background:linear-gradient(90deg,var(--teal),var(--turquoise))!important;box-shadow:0 2px 10px rgba(64,224,208,.42)!important;}
[data-testid="stSlider"] [role="slider"]{background:linear-gradient(145deg,var(--cream),var(--vanilla))!important;
  border:2px solid var(--turquoise)!important;
  box-shadow:3px 4px 10px rgba(0,0,0,.5),-1px -1px 4px rgba(255,255,255,.14),0 0 14px rgba(64,224,208,.32)!important;width:20px!important;height:20px!important;}
[data-testid="stSelectbox"]>div>div{background:linear-gradient(145deg,rgba(18,26,46,.92),rgba(28,40,65,.88))!important;
  border:1px solid rgba(141,169,179,.28)!important;border-radius:12px!important;color:var(--cream)!important;
  box-shadow:inset 2px 2px 7px rgba(0,0,0,.38),0 2px 8px rgba(0,0,0,.3)!important;}
[data-testid="stExpander"]{background:linear-gradient(145deg,rgba(28,40,65,.68),rgba(18,26,46,.92))!important;
  border:1px solid rgba(141,169,179,.18)!important;border-radius:14px!important;margin-bottom:10px!important;
  box-shadow:4px 6px 18px rgba(0,0,0,.42),inset 0 1px 0 rgba(255,255,255,.06)!important;overflow:hidden;transition:all .25s ease!important;}
[data-testid="stExpander"]:hover{border-color:rgba(64,224,208,.22)!important;box-shadow:4px 6px 22px rgba(0,0,0,.52),0 0 14px rgba(64,224,208,.07)!important;}
[data-testid="stExpander"] summary{color:var(--pastel)!important;font-weight:600!important;font-size:.86rem!important;padding:12px 16px!important;letter-spacing:.05em;}
[data-testid="stExpander"] summary:hover{color:var(--turquoise)!important;}
.stButton>button{font-family:'Raleway',sans-serif!important;font-weight:700!important;font-size:.8rem!important;
  letter-spacing:.09em!important;text-transform:uppercase!important;color:var(--yankees)!important;
  background:linear-gradient(145deg,var(--turquoise),var(--teal))!important;border:none!important;border-radius:12px!important;padding:10px 20px!important;
  box-shadow:4px 6px 18px rgba(0,0,0,.52),-1px -1px 4px rgba(255,255,255,.1),inset 0 1px 0 rgba(255,255,255,.22),inset 0 -2px 0 rgba(0,0,0,.22)!important;
  transform:perspective(400px) rotateX(4deg);transition:all .22s cubic-bezier(.34,1.56,.64,1)!important;}
.stButton>button:hover{background:linear-gradient(145deg,#5ef5e5,var(--turquoise))!important;
  transform:perspective(400px) rotateX(0deg) translateY(-3px)!important;box-shadow:6px 14px 28px rgba(0,0,0,.62),0 0 22px rgba(64,224,208,.38)!important;}
.stButton>button:active{transform:perspective(400px) rotateX(7deg) translateY(2px)!important;box-shadow:2px 3px 9px rgba(0,0,0,.52),inset 0 2px 4px rgba(0,0,0,.3)!important;}
[data-testid="stProgressBar"]>div{background:rgba(28,40,65,.82)!important;border:1px solid rgba(141,169,179,.18)!important;
  border-radius:20px!important;box-shadow:inset 2px 2px 7px rgba(0,0,0,.42)!important;height:10px!important;}
[data-testid="stProgressBar"]>div>div{background:linear-gradient(90deg,var(--teal),var(--turquoise),var(--pastel))!important;
  border-radius:20px!important;box-shadow:0 2px 10px rgba(64,224,208,.42),inset 0 1px 0 rgba(255,255,255,.2)!important;}
[data-testid="stSuccess"]{background:linear-gradient(135deg,rgba(64,224,208,.1),rgba(54,117,136,.14))!important;border:1px solid rgba(64,224,208,.32)!important;border-radius:14px!important;color:var(--turquoise)!important;}
[data-testid="stWarning"]{background:linear-gradient(135deg,rgba(194,178,128,.1),rgba(107,66,38,.14))!important;border:1px solid rgba(194,178,128,.32)!important;border-radius:14px!important;color:var(--vanilla)!important;}
[data-testid="stError"]{background:linear-gradient(135deg,rgba(107,66,38,.18),rgba(61,28,2,.24))!important;border:1px solid rgba(107,66,38,.42)!important;border-radius:14px!important;color:var(--sand)!important;}
[data-testid="stInfo"]{background:linear-gradient(135deg,rgba(141,169,179,.1),rgba(54,117,136,.11))!important;border:1px solid rgba(141,169,179,.28)!important;border-radius:14px!important;color:var(--pastel)!important;}
[data-testid="stDataFrame"]{background:linear-gradient(145deg,rgba(18,26,46,.97),rgba(28,40,65,.92))!important;
  border:1px solid rgba(141,169,179,.18)!important;border-radius:14px!important;overflow:hidden!important;box-shadow:4px 8px 22px rgba(0,0,0,.55)!important;}
hr{border-color:rgba(141,169,179,.18)!important;}
label,.stTextInput label,.stNumberInput label,.stSelectbox label,.stSlider label{
  color:var(--pewter)!important;font-size:.76rem!important;font-weight:600!important;letter-spacing:.08em!important;text-transform:uppercase!important;}
small,.stCaption,[data-testid="stCaptionContainer"] p{color:var(--pewter)!important;font-style:italic;}
::-webkit-scrollbar{width:6px;height:6px;}::-webkit-scrollbar-track{background:var(--yankees2);}
::-webkit-scrollbar-thumb{background:linear-gradient(var(--teal),var(--pewter));border-radius:10px;}
::-webkit-scrollbar-thumb:hover{background:var(--turquoise);}
[data-testid="stCheckbox"] label{color:var(--pastel)!important;font-weight:500!important;text-transform:none!important;font-size:.88rem!important;}
.block-container{padding-top:2rem!important;padding-bottom:2rem!important;}
.chat-user{background:linear-gradient(135deg,#1C2841,#0d1a2e);padding:12px 16px;border-radius:18px 18px 6px 18px;
  margin:8px 0;border:1px solid rgba(64,224,208,.25);text-align:right;}
.chat-ai{background:linear-gradient(135deg,#0d1a2e,#1C2841);padding:12px 16px;border-radius:18px 18px 18px 6px;
  margin:8px 0;border:1px solid rgba(155,187,204,.25);}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
def fmt(amount: float) -> str:
    a = abs(float(amount))
    sign = "-" if amount < 0 else ""
    if a >= 10_000_000: return f"{sign}Rs {a/10_000_000:.2f} Cr"
    if a >= 100_000:    return f"{sign}Rs {a/100_000:.2f} L"
    return f"{sign}Rs {a:,.0f}"

def calculate_sip(monthly: float, annual_rate: float, years: int):
    if annual_rate == 0 or monthly == 0:
        t = monthly * years * 12; return t, t
    r = annual_rate / 12 / 100
    n = years * 12
    fv = monthly * (((1 + r) ** n - 1) / r) * (1 + r)
    return fv, monthly * n

def calculate_step_up_sip(monthly: float, annual_rate: float, years: int, step_up: float = 0):
    if annual_rate == 0:
        t = monthly * years * 12; return t, t
    r = annual_rate / 12 / 100
    fv = invested = 0.0
    sip = monthly
    for _ in range(years):
        fv = fv * (1 + r) ** 12 + sip * (((1 + r) ** 12 - 1) / r)
        invested += sip * 12
        sip *= (1 + step_up / 100)
    return fv, invested

# ══════════════════════════════════════════════════════════════════════════════
# MOCK AI ADVISOR (no API key needed)
# ══════════════════════════════════════════════════════════════════════════════
class MockFinanceAIChat:
    """Simple rule‑based chatbot that uses the user's financial data."""

    def get_advice(self, query: str, user_data: dict) -> str:
        """Generate a response based on the query and user data."""
        query_lower = query.lower()

        # FIRE / retirement related
        if "fire" in query_lower or "retire" in query_lower:
            if user_data.get("fire_number", 0) > 0:
                progress = user_data.get("fire_progress", 0) * 100
                return (f"Your FIRE number is **{fmt(user_data['fire_number'])}**. "
                        f"You are **{progress:.1f}%** there. "
                        f"{'Keep going!' if progress < 100 else 'Congratulations, you have reached your goal!'}")
            else:
                return "To calculate your FIRE number, please fill in your expenses and portfolio in the other tabs."

        # SIP / investment related
        if "sip" in query_lower or "invest" in query_lower:
            monthly = user_data.get("monthly_sip", 0)
            if monthly > 0:
                ret = user_data.get("portfolio_return", 0)
                years = max(60 - user_data.get("age", 30), 1)
                future, _ = calculate_sip(monthly, ret, years)
                return (f"You currently invest **{fmt(monthly)}** per month at an expected return of **{ret:.1f}%**. "
                        f"In {years} years (at age 60) this could grow to approximately **{fmt(future)}**.")
            else:
                return "You haven't entered any SIP amounts yet. Go to the **Portfolio** tab to add your monthly investments."

        # Savings / corpus related
        if "saving" in query_lower or "corpus" in query_lower:
            saved = user_data.get("savings", 0)
            return f"Your current savings / corpus is **{fmt(saved)}**. " + (
                "Great start!" if saved > 0 else "Consider building an emergency fund first."
            )

        # Expense related
        if "expense" in query_lower or "spend" in query_lower:
            expenses = user_data.get("expenses", 0)
            income = user_data.get("salary", 0)
            if income > 0:
                pct = (expenses / income) * 100
                return (f"Your monthly expenses are **{fmt(expenses)}**, which is **{pct:.1f}%** of your income. "
                        f"{'Try to keep expenses below 70% for healthy savings.' if pct > 70 else 'Good control over expenses!'}")
            else:
                return f"Your monthly expenses are **{fmt(expenses)}**. Add your salary in the Profile tab for more insights."

        # General tips
        if "tip" in query_lower or "advice" in query_lower or "suggest" in query_lower:
            return ("Here are some general tips:\n"
                    "- Save at least 20% of your income.\n"
                    "- Maintain an emergency fund of 6 months' expenses.\n"
                    "- Diversify your investments across asset classes.\n"
                    "- Review your portfolio annually.")

        # Default fallback
        return ("I can help with questions about FIRE, SIP, expenses, savings, or general financial tips. "
                "Please ask something specific, or click one of the suggested questions below.")

    def analyze_portfolio(self, portfolio_data: dict) -> str:
        """Give a simple analysis of the portfolio."""
        total = sum(d["amount"] for d in portfolio_data.values())
        if total == 0:
            return "No investments entered yet. Add some in the Portfolio tab."

        # Count asset classes
        active = [a for a, d in portfolio_data.items() if d["amount"] > 0]
        num_assets = len(active)

        # Risk assessment based on assets
        high_risk = any(ASSETS[a]["risk"] == "High" for a in active)
        low_risk = all(ASSETS[a]["risk"] in ["Low", "Low-Moderate"] for a in active)

        analysis = f"**Portfolio Analysis**\n\n"
        analysis += f"You have {num_assets} asset class{'es' if num_assets != 1 else ''}."
        if num_assets < 3:
            analysis += " Consider diversifying into more asset types.\n"
        else:
            analysis += " Good diversification.\n"

        if high_risk:
            analysis += " Your portfolio includes high‑risk assets – suitable for long‑term growth but volatile.\n"
        if low_risk:
            analysis += " Your portfolio is mostly low‑risk – safe but may not beat inflation.\n"

        # Suggest improvement
        analysis += "\n**Suggestion:** "
        if total < 5000:
            analysis += "Try to increase your monthly SIP amount."
        elif num_assets < 3:
            analysis += "Add one more asset class (e.g., Bonds or Gold) for balance."
        else:
            analysis += "Your portfolio looks balanced. Keep monitoring regularly."

        return analysis

# Instantiate the mock AI
if "ai_chat" not in st.session_state:
    st.session_state.ai_chat = MockFinanceAIChat()

# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════
PALETTE = ["#40E0D0", "#367588", "#9BBBCC", "#AEC6CF", "#8DA9B3", "#C2B280",
           "#F3E5AB", "#FFFDD0", "#F0EAD6", "#6B4226", "#3D1C02"]
CHART_THEME = {
    "background": "transparent",
    "textColor": "#8DA9B3",
    "fontSize": 12,
    "grid": {"line": {"stroke": "rgba(141,169,179,0.12)"}},
    "tooltip": {
        "container": {
            "background": "#0d1a2e",
            "color": "#F0EAD6",
            "fontSize": "13px",
            "borderRadius": "10px",
            "border": "1px solid rgba(64,224,208,0.28)"
        }
    }
}
RISK_W = {"Low": 0.2, "Low-Moderate": 0.4, "Moderate": 0.6, "Moderate-High": 0.8, "High": 1.0}

# ══════════════════════════════════════════════════════════════════════════════
# TITLE & TABS
# ══════════════════════════════════════════════════════════════════════════════
st.title("💰 Personal Finance Planner")
st.caption("Plan your FIRE journey · Track investments · Visualize portfolio growth")

tab0, tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "👤 Profile", "🧾 Expenses", "📊 Portfolio",
    "📈 Projections", "📜 History", "💡 Insights", "🤖 AI Advisor"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 0 – PROFILE
# ══════════════════════════════════════════════════════════════════════════════
with tab0:
    st.subheader("Your Profile")
    l0, r0 = st.columns([1, 1.6], gap="large")
    with l0:
        st.markdown("##### 👤 Basic Info")
        st.session_state.name = st.text_input("Full Name", value=st.session_state.name)
        st.session_state.age = st.number_input("Current Age", min_value=18, max_value=80,
                                                value=int(st.session_state.age))
        st.session_state.salary = st.number_input("Monthly Salary (Rs)", min_value=0, step=1000,
                                                   value=int(st.session_state.salary))
        st.session_state.retirement_age = st.number_input("Retirement Age", min_value=40, max_value=80,
                                                           value=int(st.session_state.retirement_age))
        st.divider()
        st.markdown("##### 💰 Current Savings")
        st.session_state.current_saved = st.number_input("Total Savings / Existing Corpus (Rs)",
                                                          min_value=0, step=10000,
                                                          value=int(st.session_state.current_saved))
    with r0:
        yrs_left = max(int(st.session_state.retirement_age) - int(st.session_state.age), 0)
        if st.session_state.name:
            st.success(f"👋 Welcome, {st.session_state.name}! {yrs_left} years until traditional retirement.")
        st.info("ℹ️ Your FIRE number is auto‑calculated in **📊 Portfolio** once you fill Expenses and Portfolio.")
        p1, p2, p3 = st.columns(3)
        p1.metric("Current Age", int(st.session_state.age))
        p2.metric("Retirement Age", int(st.session_state.retirement_age))
        p3.metric("Years to Retirement", yrs_left)
        st.divider()
        st.metric("Current Corpus", fmt(st.session_state.current_saved))
        if st.session_state.salary > 0:
            st.metric("Monthly Income", fmt(st.session_state.salary))

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 – EXPENSES (simplified, you can expand as needed)
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.header("🧾 Monthly Expense Calculator")
    l1, r1 = st.columns([1, 1.6], gap="large")
    with l1:
        housing = st.number_input("Housing (Rent/Mortgage)", 0, step=500, key="exp_housing")
        utilities = st.number_input("Utilities", 0, step=500, key="exp_utils")
        food = st.number_input("Food", 0, step=500, key="exp_food")
        transport = st.number_input("Transport", 0, step=500, key="exp_transport")
        health = st.number_input("Health/Insurance", 0, step=500, key="exp_health")
        debt = st.number_input("Debt Payments", 0, step=500, key="exp_debt")
        entertainment = st.number_input("Entertainment", 0, step=500, key="exp_entertain")
        misc = st.number_input("Miscellaneous", 0, step=500, key="exp_misc")
        grand_total = housing + utilities + food + transport + health + debt + entertainment + misc
        st.session_state.grand_total = grand_total

    with r1:
        st.metric("Total Monthly Expenses", fmt(grand_total))
        if st.session_state.salary > 0:
            savings = st.session_state.salary - grand_total
            rate = savings / st.session_state.salary * 100
            st.metric("Net Savings", fmt(max(savings, 0)), delta=f"{rate:.1f}% of income")
            if savings < 0:
                st.error("⚠️ Overspending!")
            elif rate < 20:
                st.warning("💡 Try to save at least 20%.")
            else:
                st.success("✅ Good saving rate!")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 – PORTFOLIO (with FIRE calculation)
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.header("📊 Asset Allocation")
    l2, r2 = st.columns([1, 1.6], gap="large")

    with l2:
        st.markdown("##### Enter Monthly Investments")
        total = 0
        weighted_sum = 0.0
        for asset, details in ASSETS.items():
            st.markdown(f"**{asset}**  ")
            st.caption(f"Risk: {details['risk']} | Default Return: {details['rate']}%")
            col1, col2 = st.columns(2)
            with col1:
                amt = st.number_input(
                    f"{asset} monthly (Rs)", min_value=0, step=500,
                    key=f"port_{asset}_amt", label_visibility="collapsed",
                    value=int(st.session_state.portfolio[asset]["amount"])
                )
            with col2:
                ret = st.slider(
                    f"{asset} return %", 0.0, 20.0,
                    value=float(st.session_state.portfolio[asset]["return"]),
                    step=0.5, key=f"port_{asset}_ret", format="%.1f%%",
                    label_visibility="collapsed"
                )
            st.session_state.portfolio[asset]["amount"] = amt
            st.session_state.portfolio[asset]["return"] = ret
            total += amt
            weighted_sum += amt * ret

        st.session_state.total_sip = total
        if total > 0:
            st.session_state.weighted_return = weighted_sum / total
        else:
            st.session_state.weighted_return = 0.0

    with r2:
        if st.session_state.total_sip > 0:
            future_10yr, _ = calculate_sip(st.session_state.total_sip,
                                            st.session_state.weighted_return, 10)
            cola, colb, colc = st.columns(3)
            cola.metric("Monthly SIP", fmt(st.session_state.total_sip))
            colb.metric("Weighted Return", f"{st.session_state.weighted_return:.1f}%")
            colc.metric("10‑Year Value", fmt(future_10yr))

            # Simple pie chart
            with elements("portfolio_pie"):
                with mui.Box(sx={"height": 300}):
                    data = [{"id": a, "value": d["amount"]}
                            for a, d in st.session_state.portfolio.items() if d["amount"] > 0]
                    if data:
                        nivo.Pie(
                            data=data,
                            margin={"top": 20, "right": 20, "bottom": 60, "left": 20},
                            innerRadius=0.65,
                            padAngle=1.5,
                            cornerRadius=8,
                            colors=PALETTE,
                            theme=CHART_THEME,
                            enableArcLinkLabels=False,
                            enableArcLabels=True,
                            arcLabelsTextColor="#1C2841"
                        )
        else:
            st.info("👈 Enter investment amounts to see charts.")

    # FIRE calculator (simplified)
    st.divider()
    st.markdown("### 🔥 FIRE Calculator")
    mexp = st.session_state.grand_total
    if mexp == 0:
        st.warning("Fill in expenses first.")
    elif st.session_state.total_sip == 0:
        st.warning("Add investments above.")
    else:
        fire_swr = st.slider("Safe Withdrawal Rate (%)", 2.0, 6.0, 4.0, 0.5)
        fire_number = (mexp * 12 / fire_swr) * 100
        st.metric("Your FIRE Number", fmt(fire_number))
        st.session_state["fire_number"] = fire_number
        st.session_state["fire_progress"] = min(st.session_state.current_saved / fire_number, 1.0) if fire_number > 0 else 0

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 – PROJECTIONS (simplified)
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.header("📈 Growth Projections")
    if st.session_state.total_sip > 0 and st.session_state.weighted_return > 0:
        years = st.slider("Projection years", 1, 40, 20)
        values, invested = calculate_sip(st.session_state.total_sip,
                                          st.session_state.weighted_return, years)
        st.metric("Final Corpus", fmt(values), delta=f"Invested: {fmt(invested)}")
    else:
        st.info("Add investments in the Portfolio tab first.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 – HISTORY
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.header("📜 Investment History")
    cola, colb = st.columns(2)
    with cola:
        add_amt = st.number_input("Add entry (Rs)", min_value=0, step=500, key="hist_add")
        if st.button("➕ Add"):
            if add_amt > 0:
                st.session_state.history.append(int(add_amt))
                st.session_state.history_dates.append(datetime.now().strftime("%Y-%m-%d"))
                st.rerun()
    with colb:
        if st.button("🗑 Clear"):
            st.session_state.history = []
            st.session_state.history_dates = []
            st.rerun()

    if st.session_state.history:
        df = pd.DataFrame({"Date": st.session_state.history_dates,
                           "Amount": st.session_state.history})
        df["Cumulative"] = df["Amount"].cumsum()
        st.dataframe(df, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 – INSIGHTS (simplified)
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.header("💡 Insights")
    if st.session_state.total_sip > 0:
        st.metric("Current Monthly SIP", fmt(st.session_state.total_sip))
        st.metric("Portfolio Return", f"{st.session_state.weighted_return:.1f}%")
        # Simple risk assessment
        active_assets = [a for a, d in st.session_state.portfolio.items() if d["amount"] > 0]
        if len(active_assets) < 3:
            st.warning("Consider adding more asset classes for diversification.")
        else:
            st.success("Good diversification.")
    else:
        st.info("Enter investments to see insights.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 – AI ADVISOR (mock chatbot, no API needed)
# ══════════════════════════════════════════════════════════════════════════════
with tab6:
    st.header("🤖 AI Financial Advisor")
    st.caption("Ask me anything about your finances – no API key required!")

    # Prepare user data dictionary for the bot
    user_data = {
        "age": st.session_state.age,
        "salary": st.session_state.salary,
        "expenses": st.session_state.grand_total,
        "savings": st.session_state.current_saved,
        "fire_number": st.session_state.get("fire_number", 0),
        "fire_progress": st.session_state.get("fire_progress", 0),
        "monthly_sip": st.session_state.total_sip,
        "portfolio_return": st.session_state.weighted_return,
    }

    chat_col, info_col = st.columns([1.2, 0.8], gap="large")

    with chat_col:
        st.markdown("##### 💬 Chat with AI Advisor")
        with st.container(height=320):
            if not st.session_state.chat_history:
                st.info("👋 Start a conversation! Ask about FIRE, SIP, expenses, or get a tip.")
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    st.markdown(
                        f"<div class='chat-user'>"
                        f"<span style='color:#40E0D0;font-size:.78rem;font-weight:600'>YOU</span><br>"
                        f"<span style='color:#F0EAD6'>{msg['content']}</span></div>",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"<div class='chat-ai'>"
                        f"<span style='color:#9BBBCC;font-size:.78rem;font-weight:600'>🤖 AI ADVISOR</span><br>"
                        f"<span style='color:#F3E5AB'>{msg['content']}</span></div>",
                        unsafe_allow_html=True
                    )

        user_q = st.text_area("Ask a question:",
                              placeholder="E.g., Am I on track for FIRE? How's my portfolio?",
                              height=90, key="ai_question")
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("🚀 Send", use_container_width=True):
                if user_q.strip():
                    st.session_state.chat_history.append({"role": "user", "content": user_q})
                    with st.spinner("Thinking…"):
                        resp = st.session_state.ai_chat.get_advice(user_q, user_data)
                    st.session_state.chat_history.append({"role": "assistant", "content": resp})
                    st.rerun()
        with b2:
            if st.button("🗑 Clear Chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
        with b3:
            if st.button("💡 Quick Tip", use_container_width=True):
                tip_q = "Give me a quick financial tip."
                st.session_state.chat_history.append({"role": "user", "content": tip_q})
                with st.spinner("Getting tip…"):
                    resp = st.session_state.ai_chat.get_advice(tip_q, user_data)
                st.session_state.chat_history.append({"role": "assistant", "content": resp})
                st.rerun()

    with info_col:
        st.markdown("##### 📊 Your Snapshot")
        for lbl, val, emoji in [
            ("Age", str(user_data["age"]), "👤"),
            ("Monthly Income", fmt(user_data["salary"]), "💰"),
            ("Monthly Expenses", fmt(user_data["expenses"]), "💳"),
            ("Current Savings", fmt(user_data["savings"]), "🏦"),
            ("Monthly SIP", fmt(user_data["monthly_sip"]), "📈"),
            ("FIRE Progress", f"{user_data['fire_progress']*100:.1f}%", "🔥"),
        ]:
            st.markdown(
                f"<div style='background:linear-gradient(135deg,#1C2841,#0d1a2e);"
                f"padding:11px 14px;border-radius:12px;margin-bottom:9px;"
                f"border-left:3px solid #40E0D0;box-shadow:3px 5px 14px rgba(0,0,0,.45)'>"
                f"<span style='color:#8DA9B3;font-size:.77rem'>{emoji} {lbl}</span><br>"
                f"<span style='color:#F3E5AB;font-size:1.15rem;font-weight:700'>{val}</span></div>",
                unsafe_allow_html=True
            )
        st.divider()
        st.markdown("##### 🔍 Portfolio Analysis")
        if st.button("Analyze My Portfolio", use_container_width=True):
            with st.spinner("Analyzing…"):
                analysis = st.session_state.ai_chat.analyze_portfolio(st.session_state.portfolio)
            st.session_state.chat_history.append({"role": "user", "content": "Please analyze my portfolio."})
            st.session_state.chat_history.append({"role": "assistant", "content": analysis})
            st.rerun()
        st.divider()
        st.markdown("##### 💭 Suggested Questions")
        for sugg in [
            "How can I optimize my investments?",
            "Am I on track for early retirement?",
            "Should I increase my SIP amount?",
            "How is my portfolio diversification?",
            "What should my emergency fund size be?",
        ]:
            if st.button(f"💬 {sugg}", use_container_width=True, key=f"sug_{sugg}"):
                st.session_state.chat_history.append({"role": "user", "content": sugg})
                with st.spinner("Getting answer…"):
                    resp = st.session_state.ai_chat.get_advice(sugg, user_data)
                st.session_state.chat_history.append({"role": "assistant", "content": resp})
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.divider()
_, fc, _ = st.columns(3)
with fc:
    if st.button("🔄 Reset All Data", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
st.markdown(
    "<p style='text-align:center;color:#8DA9B3;font-size:.74rem;font-style:italic;margin-top:8px'>"
    "⚠️ Disclaimer: Estimated projections only. Actual returns may vary.</p>",
    unsafe_allow_html=True
)