# TASKS — nd_estruturas

Quadro vivo de tarefas. O Claude atualiza a cada sessão. O que não está escrito aqui, considere esquecido.

## Agora

- [ ] Aplicar docs/referencias_pranchas.md ao prancha_nd: escala gráfica por vista, bolhas de corte/detalhe no padrão, lista de materiais com peso em toda prancha metálica, tabela de ferros por unidade e por N unidades, resumo por bitola.
- [ ] Módulo `prefabricados` (DEC-008) — falta: objeto peça/armadura/inserto, volume/peso/CG, marcas por identidade, listas. Coeficientes ainda soltos no código: migrar para o registro de normas.
- [ ] Prancha de peça automática (fôrma + armação + quadro da peça + dobramento) e planta de montagem, usando `prancha_nd.py`.
- [ ] Teste real com a obra Letsara (precisa do PDF arquitetônico R01).
- [ ] Alinhar as skills `projetos-estruturais-concreto-armado-protendido` e `mef-opensees-opsvis` com a Parte D (especificação viva).
- [ ] Criar o registro de normas por chave com ano (`"NBR6118:2023"`) e os objetos de valor (Concreto, Aco, Secao).

## Próximas

- [ ] Letsara: zip ND-LET-EXECUTIVO-rev09 com DXF e IFC depois da aprovação do Nathan dos PDF do pacote rev09.
- [ ] Letsara rev09 (24/10, AGUARDA DECISÃO — quadro decisao_portao_l4.png: PG viram apoio / subir a linha 4 / portão 7,40): portões da linha 4 (500 × 750, vãos B–P21 e P19–D): fundo da TS-01A/V409/V410 em +7,50 no vão de cada portão (nada abaixo de 7,50); placas protendidas novas entre o topo do portão e a viga onde a viga sobe; conferir colisões com P19, P20, P21 e a V401; atualizar TS-01A, pilares da linha 4, placas da linha 4, lista, quantitativos e 3D.

- [ ] Letsara (DEC-027): confirmar com a Kingspan arrancamento dos parafusos em #0,65, distribuição de clipes e junta de dilatação na água de 39,6 m.

- [ ] Letsara rev06 (DEC-026): trocar as medidas de pré-dimensionamento do CS-1, NC-1 e cartola PT-1 pelas do catálogo 09 da Trejor (anexar o PDF e o DWG "Consoles 2a ETAPA" do e-mail de 05/02/2021) e recalcular `calc_fixacao_placas.py`; luvas TSA dos PT-1 da 1ª fiada no topo da viga baldrame (projeto de fundações); nas placas ao lado da porta da vista I, alinhar as TSA das peças de baixo com os pinos da peça de cima; CE-1 dos pilares do anexo (H/J/I) contadas em Z_PL[:6] (rever as fiadas reais com esquadria).
- [ ] Letsara rev06: confirmar a intensidade de chuva da cidade (NBR 10844 tab. 5; adotado 200 mm/h) e a rede de drenagem das 9 descidas Ø200; desenhar os insertos IL-1 nas vistas dos pilares PG e a CL-P em detalhe próprio; conferir com a fábrica os insertos IT-P no fundo da TS-01A entre as cordoalhas; rodar os pilares da família 40×60 com os esforços do modelo integrado (uso 0,66).

- [ ] Letsara: confirmar com o fornecedor o peso dos painéis solares (0,15 kN/m²) e a capacidade do trilho TR-1 / bucha BR-1 (≥ 12,4 kN por ponto); confirmar com a fábrica a cabeceira de 1105 kN da placa e a furação nova da grade da TS-01.
- [ ] Letsara rev04: fábrica comprovar controle de pré-fabricado (12.1.2) para o cobrimento de 2 cm das placas; TRRF do Corpo de Bombeiros; colarinho dos cálices no projeto de fundações.
- [ ] Letsara: planilha de custo dos pilares com as quantidades da rev03 e o preço do C50.

- Letsara: definir com o cliente o limite de deslocamento do ELS (9,3 mm passa H/500, não passa H/1700); função dos pilares P6/P7 do anexo; escolha da opção de pilar (A armado × B protendido).
- Letsara: atualizar `checar_conexoes.py` seções 4/5 para a geometria do R01 (ainda com 20,05/39,625 e PC 50×50).

- Letsara: resolver cobertura acima da platibanda no lado alto (consolo +9,28 + I90 + terça = +10,47 > +10,00) e completar o modelo BIM (P9, P10, P12, P6/P7, V201, contraventamento) quando o projeto fechar.
- `bim`: gerar o ModeloBIM direto das peças do `prefabricados` (DEC-008) quando o objeto peça existir; incluir dente Gerber, chanfros e insertos na geometria.
- Letsara: pranchas I110 (berços inclinados), I90 mezanino, pilares (consolos a 3%, cálice), lajes alveolares e vigas de apoio, placas e VB; registro de chaparia de todas as peças.

- [ ] Publicar o app no Streamlit Community Cloud (repositório privado, acesso só por convite).
- [ ] Tirar a cópia de código da pasta nd_estruturas do Drive (deixar só entradas e saídas).
- [ ] Definir o Protocol do motor de análise e implementar o stub de teste.
- [ ] Portar o módulo `secoes` (flexão simples, ELU) com 3 testes conferidos à mão.
- [ ] Escrever `nd_api.py` para chamar a planilha de consolos e dentes Gerber.

## Depois
- Letsara (pedido do Nathan, trabalho separado depois da rev09): DUAS VERSÕES do fechamento — versão 1 com as placas de 125 adaptadas ao arquitetônico (janelas, portas e guichê compatibilizados); versão 2 seguindo exatamente a locação de placas da Marques no R01 (com os recortes de portas dela).
- Letsara (DEC-042, colisão): plano das placas das fachadas 1/9 × face lateral dos cantos (10 cm); CE-1 das paredes internas das linhas 2 e 4 à frente da face dos pilares (15–25 cm); zipada entrando 15 cm na cabeça dos PF; X Ø16 tocando a cabeça dos PF da linha 9; reações da terça de ponta para fechar o ST-1FL — decidir com o Nathan.
- Letsara: VB mantida com uma ponta solta (DEC-033); se mudar de ideia, ligação presa nas 2 pontas para ±69 kN ou reforço da terça e das esperas ST-1P.
- Letsara: pranchas de pilar e viga em A1 conforme o tamanho do desenho (pedido do Nathan: ajustar a prancha ao desenho).

- Bases Gerdau pendências (DEC-017): identificar o modo de falha das PBR com placa pouco maior que o perfil (85 de 273 linhas; hoje coberto pelo limite tabelado); PBE com chumbadores tracionados a até 2,7 %; extrair as geometrias de todas as tabelas PBE (hoje 4 de 107); barra de cisalhamento (o manual não traz); conferir no texto da NBR 8800:2024 os itens 6.6.5, 6.7.1.5 e 6.7.2 (base "tipo 2").
- Ligação de viga metálica em consolo de pilar de concreto pré-moldado (manual 12.2.2/12.2.3: σc = fck/1,96·√(A2/A1), placa com m = t²/5·fy/γa1, chumbador com Ftd ≥ 20 kN, torção na montagem): implementar para os insertos/consolos da ND.
- Ligações Gerdau pendências: LMPA caso 1 com 3/4" (pág. 125, +4,6%, hipótese do manual não encontrada); LCHS págs. 93 e 99 (tabela acima do contato na chapa); Nd das LCPP (Drucker, raio R da cantoneira); conferir na NBR 8800:2024 as fórmulas do pilar suporte (hoje 2008/AISC J10).

- [ ] Passar o `formfinding` pelo Protocol do motor de análise (hoje chama o OpenSeesPy direto) e tirar Ecs/fctk do registro de normas.
- [ ] Vento NBR 6123:2023 no pórtico do barracão Vitalle (opção 2): confirmar Cpi com portão aberto e V0 do local.
- [ ] Vento NBR 6123:2023 e desaprumo automáticos.
- [ ] Gerador de combinações ELU e ELS.
- [ ] γz automático no módulo `porticos`.
- [ ] Armação executiva de vigas com quadro de ferros.
- [ ] Copiloto que edita o modelo com aprovação do engenheiro.

## Travadas

- [ ] Camada web FastAPI: só se o Streamlit (DEC-007) não atender.

## Feito
- Letsara rev09 (24/10): DEC-052 (W 200 × 15,0 + montantes, COB05), DEC-053 (escada externa ES02, OM-2, BE-1), DEC-054 (I130 h 120, Ø15,2, protensão limitada, fckj 50, dente MEF FS 1,19, CP-I130 com mísula; V407 h 120), DEC-055 (piso pronto +3,95, espelhos 17,95), DEC-056/057; NG01, 3D/IFC (0 colisões), quantitativos, MC09, pranchas unidas rev09 (72 folhas, 0 erros/0 avisos).

- [x] 2026-10-24 — Letsara DEC-050 (linha 2 sem montantes, W 310 direto na cabeça dos pilares, PM-02 novo) e DEC-051 (escada sem solda, base metálica BM-1); isométrico do mezanino na NG01 com o vão da escada; posição da escada conferida (escada externa da fachada A em aberto). PDF para análise; zip só após aprovação.
- [x] 2026-10-23 — Letsara rev09 (DEC-045 a DEC-049): níveis +3,90/+7,30, escada metálica, P6/P7 e P6 da linha 2, VM 30 × 75 com dente 45, linha 2 em W 310, laje de cima sem uso; pranchas em PDF para análise do Nathan (zip com DXF/IFC só após aprovação).
- 22/10 Letsara colisões: checagem do modelo inteiro (colisao_modelo.py, OBB + sólidos exatos); CE-1/CS-1 das paredes internas e parede C no lado certo; recortes da cobertura nas cabeças dos PF + RF-4P; lajes com recorte nos pilares; RF-1 com pingadeira interna a prumo; piso até as placas; ST-1FL com as reações reais da terça de ponta (verif_st1fl.py). Resolvido em DEC-044 (22/10): recorte nas placas + CE-1L e calços CS-1C/CS-1D (ND-LET-PP06). Pendente decisão: P8/P8B (PM-01) terminam em +6,55 e a CE-1 da fiada +6,25 fica acima do topo — subir o PM-01 a +7,45/+7,50?
- [x] 2026-10-22 — Letsara DEC-042: cabeça dos pilares (cantos de seção cheia + ST-1FL, armadura da cabeça para o vento da platibanda, CE-1 em ponta de parede, planta-chave com nomes).

- [x] 2026-10-21 — Letsara DEC-039: CT-1 removida; ponta da VM concretada antes das lajes trava o giro de montagem (junta verificada ao cisalhamento; fcj ≥ 20 MPa); pranchas e 3D regerados (substitui a DEC-038).
- [x] 2026-10-21 — Letsara: 3D revisado como executado (I130 com dente/NEO-2/PN-2, ST-1P4, correntes/tirantes/diagonais, CC-1) e republicado.

- [x] Letsara rev06f (DEC-032): revisão de protensão (ato, ELS, ELU, perdas), dentes Gerber (biela, tirante, suspensão, MEF), ganchos/ancoragens, CC-1 nos pilares e padrão gráfico da usina.
- [x] Letsara rev06e (DEC-031): consoles concretados na face C (CC-1), tolerância ±12, geometria e MEF refeitos, posição na fôrma nas pranchas dos pilares.
- [x] Letsara rev06d (DEC-030): espessura de cada chapa e de cada solda da fixação pelo MEF (NC-1, CS-1, CE-1), aplicada em todas as pranchas, listas, IFC e páginas.
- [x] Letsara rev06d (DEC-028): ombreiras OM-1 em U na porta da vista I, PP05, placa I-15 com 12 cordoalhas (PP-05P), IFC e quantitativos.
- [x] Letsara rev06c: contagem NC-1 = IFC (404) e quantitativo do pacote Kingspan (telhas, cartolas, lã, clipes, parafusos) na COB04, planilha e LISTAS.
- [x] Letsara rev06c (DEC-027): cobertura Kingspan zipada dupla com lã de rocha — cargas, fixações à sucção, acabamentos (COB04) e IFC com camadas, cartolas e rufos.
- [x] Letsara rev06c: fixação compatibilizada (parede 3, 2 abas, 2 dentes, M16 com porca soldada, prisioneiro, grampos Ø6,3) e pranchas de fabricação PP02–PP04 com isométricos explodidos, soldas, roscas e listas; PP01 com conjunto, tolerâncias e sequência.
- [x] Letsara rev06b: projeto executivo da fixação das placas — ND-LET-PP01 (armação da ponta, NC-1 caixa, CS-1, CE-1 + N18, PT-1, PT-2), PP00, pilares, MC07, quantitativos, IFC e PDF único.
- [x] Letsara rev06 (DEC-026): fixação das placas pelo sistema Trejor — estudo IFC dos 4 sistemas, cálculo (MEF de casca, dente Gerber, console NBR 8800, CE-1, PT-1, PT-2), memória MC07, PP00/PP-x/CM01, pilares com CE-1, listas e IFC.

- [x] Letsara rev06 (17/10/2026): modelo integrado r05 + otimização do X (DEC-024), 15 espaços de terça e calha do eixo A (DEC-025), COB03, PG-01 a PG-04, ST-1V-R, memória MC06 rev06, entregas rev06.
- Letsara rev05: terças Z METSEC contínuas por transpasse, sem mão-francesa (DEC-023); estudo de terças (Ue, Z, C — Isoeste e METSEC).
- Letsara: apoios horizontais e encaixes das vigas inclinadas (DEC-022).
- Letsara: VB 15 × 60 com dente Gerber e CP-VB escondido (DEC-021).

- [x] 2026-10-16 — Letsara rev04 (DEC-020): reanálise pela NBR 9062:2017 — sem VT, Tab. 7, pilares 14 Ø20, VM meio vaso com dente (MEF), consolos/neoprenes/folgas revistos, memória MC05, pranchas e listas em PDF único, 3D.

- [x] 2026-10-14 — Letsara rev03 (DEC-019): TS-01 sem dente, cobertura rebaixada com painéis solares, terças c/1,20 m, I130, placas 10 cm, ligações sem solda; cálculos (ligacoes, modelo global, cobertura, I130, dentes, consolos, placas) e pranchas regenerados.

- [x] 2026-10-13 — `bases_aco`: emendas EP1/EP2 (seleção, com aviso de solda) e emenda parafusada por talas, bases rotuladas PBR e engastadas PBE pelo Manual Gerdau (caps. 9–11), 114 testes contra exemplos e tabelas; dados PBR em `dados/pbr_gerdau.csv` (273 linhas).

- [x] 2026-10-13 — `ligacoes_aco`: LCHE, LCHS, LMPA, LT/LMTS e recortes da LCPP pelo Manual Gerdau (caps. 3–8), 58 testes novos contra exemplos e tabelas.

- [x] 2026-10-13 — `metalica_laminada`: perfis W/HP Gerdau pela NBR 8800:2024 (MRd, VRd, NcRd, NtRd, interação, flecha, TVPA), 57 testes contra a Tabela de Vãos e Cargas e o manual de galpões. Falta: conferir numeração de itens da 2024 no texto da norma; `package-data` do CSV no pyproject para instalação não editável.

- Letsara 12/10/2026: consolos sem chanfro alinhados ao fundo das vigas, I110/laje reverificadas no R01, pórtico 3D ELU/ELS com diafragma e terças de oitão, 32 pranchas sem sobreposição, quantitativos xlsx e DXF 3D.

- Letsara: cobertura no padrão das referências (X Ø16 de nó a nó com esticador, correntes com tirantes rígidos e diagonais de ancoragem, MF na alma), COB01/COB02 rev 02; LOC01, MON01 e CT01 refeitas com a geometria do R01 e a proposta de recuo da cabeça dos pilares; TS-01 com 19,15 m.

- [x] Letsara MC04 — 2º estágio das VM: duas fases, interface NBR 9062:2017 6.3.5, N9 salientes Ø8 c/15 + N10 + negativas; VM01 corte C-C, MON02 e conferência (calc_segundo_estagio.py).

- Pranchas de montagem MON01/MON02 do Letsara.
- Prancha de pilar PL-01 (opções armado/protendido) com faces, isométricos, planta-chave, cotas em cm e armadura conforme NBR 6118.

- Módulo `bim`: modelo de peças -> IFC4 + página 3D para celular; Letsara em `exemplos/letsara/modelo_bim.py`; skill `modelo-ifc-3d-nd` (2026-10-12).
- Letsara: cobertura metálica calculada (MRD), ligações e chumbadores, dentes Gerber com MEF, TS-01 rev. 01, COB-01.

- Letsara TS-01 detalhada (3 folhas) + checagem de ligações no modelo.

- [x] 2026-10-12 — `prefabricados`: seção poligonal (I, retangular), viga pré-tracionada (ato, ELS-F/D, ELU, cortante, flecha, cordoalhas superiores, isolamento), torção NBR 6118 17.5, pilar em balanço pelo método geral (OpenSeesPy, fibras, corrotacional, fluência, critério εcu/10‰); 6 testes conferidos à mão. Rodada 1 da Letsara em `exemplos/letsara/`.
- [x] 2026-10-12 — GitHub como fonte única (DEC-007): `pyproject.toml`, páginas Streamlit (arco funicular, casca nos cantos), atalhos .bat para Windows, pasta `skills/`.
- [x] 2026-10-12 — Módulo `formfinding` (JAX FDM → OpenSeesPy): casca apoiada nos cantos, arco funicular 2D, estabilidade não linear; 7 testes (2 conferidos à mão). Caso do barracão Vitalle em `exemplos/`.
- [x] 2026-10-11 — Estrutura de documentos do projeto criada.
- [x] 2026-10 — Referências estudadas: Hanai 2005, Inforsato 2009, Real 2000, Gonçalves 2017, Oliveira/Barros/Giongo 2014, Andrade 1989, apostila TM266 (MEF).
- [x] 2026-10 — Conferência do HyperFrame e do plugin python-clean-architecture.
