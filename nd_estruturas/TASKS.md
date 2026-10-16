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

- [ ] Letsara: confirmar com o fornecedor o peso dos painéis solares (0,15 kN/m²) e a capacidade do trilho TR-1 / bucha BR-1 (≥ 12,4 kN por ponto); confirmar com a fábrica a cabeceira de 1105 kN da placa e a furação nova da grade da TS-01.
- [ ] Letsara rev04: fábrica comprovar controle de pré-fabricado (12.1.2) para o cobrimento de 2 cm das placas; TRRF do Corpo de Bombeiros; catálogo TR-2/BR-2 (≥ 40 kN) da CT-1; colarinho dos cálices no projeto de fundações.
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
