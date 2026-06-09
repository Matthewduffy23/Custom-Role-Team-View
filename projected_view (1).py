# projected_view.py — Standalone Projected View
# pip install streamlit matplotlib numpy
# streamlit run projected_view.py

import io
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import streamlit as st

st.set_page_config(page_title="Projected View", layout="wide")
st.markdown('<h2 style="color:#ffffff;">🎯 Projected View</h2>', unsafe_allow_html=True)
st.markdown(
    '<p style="color:#9ca3af;font-size:13px;">'
    'Enter percentiles (0–100) for each metric then click <b>Generate</b>. '
    'Left = Team &nbsp;·&nbsp; Right = Role</p>',
    unsafe_allow_html=True,
)

# ── Chart function ─────────────────────────────────────────────────────────────
_CMAP = LinearSegmentedColormap.from_list("rr", ["#ef4444", "#f97316", "#facc15", "#4ade80"])

def build_chart(team_labels, team_pcts, role_labels, role_pcts):
    TEAM_TRACK = "#2b3646"
    ROLE_TRACK = "#362b46"
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

# ── Role configs ───────────────────────────────────────────────────────────────
TABS = {
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

# ── Render ─────────────────────────────────────────────────────────────────────
tabs = st.tabs(list(TABS.keys()))

for tab, (title, cfg) in zip(tabs, TABS.items()):
    with tab:
        rk = title.lower().replace(" ", "_")
        cache_key = f"png_{rk}"

        c1, c2 = st.columns([1, 2])

        with c1:
            st.markdown('<p style="color:#60a5fa;font-weight:700;font-size:13px;margin-bottom:4px;">TEAM</p>', unsafe_allow_html=True)
            t_pcts = []
            for m in cfg["team"]:
                t_pcts.append(st.number_input(m, 0, 100, 50, 1, key=f"t_{rk}_{m}"))

            st.markdown('<p style="color:#f472b6;font-weight:700;font-size:13px;margin-top:10px;margin-bottom:4px;">ROLE</p>', unsafe_allow_html=True)
            r_pcts = []
            for m in cfg["role"]:
                r_pcts.append(st.number_input(m, 0, 100, 50, 1, key=f"r_{rk}_{m}"))

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            if st.button("Generate", key=f"gen_{rk}", use_container_width=True, type="primary"):
                fig = build_chart(cfg["team"], t_pcts, cfg["role"], r_pcts)
                buf = io.BytesIO()
                fig.savefig(buf, format="png", dpi=300, bbox_inches="tight",
                            facecolor=fig.get_facecolor())
                plt.close(fig)
                buf.seek(0)
                st.session_state[cache_key] = buf.getvalue()

        with c2:
            if cache_key in st.session_state:
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
