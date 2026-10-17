# Histórico de alterações

Mudanças relevantes do nd_estruturas. Formato Keep a Changelog, versões semânticas.

## [Não lançado]

- Letsara rev06 (DEC-024, DEC-025): modelo integrado r05 com toda a estrutura e o vento da NBR 6123 (`nd_estruturas.vento_nbr6123`, `modelo_integrado_r05.py`, validação), estudo de 14 arranjos de X; X nos vãos 4-5 a 8-9, 15 espaços de terça com calha no eixo A (`calc_calha.py`, COB03 nova), ST-1V-R no eixo 9, grampos nas ES-1, pilares dos portões PG-01 a PG-04 ligados à TS-01; `calc_cobertura_metalica.py` lendo o modelo integrado; COB01/02, TS-01, VB01, PL-07/08, fechamento, BIM (X, calha, descidas), memória MC06 rev06, listas e PDFs rev06.

- Letsara rev05 (DEC-023): terças Z 302×90/82×2,30 METSEC contínuas por transpasse (METLAP), sem mão-francesa — `calc_cobertura_metalica.py` com MEF de viga contínua, transpasse 450 + 450, apoio 4 M12 e emendas 2 M12; COB01/COB02 refeitas (planta com peças e transpasses, apoio na TS-01 e na VB, emenda, seção e furação do Z); ES-3/CMF-1/MF-1 retirados das TS-01 e VB; BIM com o polígono real do Z, transpasses, ST-1V e 2176 parafusos; memória ND-LET-MC06; entregas rev05.
- `nd_estruturas.viga_continua`: viga contínua por MEF com EI variável (testes com fórmulas clássicas); `PerfilZ` com abas desiguais.

- `metalica_fria.PerfilZ`: Z enrijecido ponto-simétrico (bordas a 45°), FLT 0,5·Cb·r0·√(Ney·Nez) e compressão nos eixos principais; teste com a área do catálogo Isoeste (Z272 × 2,30). Estudo das terças sem mão-francesa em andamento.
- Letsara: `estudo_tercas_sem_mf.py` — escolha automática do perfil mais leve (Ue e Z45 Isoeste, biapoiada × contínua, 2 × 3 linhas de correntes) com apoio por 2 M12 na alma; Ue 300×85×25×2,65 atual passa sem MF (apoio 0,41); com aço CIVIL 300 (fy 300) uma escora do vão 1-2 dá 1,06 → #3,00 nessa linha. Incluídos Z (abas desiguais, `PerfilZ(bf_inf, D_inf)`) e C da Metsec/voestalpine Meincol (fy 400): melhor biapoiada C 342×88×18×2,30 (26,0 t, sucção 0,92; 5 escoras do oitão/beiral do vão 1-2/2-3 em #2,70).
- Letsara (DEC-022): apoios horizontais das vigas inclinadas — cunhas nas pontas da TS-01, pinos simétricos, recuos e topo da I130/pilares centrais horizontais (2 níveis), VB com dentes nivelados e pontas a prumo, CP-VB por face, VB-05 a VB-08 espelhadas; BIM com `PerfilPoligono`/`extrusao_y`.
- Letsara: `calc_vb_dente.py` — VB das fachadas 1 e 9 com dente Gerber e consolo escondido, varredura b 15/20 × h 90 a 40 (5 em 5 cm): passa até h 50; mais econômica 15 × 55; adotada 15 × 60 pelo Nathan (DEC-021): VB01, AR-VIG-04, CP-VB nos pilares de fachada (15 × 27 × 29, PN-6 roscado), MC05, BIM, listas e PDF único.
- Letsara rev04 (NBR 9062:2017, DEC-020): `modelo_global_r04.py` (sem VT, Anexo A, desaprumo, γz da 5.1.2.12, Tab. 7, variante com placas), `calc_nbr9062.py` (aparelhos 7.2.1.6, consolos 7.3, apoio sem recorte 7.5, cintamento 6.2.3, cálices 7.7, estabilidade lateral 6.1 com Lebelle, folgas, flechas, incêndio) e memória MC05; VM em meio vaso com dente (`calc_vm_meio_vaso.py`, `calc_vm_dente.py`, `mef_vm_dente.py`); pilares 14 Ø20; pranchas VM01 (nova), AR-VIG-03, LA01, MON02, PP/CM01 (junta 20 mm, sem VT), pilares, I130, VB01, TS01-1; listas em PDF único (tubos em barras de 6 m) e 3D com meio vaso, 2º estágio, alças e folgas.
- `pilar_metodo_geral`: parâmetro `camadas` (arranjo real das barras); `mef_dente`: largura da mesa inferior `bi` (seções T / meio vaso).

- Letsara rev03: TS-01 sem dentes (apoio no recuo dos pilares e no topo da I130, 8 cordoalhas com 2 isoladas), cobertura rebaixada para o pacote TP40 + lã 40 + zipada + painéis solares (folga 151 mm à platibanda), terças Ue 300×2,65 c/1,20 m, I110 → I130, placas de fechamento 10 cm com 8 Ø12,7, VT do eixo A a +6,25 e todas as ligações metálicas parafusadas (esperas de barra roscada, trilhos e buchas, sem solda); pranchas TS01-1/2/3, I130, COB01/02, CT01, LOC01, MON01, PP00/PP-x, VT01, VB01, pilares e armaduras regeneradas.
- `mef_dente.analisar`: opções `rampa_fim` (transferência gradual da protensão no corte artificial do modelo) e `robusto` (Newton modificado / line search quando a carga para de convergir); padrão inalterado.

- Adiciona `bases_aco.py` (Manual Gerdau caps. 9–11, kN/cm): seleção EP1/EP2 (detalhe soldado do manual, com aviso da regra ND) e `EmendaPilarParafusada` por talas; base rotulada PBR (concreto 10.4, placa AISC DG1 m/n/λn', solda de filete, limite das tabelas em `dados/pbr_gerdau.csv`); base engastada PBE (bloco de tensões DG1, placa comprimida/tracionada, chumbadores, pilar 5.5.1.2, `Md_max`); 114 testes, desvio ≤ 2 % (PBE com chumbadores tracionados até 2,7 %, DEC-017).

- Adiciona `metalica_laminada.py` (perfis W/HP Gerdau, NBR 8800:2024): catálogo `dados/perfis_w_gerdau.csv` (110 perfis), MRd (FLT com Cb, FLM, FLA), MRd em y, VRd com/sem enrijecedor, NcRd (χ, área efetiva da 2024 e método Q de 2008), NtRd, interação N+M, flecha biapoiada e `tvpa` (Tabela de Vãos e Cargas); validado contra bitolas, TVPA, TCPA e manual de galpões (57 testes).
- Adiciona `ligacoes_aco.py`: parafusos A325 (tração, corte 0,45 Ab fub na rosca, contato/rasgamento, interação, deslizamento crítico), elementos de ligação (tração, cisalhamento, bloco de cisalhamento), disposições construtivas, dupla cantoneira parafusada LCPP e emenda por talas; validado nas tabelas 1–4 e na LCPP do Manual Gerdau (22 testes).
- Estende `ligacoes_aco.py` com o Manual Gerdau caps. 3–8: LCPP com 1 ou 2 recortes (cisalhamento, bloco da alma, flexão e flambagem local da alma recortada), LCHE (todas as verificações, flexão da chapa, Nd por Drucker, solda, rotação), LCHS/shear tab (coeficiente c, casos 1 e 2), LMPA (alavanca, flexão da chapa, tração+corte, FLM, casos 1 e 2, disposições), LT/LMTS (alavanca nos T, parafusos, alma, bloco) e verificação do pilar suporte (mesa, alma, painel, enrijecedor); 58 testes novos contra exemplos e tabelas (desvio ≤ 2%, 1 xfail documentado na LMPA caso 1 com 3/4").

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
