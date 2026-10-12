# TASKS — nd_estruturas

Quadro vivo de tarefas. O Claude atualiza a cada sessão. O que não está escrito aqui, considere esquecido.

## Agora

- [ ] Módulo `prefabricados` (DEC-008) — falta: objeto peça/armadura/inserto, volume/peso/CG, marcas por identidade, listas. Coeficientes ainda soltos no código: migrar para o registro de normas.
- [ ] Prancha de peça automática (fôrma + armação + quadro da peça + dobramento) e planta de montagem, usando `prancha_nd.py`.
- [ ] Teste real com a obra Letsara (precisa do PDF arquitetônico R01).
- [ ] Alinhar as skills `projetos-estruturais-concreto-armado-protendido` e `mef-opensees-opsvis` com a Parte D (especificação viva).
- [ ] Criar o registro de normas por chave com ano (`"NBR6118:2023"`) e os objetos de valor (Concreto, Aco, Secao).

## Próximas

- Letsara: resolver cobertura acima da platibanda no lado alto (consolo +9,28 + I90 + terça = +10,47 > +10,00) e completar o modelo BIM (P9, P10, P12, P6/P7, V201, contraventamento) quando o projeto fechar.
- `bim`: gerar o ModeloBIM direto das peças do `prefabricados` (DEC-008) quando o objeto peça existir; incluir dente Gerber, chanfros e insertos na geometria.
- Letsara: pranchas I110 (berços inclinados), I90 mezanino, pilares (consolos a 3%, cálice), lajes alveolares e vigas de apoio, placas e VB; registro de chaparia de todas as peças.

- [ ] Publicar o app no Streamlit Community Cloud (repositório privado, acesso só por convite).
- [ ] Tirar a cópia de código da pasta nd_estruturas do Drive (deixar só entradas e saídas).
- [ ] Definir o Protocol do motor de análise e implementar o stub de teste.
- [ ] Portar o módulo `secoes` (flexão simples, ELU) com 3 testes conferidos à mão.
- [ ] Escrever `nd_api.py` para chamar a planilha de consolos e dentes Gerber.

## Depois

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

- Módulo `bim`: modelo de peças -> IFC4 + página 3D para celular; Letsara em `exemplos/letsara/modelo_bim.py`; skill `modelo-ifc-3d-nd` (2026-10-12).
- Letsara: cobertura metálica calculada (MRD), ligações e chumbadores, dentes Gerber com MEF, TS-01 rev. 01, COB-01.

- Letsara TS-01 detalhada (3 folhas) + checagem de ligações no modelo.

- [x] 2026-10-12 — `prefabricados`: seção poligonal (I, retangular), viga pré-tracionada (ato, ELS-F/D, ELU, cortante, flecha, cordoalhas superiores, isolamento), torção NBR 6118 17.5, pilar em balanço pelo método geral (OpenSeesPy, fibras, corrotacional, fluência, critério εcu/10‰); 6 testes conferidos à mão. Rodada 1 da Letsara em `exemplos/letsara/`.
- [x] 2026-10-12 — GitHub como fonte única (DEC-007): `pyproject.toml`, páginas Streamlit (arco funicular, casca nos cantos), atalhos .bat para Windows, pasta `skills/`.
- [x] 2026-10-12 — Módulo `formfinding` (JAX FDM → OpenSeesPy): casca apoiada nos cantos, arco funicular 2D, estabilidade não linear; 7 testes (2 conferidos à mão). Caso do barracão Vitalle em `exemplos/`.
- [x] 2026-10-11 — Estrutura de documentos do projeto criada.
- [x] 2026-10 — Referências estudadas: Hanai 2005, Inforsato 2009, Real 2000, Gonçalves 2017, Oliveira/Barros/Giongo 2014, Andrade 1989, apostila TM266 (MEF).
- [x] 2026-10 — Conferência do HyperFrame e do plugin python-clean-architecture.
