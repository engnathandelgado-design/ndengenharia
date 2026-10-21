"""BIM ND — modelo de peças lineares, exportação IFC e visualizador 3D para celular.

Camadas:
- domínio (sem dependência externa): PerfilRetangular, PerfilI, Peca, ModeloBIM, quantitativos;
- writers nas bordas: gravar_ifc (adapter do ifcopenshell), ler_malha_ifc, gravar_visualizador.

Convenção: m, coordenadas globais X (largura), Y (comprimento), Z (nível a partir do piso
acabado). Cada peça é uma extrusão do perfil entre p0 e p1; o eixo Y local do perfil fica o
mais próximo possível do vetor `cima` (vigas: +Z; pilares: +Y, com b do perfil ao longo de X).

O IFC sai com propriedades ND_Peca (Grupo, Marca, Secao, Comprimento_m, Volume_m3, Obs) e
autoria "projeto da ND Engenharia". Abre em Tekla, Revit, BIMcollab Zoom e visualizadores IFC.
"""
from __future__ import annotations

import json
import math
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path

AUTORIA = "projeto da ND Engenharia"

# classe IFC por tipo de peça (mapeamento em vez de if/elif)
CLASSES_IFC = {
    "pilar": "IfcColumn",
    "viga": "IfcBeam",
    "laje": "IfcSlab",
    "placa": "IfcPlate",
    "terca": "IfcMember",
    "contravento": "IfcMember",
    "consolo": "IfcBuildingElementProxy",
    "inserto": "IfcBuildingElementProxy",
    "fundacao": "IfcFooting",
}


class DadoInvalido(ValueError):
    """Entrada fora do que o modelo aceita; a mensagem diz o que corrigir."""


# --------------------------------------------------------------------------- perfis


@dataclass(frozen=True)
class PerfilRetangular:
    b: float  # m, ao longo do X local
    h: float  # m, ao longo do Y local
    nome: str = ""

    def __post_init__(self):
        if self.b <= 0 or self.h <= 0:
            raise DadoInvalido(f"perfil retangular com b={self.b} e h={self.h}: as duas medidas precisam ser > 0 m")

    @property
    def rotulo(self) -> str:
        return self.nome or f"{self.b * 100:.0f}x{self.h * 100:.0f}"

    @property
    def area(self) -> float:  # m²
        return self.b * self.h


@dataclass(frozen=True)
class PerfilI:
    """I simétrico de mesas retangulares (chanfros e mísulas não entram no volume)."""

    h: float   # altura total, m
    b: float   # largura das mesas, m
    tw: float  # espessura da alma, m
    tf: float  # espessura de cada mesa, m
    nome: str = ""

    def __post_init__(self):
        if min(self.h, self.b, self.tw, self.tf) <= 0:
            raise DadoInvalido("perfil I: h, b, tw e tf precisam ser > 0 m")
        if self.tw >= self.b:
            raise DadoInvalido(f"perfil I: alma tw={self.tw} m precisa ser menor que a mesa b={self.b} m")
        if 2 * self.tf >= self.h:
            raise DadoInvalido(f"perfil I: duas mesas de {self.tf} m não cabem na altura h={self.h} m")

    @property
    def rotulo(self) -> str:
        return self.nome or f"I{self.h * 100:.0f}"

    @property
    def area(self) -> float:  # m²
        return 2 * self.b * self.tf + self.tw * (self.h - 2 * self.tf)


@dataclass(frozen=True)
class PerfilPoligono:
    """Perfil qualquer dado pelo contorno (u, v) em m, sentido qualquer, sem repetir o primeiro ponto.
    Uso típico: elevação real de uma peça (pontas a prumo, dentes, cunhas) extrudada na largura."""

    pontos: tuple
    nome: str = ""

    def __post_init__(self):
        if len(self.pontos) < 3:
            raise DadoInvalido("perfil poligonal precisa de pelo menos 3 pontos")
        if self.area < 1e-8:
            raise DadoInvalido(f"perfil poligonal '{self.nome}' com área nula")

    @property
    def rotulo(self) -> str:
        return self.nome or "poligono"

    @property
    def area(self) -> float:  # m² (fórmula de Gauss)
        p = self.pontos
        return abs(sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p)))) / 2


Perfil = PerfilRetangular | PerfilI | PerfilPoligono


# --------------------------------------------------------------------------- peças e modelo


def _vet(a, b):
    return tuple(bb - aa for aa, bb in zip(a, b))


def _norma(v):
    return math.sqrt(sum(c * c for c in v))


@dataclass(frozen=True)
class Peca:
    tipo: str            # chave de CLASSES_IFC
    grupo: str           # camada no visualizador e nos quantitativos
    marca: str
    perfil: Perfil
    p0: tuple            # (x, y, z) m
    p1: tuple
    cima: tuple = (0.0, 0.0, 1.0)
    material: str = "concreto"   # "concreto" | "aco"
    obs: str = ""

    def __post_init__(self):
        if self.tipo not in CLASSES_IFC:
            raise DadoInvalido(f"tipo de peça '{self.tipo}' desconhecido; use um de {sorted(CLASSES_IFC)}")
        if self.material not in ("concreto", "aco"):
            raise DadoInvalido(f"material '{self.material}' desconhecido; use 'concreto' ou 'aco'")
        if self.comprimento < 1e-3:
            raise DadoInvalido(f"peça {self.marca}: p0 e p1 coincidem (comprimento < 1 mm)")

    @property
    def comprimento(self) -> float:
        return _norma(_vet(self.p0, self.p1))

    @property
    def volume(self) -> float:  # m³ (envelope do perfil)
        return self.perfil.area * self.comprimento

    def matriz(self):
        """Matriz 4×4 (lista de linhas) com Z local ao longo de p0→p1 e Y local perto de `cima`."""
        z = _vet(self.p0, self.p1)
        L = _norma(z)
        z = tuple(c / L for c in z)
        up = self.cima
        if abs(sum(a * b for a, b in zip(up, z))) / _norma(up) > 0.99:
            up = (0.0, 1.0, 0.0)
        x = (up[1] * z[2] - up[2] * z[1], up[2] * z[0] - up[0] * z[2], up[0] * z[1] - up[1] * z[0])
        nx = _norma(x)
        x = tuple(c / nx for c in x)
        y = (z[1] * x[2] - z[2] * x[1], z[2] * x[0] - z[0] * x[2], z[0] * x[1] - z[1] * x[0])
        return [[x[i], y[i], z[i], self.p0[i]] for i in range(3)] + [[0.0, 0.0, 0.0, 1.0]]


@dataclass
class ModeloBIM:
    """Builder do modelo: acumula peças e pendências; `congelar()` devolve tuplas imutáveis."""

    projeto: str
    obra: str = ""
    pecas: list = field(default_factory=list)
    pendencias: list = field(default_factory=list)

    def add(self, peca: Peca) -> Peca:
        self.pecas.append(peca)
        return peca

    def pilar(self, marca, x, y, b_x, b_y, z_base, z_topo, grupo="Pilares", obs=""):
        """Pilar vertical; b_x ao longo de X global, b_y ao longo de Y global."""
        return self.add(Peca("pilar", grupo, marca, PerfilRetangular(b_x, b_y), (x, y, z_base), (x, y, z_topo),
                             cima=(0.0, 1.0, 0.0), obs=obs))

    def linear(self, tipo, marca, perfil, p0, p1, grupo, cima=(0.0, 0.0, 1.0), material="concreto", obs=""):
        """Viga, terça, laje, placa: extrusão de p0 a p1 (centro do perfil), Y local perto de `cima`."""
        return self.add(Peca(tipo, grupo, marca, perfil, tuple(p0), tuple(p1), tuple(cima), material, obs))

    def extrusao_y(self, tipo, marca, contorno_xz, y, largura, grupo, material="concreto", obs=""):
        """Peça dada pela elevação real no plano XZ global (lista de (x, z) em m), extrudada na largura em torno de y.
        Serve para vigas com pontas a prumo, dentes, cunhas e caimento (o contorno já está na posição montada)."""
        x0, z0 = contorno_xz[0]
        perfil = PerfilPoligono(tuple((round(x - x0, 6), round(z - z0, 6)) for x, z in contorno_xz), marca)
        return self.add(Peca(tipo, grupo, marca, perfil, (x0, y + largura / 2, z0), (x0, y - largura / 2, z0), (0.0, 0.0, 1.0), material, obs))

    def bloco(self, tipo, marca, centro_topo, b_x, b_y, h, grupo):
        """Bloco vertical (consolo, inserto) com topo em centro_topo."""
        x, y, z = centro_topo
        return self.add(Peca(tipo, grupo, marca, PerfilRetangular(b_x, b_y), (x, y, z - h), (x, y, z),
                             cima=(0.0, 1.0, 0.0)))

    def pendente(self, texto: str):
        self.pendencias.append(texto)


def quantitativos(modelo: ModeloBIM) -> OrderedDict[str, dict]:
    """Peças, comprimento total (m) e volume de envelope (m³) por grupo, na ordem de criação."""
    q: OrderedDict[str, dict] = OrderedDict()
    for p in modelo.pecas:
        g = q.setdefault(p.grupo, {"pecas": 0, "comprimento_m": 0.0, "volume_m3": 0.0, "material": p.material})
        g["pecas"] += 1
        g["comprimento_m"] += p.comprimento
        g["volume_m3"] += p.volume
    for g in q.values():
        g["comprimento_m"] = round(g["comprimento_m"], 2)
        g["volume_m3"] = round(g["volume_m3"], 3)
    return q


# --------------------------------------------------------------------------- writer IFC (adapter)


def gravar_ifc(modelo: ModeloBIM, caminho) -> Path:
    """Grava o modelo em IFC4. Requer ifcopenshell (extra `bim`)."""
    import ifcopenshell
    import numpy as np
    from ifcopenshell import api

    f = ifcopenshell.file(schema="IFC4")
    proj = api.run("root.create_entity", f, ifc_class="IfcProject", name=modelo.projeto)
    api.run("unit.assign_unit", f, length={"is_metric": True, "raw": "METERS"})
    ctx = api.run("context.add_context", f, context_type="Model")
    body = api.run("context.add_context", f, context_type="Model", context_identifier="Body",
                   target_view="MODEL_VIEW", parent=ctx)
    site = api.run("root.create_entity", f, ifc_class="IfcSite", name=modelo.obra or modelo.projeto)
    bldg = api.run("root.create_entity", f, ifc_class="IfcBuilding", name=modelo.projeto)
    storey = api.run("root.create_entity", f, ifc_class="IfcBuildingStorey", name="Estrutura")
    api.run("aggregate.assign_object", f, relating_object=proj, products=[site])
    api.run("aggregate.assign_object", f, relating_object=site, products=[bldg])
    api.run("aggregate.assign_object", f, relating_object=bldg, products=[storey])
    mats = {
        "concreto": api.run("material.add_material", f, name="Concreto", category="concrete"),
        "aco": api.run("material.add_material", f, name="Aço", category="steel"),
    }

    perfis = {}

    def perfil_ifc(p):
        if p not in perfis:
            if isinstance(p, PerfilPoligono):
                pts = [f.create_entity("IfcCartesianPoint", Coordinates=(float(u), float(v))) for u, v in p.pontos]
                curva = f.create_entity("IfcPolyline", Points=pts + [pts[0]])
                perfis[p] = f.create_entity("IfcArbitraryClosedProfileDef", ProfileType="AREA", ProfileName=p.rotulo, OuterCurve=curva)
            elif isinstance(p, PerfilI):
                perfis[p] = f.create_entity("IfcIShapeProfileDef", ProfileType="AREA", ProfileName=p.rotulo,
                                            OverallWidth=p.b, OverallDepth=p.h, WebThickness=p.tw,
                                            FlangeThickness=p.tf)
            else:
                perfis[p] = f.create_entity("IfcRectangleProfileDef", ProfileType="AREA", ProfileName=p.rotulo,
                                            XDim=p.b, YDim=p.h)
        return perfis[p]

    for p in modelo.pecas:
        ent = api.run("root.create_entity", f, ifc_class=CLASSES_IFC[p.tipo], name=p.marca)
        rep = api.run("geometry.add_profile_representation", f, context=body, profile=perfil_ifc(p.perfil),
                      depth=p.comprimento)
        api.run("geometry.assign_representation", f, product=ent, representation=rep)
        api.run("geometry.edit_object_placement", f, product=ent, matrix=np.array(p.matriz()), is_si=True)
        api.run("spatial.assign_container", f, relating_structure=storey, products=[ent])
        api.run("material.assign_material", f, products=[ent], material=mats[p.material])
        ps = api.run("pset.add_pset", f, product=ent, name="ND_Peca")
        api.run("pset.edit_pset", f, pset=ps, properties={
            "Grupo": p.grupo, "Marca": p.marca, "Secao": p.perfil.rotulo,
            "Comprimento_m": round(p.comprimento, 3), "Volume_m3": round(p.volume, 4),
            "Obs": p.obs, "Autor": AUTORIA})
    caminho = Path(caminho)
    f.write(str(caminho))
    return caminho


def ler_malha_ifc(caminho) -> OrderedDict[str, list]:
    """Tessela cada produto do IFC; devolve {grupo: [{n, v, f, vol}]} em coordenadas globais."""
    import ifcopenshell
    import ifcopenshell.geom
    import ifcopenshell.util.element as ue
    import ifcopenshell.util.shape as us

    f = ifcopenshell.open(str(caminho))
    s = ifcopenshell.geom.settings()
    s.set("use-world-coords", True)
    grupos: OrderedDict[str, list] = OrderedDict()
    for el in sorted(f.by_type("IfcProduct"), key=lambda e: e.id()):  # ordem de criação
        if not el.Representation:
            continue
        ps = ue.get_pset(el, "ND_Peca") or {}
        sh = ifcopenshell.geom.create_shape(s, el)
        nome = f"{ps.get('Marca', el.Name or el.is_a())} · {ps.get('Secao', '')} · L = {ps.get('Comprimento_m', '?')} m"
        grupos.setdefault(ps.get("Grupo", el.is_a()), []).append({
            "n": nome, "v": [round(c, 3) for c in sh.geometry.verts], "f": list(sh.geometry.faces),
            "vol": us.get_volume(sh.geometry)})
    return grupos


# --------------------------------------------------------------------------- visualizador 3D


def _data_url(caminho):
    import base64, mimetypes
    tipo = mimetypes.guess_type(str(caminho))[0] or "image/png"
    return f"data:{tipo};base64," + base64.b64encode(Path(caminho).read_bytes()).decode()


def gravar_visualizador(malha, caminho, titulo: str, subtitulo: str = "", pendencias=(), cores=None,
                        ocultas=("Placas de fechamento",), quant=None, pranchas=(), conexoes=(), logo_cliente=None, cliente="", autoria=AUTORIA) -> Path:
    """Página HTML única (three.js) com camadas, toque na peça, pendências e marca d'água ND.

    pranchas: lista de dict(nome, desc, img) — img é data-URL (jpeg/png) da prancha, para ver no celular;
    conexoes: lista de dict(grupo, peca_a, inserto_a, peca_b, inserto_b, verificacao, valor, ok, obs);
    logo_cliente: caminho da imagem da logo do cliente (fica no canto superior direito da tela 3D).
    """
    from .visualizador_3d import MODELO_HTML

    leve = OrderedDict((g, [{"n": it["n"], "v": it["v"], "f": it["f"]} for it in itens]) for g, itens in malha.items())
    cfg = {
        "titulo": titulo, "subtitulo": subtitulo, "pendencias": list(pendencias),
        "cores": cores or {}, "ocultas": list(ocultas), "autoria": autoria, "quant": quant or {},
        "pranchas": list(pranchas), "conexoes": list(conexoes), "cliente": cliente,
        "logo_cliente": _data_url(logo_cliente) if logo_cliente else None,
    }
    html = (MODELO_HTML
            .replace("__TITULO__", _esc(titulo))
            .replace("/*CFG*/null", json.dumps(cfg, ensure_ascii=False))
            .replace("/*DATA*/null", json.dumps(leve, separators=(",", ":"))))
    caminho = Path(caminho)
    caminho.write_text(html, encoding="utf-8")
    return caminho


def _esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
