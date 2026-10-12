"""Itens comuns das páginas: marca d'água e estilo dos gráficos."""
import plotly.graph_objects as go

MARCA = "projeto da ND Engenharia"


def marcar(fig: go.Figure, altura: int = 460) -> go.Figure:
    """Aplica layout padrão e a marca 'projeto da ND Engenharia' no gráfico."""
    fig.add_annotation(text=MARCA, xref="paper", yref="paper", x=0.99, y=0.01,
                       xanchor="right", yanchor="bottom", showarrow=False,
                       font=dict(size=11, color="rgba(120,120,120,0.85)"))
    fig.update_layout(height=altura, margin=dict(l=10, r=10, t=40, b=10),
                      template="plotly_white", legend=dict(orientation="h", y=1.08))
    return fig


def fmt(v: float, casas: int = 2) -> str:
    """Número no padrão brasileiro (1.234,56)."""
    s = f"{v:,.{casas}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")
