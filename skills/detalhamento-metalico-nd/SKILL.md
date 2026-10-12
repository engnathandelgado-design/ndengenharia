---
name: "detalhamento-metalico-nd"
description: "Ler, revisar, converter (PDF/DWG→DXF) e revisar/reemitir pranchas SolidWorks de formas e estruturas metálicas no padrão ND Engenharia (ASM/SUBASM/PART), com listas de materiais e pesos."
---

# Detalhamento metálico ND — leitura, revisão, DXF e reemissão

Use quando Nathan (ND Engenharia) enviar pranchas de formas metálicas ou estruturas soldadas, geralmente exportadas do SolidWorks em PDF (montagens ASM, submontagens SUBASM, peças PART), DWG ou listas de materiais em xlsx, e pedir para:
- entender ou salvar o projeto;
- gerar DXF;
- conferir a compatibilidade entre peças, montagens, soldas, furos e balões;
- aplicar alterações do cliente (dimensões, espessuras) e reemitir as folhas compatibilizadas.

Responda em português, direto e técnico. Sempre separe o que foi **corrigido** do que ficou **para confirmar**.

## 0. Ferramentas (preparar antes)

```bash
pip install --break-system-packages -q ezdxf pymupdf cairosvg openpyxl pillow numpy matplotlib
# só se houver DWG:
mkdir -p ~/dwgtool && cd ~/dwgtool && npm init -y >/dev/null && npm i @mlightcad/libredwg-web
```

Os scripts prontos estão no Project "ND ENGENHARIA PROJETOS DE FORMAS METALICAS", em `ferramentas/`. Baixe com `Projects project_read` e salve sem o `.txt`:

| Arquivo | Função |
|---|---|
| `pdf2dxf.py` | PDF vetorial → DXF. Lê a escala da legenda (`1:N`) e gera o DXF em **mm reais** da vista principal. Detecta círculos (furos viram CIRCLE). Camadas por espessura/cor; textos na camada TEXTO. Uso: `python3 pdf2dxf.py *.pdf --saida dxf` (`--escala 0` = automático). |
| `add_rasters.py` | Recompõe as imagens raster do PDF (vistas sombreadas, isométricas, logo) e insere no DXF como IMAGE na posição exata, em `dxf/img/`. Uso: `python3 add_rasters.py pasta_pdfs pasta_dxf`. |
| `dxfops.py` | Edição: `stretch(msp, rule)` (deslocamento por vértice), `set_text`, `find_text`, `add_text`, `iso_prism` (isométrica vetorial de perfil extrudado), `remove_image`, `clean_iso`. |
| `render_pdf.py` | DXF → PDF (A1 para ASM/SUBASM, A4 para PART), com as imagens atrás e fundo branco. Junta tudo num PDF. Uso: `python3 render_pdf.py SAIDA.pdf a.dxf b.dxf ...` |
| `json2dxf.py` + `dwg_read.mjs` | DWG → JSON (libredwg-web WASM) → DXF. Converte LINE, CIRCLE, ARC, ELLIPSE, LWPOLYLINE, SPLINE, TEXT, MTEXT, ATTRIB, INSERT, DIMENSION, HATCH e SOLID. |
| `exemplo_revisao_rev02.py` | Exemplo completo de revisão: espessura de chapas, mapeamento ao longo de um eixo, warp de raster, listas e pesos. Use como modelo. |

Se o Project não estiver acessível, reescreva os scripts seguindo as descrições acima e as regras da seção 6.

## 1. Ler as pranchas

1. Rode `pdfinfo` (formato, Creator SolidWorks) e `pdftotext -layout` (lista de materiais, notas e cotas como texto).
2. Rasterize para ver: A1 com `pdftoppm -r 55`, A4 com `-r 110`. Leia **todas** as folhas.
3. Para detalhes, faça crops em alta resolução com pymupdf (`page.get_pixmap(clip=Rect(...), matrix=Matrix(z,z))`). Faça crops sempre para:
   - pontas de seta dos balões;
   - símbolos de solda;
   - seções;
   - furações.
4. Planilhas: leia com openpyxl incluindo as fórmulas (`data_only=False`).

## 2. Padrão de entrega ND (manter em toda reemissão)

**Desenhos e folhas**
- Códigos: `ASM.xxx` é a montagem geral (A1), `SUBASM.xxx` a submontagem soldada (A1), `PART.xxx` a peça de fabricação (A4 paisagem).
- Legenda no canto inferior direito, com estes campos: DESENHO 3D | DESENHO 2D | APROVADO (Nathan Henrique Delgado) | DATA | MATERIAL | PROCESSOS | TRATAMENTO | ACABAMENTO | QTDE | DESCRIÇÃO | ESCALA | DES. Nº | REV | formato | FOLHA.
- Tolerâncias gerais NBR ISO 2768-1c. Símbolo de 1º diedro.
- Peça: "ASTM A36 / Corte e furação / Sem tratamento / Pintura". Montagem: "- / Corte e soldagem".

**Notas**
- Peça (OBS 1–3): isenta de arestas cortantes e rebarbas; furos escareados; medidas em mm.
- Montagem (OBS 1–6):
  - 4: GMAW ER70S-6 com Ar mistura, ou FCAW E71T-1 com 100% CO₂;
  - 5: soldas isentas de defeitos;
  - 6: NR-12, consultar a SUBASM de proteção.

**Linguagem gráfica**
- Cotas, balões e soldas em vermelho; isométrica sombreada; explodida com balões nas SUBASM.
- Lista de materiais no topo direito: Nº ITEM | DESCRIÇÃO | MATERIAL | DESENHO | QTD | PESO UNIT | PESO TOTAL. "PESO TOTAL DO CONJUNTO" em vermelho.
- O número do item é único no conjunto e se repete igual nas SUBASM.
- Descrição da peça: `NOME CxLxE` com espessura em polegada convertida (25,4 / 19,05 / 12,7 / 6,35 / 8).
- Cotagem por ordenadas nas chapas furadas; padrões de furação em nota ("PADRÃO LINEAR DE n FUROS…").
- Solda: filete "a/a TÍP." ou "TÍP.(4X)"; bandeira para solda de campo; intermitente "a ◺ L-p".

**Pesos**
- Aço com 7850 kg/m³, descontando furos e chanfros. Arredondar o unitário **para cima** (ceil): é o padrão das listas ND.
- Concreto com 2400 kg/m³.
- O total da folha precisa bater com a planilha xlsx.

## 3. Checklist de revisão (compatibilidade e montabilidade)

Monte o conjunto "no papel" a partir das PART e confira cada ponto:

1. **Legendas**: título e DES. Nº de cada folha batem com o arquivo. Desconfie de folha copiada sem trocar título ou número.
2. **Referências cruzadas**: notas que citam SUBASM (ex.: NR-12) apontam para a folha certa de cada conjunto.
3. **Listas de materiais**:
   - quantidades da ASM = soma das SUBASM × quantidade de SUBASM;
   - itens faltando na lista da SUBASM;
   - peso em branco;
   - texto duplicado no material;
   - QTDE da PART (por conjunto ou total da obra?).
4. **Balões**:
   - todo item tem balão ou nota de "item interno";
   - **a ponta de cada seta cai na peça certa** (dê zoom; já houve balões 2/3/5/12 trocados);
   - mesma numeração em submontagens comuns a dois conjuntos.
5. **Geometria e encaixes**:
   - chapa + espessuras = envelope;
   - comprimento interno = tubos e diafragmas;
   - malhas de furos alinhadas entre chapas opostas;
   - espaçamento dos furos × largura que a barra contorna;
   - comprimento da barra roscada = aperto + 2×(arruela 4 + porca M24 ≈ 21,5) + 2–3 fios.
6. **Furos**: Ø de folga (M24 → Ø27); furo igual ao Ø interno do tubo implica tubo de topo (verificar se a solda é acessível).
7. **Soldas**:
   - toda junta tem símbolo com dimensão;
   - filete máximo na borda = t − 1,5 mm para t ≥ 6,35;
   - mínimo pela NBR 8800: 5 mm para 6,35 < t ≤ 12,5 e 8 mm para t > 19;
   - acessibilidade e sequência de soldagem em caixas fechadas.
8. **Modelagem**: acessórios (dobradiças) modelados dentro da peça aparecem na PART e se repetem em peças espelhadas.
9. **Cotas faltantes**: posição de olhais, distância entre pilares, altura de níveis e interfaces (nivelador–pista etc.).
10. **Estrutura (estimativa, nunca "cálculo")**:
    - flexão do cabeçote com a força de protensão (n cordoalhas × ~140 kN; M = PL/4);
    - chapas finas em balanço;
    - olhal único (ligamento, borda);
    - apoio de chapas finas.
    - Diga as hipóteses e peça a força real.

## 4. Gerar DXF

1. Copie os PDFs para uma pasta com nomes limpos (tire o prefixo hash do upload).
2. `python3 pdf2dxf.py pdf_orig/*.pdf --saida dxf`, depois `python3 add_rasters.py pdf_orig dxf`.
3. **Valide** no DXF:
   - diâmetros dos CIRCLE (ex.: Ø27/Ø17 exatos) e distâncias entre furos = cotas;
   - o erro esperado é ≤ 0,02% (1850 lido como 1850,4).
4. Avise o usuário destas limitações:
   - cotas e hachuras viram linhas soltas;
   - para CNC/laser, o ideal é o DXF exportado direto do SolidWorks;
   - a pasta `img/` precisa ficar junto dos DXF.
5. DWG: `node dwg_read.mjs arq.dwg arq.json`, depois `python3 json2dxf.py arq.json arq.dxf`. O código de erro 64 é aviso. Os quadros de folha são INSERT na camada FORMATO; use os bbox deles para renderizar cada folha.

## 5. Aplicar uma revisão (alteração do cliente)

1. **Entenda o papel da peça no conjunto** antes de mudar. Exemplos:
   - a maleta preenche o vão cabeçote–pilar (600) → mudar a maleta move o cabeçote, que encurta a pista;
   - espessuras do revestimento mudam o envelope do pilar, que muda o aperto das barras, que muda o comprimento da barra.
   
   Liste todas as peças afetadas e mostre as contas no resumo.
2. **Geometria do DXF**: meça as coordenadas reais lendo segmentos longos e textos (por vista; use bbox de região), depois aplique `stretch` com regras por região:
   - deslocamento rígido do lado livre;
   - para espessuras, mapeamento por distância ao eixo (`map_axis`): miolo fixo, faixa da chapa escalada, o resto deslocado;
   - mova as cotas junto (linha, extensão, seta) e reposicione e troque o texto da cota.
3. **Raster**: as vistas ortogonais das ASM **também são raster sombreado**. Quando a geometria muda, ajuste o PNG:
   - vista ao longo do eixo da mudança: reamostragem de colunas com a mesma função usada nos vetores (`warp_columns`);
   - vista frontal com pilar mais estreito: só nas linhas em que o pilar aparece sozinho (`warp_front_pillars`).
   - Isométricas não dá para corrigir: deixe nota "VISTA ISOMÉTRICA REPRESENTATIVA DA REV xx – ATUALIZAR RENDER NO MODELO 3D".
   - Nas PART, troque a isométrica por `iso_prism` vetorial e apague antes os vetores antigos da área (`clean_iso`).
4. **Textos**:
   - descrições na lista de materiais e na legenda;
   - números alinhados à direita (largura do dígito ≈ 38,8 un. no A1 1:15 com h 50,4);
   - peso unitário e total; total do conjunto;
   - REV da folha (00→01→02, por folha);
   - nota vermelha "REV nn - dd/mm/aaaa: o que mudou" em área livre, sem sobrepor OBS, balões ou moldura.
5. **Planilhas xlsx**: atualize descrição e peso (células alteradas em vermelho), título "- REV nn" e nota no fim. Recalcule o total e confira com a folha.
6. **Renderize e confira**:
   - `render_pdf.py` de todas as folhas;
   - veja a folha inteira em baixa resolução e as áreas alteradas em alta;
   - monte uma folha de contato com todas as pranchas.
7. **Entregue** com SendUserFile:
   - PDF consolidado (`DETALHAMENTO_REVnn.pdf`, display render);
   - zip dos DXF com `img/`;
   - xlsx atualizados.
   - Atualize o documento do projeto no Project (`claude/projeto-<nome>.md`) com uma seção "REV nn": pedido, compatibilização, pesos, folhas e pendências.

## 6. Armadilhas já encontradas

- **Texto branco no PDF**: use `Configuration(background_policy=BackgroundPolicy.WHITE, color_policy=ColorPolicy.COLOR)` e `draw_layout(..., filter_func=...)`. Não use `draw_entities`, que perde a cor.
- **Setas de cota** são polígonos cuja base fica ~28 un. antes da ponta: a janela do stretch precisa incluir a base.
- **Não importe** scripts de revisão que têm código no nível do módulo: isso reaplica as alterações. Funções utilitárias ficam só em `dxfops.py`.
- **Faça backup** da pasta `dxf/` antes de cada revisão (`cp -r dxf dxf_backup_revNN`).
- Imagens do SolidWorks vêm em centenas de tiles com SMask. Agrupe por proximidade e componha com alpha (feito no `add_rasters.py`).
- Caminhos de IMAGE no DXF são relativos à pasta do DXF (`img/...`).
- Chapas espelhadas (dianteira/traseira) que usam a mesma PART herdam dobradiças e outros acessórios modelados nela.
- Não descarte dados "estranhos" do PDF sem verificar. Exemplo: a chapa frontal de 400 sobre um pilar de 300 + 2×25,4 era uma inconsistência real.

## 7. Resposta ao usuário

- Comece pelo que foi feito e onde está (arquivos enviados).
- Liste as correções com números.
- Mostre as contas de compatibilização (vão, envelope, aperto, comprimento de barra, pesos e total).
- Diga quais folhas mudaram de REV.
- Liste as limitações: isométricas representativas, DXF de PDF versus exportação nativa.
- Termine com **2–3 pontos para confirmar** com o cliente ou o calculista. Exemplos: peça não incluída no pedido, verificação estrutural de chapa reduzida, folga para macacos.
- Não diga que fez cálculo estrutural. Chame de estimativa e informe as hipóteses.