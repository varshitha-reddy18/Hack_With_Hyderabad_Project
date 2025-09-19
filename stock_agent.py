#//////////////////BY TEAM DEBUG DEVILS
import streamlit as st
import pandas as pd

# ==============================
# 🎨 Streamlit Page Config
# ==============================
st.set_page_config(
    page_title="Stock Consultant Agent",
    page_icon="📈",
    layout="wide"
)

# Custom CSS for background + colorful cards
page_bg = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: linear-gradient(to right, #2c3e50, #4ca1af);
    background-size: cover;
}
[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}
.advice-card {
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 10px;
    font-size: 16px;
    font-weight: bold;
    color: white;
}
.reduce {background-color: #e74c3c;}
.add {background-color: #3498db;}
.hold {background-color: #2ecc71;}
.diversify {background-color: #f1c40f; color: black;}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# ==============================
# 📌 Usage Counters
# ==============================
if "usage" not in st.session_state:
    st.session_state.usage = {"portfolios": 0, "advice": 0}

# ==============================
# 📂 File Upload
# ==============================
st.title("📊 Stock Market Consultant Agent")
st.write("Upload your **portfolio CSV** (symbol, quantity, buy_price)")

uploaded_file = st.file_uploader("Upload Portfolio CSV", type=["csv"])
market_file = st.file_uploader("Upload Market Data CSV", type=["csv"])

if uploaded_file and market_file:
    portfolio = pd.read_csv(uploaded_file)
    market = pd.read_csv(market_file)

    # Merge portfolio with market data
    df = pd.merge(portfolio, market, on="symbol", how="left")
    df["current_value"] = df["quantity"] * df["price"]
    df["invested_value"] = df["quantity"] * df["buy_price"]
    df["profit_loss_pct"] = ((df["price"] - df["buy_price"]) / df["buy_price"]) * 100

    # Update usage
    st.session_state.usage["portfolios"] += 1

    st.subheader("📈 Portfolio Analysis")
    st.dataframe(df)

    st.subheader("💡 Investment Advice")
    advice_list = []

    total_value = df["current_value"].sum()
    sector_split = df.groupby("sector")["current_value"].sum() / total_value * 100

    for _, row in df.iterrows():
        if row["current_value"] / total_value > 0.35:
            advice_list.append(("reduce", f"{row['symbol']} is {row['current_value']/total_value:.0%} of portfolio → High risk, consider reducing."))
        elif row["profit_loss_pct"] > 20:
            advice_list.append(("reduce", f"{row['symbol']} gained {row['profit_loss_pct']:.1f}% → Book partial profits."))
        elif row["profit_loss_pct"] < -15:
            advice_list.append(("reduce", f"{row['symbol']} lost {row['profit_loss_pct']:.1f}% → Consider exit."))
        else:
            advice_list.append(("hold", f"{row['symbol']} is stable → Hold."))

    if len(sector_split) < 3:
        missing = {"Banking", "IT", "Energy", "FMCG", "Transport"} - set(df["sector"])
        if missing:
            advice_list.append(("diversify", f"Your portfolio lacks {', '.join(list(missing)[:2])} sector(s) → Diversify."))

    # Show advice as colored cards
    for typ, msg in advice_list:
        st.markdown(f"<div class='advice-card {typ}'>{msg}</div>", unsafe_allow_html=True)
        st.session_state.usage["advice"] += 1

    # ==============================
    # 📊 Usage + Billing
    # ==============================
    st.subheader("🧾 Usage & Billing")
    portfolios = st.session_state.usage["portfolios"]
    advice_count = st.session_state.usage["advice"]
    bill = portfolios * 5 + advice_count * 2

    st.write(f"📌 Portfolios analyzed: **{portfolios}** (₹{portfolios*5})")
    st.write(f"📌 Advice generated: **{advice_count}** (₹{advice_count*2})")
    st.write(f"💰 **Total Bill = ₹{bill}**")
