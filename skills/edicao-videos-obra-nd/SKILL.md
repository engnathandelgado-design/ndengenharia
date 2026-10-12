---
name: "edicao-videos-obra-nd"
description: "Ler e editar vídeos de obra/fábrica (celular, WhatsApp) para Reels da ND: folha de contato, melhores trechos, vertical 1080x1920, estabilização, cor, câmera lenta, marca ND e junção com renders 3D."
---

# Leitura e edição de vídeos — ND Engenharia

Use quando o Nathan mandar vídeo de obra, fábrica ou peça (mp4 do celular/WhatsApp) para virar Reels, juntar com modelo 3D (skill `modelagem-3d-reels-nd`) ou tirar quadros para post. Responder em português técnico, direto.

## 1. Ferramenta
Script `video_nd.py` (Apêndice A) — copiar para a pasta de trabalho. Precisa de ffmpeg, numpy, PIL e fontes Inter (`/usr/share/fonts/opentype/inter`). O ffmpeg do ambiente não tem `vidstab`: estabilização é `deshake` (rx/ry múltiplos de 16). **Não usar `zoompan` em vídeo** (trava/fica lentíssimo); o zoom lento é `scale ... eval=frame` + `crop` (já implementado).

## 2. Ler antes de editar (obrigatório)
1. `info` — duração, resolução, fps, rotação, áudio. Vídeo de WhatsApp costuma vir 474×850 a 30 fps: ampliar para 1080×1920 amolece; compensar com `unsharp` leve (já na cadeia) e preferir trechos curtos em câmera lenta.
2. `folha VIDEO folha.jpg 0.5` e **olhar a imagem**: o que aparece em cada instante (peça inteira, detalhe, mão na frente, ferramenta, defeito, céu estourado).
3. `notas VIDEO 0.25` — nitidez (laplaciano), brilho e movimento. Bom trecho: nitidez alta, movimento baixo/moderado, brilho 90–180. Juntar com o que se viu na folha.
4. Montar a lista de trechos (ini–fim em s) e dizer ao Nathan quais foram escolhidos e por quê, se houver dúvida.

## 3. Editar
- `trecho(v, saida, ini, fim, vel, zoom, sobrepor=png, ocultar=[...], cobrir=True)`: corta, câmera lenta (`vel` 0,5–0,7 fica natural), estabiliza, preenche a tela vertical (`cobrir=True`) ou mantém o quadro inteiro sobre fundo desfocado (`cobrir=False`, útil em vídeo horizontal), cor suave e nitidez. Saída sem áudio, 1080×1920, 24 fps.
- `juntar(saida, [clipes], xfade=0.4)` — fusão entre clipes; todos já em 1080×1920/24 fps (renders 3D também).
- Legendas/marca: gerar PNG RGBA 1080×1920 com as funções de sobreposição da `modelagem-3d-reels-nd` (marca ND + "projeto da ND Engenharia", legenda embaixo, CTA com WhatsApp (46) 92000-4685) e aplicar com `sobrepor=` (estática) ou `sobrepor_seq` (animada, o_00000.png…). Alternativa: `quadros_de` + compor com PIL + `codificar`.
- Duração típica do trecho real dentro do Reels: 3–8 s; abrir com o melhor plano (peça inteira, profundidade, guindaste).
- Vídeo "projeto e execução": primeiro o projeto (render 3D da peça/obra), depois a execução com o trecho real começando pelo plano mais bonito da peça.

## 4. Regra de honestidade
- Pode: escolher os melhores planos, cortar, enquadrar, estabilizar, corrigir cor/exposição, câmera lenta, esconder distração pequena e irrelevante (logo de app, ferramenta no canto) com `delogo` ou recorte.
- Não pode: apagar, maquiar ou "corrigir" defeito real da peça ou da obra (lascamento, ninho de concretagem, fissura, ferrugem, cabeça quebrada) e apresentar como real. Quando o objetivo é mostrar a peça "com acabamento de qualidade", usar **trecho real em que ela está boa** ou **render 3D marcado como projeto da ND Engenharia** — nunca retoque disfarçado.
- Se o vídeo mostrar patologia, avisar o Nathan com leitura técnica curta (ex.: lascamento na cabeça junto às cordoalhas → suspeita de fendilhamento na liberação da protensão; conferir fretagem/estribos da extremidade, resistência na liberação e sequência de corte das cordoalhas).

## 5. Padrão de entrega
- mp4 H.264, yuv420p, `+faststart`, < 30 MB (crf 20–23), 1080×1920.
- Mostrar quadros-chave/folha de contato na tela e enviar o mp4 (sem .zip).
- Não citar cliente/cidade sem o Nathan confirmar; não especificar materiais/perfis em material de marketing.

## Apêndice A — video_nd.py
```python
"""video_nd.py — leitura e edição de vídeos de obra/fábrica para a ND Engenharia (ffmpeg + PIL + numpy).

Uso rápido (CLI):
  python3 video_nd.py info  VIDEO
  python3 video_nd.py folha VIDEO saida.jpg [passo_s=0.5]          # folha de contato com tempo em cada quadro
  python3 video_nd.py notas VIDEO [passo_s=0.25]                    # nitidez/brilho/movimento por instante -> melhores trechos
  python3 video_nd.py cenas VIDEO [limiar=0.3]                      # cortes de cena
  python3 video_nd.py trecho VIDEO saida.mp4 INI FIM [vel=1.0] [zoom=0.0]
  python3 video_nd.py juntar saida.mp4 a.mp4 b.mp4 ... [--xfade 0.4]
Funções também importáveis (ver docstrings)."""
import json, os, subprocess, sys, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 24
FONTE = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'


def _run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: raise RuntimeError(r.stderr[-1500:])
    return r.stdout


# ------------------------------------------------------------------ leitura
def info(v):
    """duração, resolução, fps, rotação e se tem áudio"""
    j = json.loads(_run(['ffprobe', '-v', 'error', '-print_format', 'json', '-show_streams', '-show_format', v]))
    vs = [s for s in j['streams'] if s['codec_type'] == 'video'][0]
    num, den = map(int, vs['r_frame_rate'].split('/'))
    rot = 0
    for sd in vs.get('side_data_list', []):
        rot = int(sd.get('rotation', 0) or 0)
    return dict(dur=float(j['format']['duration']), w=vs['width'], h=vs['height'], fps=num/max(den, 1), rot=rot,
                audio=any(s['codec_type'] == 'audio' for s in j['streams']))


def quadros(v, passo=0.5, larg=360):
    """lista de (t, PIL.Image) amostrados a cada `passo` s"""
    d = tempfile.mkdtemp()
    _run(['ffmpeg', '-v', 'error', '-i', v, '-vf', f'fps=1/{passo},scale={larg}:-2', f'{d}/q_%04d.jpg'])
    fs = sorted(os.listdir(d))
    return [(i*passo, Image.open(os.path.join(d, f)).convert('RGB')) for i, f in enumerate(fs)]


def folha(v, saida, passo=0.5, larg=180, cols=10):
    """folha de contato com o tempo escrito em cada quadro — SEMPRE olhar antes de editar"""
    qs = quadros(v, passo, larg); w, h = qs[0][1].size
    rows = (len(qs) + cols - 1)//cols
    S = Image.new('RGB', (w*cols, h*rows), 'white'); fn = ImageFont.truetype(FONTE, 14)
    for k, (t, im) in enumerate(qs):
        d = ImageDraw.Draw(im); d.rectangle((0, 0, 56, 20), fill='black'); d.text((4, 2), f'{t:.1f}s', fill='yellow', font=fn)
        S.paste(im, ((k % cols)*w, (k//cols)*h))
    S.save(saida, quality=88); return saida


def notas(v, passo=0.25):
    """por instante: nitidez (variância do laplaciano), brilho médio e movimento (dif. para o quadro anterior).
    Trechos bons para Reels = nitidez alta, movimento baixo/moderado, brilho 90–180."""
    qs = quadros(v, passo, 320); out = []; prev = None
    for t, im in qs:
        g = np.asarray(im.convert('L'), float)
        lap = g[1:-1, 1:-1]*4 - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:]
        mov = 0.0 if prev is None else float(np.abs(g - prev).mean())
        out.append(dict(t=t, nitidez=float(lap.var()), brilho=float(g.mean()), mov=mov)); prev = g
    return out


def cenas(v, limiar=0.3):
    """instantes de troca de cena"""
    r = subprocess.run(['ffmpeg', '-i', v, '-vf', f"select='gt(scene,{limiar})',showinfo", '-f', 'null', '-'],
                       capture_output=True, text=True)
    return [float(l.split('pts_time:')[1].split()[0]) for l in r.stderr.splitlines() if 'pts_time:' in l]


# ------------------------------------------------------------------ edição
def cadeia(ini, fim, vel=1.0, zoom=0.0, cobrir=True, estabilizar=True, cor=True, fps=FPS, ocultar=()):
    """monta o filtro de vídeo: corte, velocidade, estabilização, enquadramento vertical 1080x1920,
    correção de cor suave, nitidez e zoom lento (0..0.15).
    ocultar = [(x,y,w,h)] em pixels do ORIGINAL — só para distrações pequenas (logo de app, ferramenta no canto)."""
    f = [f'trim={ini}:{fim}', f'setpts=(PTS-STARTPTS)/{vel}']
    for (x, y, w, h) in ocultar: f.append(f'delogo=x={x}:y={y}:w={w}:h={h}')
    if estabilizar: f.append('deshake=rx=32:ry=32')
    if cobrir:   # preenche a tela vertical cortando as sobras (sem barras)
        f.append(f'scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}')
    else:        # mantém o quadro inteiro sobre fundo desfocado do próprio vídeo
        f.append(f'split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},gblur=sigma=30[bg];'
                 f'[b]scale={W}:{H}:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2')
    if zoom > 0:   # zoom lento: escala crescente quadro a quadro + recorte central
        dur = (fim - ini)/vel
        f.append(f"scale=w='trunc({W}*(1+{zoom}*t/{dur:.3f})/2)*2':h=-2:eval=frame,crop={W}:{H}")
    if cor: f.append('eq=contrast=1.06:saturation=1.08:brightness=0.015,unsharp=5:5:0.6:5:5:0.0')
    f += [f'fps={fps}', 'format=yuv420p']
    return ','.join(f)


def trecho(v, saida, ini, fim, vel=1.0, zoom=0.0, sobrepor=None, **kw):
    """corta e trata um trecho; `sobrepor` = PNG 1080x1920 com transparência (marca/legenda) por cima"""
    vf = cadeia(ini, fim, vel, zoom, **kw)
    if sobrepor:
        cmd = ['ffmpeg', '-y', '-v', 'error', '-i', v, '-i', sobrepor, '-filter_complex', f'[0:v]{vf}[v];[v][1:v]overlay=0:0,format=yuv420p',
               '-an', '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-movflags', '+faststart', saida]
    else:
        cmd = ['ffmpeg', '-y', '-v', 'error', '-i', v, '-vf', vf, '-an', '-c:v', 'libx264', '-preset', 'slow', '-crf', '20',
               '-movflags', '+faststart', saida]
    _run(cmd); return saida


def sobrepor_seq(v, pasta_png, saida, fps=FPS):
    """sobrepõe uma sequência de PNG RGBA (o_00000.png ...) quadro a quadro — legendas animadas"""
    _run(['ffmpeg', '-y', '-v', 'error', '-i', v, '-framerate', str(fps), '-i', f'{pasta_png}/o_%05d.png',
          '-filter_complex', '[0:v][1:v]overlay=0:0:shortest=1,format=yuv420p', '-an', '-c:v', 'libx264', '-preset', 'slow',
          '-crf', '20', '-movflags', '+faststart', saida])
    return saida


def quadros_de(v, pasta, fps=FPS):
    """extrai todos os quadros (f_00000.jpg) para compor com PIL junto de quadros renderizados"""
    os.makedirs(pasta, exist_ok=True)
    _run(['ffmpeg', '-y', '-v', 'error', '-i', v, '-vf', f'fps={fps}', '-q:v', '2', '-start_number', '0', f'{pasta}/f_%05d.jpg'])
    return sorted(os.listdir(pasta))


def duracao(v): return info(v)['dur']


def juntar(saida, videos, xfade=0.4):
    """concatena clipes já em 1080x1920/24 fps; xfade>0 faz fusão entre eles"""
    if xfade <= 0 or len(videos) == 1:
        lst = tempfile.mktemp(suffix='.txt')
        open(lst, 'w').write(''.join(f"file '{os.path.abspath(x)}'\n" for x in videos))
        _run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', saida]); return saida
    cmd = ['ffmpeg', '-y', '-v', 'error']
    for x in videos: cmd += ['-i', x]
    fc, prev, acc = [], '[0:v]', duracao(videos[0])
    for i in range(1, len(videos)):
        off = acc - xfade; lab = f'[x{i}]'
        fc.append(f'{prev}[{i}:v]xfade=transition=fade:duration={xfade}:offset={off:.3f}{lab}')
        prev = lab; acc = off + duracao(videos[i])
    cmd += ['-filter_complex', ';'.join(fc), '-map', prev, '-c:v', 'libx264', '-preset', 'slow', '-crf', '21',
            '-pix_fmt', 'yuv420p', '-movflags', '+faststart', saida]
    _run(cmd); return saida


def codificar(pasta, saida, fps=FPS, crf=21):
    """quadros f_00000.jpg -> mp4 compatível com Instagram"""
    _run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(fps), '-i', f'{pasta}/f_%05d.jpg', '-c:v', 'libx264', '-preset', 'slow',
          '-crf', str(crf), '-pix_fmt', 'yuv420p', '-movflags', '+faststart', saida])
    return saida


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[0] == 'info': print(info(a[1]))
    elif a[0] == 'folha': print(folha(a[1], a[2], float(a[3]) if len(a) > 3 else 0.5))
    elif a[0] == 'notas':
        for n in notas(a[1], float(a[2]) if len(a) > 2 else 0.25):
            print(f"{n['t']:6.2f}s  nitidez {n['nitidez']:7.1f}  brilho {n['brilho']:5.1f}  mov {n['mov']:5.1f}")
    elif a[0] == 'cenas': print(cenas(a[1], float(a[2]) if len(a) > 2 else 0.3))
    elif a[0] == 'trecho': print(trecho(a[1], a[2], float(a[3]), float(a[4]), float(a[5]) if len(a) > 5 else 1.0, float(a[6]) if len(a) > 6 else 0.0))
    elif a[0] == 'juntar':
        xf = 0.4
        if '--xfade' in a: i = a.index('--xfade'); xf = float(a[i+1]); a = a[:i] + a[i+2:]
        print(juntar(a[1], a[2:], xf))
```