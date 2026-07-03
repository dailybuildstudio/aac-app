import io
import warnings
from collections import deque
from datetime import timedelta

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

warnings.filterwarnings("ignore")

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Trading Performance Analyzer",
    page_icon="📈",
    layout="wide",
)

# ── Colors ─────────────────────────────────────────────────────────────────────
BG = "#0d1117"
CARD = "#161b22"
BORDER = "#30363d"
GREEN = "#3fb950"
RED = "#f85149"
YELLOW = "#d29922"
BLUE = "#58a6ff"
MUTED = "#8b949e"

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
    background: {BG};
  }}
  .block-container {{ padding-top: 1.5rem; }}
  .metric-card {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 18px 20px;
    text-align: center;
    height: 100%;
  }}
  .m-label {{ font-size: 11px; color: {MUTED}; text-transform: uppercase; letter-spacing: .08em; }}
  .m-value {{ font-size: 26px; font-weight: 700; margin: 6px 0 2px; }}
  .m-sub   {{ font-size: 12px; color: {MUTED}; }}
  .green {{ color: {GREEN}; }}
  .red   {{ color: {RED}; }}
  .yellow{{ color: {YELLOW}; }}
  .blue  {{ color: {BLUE}; }}
  .sh {{
    font-size: 16px; font-weight: 600; color: #c9d1d9;
    margin: 24px 0 10px; padding-bottom: 6px;
    border-bottom: 1px solid {BORDER};
  }}
  .flag-row {{
    background: {CARD}; border-left: 3px solid {YELLOW};
    border-radius: 4px; padding: 10px 14px; margin: 5px 0; font-size: 13px;
  }}
  .edge-row {{
    background: {CARD}; border-left: 3px solid {GREEN};
    border-radius: 4px; padding: 10px 14px; margin: 5px 0; font-size: 13px;
  }}
  .info-banner {{
    background: {CARD}; border: 1px solid {BORDER};
    border-radius: 8px; padding: 10px 16px; margin-bottom: 14px; font-size: 13px;
  }}
</style>
""", unsafe_allow_html=True)


# ── Formatting helpers ─────────────────────────────────────────────────────────

def fc(v):
    if pd.isna(v):
        return "—"
    sign = "+" if v > 0 else ""
    return f"{sign}${v:,.2f}"

def fp(v):
    if pd.isna(v):
        return "—"
    return f"{v:.1f}%"

def mc(label, value, color="", sub=""):
    cc = f" {color}" if color else ""
    sb = f'<div class="m-sub">{sub}</div>' if sub else ""
    return (
        f'<div class="metric-card">'
        f'<div class="m-label">{label}</div>'
        f'<div class="m-value{cc}">{value}</div>'
        f'{sb}</div>'
    )

def sh(text):
    st.markdown(f'<div class="sh">{text}</div>', unsafe_allow_html=True)

def dark_layout(fig, height=300, showlegend=False, **kwargs):
    fig.update_layout(
        paper_bgcolor=BG,
        plot_bgcolor=CARD,
        font=dict(color="#c9d1d9", size=12),
        height=height,
        margin=dict(l=4, r=4, t=28, b=4),
        showlegend=showlegend,
        hovermode="x unified",
        **kwargs,
    )
    fig.update_xaxes(gridcolor=BORDER, zerolinecolor=BORDER)
    fig.update_yaxes(gridcolor=BORDER, zerolinecolor=BORDER)
    return fig

HOLD_ORDER = ["< 1 day", "1–5 days", "1–4 weeks", "1+ month"]

def hold_bucket(days):
    if days < 1:   return "< 1 day"
    if days <= 5:  return "1–5 days"
    if days <= 28: return "1–4 weeks"
    return "1+ month"


# ── Data loading ───────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def load_and_process(file_bytes_tuple, _names):
    dfs = []
    for b in file_bytes_tuple:
        df = pd.read_csv(io.BytesIO(b))
        df.columns = df.columns.str.strip()
        dfs.append(df)
    df = pd.concat(dfs, ignore_index=True)

    df["Run Date"] = pd.to_datetime(df["Run Date"], infer_datetime_format=True, errors="coerce")

    df["Price ($)"] = pd.to_numeric(
        df["Price ($)"].astype(str).str.replace(r"[$,\s]", "", regex=True), errors="coerce"
    )
    df["Quantity"] = pd.to_numeric(
        df["Quantity"].astype(str).str.replace(r"[,\s]", "", regex=True), errors="coerce"
    ).abs()

    al = df["Action"].str.strip().str.lower().fillna("")
    df["action_type"] = np.select(
        [
            al.str.contains("bought|buy"),
            al.str.contains("sold|sell"),
            al.str.contains("distribution"),
        ],
        ["buy", "sell", "distribution"],
        default="other",
    )

    df["is_shares"] = df["Type"].str.strip().str.lower().str.contains("share", na=False)
    df["trade_value"] = df["Price ($)"] * df["Quantity"]
    return df.dropna(subset=["Run Date"])


@st.cache_data(show_spinner=False)
def compute_pnl(df_json: str) -> pd.DataFrame:
    df = pd.read_json(io.StringIO(df_json), orient="records")
    df["Run Date"] = pd.to_datetime(df["Run Date"], errors="coerce")

    trades = df[df["action_type"].isin(["buy", "sell"])].copy()
    trades = trades.sort_values("Run Date").reset_index(drop=True)

    closed = []
    lots: dict = {}

    for _, row in trades.iterrows():
        key = (row["Account Type"], row["Symbol"])
        lots.setdefault(key, deque())

        qty = float(row["Quantity"])
        price = float(row["Price ($)"])
        date = pd.Timestamp(row["Run Date"])

        if row["action_type"] == "buy":
            lots[key].append({"date": date, "price": price, "qty": qty})

        elif row["action_type"] == "sell":
            rem = qty
            while rem > 1e-9 and lots[key]:
                lot = lots[key][0]
                matched = min(lot["qty"], rem)
                pnl = (price - lot["price"]) * matched
                hold = max(0, (date - lot["date"]).days)
                ret_pct = (price - lot["price"]) / lot["price"] * 100 if lot["price"] > 0 else 0
                closed.append(
                    {
                        "Account Type": key[0],
                        "Symbol": key[1],
                        "Buy Date": lot["date"],
                        "Sell Date": date,
                        "Buy Price": lot["price"],
                        "Sell Price": price,
                        "Quantity": matched,
                        "P&L": round(pnl, 2),
                        "Hold Days": hold,
                        "Win": pnl > 0,
                        "Return %": round(ret_pct, 2),
                    }
                )
                lot["qty"] -= matched
                rem -= matched
                if lot["qty"] < 1e-9:
                    lots[key].popleft()

    if not closed:
        return pd.DataFrame(
            columns=[
                "Account Type", "Symbol", "Buy Date", "Sell Date",
                "Buy Price", "Sell Price", "Quantity", "P&L",
                "Hold Days", "Win", "Return %",
            ]
        )
    return pd.DataFrame(closed)


@st.cache_data(show_spinner=False, ttl=3600)
def get_price_history(symbol: str, start, end):
    try:
        hist = yf.Ticker(symbol).history(
            start=str(start), end=str(end + timedelta(days=7))
        )
        hist = hist.reset_index()
        if "Date" in hist.columns:
            hist["Date"] = pd.to_datetime(hist["Date"]).dt.tz_localize(None)
        return hist
    except Exception:
        return pd.DataFrame()


# ── Tab: Overview ──────────────────────────────────────────────────────────────

def tab_overview(pnl: pd.DataFrame):
    if pnl.empty:
        st.warning("No closed trades found. Check that your CSV has matching buys and sells.")
        return

    wins   = pnl[pnl["Win"]]
    losses = pnl[~pnl["Win"]]
    n      = len(pnl)
    wr     = len(wins) / n * 100
    avg_w  = wins["P&L"].mean() if not wins.empty else 0
    avg_l  = losses["P&L"].mean() if not losses.empty else 0
    net    = pnl["P&L"].sum()
    pf_den = abs(losses["P&L"].sum())
    pf     = wins["P&L"].sum() / pf_den if pf_den > 0 else float("inf")
    exp    = (wr / 100 * avg_w) + ((1 - wr / 100) * avg_l)

    best  = pnl.loc[pnl["P&L"].idxmax()]
    worst = pnl.loc[pnl["P&L"].idxmin()]

    # Row 1 — key stats
    cols = st.columns(5)
    cards = [
        mc("Win Rate",          fp(wr),   "green" if wr >= 50 else "red",  f"{len(wins)}W / {len(losses)}L"),
        mc("Net P&L",           fc(net),  "green" if net >= 0 else "red"),
        mc("Profit Factor",     f"{pf:.2f}" if pf != float('inf') else "∞",
                                           "green" if pf >= 1 else "red"),
        mc("Expectancy / Trade", fc(exp), "green" if exp >= 0 else "red"),
        mc("Closed Trades",     str(n)),
    ]
    for col, card in zip(cols, cards):
        with col:
            st.markdown(card, unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # Row 2 — win/loss detail
    cols2 = st.columns(4)
    cards2 = [
        mc("Avg Win",    fc(avg_w), "green"),
        mc("Avg Loss",   fc(avg_l), "red"),
        mc("Best Trade", f"{best['Symbol']}: {fc(best['P&L'])}",   "green"),
        mc("Worst Trade",f"{worst['Symbol']}: {fc(worst['P&L'])}", "red"),
    ]
    for col, card in zip(cols2, cards2):
        with col:
            st.markdown(card, unsafe_allow_html=True)

    # Gross breakdown
    gross_gains  = wins["P&L"].sum() if not wins.empty else 0
    gross_losses = losses["P&L"].sum() if not losses.empty else 0
    wl_ratio     = avg_w / abs(avg_l) if avg_l != 0 else float("inf")

    sh("Gross Breakdown")
    g_cols = st.columns(4)
    g_cards = [
        mc("Total Gross Gains",  fc(gross_gains),  "green"),
        mc("Total Gross Losses", fc(gross_losses), "red"),
        mc("Net P&L",            fc(net),          "green" if net >= 0 else "red"),
        mc("Win / Loss Ratio",   f"{wl_ratio:.2f}" if wl_ratio != float('inf') else "∞",
           "green" if wl_ratio >= 1 else "red"),
    ]
    for col, card in zip(g_cols, g_cards):
        with col:
            st.markdown(card, unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    g_cols2 = st.columns(4)
    g_cards2 = [
        mc("Largest Single Win",  fc(best["P&L"]),  "green"),
        mc("Largest Single Loss", fc(worst["P&L"]), "red"),
        mc("Avg Win",             fc(avg_w),        "green"),
        mc("Avg Loss",            fc(avg_l),        "red"),
    ]
    for col, card in zip(g_cols2, g_cards2):
        with col:
            st.markdown(card, unsafe_allow_html=True)

    # Waterfall chart
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    wf_fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=["relative", "relative", "total"],
        x=["Gross Gains", "Gross Losses", "Net P&L"],
        y=[gross_gains, gross_losses, 0],
        text=[fc(gross_gains), fc(gross_losses), fc(net)],
        textposition="outside",
        increasing=dict(marker=dict(color=GREEN)),
        decreasing=dict(marker=dict(color=RED)),
        totals=dict(marker=dict(color=BLUE)),
        connector=dict(line=dict(color=BORDER, width=1, dash="dot")),
    ))
    dark_layout(wf_fig, height=300,
                yaxis=dict(tickprefix="$", gridcolor=BORDER, zerolinecolor=BORDER),
                xaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER),
                margin=dict(l=4, r=4, t=36, b=4))
    st.plotly_chart(wf_fig, use_container_width=True)

    # Cumulative P&L
    sh("Cumulative P&L")
    cum = pnl.sort_values("Sell Date").copy()
    cum["Cum"] = cum["P&L"].cumsum()
    line_color = GREEN if net >= 0 else RED
    fill_color = "rgba(63,185,80,0.08)" if net >= 0 else "rgba(248,81,73,0.08)"
    fig = go.Figure(go.Scatter(
        x=cum["Sell Date"], y=cum["Cum"],
        mode="lines", fill="tozeroy",
        line=dict(color=line_color, width=2),
        fillcolor=fill_color,
    ))
    dark_layout(fig, height=260,
                yaxis=dict(tickprefix="$", gridcolor=BORDER, zerolinecolor=BORDER))
    st.plotly_chart(fig, use_container_width=True)

    # P&L distribution histogram
    sh("Trade P&L Distribution")
    fig2 = go.Figure(go.Histogram(
        x=pnl["P&L"], nbinsx=40,
        marker=dict(
            color=[GREEN if v >= 0 else RED for v in pnl["P&L"]],
            line=dict(width=0),
        ),
    ))
    dark_layout(fig2, height=220,
                xaxis=dict(tickprefix="$", gridcolor=BORDER, zerolinecolor=BORDER),
                yaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER),
                bargap=0.04)
    st.plotly_chart(fig2, use_container_width=True)


# ── Tab: By Ticker ─────────────────────────────────────────────────────────────

def tab_tickers(pnl: pd.DataFrame):
    if pnl.empty:
        st.warning("No closed trades to analyze.")
        return

    by_t = (
        pnl.groupby("Symbol")
        .agg(
            Trades=("P&L", "count"),
            Net=("P&L", "sum"),
            WR=("Win", "mean"),
            Avg=("P&L", "mean"),
            Gains=("P&L", lambda x: x[x > 0].sum()),
            Losses=("P&L", lambda x: x[x <= 0].sum()),
        )
        .reset_index()
    )
    by_t["WR"] = by_t["WR"] * 100
    by_t = by_t.sort_values("Net", ascending=False)

    c1, c2 = st.columns(2)
    for col, label, subset, ascending in [
        (c1, "Most Profitable", by_t.head(10), True),
        (c2, "Least Profitable", by_t.tail(10).sort_values("Net"), True),
    ]:
        with col:
            sh(label)
            fig = go.Figure(go.Bar(
                x=subset["Net"], y=subset["Symbol"],
                orientation="h",
                marker_color=[GREEN if v >= 0 else RED for v in subset["Net"]],
                text=[fc(v) for v in subset["Net"]],
                textposition="outside",
            ))
            dark_layout(fig, height=320,
                        xaxis=dict(tickprefix="$", gridcolor=BORDER, zerolinecolor=BORDER),
                        yaxis=dict(gridcolor=BORDER))
            st.plotly_chart(fig, use_container_width=True)

    sh("All Tickers")
    disp = by_t.copy()
    disp["Net P&L"]       = disp["Net"].apply(fc)
    disp["Win Rate"]      = disp["WR"].apply(fp)
    disp["Avg P&L/Trade"] = disp["Avg"].apply(fc)
    disp["Gross Gains"]   = disp["Gains"].apply(fc)
    disp["Gross Losses"]  = disp["Losses"].apply(fc)
    st.dataframe(
        disp[["Symbol", "Trades", "Net P&L", "Gross Gains", "Gross Losses", "Win Rate", "Avg P&L/Trade"]],
        use_container_width=True, hide_index=True, height=340,
    )


# ── Tab: Timing ────────────────────────────────────────────────────────────────

def tab_timing(pnl: pd.DataFrame):
    if pnl.empty:
        st.warning("No closed trades to analyze.")
        return

    df = pnl.copy()

    # Day of week
    sh("P&L by Day of Week")
    DOW_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    df["DOW"] = df["Sell Date"].dt.day_name()
    dow = df.groupby("DOW")["P&L"].sum().reindex(DOW_ORDER).fillna(0)
    fig = go.Figure(go.Bar(
        x=dow.index, y=dow.values,
        marker_color=[GREEN if v >= 0 else RED for v in dow.values],
        text=[fc(v) for v in dow.values], textposition="outside",
    ))
    dark_layout(fig, height=260,
                yaxis=dict(tickprefix="$", gridcolor=BORDER, zerolinecolor=BORDER))
    st.plotly_chart(fig, use_container_width=True)

    # Hold duration
    sh("P&L by Hold Duration")
    df["Bucket"] = df["Hold Days"].apply(hold_bucket)
    hold = df.groupby("Bucket")["P&L"].agg(["sum", "count"]).reindex(HOLD_ORDER).fillna(0)
    win_rate_by_hold = (
        df.groupby("Bucket")["Win"].mean().reindex(HOLD_ORDER).fillna(0) * 100
    )

    c1, c2 = st.columns(2)
    with c1:
        fig2 = go.Figure(go.Bar(
            x=hold.index, y=hold["sum"],
            marker_color=[GREEN if v >= 0 else RED for v in hold["sum"]],
            text=[fc(v) for v in hold["sum"]], textposition="outside",
        ))
        dark_layout(fig2, height=260, title_text="Net P&L",
                    yaxis=dict(tickprefix="$", gridcolor=BORDER, zerolinecolor=BORDER))
        st.plotly_chart(fig2, use_container_width=True)

    with c2:
        fig3 = go.Figure(go.Bar(
            x=win_rate_by_hold.index, y=win_rate_by_hold.values,
            marker_color=[GREEN if v >= 50 else RED for v in win_rate_by_hold.values],
            text=[fp(v) for v in win_rate_by_hold.values], textposition="outside",
        ))
        dark_layout(fig3, height=260, title_text="Win Rate",
                    yaxis=dict(ticksuffix="%", range=[0, 115], gridcolor=BORDER, zerolinecolor=BORDER))
        st.plotly_chart(fig3, use_container_width=True)

    # Monthly P&L
    sh("Monthly P&L")
    df["Month"] = df["Sell Date"].dt.to_period("M").astype(str)
    monthly = df.groupby("Month")["P&L"].sum().reset_index().sort_values("Month")
    fig4 = go.Figure(go.Bar(
        x=monthly["Month"], y=monthly["P&L"],
        marker_color=[GREEN if v >= 0 else RED for v in monthly["P&L"]],
        text=[fc(v) for v in monthly["P&L"]], textposition="outside",
    ))
    dark_layout(fig4, height=280,
                yaxis=dict(tickprefix="$", gridcolor=BORDER, zerolinecolor=BORDER))
    st.plotly_chart(fig4, use_container_width=True)


# ── Tab: Emotional Flags ───────────────────────────────────────────────────────

def tab_emotional(pnl: pd.DataFrame, raw: pd.DataFrame):
    if pnl.empty:
        st.warning("No closed trades to analyze.")
        return

    all_trades = raw[raw["action_type"].isin(["buy", "sell"])].copy()
    all_trades["size"] = all_trades["Price ($)"] * all_trades["Quantity"]

    # ── 1. FOMO Sizing ─────────────────────────────────────────────────────────
    buys_only = all_trades[all_trades["action_type"] == "buy"].copy()

    acct_avg   = all_trades.groupby("Account Type")["size"].mean().to_dict()
    sym_avg_hold = pnl.groupby("Symbol")["Hold Days"].mean().to_dict()
    buys_only["hold_bucket"] = buys_only["Symbol"].map(sym_avg_hold).fillna(5).apply(hold_bucket)
    bucket_avg = buys_only.groupby("hold_bucket")["size"].mean().to_dict()

    # Running portfolio cost basis over time
    all_ev = all_trades.sort_values("Run Date").copy()
    running_cb, cb_list = 0.0, []
    for _, r in all_ev.iterrows():
        running_cb = running_cb + r["size"] if r["action_type"] == "buy" else max(0.0, running_cb - r["size"])
        cb_list.append(running_cb)
    all_ev["portfolio_cb"] = cb_list

    buy_ev = all_ev[all_ev["action_type"] == "buy"].copy()
    buy_ev["hold_bucket"] = buy_ev["Symbol"].map(sym_avg_hold).fillna(5).apply(hold_bucket)

    fomo = []
    global_avg = buys_only["size"].mean()
    for _, row in buy_ev.iterrows():
        a_avg  = acct_avg.get(row["Account Type"], global_avg)
        b_avg  = bucket_avg.get(row["hold_bucket"], global_avg)
        a_mult = row["size"] / a_avg  if a_avg  > 0 else 0
        b_mult = row["size"] / b_avg  if b_avg  > 0 else 0
        pct_p  = row["size"] / row["portfolio_cb"] * 100 if row["portfolio_cb"] > 0 else 0
        if a_mult > 2 and b_mult > 2:
            fomo.append({
                "Date":          row["Run Date"].date(),
                "Symbol":        row["Symbol"],
                "Account":       row["Account Type"],
                "Position Size": fc(row["size"]),
                "vs Acct Avg":   f"{a_mult:.1f}×",
                "vs Bucket Avg": f"{b_mult:.1f}×",
                "% of Portfolio":f"{pct_p:.1f}%",
                "Hold Bucket":   row["hold_bucket"],
            })

    # ── 2. Revenge Trades ──────────────────────────────────────────────────────
    loss_sells = pnl[~pnl["Win"]].copy()
    buys_raw   = raw[raw["action_type"] == "buy"].copy()
    buys_raw["size"] = buys_raw["Price ($)"] * buys_raw["Quantity"]

    revenge = []
    for _, lr in loss_sells.iterrows():
        t0         = pd.Timestamp(lr["Sell Date"])
        t1         = t0 + pd.Timedelta(hours=24)
        sell_value = lr["Sell Price"] * lr["Quantity"]
        fol = buys_raw[
            (buys_raw["Run Date"] > t0) &
            (buys_raw["Run Date"] <= t1) &
            (buys_raw["Account Type"] == lr["Account Type"])
        ]
        for _, br in fol.iterrows():
            same   = br["Symbol"] == lr["Symbol"]
            larger = br["size"] > sell_value
            if same or larger:
                revenge.append({
                    "Loss Trade":    lr["Symbol"],
                    "Loss ($)":      fc(lr["P&L"]),
                    "Loss Date":     lr["Sell Date"].date(),
                    "Follow-up Buy": br["Symbol"],
                    "Buy Size":      fc(br["size"]),
                    "Hours Later":   round((br["Run Date"] - t0).total_seconds() / 3600, 1),
                    "Flag Reason":   "Same ticker" if same else "Buy > loss size",
                    "Account":       lr["Account Type"],
                })

    # ── 3. Adds to Losers ──────────────────────────────────────────────────────
    adds = []
    for (acct, sym), grp in all_trades.groupby(["Account Type", "Symbol"]):
        avg_cost, qty_held = None, 0.0
        closed_sym = pnl[(pnl["Symbol"] == sym) & (pnl["Account Type"] == acct)]
        for _, row in grp.sort_values("Run Date").iterrows():
            if row["action_type"] == "buy":
                if qty_held > 0 and avg_cost is not None and row["Price ($)"] < avg_cost:
                    down_pct = (row["Price ($)"] - avg_cost) / avg_cost * 100
                    down_amt = (row["Price ($)"] - avg_cost) * qty_held
                    add_pct  = row["Quantity"] / qty_held * 100
                    future   = closed_sym[closed_sym["Sell Date"] >= row["Run Date"]]["P&L"].sum()
                    adds.append({
                        "Symbol":            sym,
                        "Account":           acct,
                        "Add Date":          row["Run Date"].date(),
                        "Avg Cost":          f"${avg_cost:.2f}",
                        "Add Price":         f"${row['Price ($)']:.2f}",
                        "Down %":            f"{down_pct:.1f}%",
                        "Unreal. Loss":      fc(down_amt),
                        "Add Type":          "Small (<25%)" if add_pct < 25 else ("Double-down (>75%)" if add_pct > 75 else "Moderate"),
                        "Post-Add P&L":      fc(future) if future != 0 else "Still open",
                    })
                new_qty   = qty_held + row["Quantity"]
                avg_cost  = ((avg_cost or 0) * qty_held + row["Price ($)"] * row["Quantity"]) / new_qty if new_qty > 0 else row["Price ($)"]
                qty_held  = new_qty
            elif row["action_type"] == "sell":
                qty_held = max(0.0, qty_held - row["Quantity"])
                if qty_held == 0:
                    avg_cost = None

    # ── 4. Early Exits (yfinance) ──────────────────────────────────────────────
    early_exits = []
    wins_pnl = pnl[pnl["Win"]].copy()
    if not wins_pnl.empty:
        with st.spinner("Checking early exits via yfinance…"):
            for sym in wins_pnl["Symbol"].unique():
                sym_w = wins_pnl[wins_pnl["Symbol"] == sym]
                start = sym_w["Sell Date"].min().date()
                end   = (sym_w["Sell Date"].max() + timedelta(days=35)).date()
                hist  = get_price_history(sym, start, end)
                if hist.empty:
                    continue
                hist["Date"] = pd.to_datetime(hist["Date"])
                for _, t in sym_w.iterrows():
                    sell_ts = pd.Timestamp(t["Sell Date"])
                    post = hist[
                        (hist["Date"] > sell_ts) &
                        (hist["Date"] <= sell_ts + timedelta(days=30))
                    ]
                    if post.empty:
                        continue
                    max_p = post["Close"].max()
                    if max_p > t["Sell Price"] * 1.10:
                        pct_higher = (max_p - t["Sell Price"]) / t["Sell Price"] * 100
                        early_exits.append({
                            "Symbol":          sym,
                            "Sell Date":       t["Sell Date"].date(),
                            "Sell Price":      f"${t['Sell Price']:.2f}",
                            "Max 30d High":    f"${max_p:.2f}",
                            "Continued +":     f"+{pct_higher:.1f}%",
                            "Left on Table":   fc((max_p - t["Sell Price"]) * t["Quantity"]),
                            "Trade P&L":       fc(t["P&L"]),
                        })

    # ── 5. Held Through Warnings (yfinance) ────────────────────────────────────
    held_through = []
    losses_pnl = pnl[~pnl["Win"]].copy()
    if not losses_pnl.empty:
        with st.spinner("Checking max drawdowns via yfinance…"):
            for sym in losses_pnl["Symbol"].unique():
                sym_l = losses_pnl[losses_pnl["Symbol"] == sym]
                start = sym_l["Buy Date"].min().date()
                end   = sym_l["Sell Date"].max().date()
                hist  = get_price_history(sym, start, end)
                if hist.empty:
                    continue
                hist["Date"] = pd.to_datetime(hist["Date"])
                for _, t in sym_l.iterrows():
                    during = hist[
                        (hist["Date"] >= pd.Timestamp(t["Buy Date"])) &
                        (hist["Date"] <= pd.Timestamp(t["Sell Date"]))
                    ]
                    if during.empty:
                        continue
                    min_p  = during["Close"].min()
                    max_dd = (min_p - t["Buy Price"]) / t["Buy Price"] * 100
                    if max_dd < -7:
                        held_through.append({
                            "Symbol":        sym,
                            "Buy Date":      t["Buy Date"].date(),
                            "Sell Date":     t["Sell Date"].date(),
                            "Buy Price":     f"${t['Buy Price']:.2f}",
                            "Min During":    f"${min_p:.2f}",
                            "Max Drawdown":  f"{max_dd:.1f}%",
                            "Final Loss":    fc(t["P&L"]),
                            "Hold Days":     t["Hold Days"],
                        })

    # ── Summary header ─────────────────────────────────────────────────────────
    def flag_color(n): return "yellow" if n > 0 else "green"

    cols = st.columns(5)
    summaries = [
        mc("Revenge Trades",     str(len(revenge)),     flag_color(len(revenge))),
        mc("FOMO Sized",         str(len(fomo)),        flag_color(len(fomo))),
        mc("Added to Losers",    str(len(adds)),        flag_color(len(adds))),
        mc("Early Exits",        str(len(early_exits)), flag_color(len(early_exits))),
        mc("Held Thru Warning",  str(len(held_through)),flag_color(len(held_through))),
    ]
    for col, card in zip(cols, summaries):
        with col:
            st.markdown(card, unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    total_flags = len(revenge) + len(fomo) + len(adds) + len(early_exits) + len(held_through)
    if total_flags == 0:
        st.success("No emotional trading patterns detected. Clean record.")
        return

    # ── Detail sections ────────────────────────────────────────────────────────
    if revenge:
        sh(f"⚠️ Revenge Trades ({len(revenge)})")
        st.caption("Same-ticker re-entry OR buy larger than the loss — within 24 hours of a loss")
        st.dataframe(pd.DataFrame(revenge), use_container_width=True, hide_index=True)

    if fomo:
        sh(f"⚠️ FOMO Sizing ({len(fomo)})")
        st.caption("Exceeded 2× both your account-type average AND hold-duration average simultaneously")
        st.dataframe(pd.DataFrame(fomo), use_container_width=True, hide_index=True)

    if adds:
        sh(f"⚠️ Added to Losing Positions ({len(adds)})")
        st.caption("Bought more shares while the open position was underwater — with ultimate outcome")
        st.dataframe(pd.DataFrame(adds), use_container_width=True, hide_index=True)

    if early_exits:
        sh(f"⚠️ Early Exits — Left on the Table ({len(early_exits)})")
        st.caption("Winning trades where the stock rose >10% further within 30 days of your sell")
        st.dataframe(pd.DataFrame(early_exits), use_container_width=True, hide_index=True)

    if held_through:
        sh(f"⚠️ Held Through Warnings ({len(held_through)})")
        st.caption("Losing trades where the stock dropped >7% from entry before you sold")
        st.dataframe(pd.DataFrame(held_through), use_container_width=True, hide_index=True)


# ── Tab: Opportunity Map ───────────────────────────────────────────────────────

def tab_opportunity(pnl: pd.DataFrame):
    if pnl.empty:
        st.warning("No closed trades to analyze.")
        return

    import plotly.express as px

    by_t = (
        pnl.groupby("Symbol")
        .agg(
            Trades=("P&L", "count"),
            Net=("P&L", "sum"),
            WR=("Win", "mean"),
            Last=("Sell Date", "max"),
        )
        .reset_index()
    )
    by_t["WR"]   = by_t["WR"] * 100
    by_t["Edge"] = (by_t["WR"] > 55) & (by_t["Trades"] >= 3)
    cutoff       = pd.Timestamp.now() - pd.DateOffset(months=6)
    by_t["Stale"]= by_t["Last"] < cutoff

    sh("Win Rate vs Net P&L — All Tickers")
    fig = px.scatter(
        by_t,
        x="WR", y="Net",
        size="Trades",
        text="Symbol",
        color=by_t["Net"].apply(lambda v: GREEN if v >= 0 else RED),
        color_discrete_map="identity",
        labels={"WR": "Win Rate (%)", "Net": "Net P&L ($)"},
        hover_data={"Trades": True, "WR": ":.1f", "Net": ":$,.2f"},
    )
    fig.add_vline(x=55, line_dash="dash", line_color=YELLOW,
                  annotation_text="55% edge line", annotation_font_color=YELLOW)
    fig.add_hline(y=0, line_dash="dash", line_color=MUTED)
    fig.update_traces(textposition="top center", marker=dict(line=dict(width=0)))
    fig.update_layout(
        paper_bgcolor=BG, plot_bgcolor=CARD,
        font=dict(color="#c9d1d9"),
        height=400, margin=dict(l=4, r=4, t=28, b=4), showlegend=False,
        xaxis=dict(ticksuffix="%", gridcolor=BORDER, zerolinecolor=BORDER),
        yaxis=dict(tickprefix="$", gridcolor=BORDER, zerolinecolor=BORDER),
    )
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        edge = by_t[by_t["Edge"]].sort_values("Net", ascending=False)
        sh(f"Edge Tickers — {len(edge)}")
        if not edge.empty:
            for _, r in edge.iterrows():
                st.markdown(
                    f'<div class="edge-row"><strong>{r["Symbol"]}</strong>'
                    f' &nbsp;·&nbsp; {r["Trades"]} trades'
                    f' &nbsp;·&nbsp; <span class="green">{fp(r["WR"])}</span> win rate'
                    f' &nbsp;·&nbsp; <span class="green">{fc(r["Net"])}</span></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("No tickers with confirmed edge yet (need >55% WR, ≥3 trades).")

    with c2:
        stale = by_t[by_t["Stale"]].sort_values("Net", ascending=False)
        sh(f"Re-examine List (no trades in 6+ months) — {len(stale)}")
        if not stale.empty:
            for _, r in stale.iterrows():
                cls = "green" if r["Net"] >= 0 else "red"
                st.markdown(
                    f'<div class="flag-row"><strong>{r["Symbol"]}</strong>'
                    f' &nbsp;·&nbsp; Last: {r["Last"].date()}'
                    f' &nbsp;·&nbsp; <span class="{cls}">{fc(r["Net"])}</span>'
                    f' ({r["Trades"]} trades)</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("All traded tickers have recent activity.")

    sh("Ticker Lookup")
    lookup = st.text_input("Enter a ticker to check your history", placeholder="e.g. AAPL").upper().strip()
    if lookup:
        row = by_t[by_t["Symbol"] == lookup]
        if not row.empty:
            r   = row.iloc[0]
            cls = "green" if r["Net"] >= 0 else "red"
            st.markdown(
                f'<div class="info-banner">'
                f'<strong>{lookup}</strong> — you have history on this ticker<br>'
                f'Closed trades: <strong>{int(r["Trades"])}</strong> &nbsp;·&nbsp; '
                f'Net P&L: <strong><span class="{cls}">{fc(r["Net"])}</span></strong> &nbsp;·&nbsp; '
                f'Win rate: <strong>{fp(r["WR"])}</strong> &nbsp;·&nbsp; '
                f'Last traded: <strong>{r["Last"].date()}</strong> &nbsp;·&nbsp; '
                f'Edge: <strong>{"✅" if r["Edge"] else "❌"}</strong>'
                f'</div>',
                unsafe_allow_html=True,
            )
        else:
            st.warning(f"No trade history found for **{lookup}**.")


# ── Tab: Entry / Exit ──────────────────────────────────────────────────────────

def tab_entry_exit(pnl: pd.DataFrame, raw: pd.DataFrame):
    if pnl.empty:
        st.warning("No closed trades to analyze.")
        return

    top_tickers = (
        pnl.groupby("Symbol").size().sort_values(ascending=False).head(30).index.tolist()
    )
    selected = st.selectbox("Select ticker", top_tickers)
    if not selected:
        return

    ticker_pnl = pnl[pnl["Symbol"] == selected].copy()
    ticker_raw = raw[raw["Symbol"] == selected].copy()

    start = (ticker_raw["Run Date"].min() - timedelta(days=20)).date()
    end   = (ticker_raw["Run Date"].max() + timedelta(days=20)).date()

    with st.spinner(f"Fetching price history for {selected}…"):
        hist = get_price_history(selected, start, end)

    fig = go.Figure()

    if not hist.empty and "Close" in hist.columns:
        fig.add_trace(go.Scatter(
            x=hist["Date"], y=hist["Close"],
            mode="lines", name="Close",
            line=dict(color=BLUE, width=1.5),
            hovertemplate="%{x}<br>$%{y:.2f}<extra>Price</extra>",
        ))
    else:
        st.warning(f"Could not load price history for {selected} from yfinance.")

    buys  = ticker_raw[ticker_raw["action_type"] == "buy"]
    sells = ticker_raw[ticker_raw["action_type"] == "sell"]

    if not buys.empty:
        fig.add_trace(go.Scatter(
            x=buys["Run Date"], y=buys["Price ($)"],
            mode="markers", name="Buy",
            marker=dict(symbol="triangle-up", size=13, color=GREEN,
                        line=dict(color="white", width=1)),
            hovertemplate="<b>BUY</b> %{x}<br>$%{y:.2f}<extra></extra>",
        ))
    if not sells.empty:
        fig.add_trace(go.Scatter(
            x=sells["Run Date"], y=sells["Price ($)"],
            mode="markers", name="Sell",
            marker=dict(symbol="triangle-down", size=13, color=RED,
                        line=dict(color="white", width=1)),
            hovertemplate="<b>SELL</b> %{x}<br>$%{y:.2f}<extra></extra>",
        ))

    for _, trade in ticker_pnl.iterrows():
        color = GREEN if trade["Win"] else RED
        fig.add_shape(
            type="line",
            x0=trade["Buy Date"],  y0=trade["Buy Price"],
            x1=trade["Sell Date"], y1=trade["Sell Price"],
            line=dict(color=color, width=1, dash="dot"),
        )

    dark_layout(
        fig, height=460,
        title_text=f"{selected} — Entries & Exits",
        showlegend=True,
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=BORDER),
        xaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER),
        yaxis=dict(tickprefix="$", gridcolor=BORDER, zerolinecolor=BORDER),
    )
    st.plotly_chart(fig, use_container_width=True)

    sh(f"Closed Trades — {selected}")
    disp = ticker_pnl[[
        "Buy Date", "Sell Date", "Buy Price", "Sell Price",
        "Quantity", "P&L", "Hold Days", "Return %",
    ]].copy()
    disp["P&L"]       = disp["P&L"].apply(fc)
    disp["Return %"]  = disp["Return %"].apply(fp)
    disp["Buy Price"] = disp["Buy Price"].apply(lambda v: f"${v:.2f}")
    disp["Sell Price"]= disp["Sell Price"].apply(lambda v: f"${v:.2f}")
    st.dataframe(disp, use_container_width=True, hide_index=True)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    st.title("📈 Trading Performance Analyzer")
    st.markdown(f'<hr style="border-color:{BORDER};margin:4px 0 20px">', unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Drop your CSV trade history file(s) here",
        type=["csv"],
        accept_multiple_files=True,
    )

    if not uploaded:
        st.info("Upload a CSV file to begin. Add multiple files to merge account histories.")
        return

    file_bytes = tuple(f.read() for f in uploaded)
    file_names = tuple(f.name for f in uploaded)

    with st.spinner("Loading trades…"):
        raw = load_and_process(file_bytes, file_names)

    if raw.empty:
        st.error("No valid rows found. Check that your CSV matches the expected format.")
        return

    # ── Account toggle ─────────────────────────────────────────────────────────
    accounts = sorted(raw["Account Type"].dropna().unique().tolist())
    options  = ["All Accounts"] + accounts

    col_toggle, col_info = st.columns([4, 1])
    with col_toggle:
        selected_acct = st.radio("Account", options, horizontal=True, label_visibility="collapsed")
    with col_info:
        st.markdown(
            f'<div style="text-align:right;color:{MUTED};font-size:12px;padding-top:6px">'
            f'{len(raw):,} rows loaded</div>',
            unsafe_allow_html=True,
        )

    st.markdown(f'<hr style="border-color:{BORDER};margin:8px 0 14px">', unsafe_allow_html=True)

    filt = raw if selected_acct == "All Accounts" else raw[raw["Account Type"] == selected_acct]

    # Distribution income banner
    dist      = filt[filt["action_type"] == "distribution"]
    dist_cash = (dist["Price ($)"] * dist["Quantity"]).sum()
    if dist_cash > 0:
        st.markdown(
            f'<div class="info-banner">💰 <strong>Distribution income:</strong> '
            f'<span class="green">{fc(dist_cash)}</span> received — excluded from trade P&L</div>',
            unsafe_allow_html=True,
        )

    # Compute P&L
    with st.spinner("Calculating P&L…"):
        pnl = compute_pnl(filt.to_json(orient="records", date_format="iso"))

    # ── Debug expander ─────────────────────────────────────────────────────────
    with st.expander("🔍 Data diagnostics", expanded=pnl.empty):
        buy_rows  = filt[filt["action_type"] == "buy"]
        sell_rows = filt[filt["action_type"] == "sell"]
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Action values detected**")
            st.dataframe(
                filt["Action"].value_counts().rename_axis("Action").reset_index(name="Count"),
                hide_index=True, height=200,
            )
        with c2:
            st.markdown("**Type values detected**")
            st.dataframe(
                filt["Type"].value_counts().rename_axis("Type").reset_index(name="Count"),
                hide_index=True, height=200,
            )
        st.markdown(
            f"Buys detected: `{len(buy_rows)}` &nbsp;·&nbsp; "
            f"Sells detected: `{len(sell_rows)}` &nbsp;·&nbsp; "
            f"Closed trades matched: `{len(pnl)}`"
        )

    # ── Tabs ───────────────────────────────────────────────────────────────────
    t1, t2, t3, t4, t5, t6 = st.tabs([
        "📊 Overview",
        "📋 By Ticker",
        "🕐 Timing",
        "🧠 Emotional Flags",
        "🗺️ Opportunity Map",
        "📈 Entry / Exit",
    ])

    with t1: tab_overview(pnl)
    with t2: tab_tickers(pnl)
    with t3: tab_timing(pnl)
    with t4: tab_emotional(pnl, filt)
    with t5: tab_opportunity(pnl)
    with t6: tab_entry_exit(pnl, filt)


if __name__ == "__main__":
    main()
