# TASKS — nd_estruturas

Quadro vivo de tarefas. O Claude atualiza a cada sessão. O que não está escrito aqui, considere esquecido.

## Agora

- [ ] Módulo `prefabricados` (DEC-008): peça, armadura, inserto; volume/peso/CG; marcas por identidade; lista de peças e aço por bitola; pytest com conferência manual.
- [ ] Prancha de peça automática (fôrma + armação + quadro da peça + dobramento) e planta de montagem, usando `prancha_nd.py`.
- [ ] Teste real com a obra Letsara (precisa do PDF arquitetônico R01).
- [ ] Alinhar as skills `projetos-estruturais-concreto-armado-protendido` e `mef-opensees-opsvis` com a Parte D (especificação viva).
- [ ] Criar o registro de normas por chave com ano (`"NBR6118:2023"`) e os objetos de valor (Concreto, Aco, Secao).

## Próximas

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

- [x] 2026-10-12 — GitHub como fonte única (DEC-007): `pyproject.toml`, páginas Streamlit (arco funicular, casca nos cantos), atalhos .bat para Windows, pasta `skills/`.
- [x] 2026-10-12 — Módulo `formfinding` (JAX FDM → OpenSeesPy): casca apoiada nos cantos, arco funicular 2D, estabilidade não linear; 7 testes (2 conferidos à mão). Caso do barracão Vitalle em `exemplos/`.
- [x] 2026-10-11 — Estrutura de documentos do projeto criada.
- [x] 2026-10 — Referências estudadas: Hanai 2005, Inforsato 2009, Real 2000, Gonçalves 2017, Oliveira/Barros/Giongo 2014, Andrade 1989, apostila TM266 (MEF).
- [x] 2026-10 — Conferência do HyperFrame e do plugin python-clean-architecture.
