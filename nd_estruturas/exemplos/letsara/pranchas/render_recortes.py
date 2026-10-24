"""Recortes 3D do modelo da obra (lidos da página letsara_3d.html) para as folhas de montagem (CT02, CT03, CT04)."""
import json, sys, numpy as np, pyvista as pv
pv.OFF_SCREEN=True
s=open('/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/saidas/letsara_3d.html').read()
i=s.find('const DATA = ')+13; j=s.find('\n',i); D=json.loads(s[i:j].rstrip(';'))
COR={'Pilares':'#c9c4bb','Vigas I90 de cobertura':'#b9b3a8','Vigas centrais I130':'#a9a398','Consolos':'#9c968b','Vigas de borda':'#b0aa9f',
 'Terças metálicas':'#5b7490','Ligações da cobertura':'#e8742c','Esperas e insertos embutidos':'#444444','Parafusos da cobertura':'#dddddd',
 'Contraventamento':'#b0272d','Correntes, tirantes rígidos e diagonais':'#2a9d6f','Pinos, tubos e neoprenes':'#222222',
 'Vigas de mezanino (retangulares protendidas)':'#b9b3a8','Cobertura metálica da linha 2':'#5b7490','Escada metálica':'#4a6a8a','Laje alveolar':'#d8d4cc','Concreto de 2º estágio (obra, com a capa)':'#8fa3b8','Alças N9 (2º estágio)':'#22aa88',
 'Insertos metálicos':'#e8742c','Calha e descidas':'#888888','Placas de fechamento':'#ddd8cf','Fixação das placas':'#e8742c'}
def mesh(it):
    v=np.array(it['v']).reshape(-1,3); f=np.array(it['f']).reshape(-1,3)
    return pv.PolyData(v,np.hstack([np.full((len(f),1),3),f]).ravel())
def cena(nome,box,cam,grupos=None,excl=(),hl=None,titulo="",transp=(),k=1.0,marca=False):
    """marca=False (padrão): sem "projeto da ND Engenharia" — obra da fábrica (Nathan, 21/10/2026). marca=True para material próprio da ND."""
    import numpy as _n
    fo=_n.array(cam[1]);cam=[tuple(fo+(_n.array(cam[0])-fo)*k),cam[1],cam[2]]
    p=pv.Plotter(window_size=(1600,1100)); p.set_background('white')
    x0,x1,y0,y1,z0,z1=box
    lotes={}
    for g,its in D.items():
        if g in excl or (grupos and g not in grupos): continue
        for it in its:
            v=np.array(it['v']).reshape(-1,3)
            if v[:,0].max()<x0 or v[:,0].min()>x1 or v[:,1].max()<y0 or v[:,1].min()>y1 or v[:,2].max()<z0 or v[:,2].min()>z1: continue
            m=mesh(it)
            if not (v[:,0].min()>=x0 and v[:,0].max()<=x1 and v[:,1].min()>=y0 and v[:,1].max()<=y1 and v[:,2].min()>=z0 and v[:,2].max()<=z1):
                m=m.clip_box(box,invert=False)
                if m.n_points==0: continue
            c=COR.get(g,'#aaaaaa')
            if hl and hl in it['n']: c='#ff5a00'
            lotes.setdefault((c, 0.35 if g in transp else 1.0), []).append(m)
    for (c, op), ms in lotes.items():                       # uma malha por cor/opacidade: milhares de peças em segundos
        p.add_mesh(pv.merge(ms) if len(ms) > 1 else ms[0],color=c,smooth_shading=False,specular=0.1,opacity=op)
    p.camera_position=cam
    p.add_text(titulo,font_size=12,color='black',position='upper_left') if titulo else None
    if marca: p.add_text("projeto da ND Engenharia",font_size=9,color="#666666",position="lower_right")
    p.enable_parallel_projection() if False else None
    p.screenshot(nome); p.close()
