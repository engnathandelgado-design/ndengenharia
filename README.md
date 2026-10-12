# ndengenharia

Repositório interno da ND Engenharia e Assessoria LTDA. É a fonte única do código e das skills.
O Google Drive guarda só materiais (normas, catálogos, PDFs), entradas das obras e resultados (memoriais, pranchas, imagens).

## O que tem aqui

| Pasta / arquivo | Conteúdo |
|---|---|
| `nd_estruturas/` | Pacote Python do software estrutural (cálculo, MEF, form-finding), com testes |
| `app/` + `streamlit_app.py` | Páginas web das ferramentas (rodam no PC e online) |
| `skills/` | Skills da ND usadas pelo Claude (cópia mestre, versionada) |
| `requirements.txt` | Dependências para rodar as páginas |
| `*.bat` | Atalhos para Windows |

## Rodar no PC (Windows)

Precisa ter instalado: Git e Python 3.12 (python.org, marcar "Add to PATH").

Primeira vez:

```
git clone https://github.com/engnathandelgado-design/ndengenharia
```

Depois, dentro da pasta `ndengenharia`:

1. Dois cliques em `instalar_windows.bat` (só na primeira vez; leva alguns minutos).
2. Dois cliques em `abrir_ferramentas.bat`. Ele puxa a versão mais nova do GitHub e abre o navegador.
3. `rodar_testes.bat` confere o pacote (todos os testes devem passar).

Linha de comando equivalente:

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e "nd_estruturas[dev]"
streamlit run streamlit_app.py
```

## Rodar online (celular)

Streamlit Community Cloud (share.streamlit.io):

1. Entrar com a conta do GitHub.
2. Create app → repositório `engnathandelgado-design/ndengenharia`, branch `main`, arquivo `streamlit_app.py`.
3. Advanced settings → Python 3.12 → Deploy.

O app se atualiza sozinho a cada `git push`. Com o repositório privado, o app fica restrito a quem você liberar em Settings → Sharing.

## Fluxo de trabalho

- Mudança de código ou de skill: feita aqui, com commit e push. Nunca editar cópia no Drive.
- Entradas de obra (JSON) e saídas (memoriais, imagens): pasta da obra no Drive.

## Responsabilidade técnica

Os resultados não dispensam a revisão do engenheiro responsável.
