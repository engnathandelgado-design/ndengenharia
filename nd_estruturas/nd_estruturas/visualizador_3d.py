"""Modelo HTML do visualizador 3D (three.js r128) usado por bim.gravar_visualizador.

Página única para publicar como artefato e abrir no celular: camadas por grupo, toque na peça
(marca, seção, comprimento), vistas isométrica/planta/frontal, quantitativos, pendências e
marca d'água "projeto da ND Engenharia". Tema claro e escuro.
Marcadores substituídos: __TITULO__, /*CFG*/null, /*DATA*/null.
"""

MODELO_HTML = r"""<title>__TITULO__</title>
<style>
/* Layout: canvas 3D no topo; camadas, quantitativos e pendências abaixo. Celular primeiro. */
:root{
  --bg:#f2f3f1; --surface:#ffffff; --fg:#1d2321; --muted:#5d6763; --line:#d9ddd9;
  --accent:#b8612d; --warn:#9a5b00; --warn-bg:#fdf2dc; --scene:#e9ebe8;
  --f-body:"Archivo",system-ui,sans-serif; --f-mono:"IBM Plex Mono",ui-monospace,monospace;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#161a19; --surface:#1f2423; --fg:#e7ebe8; --muted:#9aa49f; --line:#323a38;
  --accent:#e08a52; --warn:#f0b65a; --warn-bg:#33291a; --scene:#202625; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#161a19; --surface:#1f2423; --fg:#e7ebe8; --muted:#9aa49f; --line:#323a38;
  --accent:#e08a52; --warn:#f0b65a; --warn-bg:#33291a; --scene:#202625; color-scheme:dark}
body{background:var(--bg);color:var(--fg);font-family:var(--f-body);font-size:15px;line-height:1.5}
.wrap{max-width:1100px;margin:0 auto;padding-inline:16px;padding-block:14px 32px;display:grid;gap:14px}
header{display:grid;gap:2px}
h1{font-weight:800;font-size:1.45rem;letter-spacing:-.01em;margin:0;text-wrap:balance}
.sub{color:var(--muted);font-size:.85rem;margin:0}
.stage{position:relative;height:62vh;min-height:340px;border-radius:10px;overflow:hidden;background:var(--scene);border:1px solid var(--line)}
canvas{display:block;width:100%;height:100%;touch-action:none}
.mark{position:absolute;right:10px;bottom:8px;font:600 .72rem var(--f-mono);letter-spacing:.06em;text-transform:uppercase;color:var(--muted);pointer-events:none}
.pick{position:absolute;left:10px;top:10px;right:10px;max-width:440px;background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:8px 10px;font:.82rem var(--f-mono);color:var(--fg)}
.views{position:absolute;left:10px;bottom:8px;display:flex;gap:6px;flex-wrap:wrap}
button{font:600 .8rem var(--f-body);color:var(--fg);background:var(--surface);border:1px solid var(--line);border-radius:6px;padding:6px 10px;cursor:pointer}
button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,320px),1fr));gap:14px}
section{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:12px 14px;min-width:0}
h2{font:700 .78rem var(--f-body);letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:0 0 8px}
label.l{display:grid;grid-template-columns:auto 14px 1fr auto auto;align-items:center;gap:10px;padding:6px 2px;border-bottom:1px solid var(--line);cursor:pointer}
label.l:last-child{border-bottom:0}
.sw{width:14px;height:14px;border-radius:3px}
.n{font:.8rem var(--f-mono);color:var(--muted);font-variant-numeric:tabular-nums;text-align:right}
ul{margin:0;padding-left:18px;display:grid;gap:8px}
li.alert{background:var(--warn-bg);border-left:3px solid var(--warn);padding:8px 10px;border-radius:4px;list-style:none;margin-left:-18px}
.foot{color:var(--muted);font-size:.8rem;margin:0}
</style>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;600;800&family=IBM+Plex+Mono:wght@400;600&display=swap">

<div class="wrap">
  <header><h1 id="titulo"></h1><p class="sub" id="subtitulo"></p></header>
  <div class="stage" id="stage">
    <canvas id="c" aria-label="Modelo 3D da estrutura"></canvas>
    <div class="pick" id="pick">Toque numa peça para ver marca, seção e comprimento.</div>
    <div class="views">
      <button id="v-iso" type="button">Isométrica</button>
      <button id="v-top" type="button">Planta</button>
      <button id="v-front" type="button">Frontal</button>
    </div>
    <div class="mark" id="mark"></div>
  </div>
  <div class="grid">
    <section><h2>Camadas · peças · volume (m³)</h2><div id="layers"></div></section>
    <section id="sec-pend"><h2>Pendências do modelo</h2><ul id="pend"></ul></section>
  </div>
  <p class="foot">Gerado do modelo IFC da obra. Volumes pelo envelope do perfil (sem alvéolos, chanfros ou recortes).</p>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
const CFG = /*CFG*/null;
const DATA = /*DATA*/null;
const PALETA = [0x8b9096,0xb84a2e,0xd98b3a,0x3b78c9,0x8a5fa8,0xbdb7a8,0x5c6168,0xa5753f,0x3f8f6b,0xdcd8cf];
document.getElementById('titulo').textContent = CFG.titulo;
document.getElementById('subtitulo').textContent = CFG.subtitulo;
document.getElementById('mark').textContent = CFG.autoria;
const ul = document.getElementById('pend');
if (!CFG.pendencias.length) document.getElementById('sec-pend').hidden = true;
CFG.pendencias.forEach((t, i) => { const li = document.createElement('li'); li.textContent = t; if (t.startsWith('!')) { li.className = 'alert'; li.textContent = t.slice(1).trim(); } ul.appendChild(li); });

const canvas = document.getElementById('c'), stage = document.getElementById('stage');
const renderer = new THREE.WebGLRenderer({canvas, antialias:true, alpha:true});
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
const scene = new THREE.Scene();
const cam = new THREE.PerspectiveCamera(40, 1, 0.1, 5000);
const ctr = new THREE.OrbitControls(cam, canvas); ctr.enableDamping = true;
scene.add(new THREE.HemisphereLight(0xffffff, 0x8a8a80, 0.85));
const sun = new THREE.DirectionalLight(0xffffff, 0.65); sun.position.set(60, 120, 40); scene.add(sun);

const box = new THREE.Box3(), pickables = [];
let k = 0;
for (const [g, itens] of Object.entries(DATA)) {
  const cor = CFG.cores[g] !== undefined ? CFG.cores[g] : PALETA[k++ % PALETA.length];
  const oculta = CFG.ocultas.includes(g);
  const grp = new THREE.Group();
  const mat = new THREE.MeshLambertMaterial({color: cor, transparent: oculta, opacity: oculta ? 0.55 : 1, side: THREE.DoubleSide});
  for (const it of itens) {
    const pos = new Float32Array(it.v.length);
    for (let i = 0; i < it.v.length; i += 3) { pos[i] = it.v[i]; pos[i+1] = it.v[i+2]; pos[i+2] = -it.v[i+1]; }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    geo.setIndex(it.f); geo.computeVertexNormals(); geo.computeBoundingBox(); box.union(geo.boundingBox);
    const m = new THREE.Mesh(geo, mat); m.userData = {nome: it.n, grupo: g};
    grp.add(m); pickables.push(m);
  }
  grp.visible = !oculta; scene.add(grp);
  const q = CFG.quant[g] || {};
  const lab = document.createElement('label'); lab.className = 'l';
  const inp = document.createElement('input'); inp.type = 'checkbox'; inp.checked = grp.visible; inp.id = 'cam-' + k;
  inp.addEventListener('change', e => { grp.visible = e.target.checked; });
  const sw = document.createElement('span'); sw.className = 'sw'; sw.style.background = '#' + cor.toString(16).padStart(6, '0');
  const nm = document.createElement('span'); nm.textContent = g;
  const n1 = document.createElement('span'); n1.className = 'n'; n1.textContent = itens.length;
  const n2 = document.createElement('span'); n2.className = 'n'; n2.textContent = q.volume_m3 !== undefined && q.material !== 'aco' ? q.volume_m3.toFixed(1) : '';
  lab.append(inp, sw, nm, n1, n2); document.getElementById('layers').appendChild(lab);
}

const centro = box.getCenter(new THREE.Vector3()), tam = box.getSize(new THREE.Vector3());
const R = Math.max(tam.x, tam.y, tam.z);
function vista(tipo) {
  const p = {iso: [centro.x - 0.9*R, centro.y + 0.75*R, centro.z + 0.9*R],
             top: [centro.x, centro.y + 1.6*R, centro.z + 0.001],
             front: [centro.x, centro.y + 0.08*R, centro.z + 1.3*R]}[tipo];
  cam.position.set(...p); ctr.target.copy(centro); ctr.update();
}
['iso', 'top', 'front'].forEach(t => document.getElementById('v-' + t).addEventListener('click', () => vista(t)));
vista('iso');

const ray = new THREE.Raycaster(), ptr = new THREE.Vector2(); let down = null, sel = null, selMat = null;
const realce = new THREE.MeshLambertMaterial({color: 0xe0702a});
canvas.addEventListener('pointerdown', e => { down = [e.clientX, e.clientY]; });
canvas.addEventListener('pointerup', e => {
  if (!down || Math.hypot(e.clientX - down[0], e.clientY - down[1]) > 6) return;
  const r = canvas.getBoundingClientRect();
  ptr.set((e.clientX - r.left) / r.width * 2 - 1, -(e.clientY - r.top) / r.height * 2 + 1);
  ray.setFromCamera(ptr, cam);
  const hit = ray.intersectObjects(pickables.filter(m => m.parent.visible))[0];
  if (sel) { sel.material = selMat; sel = null; }
  const pk = document.getElementById('pick');
  if (hit) { sel = hit.object; selMat = sel.material; sel.material = realce; pk.textContent = sel.userData.grupo + ' — ' + sel.userData.nome; }
  else pk.textContent = 'Toque numa peça para ver marca, seção e comprimento.';
});
function resize() { const w = stage.clientWidth, h = stage.clientHeight; renderer.setSize(w, h, false); cam.aspect = w / h; cam.updateProjectionMatrix(); }
new ResizeObserver(resize).observe(stage); resize();
(function loop() { ctr.update(); renderer.render(scene, cam); requestAnimationFrame(loop); })();
</script>
"""
