"""
analysis.py - Data Analytics Dashboard
Loads chat_log.csv and generates sentiment visualizations using Pandas + Matplotlib.
Run: python analysis.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.gridspec import GridSpec
import os
import sys

# ─────────────────────────────────────────────
#  LOAD DATA
# ─────────────────────────────────────────────
LOG_FILE = "chat_log.csv"

def load_data() -> pd.DataFrame:
    """Load and validate the chat log CSV."""
    if not os.path.exists(LOG_FILE):
        print(f"[ERROR] '{LOG_FILE}' not found. Start the chatbot and have a conversation first!")
        sys.exit(1)

    df = pd.read_csv(LOG_FILE, parse_dates=["timestamp"])

    if df.empty:
        print("[ERROR] The log file is empty. No data to analyze.")
        sys.exit(1)

    print(f"[INFO] Loaded {len(df)} messages from '{LOG_FILE}'")
    return df


# ─────────────────────────────────────────────
#  PLOT 1: Sentiment Distribution (Pie + Bar)
# ─────────────────────────────────────────────
SENTIMENT_COLORS = {
    "positive": "#4CAF50",
    "negative": "#F44336",
    "neutral":  "#2196F3",
    "crisis":   "#FF5722",
}

def plot_sentiment_distribution(ax_pie, ax_bar, df: pd.DataFrame):
    """Dual chart: pie and bar for sentiment distribution."""
    counts = df["sentiment"].value_counts()
    colors = [SENTIMENT_COLORS.get(s, "#9E9E9E") for s in counts.index]

    # Pie chart
    wedges, texts, autotexts = ax_pie.pie(
        counts,
        labels=counts.index.str.capitalize(),
        autopct="%1.1f%%",
        colors=colors,
        startangle=140,
        wedgeprops=dict(edgecolor="white", linewidth=2),
        textprops={"fontsize": 11}
    )
    for at in autotexts:
        at.set_fontsize(9)
        at.set_color("white")
        at.set_fontweight("bold")
    ax_pie.set_title("Sentiment Distribution", fontsize=14, fontweight="bold", pad=15)

    # Bar chart
    bars = ax_bar.bar(
        counts.index.str.capitalize(),
        counts.values,
        color=colors,
        edgecolor="white",
        linewidth=1.5,
        width=0.55
    )
    for bar, val in zip(bars, counts.values):
        ax_bar.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                    str(val), ha="center", va="bottom", fontsize=11, fontweight="bold")
    ax_bar.set_title("Message Count by Sentiment", fontsize=14, fontweight="bold", pad=15)
    ax_bar.set_ylabel("Number of Messages", fontsize=11)
    ax_bar.set_xlabel("Sentiment", fontsize=11)
    ax_bar.set_ylim(0, counts.max() * 1.2)
    ax_bar.spines[["top", "right"]].set_visible(False)
    ax_bar.grid(axis="y", alpha=0.3, linestyle="--")


# ─────────────────────────────────────────────
#  PLOT 2: Sentiment Over Time
# ─────────────────────────────────────────────
def plot_sentiment_over_time(ax, df: pd.DataFrame):
    """Line chart of sentiment frequency grouped by hour."""
    df = df.copy()
    df["hour"] = df["timestamp"].dt.floor("H")

    pivot = (
        df.groupby(["hour", "sentiment"])
        .size()
        .unstack(fill_value=0)
    )

    for sentiment, color in SENTIMENT_COLORS.items():
        if sentiment in pivot.columns:
            ax.plot(pivot.index, pivot[sentiment],
                    label=sentiment.capitalize(),
                    color=color,
                    linewidth=2.5,
                    marker="o",
                    markersize=5)

    ax.set_title("Sentiment Trend Over Time", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Time", fontsize=11)
    ax.set_ylabel("Message Count", fontsize=11)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d\n%H:%M"))
    ax.legend(fontsize=10, framealpha=0.7)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(alpha=0.3, linestyle="--")


# ─────────────────────────────────────────────
#  PLOT 3: Summary Stats Table
# ─────────────────────────────────────────────
def plot_summary_table(ax, df: pd.DataFrame):
    """Text-based summary statistics."""
    ax.axis("off")
    total = len(df)
    counts = df["sentiment"].value_counts()
    most_common = counts.idxmax()

    time_range = ""
    if pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        start = df["timestamp"].min().strftime("%Y-%m-%d %H:%M")
        end   = df["timestamp"].max().strftime("%Y-%m-%d %H:%M")
        time_range = f"{start}  →  {end}"
    else:
        time_range = "N/A"

    lines = [
        ("📊 Total Messages",       str(total)),
        ("💚 Positive",             str(counts.get("positive", 0))),
        ("❤️  Negative",            str(counts.get("negative", 0))),
        ("💙 Neutral",              str(counts.get("neutral", 0))),
        ("🚨 Crisis",               str(counts.get("crisis", 0))),
        ("🏆 Most Common Sentiment", most_common.capitalize()),
        ("🕐 Time Range",           time_range),
    ]

    ax.set_title("Summary Statistics", fontsize=14, fontweight="bold", pad=15)
    for i, (label, value) in enumerate(lines):
        y = 0.88 - i * 0.13
        ax.text(0.05, y, label, transform=ax.transAxes,
                fontsize=11, color="#555", va="top")
        ax.text(0.65, y, value, transform=ax.transAxes,
                fontsize=11, color="#111", va="top", fontweight="bold")


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def main():
    df = load_data()

    # Set up figure
    fig = plt.figure(figsize=(16, 10), facecolor="#F8F9FA")
    fig.suptitle(
        "🧠 Mental Health Chatbot — Sentiment Analytics Dashboard",
        fontsize=18, fontweight="bold", y=0.98, color="#333"
    )

    gs = GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)
    ax_pie   = fig.add_subplot(gs[0, 0])
    ax_bar   = fig.add_subplot(gs[0, 1])
    ax_stats = fig.add_subplot(gs[0, 2])
    ax_time  = fig.add_subplot(gs[1, :])  # full-width bottom row

    # Set subplot backgrounds
    for ax in [ax_pie, ax_bar, ax_stats, ax_time]:
        ax.set_facecolor("#FFFFFF")

    plot_sentiment_distribution(ax_pie, ax_bar, df)
    plot_summary_table(ax_stats, df)
    plot_sentiment_over_time(ax_time, df)

    output_path = "sentiment_analysis.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="#F8F9FA")
    print(f"[INFO] Dashboard saved to '{output_path}'")
    plt.show()


if __name__ == "__main__":
    main()
