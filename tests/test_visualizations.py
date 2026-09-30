import plotly.graph_objects as go

from benefits_market_intelligence.visualizations import save, style


def test_base_theme_sets_title_and_house_style():
    fig = style.base_theme(go.Figure(go.Bar(x=[1], y=[2])), "Broker pay", height=400)
    assert fig.layout.title.text == "Broker pay"
    assert fig.layout.height == 400
    assert tuple(fig.layout.colorway) == tuple(style.PALETTE)
    assert fig.data[0].marker.line.width == 0


def test_base_theme_puts_the_subtitle_on_a_second_line():
    fig = style.base_theme(go.Figure(go.Scatter(x=[1], y=[2])), "Title", "Subtitle")
    assert fig.layout.title.text == "Title<br><sup>Subtitle</sup>"
    assert fig.layout.height == 620
    assert fig.data[0].line.width == 2


def test_save_figure_writes_a_png_at_double_scale(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(
        go.Figure, "write_image", lambda self, *a, **k: calls.append((a, k))
    )
    save.save_figure(go.Figure(), "chart", tmp_path)
    assert calls == [((tmp_path / "chart.png",), {"scale": 2})]
