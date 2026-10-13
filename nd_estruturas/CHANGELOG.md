# Histórico de alterações

Mudanças relevantes do nd_estruturas. Formato Keep a Changelog, versões semânticas.

## [Não lançado]

- Adiciona `metalica_laminada.py` (perfis W/HP Gerdau, NBR 8800:2024): catálogo `dados/perfis_w_gerdau.csv` (110 perfis), MRd (FLT com Cb, FLM, FLA), MRd em y, VRd com/sem enrijecedor, NcRd (χ, área efetiva da 2024 e método Q de 2008), NtRd, interação N+M, flecha biapoiada e `tvpa` (Tabela de Vãos e Cargas); validado contra bitolas, TVPA, TCPA e manual de galpões (57 testes).
- Adiciona `ligacoes_aco.py`: parafusos A325 (tração, corte 0,45 Ab fub na rosca, contato/rasgamento, interação, deslizamento crítico), elementos de ligação (tração, cisalhamento, bloco de cisalhamento), disposições construtivas, dupla cantoneira parafusada LCPP e emenda por talas; validado nas tabelas 1–4 e na LCPP do Manual Gerdau (22 testes).

### Adicionado

- Letsara (13/10/2026): prancha própria para cada marca da família 40×60 (PL-02 a PL-12, PF-01 a PF-06) com cabeça recuada, consolos e insertos da marca (`pilares_familia.py`, `familia_pl.py`); `pilar_generico` com cabeça recuada (vistas, corte C-C, N1A/N13/N14, isométrico); quantitativos por marca; PDF em 3 volumes.

- Letsara (12/10/2026): consolos sem chanfro com h = altura da viga − dente − neoprene (fundos alinhados), verificados pela NBR 9062:2017 7.3 em `calc_consolos.py` (nenhum precisou de mísula); I110 reverificada com os vãos do R01 (`calc_i110_r01.py`, 4 Ø20 na mesa); laje h20 com 8 Ø12,7; pórtico global `modelo_global_r01.py` (OpenSeesPy, P-Δ, X só de tração, diafragma rígido do mezanino, todas as terças inclusive nos vãos de oitão sobre a VB) e página `letsara_portico.html` com deformadas ELU/ELS e tabela 3D × pórtico; todas as 32 pranchas regeradas sem textos sobrepostos (aviso com posição no `prancha_nd`), relação do aço da VT, aço passivo das placas, `quantitativos.py` (xlsx a partir das tabelas das pranchas, exportadas em `*.tabelas.json`) e `dxf3d.py` (modelo 3D em DXF).

- Letsara: `geometria.py` aplicado à cobertura (ligacoes, calc_cobertura_metalica, checar_conexoes 81 itens), COB01/COB02 rev 02 com o travamento das coberturas de referência, LOC01/MON01/CT01 com geometria do R01 e recuo da cabeça dos pilares (a validar), 3D atualizado.

- prancha_nd: `MEMORIA_NA_PRANCHA = False` — tabelas de memória/verificações não entram nas pranchas de detalhamento para o cliente (ficam nas memórias MC); todas as pranchas Letsara regeradas.
- Letsara MC04: `calc_segundo_estagio.py` (análise em duas fases da VM I90 + laje alveolar + capa, interface NBR 9062:2017 6.3.5, armadura de 2º estágio); VM01 com corte C-C da solidarização (N9 salientes Ø8 c/15, N10, enchimento + capa, tela, negativas) e sequência de obra; MON02 e `checar_conexoes` (77 itens).
- Letsara: contraventamento da cobertura em X por subpainel 3158 × L/4 (diagonais Ø12,5 de ≈ 4 m, esticador) com nós CH-X nas terças e correntes rígidas como corda intermediária; cálculo em `calc_cobertura_metalica` (cortante do modelo global dividida pelas 4 subdiagonais) e 75 verificações em `checar_conexoes`.
- Letsara: ND-LET-COB01 rev. 01 refeita no padrão das pranchas de cobertura de referência — planta de enterçamento de todo o pavilhão (1:175, marcas T-1..T-8, cadeia de espaçamentos, L = vão − 20, folgas de montagem), suporte de terça ST-1 (chapa 8×220×290 soldada na CH-T1/CH-T2, 2 M12 por ponta, furos centrados na alma a 100/200) e mão-francesa na orelha OR-1 (chapa 8×300×100 furada, soldada na CH-MF); ND-LET-COB02 (correntes, diagonais no ST-1, contraventamento, memória). TS01-1/TS01-3 rev. 02 sem luvas nem CT-1; `checar_conexoes` com 71 verificações.
- docs/referencias_pranchas.md: convenções extraídas das pranchas de referência (metálica e pré-moldado) para o padrão de apresentação da ND.
- prancha_nd: camadas de cor da armadura (ARMADURA azul = longitudinal, ARM_TRANSV magenta = transversal, ARM_PROT verde = cordoalhas) e `legenda_armadura`; aplicado em todas as pranchas.
- Letsara: VM volta a ter dentes Gerber (I90, 45×30, MEF FS 1,14); CM01 rev. 01 com a locação de placas do R01 (vistas A–J, portões na linha 3); ND-LET-VT01 (vigas de travamento e vergas 25×60 a +5,50/+6,10 escondidas no fechamento); CP-VT nos pilares PL.
- Letsara: pranchas de todas as peças — I110 (V405/406/407), VM (mezanino, I70 sem dente), VB-01 (15×90), PC-01/02 (50×50), PM-01, LA-01 (lajes) e CM-01 (placas); geradores genéricos `viga_i.py`, `pilar_generico.py`, `iso3d_pilar_gen.py`; galeria do artefato com as 17 páginas.
- bim/visualizador: galeria de pranchas (imagens embutidas, ampliáveis no celular) e tabela de conferência cruzada de conexões na página 3D.
- Letsara: `checar_conexoes.py` (68 verificações inserto × inserto entre peças) e insertos/pinos/consolos CP-VB e CP-MEZ no modelo 3D; pino PN-1 unificado em Ø20 (TB-1 Ø50×3,0) para todas as TS-01.
- Letsara: pranchas de montagem ND-LET-MON01 (cobertura: planta, corte do pórtico, lista de peças, sequência) e ND-LET-MON02 (mezanino +3,15/+6,55: plantas, corte, lista, sequência).
- prancha_nd: `Vista.cota_ord_v` (cotas ordenadas verticais) e `Vista.chapa` (chaparia hachurada ANSI31).
- Letsara: pilar PL-01 desenhado em pé (posição de montagem), rev. 02, com Detalhe 4 de protensão (posição das cordoalhas e força no macaco) na opção B.
- prancha_nd: modo `unidade="cm"` nas vistas (cotas de concreto pré-moldado em cm, chaparia em mm); subtítulo indica a unidade.
- Letsara: prancha de pilar PL-01 (A0, opções A e B) refeita no padrão de desenho de peça: vistas das faces A/B/C, cortes, 3 detalhes, isométricos com insertos, planta-chave de locação com marcas, cabeçalho com marca/seção/comprimento, estribos e grampos conforme NBR 6118:2023 18.4.3, cobrimento 30 mm conferido.

- `pilar_metodo_geral` aceita cordoalhas pré-tracionadas; Letsara: folgas de montagem, apoios sobre consolos e pilares protendidos (DEC-012).
- Módulo `bim`: perfis, peças e modelo com quantitativos; gravação IFC4 (pset ND_Peca), leitura de malha de IFC e visualizador 3D (three.js) com camadas, pendências e marca "projeto da ND Engenharia"; extra `bim` no pyproject (2026-10-12).
- Letsara: `exemplos/letsara/modelo_bim.py` gera o IFC e a página 3D do pavilhão (2026-10-12).
- `metalica_fria.py` (NBR 14762 MRD com faixas finitas, parafusos, barras), `ancoragem.py` (ACI 318-19 cap. 17), `dente_consolo.py` (NBR 9062 + PCI) e `mef_dente.py` (MEF não linear 2D do dente), com testes conferidos à mão.
- Letsara: terças, correntes, CT-1, mão-francesa no fundo da viga, chumbadores; dentes Gerber em todas as vigas com MEF; folhas TS-01 rev. 01 e COB-01; memória MC02.
- Letsara: TS-01 em 3 folhas no padrão de prancha de peça (fôrma/insertos/transitórias A0, armação com croquis A1, chaparia A1) com isométricos 3D; registro de chaparia e checagem de ligações (pinos, terças, berço, tirantes × terças); transitórias com 4 alças e 2 calços; contraventamento em painéis de 3,20 m.
- Motor de pranchas: imagem no PDF, cotas ordenadas e relação do aço com croquis.
- `pyproject.toml`: instalação com `pip install -e .[dev]`; extras `formfinding` e `web` (2026-10-12).
- Páginas web (Streamlit, na raiz do repositório): arco/tesoura funicular e casca apoiada nos cantos, com conferência à mão na tela (2026-10-12).
- Módulo `formfinding`: form-finding inverso com JAX FDM e ponte para cascas/pórticos no OpenSeesPy, com testes (2026-10-12).
- Exemplo `exemplos/portico_barracao_vitalle.py`: opção 2 do barracão 20 × 30 (reta × funicular, gravidade e sucção) (2026-10-12).
- Estrutura de documentos do projeto (2026-10-11).

### Alterado

### Corrigido

<!--
Ao lançar uma versão, copie:

## [X.Y.Z] — AAAA-MM-DD
### Adicionado
### Alterado
### Corrigido
-->
