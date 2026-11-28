"""Original royalty-free background track (synthesized): warm pads, pluck arpeggio, soft kick/hat. 110 BPM."""
import numpy as np, sys, wave
SR=44100; BPM=110; beat=60/BPM; dur=float(sys.argv[2]) if len(sys.argv)>2 else 28
n=int(SR*dur); out=np.zeros((n,2))
def hz(m): return 440*2**((m-69)/12)
def env(L,a=0.01,r=0.3):
    t=np.arange(L)/SR; e=np.minimum(1,t/a)*np.exp(-t/r); return e
prog=[[57,60,64],[53,57,60],[48,52,55],[55,59,62]]  # Am F C G
bar=4*beat
rng=np.random.default_rng(7)
t_all=np.arange(n)/SR
for b in range(int(dur/bar)+1):
    ch=prog[b%4]; s=int(b*bar*SR); L=min(int(bar*SR),n-s)
    if L<=0: break
    t=np.arange(L)/SR
    pad=sum(np.sin(2*np.pi*hz(m)*t)+0.3*np.sin(2*np.pi*hz(m)*2.003*t) for m in ch)
    pe=np.minimum(1,t/0.4)*np.minimum(1,(bar-t)/0.4)
    out[s:s+L,0]+=0.05*pad*pe; out[s:s+L,1]+=0.05*pad*pe
    bass=np.sin(2*np.pi*hz(ch[0]-24)*t)*np.exp(-((t%beat))/0.5)
    out[s:s+L]+= (0.18*bass)[:,None]
    arp=[ch[0]+12,ch[1]+12,ch[2]+12,ch[1]+24]
    for k in range(8):
        st=s+int(k*beat/2*SR); m=arp[k%4]; Ln=int(0.45*SR)
        if st+Ln>n: continue
        tt=np.arange(Ln)/SR
        tone=(np.sin(2*np.pi*hz(m)*tt)+0.4*np.sin(2*np.pi*hz(m)*2*tt))*env(Ln,0.004,0.18)
        pan=0.3+0.4*(k%2)
        out[st:st+Ln,0]+=0.07*tone*(1-pan); out[st:st+Ln,1]+=0.07*tone*pan
for k in range(int(dur/beat)):
    st=int(k*beat*SR)
    if k>=8 and st+int(0.3*SR)<n:  # kick enters after 2 bars
        Lk=int(0.3*SR); tt=np.arange(Lk)/SR
        f=50+90*np.exp(-tt/0.03); kick=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt/0.12)
        out[st:st+Lk]+= (0.35*kick)[:,None]
    sh=int((k+0.5)*beat*SR); Lh=int(0.05*SR)
    if k>=4 and sh+Lh<n:
        h=rng.standard_normal(Lh)*np.exp(-np.arange(Lh)/SR/0.012)
        h=np.diff(h,prepend=0)
        out[sh:sh+Lh]+= (0.05*h)[:,None]
fade=int(2.5*SR); out[-fade:]*=np.linspace(1,0,fade)[:,None]; out[:int(0.5*SR)]*=np.linspace(0,1,int(0.5*SR))[:,None]
out/=np.max(np.abs(out))*1.12
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((out*32767).astype('<i2').tobytes()); w.close()
