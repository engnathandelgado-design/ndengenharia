"""Resumo da fase 1 da otimização (22/10/2026): junta otimizar_i130/ts01/vm.json e as famílias avaliadas pelos usos vigentes."""
import json
from pathlib import Path
AQ = Path(__file__).parent
KG = 0.792
i = json.loads((AQ / "otimizar_i130.json").read_text()); t = json.loads((AQ / "otimizar_ts01.json").read_text()); v = json.loads((AQ / "otimizar_vm.json").read_text())
R = {}
R["I130"] = {k: dict(atual=x["atual"], caa2=x["melhor"] and x["melhor"]["n"], caa1=x["melhor_caa1"] and x["melhor_caa1"]["n"],
                     arr_caa1=x["melhor_caa1"] and x["melhor_caa1"]["arranjo"], L=x["L"],
                     kg_caa2=round((x["atual"] - (x["melhor"]["n"] if x["melhor"] else x["atual"])) * x["L"] * KG, 1),
                     kg_caa1=round((x["atual"] - (x["melhor_caa1"]["n"] if x["melhor_caa1"] else x["atual"])) * x["L"] * KG, 1)) for k, x in i.items()}
R["I90_cobertura"] = dict(atual=8, caa2=8, caa1="7 (passa ELS-F e ELU; falta resolver o ato no apoio com isolamento)", n_pecas=14, L=19.7,
                          kg_caa1=round(14 * 19.7 * KG, 1))
R["VM"] = dict(atual="h 80, 8+2", caa2="h 80, 8+2 (nenhuma menor passa no ELS-D)", caa1="h 80, 6+0 (só falhava ELS-D)",
               kg_caa1=round(4 * 16 * 9.30 * KG, 1))
R["VB"] = dict(atual="15×60", melhor="15×55 (ranking vb_dente.json)", kg_ca50=round(8 * (136.8 - 121.5), 1), m3=round(8 * (0.824 - 0.758), 2),
               obs="muda o consolo CP-VB (h 29→24) e o nível do topo da VB; ~11 % do aço das VB")
R["manter"] = {"Placas PP": "10 fios Ø6 vale para a pista; PP-08/09 curtas (14 peças) dariam < 2 % dos fios", "Laje LP20": "7 Ø12,7 = 1 por nervura, LA-02 já com 4; capa/tela no mínimo",
               "Consolos": "tirantes com uso 0,80 (CP-I130), 0,88 (CP-MEZ); CP-VB 1 alça Ø12,5 (mínimo construtivo)",
               "Fixação das placas": "NC-1 0,96, CS-1 0,97, CE-1 0,88 — já otimizadas (MEF)",
               "Cobertura metálica": "terça 0,85–0,95, X 0,70, correntes 0,80, suportes 0,79–0,92 — já otimizadas no r05",
               "I90 em CAA II": "8 cordoalhas: 6 falha ELU, 7 falha ELS-D"}
(AQ / "otimizar_resumo.json").write_text(json.dumps(R, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps(R, indent=1, ensure_ascii=False))
