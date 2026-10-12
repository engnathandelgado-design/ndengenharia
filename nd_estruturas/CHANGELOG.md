# Histórico de alterações

Mudanças relevantes do nd_estruturas. Formato Keep a Changelog, versões semânticas.

## [Não lançado]

### Adicionado

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
