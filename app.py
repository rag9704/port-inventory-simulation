"""
Inventory Balance Visualizer — Streamlit app

Run with:
    pip install streamlit plotly
    streamlit run inventory_balance_app.py
"""

import streamlit as st
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Port Inventory Balance",
    page_icon="🛴",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Core equation
# ---------------------------------------------------------------------------
def inventory_balance(current_inventory, capacity, pickup_demand, dropoff_demand):
    available_space = capacity - current_inventory
    actual_in       = min(dropoff_demand, available_space)
    actual_out      = min(pickup_demand,  current_inventory)
    return {
        "actual_in":      actual_in,
        "actual_out":     actual_out,
        "next_inventory": current_inventory + actual_in - actual_out,
        "spillover":      dropoff_demand - actual_in,
        "lost_demand":    pickup_demand  - actual_out,
    }

# ---------------------------------------------------------------------------
# Tank chart (Plotly)
# ---------------------------------------------------------------------------
def build_tank_chart(capacity, current_inventory, result):
    next_inv    = result["next_inventory"]
    actual_in   = result["actual_in"]
    actual_out  = result["actual_out"]
    spillover   = result["spillover"]
    lost_demand = result["lost_demand"]

    TEAL    = "#1D9E75"
    BLUE    = "#378ADD"
    CORAL   = "#D85A30"
    AMBER   = "#BA7517"
    GRAY    = "#888780"
    BORDER  = "#B4B2A9"

    fig = go.Figure()

    # ── Tank background (available space) ──────────────────────────────────
    fig.add_shape(
        type="rect",
        x0=0.2, x1=0.8, y0=0, y1=capacity,
        fillcolor="#E1F5EE", opacity=0.5,
        line=dict(color=BORDER, width=1.5),
    )

    # ── Current inventory fill ──────────────────────────────────────────────
    if current_inventory > 0:
        fig.add_shape(
            type="rect",
            x0=0.2, x1=0.8, y0=0, y1=current_inventory,
            fillcolor="#B5D4F4", opacity=0.8,
            line=dict(width=0),
        )

    # ── Next inventory level (dashed line) ─────────────────────────────────
    if abs(next_inv - current_inventory) > 0.05 and 0 < next_inv <= capacity:
        fig.add_shape(
            type="line",
            x0=0.2, x1=0.8, y0=next_inv, y1=next_inv,
            line=dict(color=BLUE, width=1.5, dash="dash"),
        )
        fig.add_annotation(
            x=0.82, y=next_inv,
            text=f"<b>I'={next_inv:.1f}</b>",
            showarrow=False, xanchor="left",
            font=dict(color=BLUE, size=12),
        )

    # ── Tank border (drawn on top of fills) ────────────────────────────────
    fig.add_shape(
        type="rect",
        x0=0.2, x1=0.8, y0=0, y1=capacity,
        fillcolor="rgba(0,0,0,0)",
        line=dict(color=BORDER, width=2),
    )

    # ── Zone labels ────────────────────────────────────────────────────────
    available_space = capacity - current_inventory
    if available_space > capacity * 0.12:
        fig.add_annotation(
            x=0.5, y=current_inventory + available_space / 2,
            text="available space",
            showarrow=False, font=dict(color="#0F6E56", size=11),
        )
    if current_inventory > capacity * 0.12:
        fig.add_annotation(
            x=0.5, y=current_inventory / 2,
            text="stock",
            showarrow=False, font=dict(color="#185FA5", size=11),
        )

    # ── Inflow arrow (dropoff → right side of tank) ────────────────────────
    arrow_y_in = current_inventory + available_space / 2 if available_space > 0 else capacity - 0.5
    if actual_in > 0:
        fig.add_annotation(
            ax=1.05, ay=arrow_y_in, axref="x", ayref="y",
            x=0.81,  y=arrow_y_in, xref="x",  yref="y",
            arrowhead=2, arrowwidth=2, arrowcolor=TEAL,
            showarrow=True, text="",
        )
        fig.add_annotation(
            x=1.07, y=arrow_y_in,
            text=f"<b>+{actual_in:.1f}</b>",
            showarrow=False, xanchor="left",
            font=dict(color=TEAL, size=12),
        )

    # ── Spillover arrow (dashed, above tank top) ───────────────────────────
    if spillover > 0:
        fig.add_annotation(
            ax=0.81, ay=capacity,      axref="x", ayref="y",
            x=1.05,  y=capacity + 0.5, xref="x",  yref="y",
            arrowhead=2, arrowwidth=1.5, arrowcolor=CORAL,
            showarrow=True, text="",
        )
        fig.add_annotation(
            x=1.07, y=capacity + 0.5,
            text=f"↑ spill {spillover:.1f}",
            showarrow=False, xanchor="left",
            font=dict(color=CORAL, size=11),
        )

    # ── Outflow arrow (pickup → left side of tank) ─────────────────────────
    arrow_y_out = current_inventory / 2 if current_inventory > 0 else 0.5
    if actual_out > 0:
        fig.add_annotation(
            ax=-0.05, ay=arrow_y_out, axref="x", ayref="y",
            x=0.19,   y=arrow_y_out, xref="x",  yref="y",
            arrowhead=2, arrowwidth=2, arrowcolor=BLUE,
            showarrow=True, text="",
        )
        fig.add_annotation(
            x=-0.07, y=arrow_y_out,
            text=f"<b>−{actual_out:.1f}</b>",
            showarrow=False, xanchor="right",
            font=dict(color=BLUE, size=12),
        )

    # ── Lost demand arrow (dashed, below outflow) ──────────────────────────
    if lost_demand > 0:
        offset = max(arrow_y_out - capacity * 0.12, 0.3)
        fig.add_annotation(
            ax=0.19,  ay=offset, axref="x", ayref="y",
            x=-0.05,  y=offset,  xref="x",  yref="y",
            arrowhead=2, arrowwidth=1.5, arrowcolor=AMBER,
            showarrow=True, text="",
        )
        fig.add_annotation(
            x=-0.07, y=offset,
            text=f"✕ {lost_demand:.1f}",
            showarrow=False, xanchor="right",
            font=dict(color=AMBER, size=11),
        )

    # ── Axis labels ────────────────────────────────────────────────────────
    fig.add_annotation(x=0.18, y=capacity,    text=f"C={capacity}", showarrow=False,
                       xanchor="right", font=dict(color=GRAY, size=11))
    fig.add_annotation(x=0.18, y=0,           text="0",             showarrow=False,
                       xanchor="right", font=dict(color=GRAY, size=11))
    if current_inventory > 0:
        fig.add_annotation(x=0.18, y=current_inventory, text=f"I={current_inventory}",
                           showarrow=False, xanchor="right", font=dict(color="#3d3d3a", size=11))

    fig.update_layout(
        height=340,
        margin=dict(l=60, r=90, t=20, b=20),
        xaxis=dict(visible=False, range=[-0.2, 1.4]),
        yaxis=dict(visible=False, range=[-0.5, capacity + 1.5]),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig

# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
st.title("🛴 Port Inventory Balance")
st.caption("Visualise how pickup demand, dropoff demand, and port capacity interact each hour.")

col_ctrl, col_tank, col_results = st.columns([1.2, 1.2, 1.4])

with col_ctrl:
    st.subheader("Parameters")
    capacity          = st.slider("Capacity C(p)",          min_value=2,  max_value=20, value=12)
    current_inventory = st.slider("Current inventory I(p,t)", min_value=0, max_value=capacity, value=7)
    pickup_demand     = st.slider("Pickup demand (outflow)",  min_value=0, max_value=15, value=5)
    dropoff_demand    = st.slider("Dropoff demand (inflow)",  min_value=0, max_value=15, value=4)

result = inventory_balance(current_inventory, capacity, pickup_demand, dropoff_demand)
next_inv    = result["next_inventory"]
actual_in   = result["actual_in"]
actual_out  = result["actual_out"]
spillover   = result["spillover"]
lost_demand = result["lost_demand"]

with col_tank:
    st.subheader("Port state")
    fig = build_tank_chart(capacity, current_inventory, result)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Legend
    lcol1, lcol2 = st.columns(2)
    lcol1.markdown("🟢 &nbsp;**Inflow** (dropoffs accepted)")
    lcol1.markdown("🔴 &nbsp;**Spillover** (dropoffs rejected)")
    lcol2.markdown("🔵 &nbsp;**Outflow** (pickups served)")
    lcol2.markdown("🟡 &nbsp;**Lost demand** (pickups missed)")

with col_results:
    st.subheader("Balance equation")

    st.code(
        "I(t+1) = I(t) + actual_in − actual_out\n"
        "actual_in  = min(dropoff,  C − I(t))\n"
        "actual_out = min(pickup,   I(t))",
        language="python",
    )

    st.markdown("**Inflow**")
    c1, c2 = st.columns(2)
    c1.metric("Actual in", f"{actual_in:.1f}", help="Dropoffs accepted by the port")
    c2.metric("Spillover",  f"{spillover:.1f}",
              delta=f"−{spillover:.1f} lost" if spillover > 0 else None,
              delta_color="inverse",
              help="Dropoff demand that couldn't fit")

    st.markdown("**Outflow**")
    c3, c4 = st.columns(2)
    c3.metric("Actual out",   f"{actual_out:.1f}",  help="Pickups served from the port")
    c4.metric("Lost demand",  f"{lost_demand:.1f}",
              delta=f"−{lost_demand:.1f} unserved" if lost_demand > 0 else None,
              delta_color="inverse",
              help="Pickup demand that couldn't be served")

    st.divider()

    # Next inventory + status
    fill_pct = next_inv / capacity * 100
    if next_inv <= 0:
        status_label, status_color = "🔴 Empty — needs restock",   "red"
    elif next_inv >= capacity:
        status_label, status_color = "🟡 Full — excess vehicles",  "orange"
    else:
        status_label, status_color = "🟢 Healthy",                 "green"

    st.metric(
        label="Next inventory I(p, t+1)",
        value=f"{next_inv:.1f} / {capacity}",
        delta=f"{next_inv - current_inventory:+.1f} vs now",
    )
    st.progress(int(fill_pct), text=f"{fill_pct:.0f}% full  ·  {status_label}")

    # Redeployment hint
    if lost_demand > 0 and spillover == 0:
        st.info(f"**Send vehicles here.** {lost_demand:.0f} rides could not be served.")
    elif spillover > 0 and lost_demand == 0:
        st.warning(f"**Pull vehicles from here.** {spillover:.0f} dropoffs were rejected.")
    elif lost_demand > 0 and spillover > 0:
        st.warning("Mixed signals — both lost demand and spillover present.")
    else:
        st.success("Port is balanced for this hour.")
