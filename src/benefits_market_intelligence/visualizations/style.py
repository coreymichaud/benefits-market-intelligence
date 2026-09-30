# Color palette
PALETTE = [
    "#86BC25",  # D. Green
    "#43B02A",  # Green 4
    "#046A38",  # Green 6
]

# Accent colors
ACCENT = "#0D8390"
ACCENT_2 = "#007CB0"

# Text colors
BLACK = "#000000"
GREY = "#929292"

# Optional semantic colors
RED = "#AA3036"
GREEN = "#43B02A"


# Base theme for all figures
def base_theme(fig, title, subtitle=None, height=620):
    title_text = title if not subtitle else f"{title}<br><sup>{subtitle}</sup>"

    fig.update_layout(
        template="plotly_white",
        colorway=PALETTE,
        title={
            "text": title_text,
            "x": 0.02,
            "xanchor": "left",
            "font": dict(
                color=BLACK,
                family="Arial, sans-serif",
            ),
        },
        height=height,
        margin=dict(l=60, r=40, t=90, b=60),
        font=dict(
            family="Arial, sans-serif",
            color=BLACK,
        ),
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="right",
            x=1,
            font=dict(color=BLACK),
        ),
        hoverlabel=dict(
            bgcolor="white",
            font=dict(color=BLACK),
        ),
        # Axis styling
        xaxis=dict(
            title_font=dict(color=BLACK),
            tickfont=dict(color=BLACK),
        ),
        yaxis=dict(
            title_font=dict(color=BLACK),
            tickfont=dict(color=BLACK),
        ),
    )

    # Default trace styling
    fig.update_traces(
        marker_line_width=0,
        selector=dict(type="bar"),
    )

    # General trace styling
    fig.update_traces(
        selector=dict(type="scatter"),
        line=dict(width=2),
    )

    return fig
