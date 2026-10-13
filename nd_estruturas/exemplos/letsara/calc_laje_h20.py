import numpy as np, math
# Laje alveolar genérica LP20 (largura 1245, 6 alvéolos Ø152) + capa 50 (C30); C50, 7 cord. Ø12,7 a 40 do fundo
b, h, nal, dal = 1.245, 0.20, 6, 0.152
dy=0.0005
ys=np.arange(dy/2,h,dy)
def larg(y):
    w=b
    for k in range(nal):
        yc=h/2; r=dal/2
        if abs(y-yc)<r: w-=2*math.sqrt(r*r-(y-yc)**2)
    return w
W=np.array([larg(y) for y in ys])
A=(W*dy).sum(); yc=(W*dy*ys).sum()/A; I=(W*dy*(ys-yc)**2).sum()
Ec50, Ec30 = 0.85*5600*math.sqrt(50)*1e3, 0.85*5600*math.sqrt(30)*1e3
n=Ec30/Ec50
# composta (capa 50 em cima, largura 1,25)
Ac=1.25*0.05*n; ycc=(A*yc+Ac*(h+0.025))/(A+Ac); Icomp=I+A*(yc-ycc)**2+1.25*n*0.05**3/12+Ac*(h+0.025-ycc)**2
print(f"A={A:.4f} m² ({A*25/1.25:.2f} kN/m²) yc={yc:.3f} I={I*1e6:.0f}e-6  comp: ycc={ycc:.3f} I={Icomp*1e6:.0f}e-6")
L=9.65-0.40+0.10                     # geometria do R01: vão de cálculo entre apoios (mesas das VM)
q_, rev, capa = 5.0*1.25, 1.0*1.25, 1.25*1.25
g1=A*25
fpd=1900/1.15*0.95  # aprox sigma pd
for ncord in (7, 8, 9):
    Ap=ncord*98.7e-6; ep=yc-0.040
    P0=ncord*98.7e-6*1400e3*0.95; Pinf=P0*0.80
    Mg1=g1*L**2/8; Mcapa=capa*L**2/8; Mrev=rev*L**2/8; Mq=q_*L**2/8
    Wi=I/yc; Wic=Icomp/ycc
    # fibra inferior: protensão + g1+capa na seção simples; rev e q na composta
    def sinf(psi):
        return -Pinf/A - Pinf*ep/Wi + (Mg1+Mcapa)/Wi + (Mrev+psi*Mq)/Wic
    fctk=0.7*0.3*50**(2/3)
    print(f"L={L:.2f} m  Mg1={Mg1:.1f} Mcapa={Mcapa:.1f} Mrev={Mrev:.1f} Mq={Mq:.1f} kN·m")
    print(f"  σinf ELS-F (ψ1=0,6, abertura): {sinf(0.6)/1e3:.2f} MPa  limite fctk,f≈{1.2*fctk:.2f}")
    print(f"  σinf ELS-D (ψ2=0,4, descompressão): {sinf(0.4)/1e3:.2f} MPa  limite 0")
    Md=1.4*(Mg1+Mcapa+Mrev)+1.4*Mq
    T=Ap*1480e3; x=T/(0.8*1.25*0.85*30/1.4*1e3); MRd=T*(0.21-0.4*x)
    print(f"  ELU Md={Md:.0f} kN·m  MRd≈{MRd:.0f} kN·m  (x={x*1000:.0f} mm)")
    Lmax=math.sqrt(8*MRd/(1.4*(g1+capa+rev+q_)))
    print(f"  vão máximo pelo ELU ≈ {Lmax:.2f} m")
    # vão máximo pelo ELS-D
    for Lt in np.arange(10,6,-0.05):
        s=(-Pinf/A - Pinf*ep/Wi + (g1+capa)*Lt**2/8/Wi + (rev+0.4*q_)*Lt**2/8/Wic)
        if s<=0: print(f"  vão máximo pelo ELS-D (descompressão, ψ2=0,4) ≈ {Lt:.2f} m"); break
    for Lt in np.arange(10,6,-0.05):
        s=(-Pinf/A - Pinf*ep/Wi + (g1+capa)*Lt**2/8/Wi + (rev+0.6*q_)*Lt**2/8/Wic)
        if s<=1.2*fctk*1e3: print(f"  vão máximo pelo ELS-F ≈ {Lt:.2f} m"); break
    # h26,5 for comparison skipped
