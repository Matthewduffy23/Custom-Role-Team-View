# projected_view.py — Standalone Projected View
# streamlit run projected_view.py

import io
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import streamlit as st

st.set_page_config(page_title="Projected View", layout="wide")

st.markdown("""
<style>
body, .stApp { background-color: #0a0f1c; color: #ffffff; }
div[data-testid="stNumberInput"] label p,
div[data-testid="stSelectbox"] label p,
div[data-testid="stButton"] p { color: #ffffff !important; }
div[data-testid="stNumberInput"] input { color: #ffffff !important; background: #1a2035 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h2 style="color:#ffffff;margin-bottom:2px;">🎯 Projected View</h2>', unsafe_allow_html=True)
st.markdown('<p style="color:#9ca3af;font-size:13px;margin-top:0;">Enter percentiles (0–100). Left = Team &nbsp;·&nbsp; Right = Role. Add/remove metrics then hit <b>Generate</b>.</p>', unsafe_allow_html=True)

# ── Exact colormap from main app ───────────────────────────────────────────────
_VALUE_COLORS = ["#be2a3e","#e25f48","#f88f4d","#f4d166","#90b960","#4b9b5f","#22763f"]
_CMAP = LinearSegmentedColormap.from_list("rr_pct", _VALUE_COLORS)

# ── Chart — exact copy of _rr_split_polar_fig ─────────────────────────────────
def build_chart(team_labels, team_pcts, role_labels, role_pcts):
    TEAM_TRACK = "#2b3646"; ROLE_TRACK = "#362b46"
    fig = plt.figure(figsize=(9.2, 8.2))
    fig.patch.set_facecolor("#0a0f1c")
    ax = fig.add_axes([0.06, 0.06, 0.88, 0.88], polar=True)
    ax.set_facecolor("#0a0f1c")
    RMAX = 110
    ax.set_rlim(0, RMAX)
    ax.set_xticks([]); ax.set_yticks([])
    ax.grid(False); ax.spines["polar"].set_visible(False)

    n_t = len(team_labels); n_r = len(role_labels)
    step_t = np.pi / n_t;   step_r = np.pi / n_r
    angles_t = (np.pi / 2) + (step_t / 2) + np.arange(n_t) * step_t
    angles_r = (-np.pi / 2) + (step_r / 2) + np.arange(n_r) * step_r
    angles   = np.concatenate([angles_t, angles_r])
    all_vals = list(team_pcts) + list(role_pcts)
    all_labs = list(team_labels) + list(role_labels)
    widths   = [step_t * 0.76] * n_t + [step_r * 0.76] * n_r

    theta_ring = np.linspace(0, 2 * np.pi, 361)
    for r, a, lw in [(25, 0.08, 0.8), (50, 0.22, 1.8), (75, 0.08, 0.8)]:
        ax.plot(theta_ring, np.full_like(theta_ring, r),
                color="white", alpha=a, linewidth=lw, zorder=0)
    for th in (np.pi / 2, 3 * np.pi / 2):
        ax.plot([th, th], [0, RMAX], color="white", linewidth=4.8, alpha=0.65, zorder=0)

    for i, (th, w) in enumerate(zip(angles, widths)):
        ax.bar(th, 100, width=w, bottom=0,
               color=TEAM_TRACK if i < n_t else ROLE_TRACK,
               alpha=0.78, edgecolor="none", zorder=1)
    for th, w, v in zip(angles, widths, all_vals):
        v = int(max(0, min(100, v)))
        ax.bar(th, v, width=w, bottom=0,
               color=_CMAP(v / 100), edgecolor="white", linewidth=1.4, zorder=3)
    for th, lab in zip(angles, all_labs):
        ax.text(th, 128, str(lab).upper(),
                ha="center", va="center", fontsize=9.6,
                fontweight="bold", color="white", alpha=0.95, zorder=4)

    fig.text(0.04, 0.965, "TEAM", ha="left",  va="top", fontsize=18, fontweight="900", color="#f472b6")
    fig.text(0.96, 0.965, "ROLE", ha="right", va="top", fontsize=18, fontweight="900", color="#f472b6")
    return fig

# ── All available metric options ───────────────────────────────────────────────
ALL_METRICS = sorted([
    "Aerial Requirement", "Aerial Volume", "Attacking Contribution", "Attacking Territory",
    "Ball Carrying", "Box Entries", "Build Up Speed", "Claim Rate", "Command of Area",
    "Compactness", "Counter Press", "Creativity", "Crosses", "Deeper Playmaking",
    "Defensive Volume", "Direct Play", "Distribution", "Goal Output", "Goal Threat",
    "High Press", "Line Height", "Long Balls", "Long Pass Volume", "Off Ball Movement",
    "Opportunities", "Pass Verticality", "Pass Volume", "Passes", "Possession",
    "Pressing", "Pressing Intensity", "Progression Volume", "Retention", "Set Piece Threat",
    "Shot Volume", "Shots Faced", "Sweeping", "Transition Speed", "Vertical Runs",
    "Width", "xG", "xGA",
])

# ── Default configs ────────────────────────────────────────────────────────────
DEFAULTS = {
    "Center Backs": {
        "team": ["Possession", "Passes", "Pressing", "Build Up Speed", "Line Height"],
        "role": ["Pass Volume", "Progression Volume", "Pass Verticality", "Defensive Volume", "Aerial Volume"],
    },
    "Fullbacks": {
        "team": ["Possession", "Passes", "Pressing", "Build Up Speed", "Attacking Territory"],
        "role": ["Pass Volume", "Progression Volume", "Defensive Volume", "Attacking Contribution", "Retention"],
    },
    "Central Midfield": {
        "team": ["Possession", "Passes", "Pressing", "Build Up Speed", "Attacking Territory"],
        "role": ["Pass Volume", "Progression Volume", "Defensive Volume", "Attacking Contribution", "Retention"],
    },
    "Attackers": {
        "team": ["Possession", "Passes", "Pressing", "Build Up Speed", "Attacking Territory", "Long Balls"],
        "role": ["Pass Volume", "Creativity", "Goal Threat", "Deeper Playmaking", "Ball Carrying", "Retention"],
    },
    "Strikers": {
        "team": ["Possession", "Passes", "Pressing", "Build Up Speed", "Attacking Territory", "xG"],
        "role": ["Pass Volume", "Aerial Requirement", "Ball Carrying", "Retention", "Opportunities", "Goal Output"],
    },
    "Goalkeepers": {
        "team": ["Possession", "Passes", "Build Up Speed", "Long Balls", "Line Height"],
        "role": ["Pass Volume", "Sweeping", "Retention", "Shots Faced"],
    },
}

# ── Init session state ─────────────────────────────────────────────────────────
for title, cfg in DEFAULTS.items():
    rk = title.lower().replace(" ", "_")
    for side in ("team", "role"):
        sk = f"metrics_{rk}_{side}"
        if sk not in st.session_state:
            st.session_state[sk] = list(cfg[side])

# ── Callbacks ──────────────────────────────────────────────────────────────────
def do_add(rk, side):
    sel = st.session_state.get(f"addsel_{rk}_{side}", "")
    sk  = f"metrics_{rk}_{side}"
    if sel and sel != "—" and sel not in st.session_state[sk]:
        st.session_state[sk].append(sel)

def do_remove(rk, side, metric):
    sk = f"metrics_{rk}_{side}"
    if metric in st.session_state[sk] and len(st.session_state[sk]) > 4:
        st.session_state[sk].remove(metric)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tabs = st.tabs(list(DEFAULTS.keys()))

for tab, title in zip(tabs, DEFAULTS.keys()):
    with tab:
        rk        = title.lower().replace(" ", "_")
        cache_key = f"png_{rk}"
        c1, c2    = st.columns([1, 2])

        with c1:
            for side, color in (("team", "#60a5fa"), ("role", "#f472b6")):
                sk      = f"metrics_{rk}_{side}"
                metrics = st.session_state[sk]

                st.markdown(
                    f'<p style="color:{color};font-weight:700;font-size:13px;'
                    f'margin-top:10px;margin-bottom:4px;">{side.upper()}</p>',
                    unsafe_allow_html=True,
                )

                # Add row
                available = ["—"] + [m for m in ALL_METRICS if m not in metrics]
                a1, a2 = st.columns([4, 1])
                with a1:
                    st.selectbox("add", available, key=f"addsel_{rk}_{side}",
                                 label_visibility="collapsed")
                with a2:
                    st.button("＋", key=f"addbtn_{rk}_{side}",
                              on_click=do_add, args=(rk, side),
                              use_container_width=True)

                # Metric rows
                for m in list(metrics):
                    r1, r2 = st.columns([3, 1])
                    with r1:
                        st.number_input(m, 0, 100, 50, 1,
                                        key=f"val_{rk}_{side}_{m}")
                    with r2:
                        if len(metrics) > 4:
                            st.button("✕", key=f"rem_{rk}_{side}_{m}",
                                      on_click=do_remove, args=(rk, side, m),
                                      use_container_width=True)

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            generate = st.button("Generate", key=f"gen_{rk}",
                                 use_container_width=True, type="primary")

        with c2:
            if generate:
                t_metrics = st.session_state[f"metrics_{rk}_team"]
                r_metrics = st.session_state[f"metrics_{rk}_role"]
                t_pcts = [int(st.session_state.get(f"val_{rk}_team_{m}", 50)) for m in t_metrics]
                r_pcts = [int(st.session_state.get(f"val_{rk}_role_{m}", 50)) for m in r_metrics]

                fig = build_chart(t_metrics, t_pcts, r_metrics, r_pcts)
                buf = io.BytesIO()
                fig.savefig(buf, format="png", dpi=300,
                            bbox_inches="tight", facecolor=fig.get_facecolor())
                plt.close(fig)
                buf.seek(0)
                st.session_state[cache_key] = buf.getvalue()

            if cache_key in st.session_state:
                st.markdown(
                    f'<p style="color:#9ca3af;font-size:12px;margin-bottom:0;">'
                    f'{title} — Projected View</p>',
                    unsafe_allow_html=True,
                )
                st.image(st.session_state[cache_key], use_container_width=True)
                st.download_button(
                    f"⬇️ Download {title}",
                    data=st.session_state[cache_key],
                    file_name=f"projected_{rk}.png",
                    mime="image/png",
                    key=f"dl_{rk}",
                )
            else:
                st.markdown(
                    '<p style="color:#4b5563;font-size:14px;text-align:center;margin-top:100px;">'
                    'Set values and click <b>Generate</b></p>',
                    unsafe_allow_html=True,
                )
