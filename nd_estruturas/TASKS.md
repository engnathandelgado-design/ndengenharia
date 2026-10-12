# TASKS — nd_estruturas

Quadro vivo de tarefas. O Claude atualiza a cada sessão. O que não está escrito aqui, considere esquecido.

## Agora

- [ ] Alinhar as skills `projetos-estruturais-concreto-armado-protendido` e `mef-opensees-opsvis` com a Parte D (especificação viva).
- [ ] Criar o registro de normas por chave com ano (`"NBR6118:2023"`) e os objetos de valor (Concreto, Aco, Secao).

## Próximas

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

- [ ] Camada web (FastAPI): aguarda decisão da interface final.

## Feito

- [x] 2026-10-12 — Módulo `formfinding` (JAX FDM → OpenSeesPy): casca apoiada nos cantos, arco funicular 2D, estabilidade não linear; 7 testes (2 conferidos à mão). Caso do barracão Vitalle em `exemplos/`.
- [x] 2026-10-11 — Estrutura de documentos do projeto criada.
- [x] 2026-10 — Referências estudadas: Hanai 2005, Inforsato 2009, Real 2000, Gonçalves 2017, Oliveira/Barros/Giongo 2014, Andrade 1989, apostila TM266 (MEF).
- [x] 2026-10 — Conferência do HyperFrame e do plugin python-clean-architecture.
