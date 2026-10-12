---
name: "modelo-ifc-3d-nd"
description: "Gerar o modelo IFC (abre no Tekla, Revit e visualizadores IFC) e a página 3D para celular de uma obra ND a partir das definições de projeto; ler IFC recebido e tirar peças, volumes e 3D. Use ao concluir ou revisar um projeto, quando Nathan pedir IFC, modelo BIM, 3D da estrutura ou para replicar/adaptar um modelo, sem precisar de Tekla."
---

# Modelo IFC e 3D da ND

Nathan não tem licença do Tekla. O caminho da ND para modelo estrutural é o **IFC** (formato aberto que Tekla, Revit, Eberick e TQS importam e exportam), gerado em Python com ifcopenshell a partir do mesmo modelo de peças que alimenta cálculo, pranchas e listas (DEC-008 e DEC-009 do nd_estruturas).

Use junto com: `projeto-estruturas-pre-moldadas` (concepção e ligações), `pranchas-tecnicas-nd` (convenção de marcas), `arquitetura-software-nd` (regras de código), `modelagem-3d-reels-nd` (imagens/vídeo de marketing, que são outra coisa).

## Onde está o código

Repositório `engnathandelgado-design/ndengenharia`, pacote `nd_estruturas`:

- `nd_estruturas/bim.py`: domínio e writers.
  - `PerfilRetangular(b, h)` e `PerfilI(h, b, tw, tf)` validam a entrada e calculam a área.
  - `Peca(tipo, grupo, marca, perfil, p0, p1, cima, material, obs)` é uma extrusão do perfil de p0 a p1. Tipos: pilar, viga, laje, placa, terca, contravento, consolo, inserto, fundacao.
  - `ModeloBIM` é o builder: `pilar()`, `linear()`, `bloco()`, `pendente()`.
  - `quantitativos(modelo)` dá peças, comprimento e volume por grupo.
  - `gravar_ifc(modelo, caminho)` grava IFC4, com pset `ND_Peca` (Grupo, Marca, Secao, Comprimento_m, Volume_m3, Obs, Autor).
  - `ler_malha_ifc(caminho)` tessela o IFC, inclusive um IFC recebido de terceiros.
  - `gravar_visualizador(malha, html, titulo, subtitulo, pendencias, quant)` gera a página 3D.
- `nd_estruturas/visualizador_3d.py`: modelo HTML (three.js r128). Tem camadas, toque na peça, vistas e pendências, marca d'água "projeto da ND Engenharia" e tema claro e escuro.
- `tests/test_bim.py`: testes conferidos à mão (área da I90, viga a 3 %) e um ponta a ponta (IFC, malha e HTML, com volume tesselado igual ao do domínio).
- Exemplo completo: `exemplos/letsara/modelo_bim.py`.

Instalação: `pip install -e ".[bim]"` dentro de `nd_estruturas` (no ambiente do Claude: `pip install ifcopenshell --break-system-packages`).

## Fluxo ao concluir um projeto

1. **Juntar as definições finais**, de onde estiverem: documento de controle da obra no Drive (pasta da obra), rodadas de cálculo, pranchas de montagem, `exemplos/<obra>/`. Se a obra já tem `modelo_bim.py`, só atualizar os parâmetros.
2. **Escrever ou atualizar `exemplos/<obra>/modelo_bim.py`**:
   - parâmetros no topo (eixos, níveis, inclinação, seções);
   - uma função `montar()` que devolve o `ModeloBIM`;
   - as pendências registradas com `m.pendente()`. Use o prefixo `!` para um conflito de nível ou geometria; ele aparece em destaque na página.
3. **Rodar** `python exemplos/<obra>/modelo_bim.py` (saída em `exemplos/<obra>/saidas/`, fora do git). Conferir os quantitativos impressos contra o orçamento e a memória.
4. **Conferir antes de entregar**:
   - contagem por grupo;
   - volumes na ordem de grandeza;
   - z mínimo e z máximo contra os níveis do arquitetônico (cobertura x platibanda, consolos x vigas);
   - uma vista renderizada (matplotlib ou a própria página) para pegar peça deitada ou girada.

   A orientação vem do vetor `cima`:
   - pilares usam `cima=(0, 1, 0)`, com b ao longo de X;
   - vigas e placas usam `cima=(0, 0, 1)`, com b do perfil na horizontal.
5. **Entregar**:
   - publicar `saidas/<obra>_3d.html` como artefato, para Nathan ver no celular (nada de .zip). Se a obra já tem página, republicar no mesmo link com `url`;
   - mandar o `.ifc` com SendUserFile;
   - salvar o script na pasta da obra no Drive quando o repositório não estiver acessível;
   - fazer commit do `modelo_bim.py` (nunca das saídas).

## Ler ou replicar um modelo recebido

- IFC exportado do Tekla ou do Revit: `ler_malha_ifc()` para o 3D. Para quantitativos, ler os psets do arquivo (`ifcopenshell.util.element.get_psets`) e agrupar por classe e perfil.
- Para replicar ou adaptar o modelo, reconstruir como `ModeloBIM` parametrizado, com vãos, alturas e módulos nos parâmetros, e gerar um IFC novo.
- Sem IFC, só com PDF de pranchas: tirar eixos, níveis e seções da prancha e montar o `modelo_bim.py`. Registrar como pendência tudo o que foi suposto.

## Limites (dizer ao Nathan quando importar)

- Geometria é envelope do perfil: sem alvéolos, chanfros, recortes, dentes Gerber ou insertos detalhados. O volume serve para conferência, não para o orçamento final de concreto da laje alveolar.
- Não gera armadura nem desenho de fábrica no IFC. Pranchas saem pelo `pranchas-tecnicas-nd`.
- Terça metálica entra como caixa envelope; o peso de aço vem do cálculo, não do volume do IFC.

## Lições da Letsara (12/10/2026)

- O modelo mostrou um conflito que a planilha não mostrou: com consolo em +9,28 no lado alto, a I90 e a terça passam do topo da platibanda (+10,00). Sempre comparar o z máximo da cobertura com o topo do pilar nos dois lados da água.
- A ordem de `IfcProduct` no arquivo não é a de criação; `ler_malha_ifc` ordena pelo id.
- Placas das fachadas de frente e fundo saíram deitadas na primeira versão por trocar b e h. O teste de orientação do pilar e a vista renderizada pegam esse tipo de erro.
