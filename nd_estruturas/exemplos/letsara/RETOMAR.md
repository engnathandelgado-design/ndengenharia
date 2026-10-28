# Letsara — ponto de parada (28/10/2026 00:15, parado a pedido do Nathan)

## Estado
- Decisões aplicadas (27/10): pilares de canto 10 cm para fora (DEC-084), VM da linha 1 rente à face externa e lajes do vão 1–2 alongadas (DEC-090), consolo com a largura da viga (DEC-091), P21/P19 com a face no plano dos vizinhos e portões de 5,00 m (DEC-092). Nenhuma decisão pendente do Nathan sobre a rev12.
- Processo novo (DEC-093): gate de lançamento (`verificar_lancamento.py`), `gerar_tudo` incremental (`pranchas/rodar_rastreado.py`, manifestos em /home/claude/letsara/pranchas/manifestos), revisão por diferença (`alteradas.json` × `emissao_revisada.json`).
- Última emissão completa revisada: 27/10 23:20 (86 folhas 0/0, conferência 1295 sem divergência, 3D republicado no link de sempre, versão 47). `emissao_revisada.json` = essa emissão.
- Revisão independente dessa emissão: /home/claude/letsara/entregas/REVISAO_rev12b.md — DEVOLVER, 24 itens (2 impedem fabricar, 2 impedem montar).
- Correção desses 24 itens: INTERROMPIDA no meio do lote 1 (regerando pilares). Scripts já alterados estão neste commit; geometria.py, memorias, CHECKLIST seção 12 também. Situação item a item não confirmada.

## Para retomar (fazer direto, em lotes pequenos, sem abrir agente novo)
1. `cd /home/claude/letsara/pranchas && python3 gerar_tudo.py --fim` — ver erros/divergências do estado atual.
2. Conferir no REVISAO_rev12b.md, item a item, o que já foi corrigido nos scripts (lote 1: PE03 2 BA-1 no +7,30; cotas horizontais das bainhas PF01–PF03; topo do CP-MEZ horizontal; lado das placas da linha 4 nas PG01–PG04/CT03/MON03 pelo modelo — placas no lado −y, y 29,475–29,575. Lote 2: aço das VB no PR01/NG01; textos velhos CP-I120 50, VM 25, CP-MEZ 40, laje 9,55; renomeação COB04 e "P6/P7" do R01; anexo da MC12 sem referências internas).
3. Regerar só as etapas afetadas (`python3 gerar_tudo.py <scripts>` ou `--etapa N`), depois `--fim`, `--fim --3d`, `unir_pranchas.py`, `memoria_rev12.py`.
4. Revisor-nd por diferença (alteradas.json + folhas-resumo + 24 itens), sem amostra se o Nathan quiser economizar.
5. Republicar o 3D no mesmo link, gravar `--emissao`, mandar os PDFs ao Nathan. Zip DXF+IFC só após aprovação.

Estimativa para concluir (28/10): 0,3–0,6 milhão de tokens, 1,5–3 h (maior parte é tempo de geração).
