---
name: "modelagem-3d-reels-nd"
description: "Modelar em 3D estruturas pré-moldadas e metálicas da ND (galpões, tesouras, pontes rolantes, ligações parafusadas) a partir de pranchas e gerar imagens técnicas e Reels/carrossel para Instagram."
---

# Modelagem 3D e Reels — ND Engenharia

Use quando o Nathan pedir para modelar uma estrutura em 3D a partir de pranchas (PDF/DWG) e/ou fazer material de divulgação (Reels, carrossel, imagens para cliente). Responder em português técnico.

## 1. Ferramenta: pacote Python `nd3d`
Código salvo pelo Nathan (pasta `nd3d` — conferir onde está: Google Drive "materiais gerdau/ferramenta/nd3d" ou repositório GitHub). Baixar/clonar antes de começar; se não houver acesso, reconstruir pelos módulos abaixo.
- `cena.py` — `Cena`: peças como arrays unidos por grupo (42 mil peças em ~2 s). Primitivas: caixa, prisma (normais para fora), cilindro por gabarito, perfil I/W, dupla cantoneira, haste, parafuso (cabeça+arruela+porca), chapa por contorno.
- `pecas.py` — bloco com cálice, pilar com consolos, tesoura de duas águas contínua (`tesoura_duas_aguas`, diagonais num só sentido por água) e de meia-água isolada (`tesoura`), com chapas de nó + parafusos + solda de filete + emenda de campo + apoios (fixo/oblongo), terça W com clipe, tirante com arruela biselada e esticador, viga de rolamento W + U com placa, chumbadores em furo oblongo, travamento lateral e grampos do trilho.
- `verifica.py` — treliça plana por rigidez; `sentido_diagonais()` (sentido único por água: 'desce' × 'sobe' pelo caso que governa; tesoura contínua sobre o apoio central); compressão NBR 8800; parafuso (corte/esmagamento); chumbador à tração; solda de filete; furo padrão d + 1,5 mm.
- `render.py` — paletas (real e por família de peça), `imagem()` (axonometria sem distorção, elevação em escala exata, perspectiva), `Filme` (quadros de vídeo: etapas de montagem, órbita, closes).
- `analise_portico.py` — pórtico plano (pilares engastados + tesoura contínua), deslocamentos de serviço (gravidade, vento frequente); exemplo de deformada animada em `exemplos/galpao_pontes_20t/analise_deformada.py`.
- `overlay.py` — marca ND + etiqueta "projeto da ND Engenharia", legendas, cabeçalho, cotas, níveis, escala gráfica, chamada com WhatsApp (46) 92000-4685, `codificar()` mp4.
- Exemplo completo: `exemplos/galpao_pontes_20t/` (100 × 50,78 m, pontes 20 t).
Requisitos: `pip install --break-system-packages pyvista vtk numpy pillow matplotlib`; ffmpeg; fontes Inter.

## 2. Fluxo
1. **Ler as pranchas em alta resolução** (pdftoppm -r 150, recortar cada vista). Tirar eixos, cotas, níveis, seções, inclinação e anotações (sobrecargas, pontes, insertos). Modelo sem medida da prancha é retrabalho certo — o Nathan reprova "sem proporção/escala".
2. **Conferir a concepção como projetista antes de modelar**: rodar `verifica.sentido_diagonais()` com gravidade e sucção (vento NBR 6123); pré-dimensionar banzos, alma, terças, viga de rolamento e ligações (skill `estruturas-metalicas-nd`); rodar `analise_portico` para os deslocamentos. Marcar "(conferir)" o que for hipótese (V0, carga de roda da ponte, etc.).
3. Montar a `Cena` com as peças paramétricas e testar 4–5 enquadramentos em baixa resolução antes do render longo.
4. Gerar quadros: abertura (tipo de obra, cidade, papel da ND) → montagem por etapas (concreto → aço → equipamentos → fechamento) → closes de tesoura e viga de rolamento → **closes das ligações** (inclusive terça de fechamento no pilar) → corte 2D cotado com escala gráfica → modelo por família de peças + ficha técnica → **análise: deformada animada colorida por deslocamento** (clientes gostam) → interno → chamada com WhatsApp.
5. Render em paralelo (2–3 processos por trechos), codificar com `overlay.codificar()`, entregar o mp4 e os quadros-chave na tela (não mandar .zip).

## 3. Regras de concepção (aprendidas)
- **Diagonais da tesoura: UM SÓ SENTIDO EM CADA ÁGUA, espelhadas apenas na cumeeira** (regra do Nathan — nunca inverter o sentido no meio da água; isso foi reprovado duas vezes). Em duas águas com pilar na cumeeira, modelar a tesoura contínua sobre ele. Escolher o sentido pelo cálculo: as diagonais longas (junto à cumeeira) devem ficar tracionadas no caso que governa. Caso galpão com pontes de 20 t (sucção governa): diagonais DESCEM do beiral para a cumeeira (V no banzo inferior sobre o pilar D) → +190 kN nas longas; compressão máx. −154 kN em diagonal curta (2,4 m).
- Conferir a imagem do corte antes de renderizar o vídeo: olhar a tesoura inteira em elevação e checar o sentido das diagonais em cada água.
- Com sucção o banzo inferior comprime → mãos francesas em todos os nós.
- Apoio da tesoura sofre arrancamento → chumbadores à tração. Se a tesoura precisa travar os pilares na transversal (fechamento completo, vento), apoios SEM furo oblongo nessa direção; furo oblongo só quando a estabilidade lateral não depende dela.
- Tesoura > 13 m → emendas de campo parafusadas fora do nó, segmentos ≤ ~12,7 m (+ peça de cumeeira sobre o pilar central).
- Ligações de campo 100 % parafusadas (A325, um diâmetro por obra), soldas só de fábrica de filete; bisel só para penetração total (evitar). Arruela biselada nos tirantes inclinados.
- Viga de rolamento biapoiada com junta sobre o apoio, placa com furo oblongo para alinhamento, travamento lateral da mesa superior ao pilar, grampos do trilho a cada ~600 mm.
- Com tesoura metálica não usar cinta de concreto no topo do pilar (conflita com o apoio).
- **Fechar as laterais muda o projeto**: placas + telha até o chão levam o vento inteiro aos pilares em balanço. Verificar deslocamento (H/300 combinação frequente; com ponte rolante conferir limite no nível da viga) com `analise_portico` e avisar o Nathan antes de seguir. Caso galpão 20 t: 40×60/40×70 → 63 mm; 40×80 com a tesoura ligando os 3 pilares → 33 mm (escolhido). No longitudinal: contraventamento vertical em X nas filas de fachada (vãos de extremidade e central), que também recebe a frenagem das pontes.
- Fechamento lateral padrão quando pedido: fiadas de placas pré-moldadas na base (ex.: 2 × 1,25 m, e = 15 cm, juntas nos eixos, pingadeira no topo) + telha trapezoidal pré-pintada sobre terças de fechamento (ex.: W 150×18,0 a cada ~1,6 m, alma horizontal = eixo forte contra o vento, linhas de corrente no meio do vão). Fixação no pilar pré-moldado: inserto metálico embutido + suporte em chapa dobrada parafusado no inserto e na mesa interna da terça, furos oblongos para ajuste. Mostrar o detalhe por fora com a telha oculta.

## 4. Apresentação
- Toda imagem com "projeto da ND Engenharia". Telha de cobertura na cor natural (zincalume), não colorida. Chapas em laranja-zarcão e parafusos claros para o cliente enxergar o detalhamento.
- Estilo de referência: posts técnicos/educativos (corte cotado, modelo colorido por família de peça, texto explicando o porquê).
- Imagem de deslocamento: deformada animada (ampliada ~100×) colorida por |u| em mm, com escala de cores e, na legenda, o valor máximo e o limite normativo. Só publicar se atender.
- Vídeo vertical 1080×1920; legenda na parte de baixo; objeto acima da legenda.
- Nunca citar nome de cliente, fábrica de origem das pranchas ou cidade sem o Nathan confirmar; usar o que ele indicar (tipo de obra, cidade, papel da ND — ex.: "contratada para projeto e montagem", início da montagem).

## 5. Armadilhas técnicas de render
- Não usar `show_edges` (escurece faces grandes — concreto fica preto).
- Faces com normal para fora (prisma orienta automaticamente).
- `clipping_range` curto nos closes (0,2–150 m); `p.render()` antes de cada quadro ao trocar visibilidade.
- Vídeo vertical: `SetWindowCenter(0, -0.35)` sobe o objeto acima da legenda.
- Criar milhares de objetos PyVista é lento → usar a `Cena` (arrays + junção única).
- Não matar processos com `pkill -f`/`pgrep -f` cujo padrão apareça no próprio comando (mata o shell); usar o PID.