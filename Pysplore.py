#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         P Y S P L O R E   v 1 . 0                             ║
║        Double‑click to launch. No IDE. No install. Zero Dependencies.        ║
║   Windows · Mac · Linux · Raspberry Pi · Any device with Python 3.7+         ║
║     MIT License · The Dot Protocol · Six Archives · Aurora · Meditation     ║
╚══════════════════════════════════════════════════════════════════════════════╝

MIT License 2026 Pysplore Contributors. Use freely. The dot sings.
GUARDIAN I: Dot Protocol  GUARDIAN II: Entropy Pool  GUARDIAN III: Sacred Tokenizer
ARCHIVE I: UNDB Axioms  II: Sanskrit  III: Dictionary  IV: Encyclopedia  V: Aurora  VI: Meditation
"""
import os,sys,stat as _stat
try:
    _s=os.path.abspath(__file__)
    os.chmod(_s,os.stat(_s).st_mode|_stat.S_IXUSR|_stat.S_IXGRP|_stat.S_IXOTH)
except:pass

import json,math,time,re,struct,wave,threading,subprocess,tempfile,calendar,datetime,io
from pathlib import Path
from collections import deque,defaultdict

try:
    import tkinter as tk
    from tkinter import ttk,scrolledtext,messagebox,simpledialog,filedialog,colorchooser
except ImportError:
    print("Pysplore requires tkinter.\nInstall: sudo apt-get install python3-tk")
    sys.exit(1)

# ── FILESYSTEM ──────────────────────────────────────────────────────────────
BASE_DIR=Path.home()/"Pysplore_Data"
for _d in["audio","patterns","journal","exports","notes","saves","paint","wallpapers","scenes","meditation","backdrops"]:
    (BASE_DIR/_d).mkdir(parents=True,exist_ok=True)
SCRIPT_DIR=Path(__file__).parent
SAMPLE_RATE=44100

# ── GUARDIAN I: ENTROPY POOL ────────────────────────────────────────────────
class EntropyPool:
    def __init__(self):
        self._pool=list(range(256));self._dot_clicks=0
        self._kt=deque(maxlen=64);self._mt=deque(maxlen=64)
        self._last=time.time();self._counter=0
        for v in[int(time.time()*1e9)%(2**32),id(self),os.getpid()]:self._stir(v)
    def _stir(self,value):
        v=int(value)&0xFFFFFFFF
        for i in range(len(self._pool)-1,0,-1):
            j=(v^(i*6364136223846793005))%(i+1)
            self._pool[i],self._pool[j]=self._pool[j],self._pool[i]
            v=(v*1664525+1013904223)&0xFFFFFFFF
    def feed_mouse(self,x,y):
        n=time.time();d=(n-self._last)*1e6;self._last=n
        self._mt.append(int(d)^(x*31337)^(y*7919))
        if self._mt:self._stir(sum(self._mt))
    def feed_key(self,k):
        n=time.time();i=(n-self._last)*1e6;self._last=n
        self._kt.append(int(i)^k)
        if self._kt:self._stir(sum(self._kt))
    def feed_dot(self):
        self._dot_clicks+=1;self._stir(self._dot_clicks*999983^int(time.time()*1e6))
    def moon(self):
        d=datetime.datetime.now()
        return((d-datetime.datetime(2000,1,6)).days%29.53059)/29.53059
    def sun(self):
        n=datetime.datetime.now()
        return(n.hour*3600+n.minute*60+n.second)/86400
    def randint(self,lo,hi):
        self._counter+=1;self._stir(self._counter^int(time.time()*1e9)%99991)
        idx=(self._pool[self._counter%256]^int(self.moon()*1000)^int(self.sun()*1000))%256
        return lo+(self._pool[idx]%(hi-lo+1))
    def random(self):return self.randint(0,999999)/1000000.0
    def choice(self,s):
        if not s:raise IndexError("empty")
        return s[self.randint(0,len(s)-1)]
    def shuffle(self,lst):
        for i in range(len(lst)-1,0,-1):
            j=self.randint(0,i);lst[i],lst[j]=lst[j],lst[i]

E=EntropyPool()

# ── GUARDIAN II: SACRED TOKENIZER ───────────────────────────────────────────
class SacredTokenizer:
    CF={c:440.0*(2.0**(i/12.0)) for i,c in enumerate('abcdefghijklmnopqrstuvwxyz')}
    def __init__(self):
        self.buf=deque(maxlen=1024);self.count=0;self._lk=threading.Lock()
    def tok(self,text,src='text'):
        for ch in str(text).lower():
            f=self.CF.get(ch,440.0+(ord(ch)%100))
            t={'ch':ch,'f':f,'src':src,'t':time.time()}
            with self._lk:self.buf.append(t);self.count+=1
            E.feed_key(ord(ch))
    def ambient_freq(self):
        with self._lk:
            if not self.buf:return 432.0
            r=list(self.buf)[-8:]
            return max(80.0,min(2000.0,sum(x['f']for x in r)/len(r)))
    def rhythm(self):
        with self._lk:
            if len(self.buf)<2:return 120.0
            ts=[x['t']for x in list(self.buf)[-8:]]
            iv=[ts[i+1]-ts[i]for i in range(len(ts)-1)]
            return max(40.0,min(300.0,60.0/max(0.001,sum(iv)/len(iv))))

TK=SacredTokenizer()

# ── ARCHIVE I: UNDB AXIOMS ───────────────────────────────────────────────────
AXIOMS={
    "L1":"Identity — A thing is identical to itself.",
    "L2":"Non-Contradiction — A thing cannot both be and not-be simultaneously.",
    "L3":"Excluded Middle — A proposition is either true or false.",
    "L4":"Sufficient Reason — Everything that exists has a reason.",
    "L5":"Non-Circularity — No system may use itself as its own justification.",
    "S1":"Conservation of Energy — Energy cannot be created or destroyed.",
    "S2":"Entropy — Closed systems tend toward disorder.",
    "S3":"Causality — Every effect has a cause.",
    "S4":"Falsifiability — Scientific claims must be falsifiable.",
    "S5":"Evolutionary Continuity — Life adapts and evolves.",
    "E1":"Golden Rule — Treat others as you wish to be treated.",
    "E2":"Human Dignity — All humans have inherent worth.",
    "E3":"Non-Maleficence — Do no harm.",
    "E4":"Beneficence — Act for the good of others.",
    "E5":"Autonomy — Respect self-determination.",
    "E6":"Justice — Fairness in treatment and distribution.",
    "E7":"Honesty — Truth is the foundation of trust.",
    "DOT":"The Dot Protocol — infinite recursion, perpetual refinement, freeflow, loop.",
}
DOT_STAGES=["1. FREE-FLOW EXPANSION","2. CROSS-COMPARATIVE ANALYSIS","3. RECURSIVE OPTIMIZATION","4. PERPETUAL LOOP"]

# ── ARCHIVE II: SANSKRIT ─────────────────────────────────────────────────────
SK={
    "अहम्":"aham — I, self, ego","सत्":"sat — being, existence, truth",
    "चित्":"chit — consciousness, awareness","आनन्द":"ananda — bliss, joy",
    "ब्रह्म":"brahma — the absolute","धर्म":"dharma — right action, cosmic order",
    "कर्म":"karma — action and its consequences","योग":"yoga — union, discipline",
    "ध्यान":"dhyana — meditation, absorption","प्राण":"prana — life force, vital breath",
    "आत्मन्":"atman — individual self, soul","मोक्ष":"moksha — liberation",
    "माया":"maya — illusion, the veil","नमस्ते":"namaste — I bow to the divine in you",
    "ॐ":"Om — the primordial sound","शान्ति":"shanti — peace, tranquility",
    "सत्यम्":"satyam — truth","शिवम्":"shivam — auspiciousness",
    "सुन्दरम्":"sundaram — beauty","अहिंसा":"ahimsa — non-violence",
    "चक्र":"chakra — wheel, energy center","कुण्डलिनी":"kundalini — serpent power",
    "गुरु":"guru — teacher, dispeller of darkness","मन्त्र":"mantra — sacred sound",
    "वेद":"veda — sacred knowledge","अद्वैत":"advaita — non-duality, oneness",
    "सुख":"sukha — happiness","दुःख":"duhkha — suffering","निर्वाण":"nirvana — liberation",
}

def trans_sk(t):
    t=t.strip()
    if t in SK:return f"SANSKRIT→EN: {t} = {SK[t]}"
    for k,v in SK.items():
        if t.lower()==v.split(" — ")[0].lower():return f"EN→SANSKRIT: {t} = {k}\n{v}"
    r=[f"  {k}={v}"for k,v in SK.items()if t.lower()in v.lower()or t.lower()in k.lower()]
    if r:return"RELATED:\n"+"\n".join(r[:5])
    return f"No entry for '{t}'. Try: ॐ dharma yoga karma shanti"

# ── ARCHIVE III: DICTIONARY ──────────────────────────────────────────────────
DICT={
    "algorithm":"n. A process or rules for calculation or problem-solving.",
    "axiom":"n. A statement taken to be true; self-evident truth.",
    "bliss":"n. Perfect happiness; great joy.",
    "chaos":"n. Complete disorder and confusion.",
    "consciousness":"n. The state of being aware; subjective experience.",
    "cosmos":"n. The universe seen as a well-ordered whole.",
    "entropy":"n. Lack of order; tendency to disorder.",
    "ephemeral":"adj. Lasting for a very short time; transitory.",
    "equilibrium":"n. A state of balance; mental or emotional stability.",
    "eternal":"adj. Lasting or existing forever; without end.",
    "fractal":"n. A never-ending pattern, self-similar across scales.",
    "frequency":"n. Rate of occurrence; cycles per second in wave.",
    "harmony":"n. Agreement; pleasing arrangement of parts.",
    "infinite":"adj. Limitless, endless, without boundary.",
    "intuition":"n. Understanding without conscious reasoning.",
    "liminal":"adj. Relating to a threshold or transitional stage.",
    "luminous":"adj. Full of or shedding light; glowing.",
    "meditation":"n. The practice of mental focus and contemplation.",
    "nexus":"n. A connection linking two or more things.",
    "paradox":"n. A seemingly absurd statement that may be true.",
    "recursion":"n. Defining something in terms of itself; self-reference.",
    "resonance":"n. The quality of being resonant; sympathetic vibration.",
    "sacred":"adj. Connected with God; deserving reverence.",
    "silence":"n. Absence of sound; calm and tranquility.",
    "sublime":"adj. Of great excellence; inspiring awe.",
    "transcend":"v. Be or go beyond; rise above.",
    "void":"n. Complete emptiness; a large empty space.",
    "wisdom":"n. Experience, knowledge, and good judgment.",
    "zenith":"n. The point directly above; the highest point.",
}

# ── ARCHIVE IV: ENCYCLOPEDIA ─────────────────────────────────────────────────
ENC={
    "universe":"All of time, space, matter, energy. Age: 13.8B years. Diameter: ~93B light-years.",
    "consciousness":"Awareness of self and surroundings. The 'hard problem': why does subjective experience exist?",
    "meditation":"Focused attention for clarity and insight. 432 Hz associated with deep meditation states.",
    "quantum mechanics":"Physics at atomic scales. Wave-particle duality, Heisenberg uncertainty, entanglement.",
    "entropy":"Thermodynamic disorder. Increases in closed systems. Second Law of Thermodynamics.",
    "recursion":"A process that refers to itself. Fractals, trees, snowflakes. Self-similar at all scales.",
    "solfeggio":"Sacred frequencies: 396Hz liberation, 417Hz change, 528Hz DNA/transform, 639Hz connection, 741Hz awakening, 852Hz intuition, 963Hz divine.",
    "chakra":"Sanskrit 'wheel'. Seven energy centers root to crown, each with color, sound, function.",
    "aurora":"Northern/southern lights. Charged solar particles colliding with atmosphere. Green=oxygen, purple=nitrogen.",
    "fibonacci":"0,1,1,2,3,5,8,13... Each number sum of previous two. Golden ratio φ≈1.618. Found in galaxies.",
    "dna":"Deoxyribonucleic acid. Blueprint of life. Double helix Watson+Crick 1953. 528Hz resonance.",
    "mycelium":"Underground fungal network connecting trees. 'Wood wide web'. Intelligence without neurons.",
}

# ── ARCHIVE V: AURORA SYNTH ──────────────────────────────────────────────────
NOTE_NAMES=['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
SCALES={'major':[0,2,4,5,7,9,11],'minor':[0,2,3,5,7,8,10],'pentatonic':[0,2,4,7,9],
        'blues':[0,3,5,6,7,10],'dorian':[0,2,3,5,7,9,10],'chromatic':list(range(12))}
CHORD_IV={'major':[0,4,7],'minor':[0,3,7],'dim':[0,3,6],'maj7':[0,4,7,11],'min7':[0,3,7,10],'sus4':[0,5,7]}
CHAKRA_F={'Root':396,'Sacral':417,'Solar':528,'Heart':639,'Throat':741,'Third Eye':852,'Crown':963}
SOLFEG_F={'UT(liberation)':396,'RE(change)':417,'MI(transform)':528,'FA(connection)':639,'SOL(awaken)':741,'LA(intuition)':852}
SCENE_F={'Mountain Lake':432,'Forest Clearing':528,'Ocean Shore':396,'Desert Night':417,'Meadow':639,'Cave':741,'Sky':852}

def note_freq(n):
    nm={'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
    sm={'C#':1,'D#':3,'F#':6,'G#':8,'A#':10,'Bb':10,'Eb':3,'Ab':8}
    try:
        if len(n)>=3 and n[1]in'#b':k=n[:2];o=int(n[2:]);s=sm.get(k,0)
        else:k=n[0];o=int(n[1:]);s=nm.get(k,0)
        return 440.0*(2.0**(((o+1)*12+s-69)/12.0))
    except:return 440.0

def gen_wave(freq,dur,wtype='sine',vol=0.5):
    n=int(SAMPLE_RATE*dur);out=[]
    for i in range(n):
        t=i/SAMPLE_RATE;p=2*math.pi*freq*t
        if wtype=='sine':s=math.sin(p)
        elif wtype=='square':s=1.0 if math.sin(p)>=0 else -1.0
        elif wtype=='saw':s=2.0*((freq*t)%1.0)-1.0
        elif wtype=='triangle':s=2.0*abs(2.0*((freq*t)%1.0)-1.0)-1.0
        elif wtype=='noise':s=E.random()*2-1
        else:s=math.sin(p)
        out.append(s*vol)
    return out

def adsr(samp,atk=0.01,dec=0.05,sus=0.7,rel=0.1):
    n=len(samp);a=int(atk*SAMPLE_RATE);d=int(dec*SAMPLE_RATE);r=int(rel*SAMPLE_RATE)
    sl=max(0,n-a-d-r);out=[]
    for i,s in enumerate(samp):
        if i<a:env=i/max(a,1)
        elif i<a+d:env=1.0-(1.0-sus)*((i-a)/max(d,1))
        elif i<a+d+sl:env=sus
        else:env=sus*((n-i)/max(r,1))
        out.append(s*env)
    return out

def to_wav(samp):
    buf=bytearray()
    for s in samp:buf+=struct.pack('<h',int(max(-1.0,min(1.0,s))*32767))
    w=io.BytesIO()
    with wave.open(w,'wb')as wf:wf.setnchannels(1);wf.setsampwidth(2);wf.setframerate(SAMPLE_RATE);wf.writeframes(bytes(buf))
    return w.getvalue()

def play_wav(data):
    try:
        tmp=tempfile.NamedTemporaryFile(suffix='.wav',delete=False)
        tmp.write(data);tmp.close()
        if sys.platform=='win32':
            import winsound;winsound.PlaySound(tmp.name,winsound.SND_FILENAME|winsound.SND_ASYNC)
        elif sys.platform=='darwin':
            subprocess.Popen(['afplay',tmp.name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        else:
            for p in['aplay','paplay','ffplay','mpv','mplayer']:
                if subprocess.run(['which',p],capture_output=True).returncode==0:
                    subprocess.Popen([p,'-q',tmp.name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);break
    except:pass

def startup_sound():
    def _g():
        try:
            all_s=[]
            for note,vol in[('C3',.4),('E3',.3),('G3',.3),('B3',.2)]:
                s=adsr(gen_wave(note_freq(note),.8,'sine',vol),atk=.1,dec=.1,sus=.8,rel=.3)
                while len(all_s)<len(s):all_s.append(0.)
                for i,v in enumerate(s):all_s[i]+=v
            mx=max(abs(x)for x in all_s)or 1;all_s=[x/mx*.7 for x in all_s]
            for note in['C4','E4','G4','C5']:
                seg=adsr(gen_wave(note_freq(note),.15,'sine',.5),atk=.01,dec=.05,sus=.6,rel=.08)
                all_s.extend(seg)
            play_wav(to_wav(all_s))
        except:pass
    threading.Thread(target=_g,daemon=True).start()

def build_chord(root,ctype,octave=4):
    ri=NOTE_NAMES.index(root)if root in NOTE_NAMES else 0
    ivs=CHORD_IV.get(ctype,[0,4,7]);out=[]
    for iv in ivs:
        idx=(ri+iv)%12;oa=(ri+iv)//12
        name=NOTE_NAMES[idx]+str(octave+oa);out.append((name,note_freq(name)))
    return out

def gen_melody(root='C',scale='major',octave=4,bars=2,tempo=120):
    ri=NOTE_NAMES.index(root)if root in NOTE_NAMES else 0
    ivs=SCALES.get(scale,SCALES['major']);notes=[]
    for iv in ivs:
        idx=(ri+iv)%12;oa=(ri+iv)//12
        name=NOTE_NAMES[idx]+str(octave+oa);notes.append((name,note_freq(name)))
    beat=60./tempo;durs=[beat/2,beat,beat*2];mel=[]
    for _ in range(bars*4):mel.append((E.choice(notes)[1],E.choice(durs)))
    return mel

# ── ARCHIVE VI: AURORA AMBIENT ───────────────────────────────────────────────
class Aurora:
    def __init__(self):
        self.layers={'Wind':{'on':True,'vol':.3},'Water':{'on':True,'vol':.25},
                     'Birds':{'on':True,'vol':.2},'Insects':{'on':False,'vol':.15},
                     'Thunder':{'on':False,'vol':.1},'Om Tone':{'on':True,'vol':.2}}
        self.freq=432.;self.playing=False;self._lk=threading.Lock()
    def _wind(self,dur=1.,vol=.3):
        n=int(SAMPLE_RATE*dur);raw=[E.random()*2-1 for _ in range(n)]
        f=raw[:];
        for i in range(1,n-1):f[i]=(raw[i-1]+raw[i]*2+raw[i+1])/4.
        lf=.3+E.random()*.4
        return[f[i]*vol*(.5+.5*math.sin(2*math.pi*lf*i/SAMPLE_RATE))for i in range(n)]
    def _water(self,dur=1.,vol=.25):
        n=int(SAMPLE_RATE*dur);out=[0.]*n
        for freq,v in zip([80+E.randint(0,20),120+E.randint(0,30),200+E.randint(0,50)],[.4,.3,.2]):
            ph=E.random()*2*math.pi
            for i in range(n):out[i]+=math.sin(2*math.pi*freq*i/SAMPLE_RATE+ph)*v*vol
        for i in range(n):out[i]+=(E.random()-.5)*.05
        return out
    def _birds(self,dur=1.,vol=.2):
        n=int(SAMPLE_RATE*dur);out=[0.]*n
        for _ in range(E.randint(0,2)):
            cs=E.randint(0,max(0,n-int(SAMPLE_RATE*.15)));cf=2000+E.randint(0,3000)
            cn=min(int(SAMPLE_RATE*(.05+E.random()*.1)),n-cs)
            for i in range(cn):
                env=math.sin(math.pi*i/max(cn,1))
                out[cs+i]+=math.sin(2*math.pi*cf*i/SAMPLE_RATE)*env*vol
        return out
    def _insects(self,dur=1.,vol=.15):
        n=int(SAMPLE_RATE*dur);cf=4000+E.randint(0,1000);lf=8+E.randint(0,5)
        return[math.sin(2*math.pi*cf*i/SAMPLE_RATE)*max(0,math.sin(2*math.pi*lf*i/SAMPLE_RATE))*vol for i in range(n)]
    def _thunder(self,dur=1.,vol=.1):
        n=int(SAMPLE_RATE*dur)
        if E.randint(0,19)!=0:return[0.]*n
        ts=E.randint(0,max(0,n//2));out=[]
        for i in range(n):
            if i<ts or i>ts+n//3:out.append(0.)
            else:
                pos=i-ts;ln=n//3
                env=math.sin(math.pi*pos/ln)*math.exp(-pos/(ln*.5))
                out.append(((E.random()*2-1)*.6+math.sin(2*math.pi*50*pos/SAMPLE_RATE)*.4)*env*vol)
        return out
    def _om(self,dur=1.,vol=.2):
        n=int(SAMPLE_RATE*dur);f=self.freq
        return[(math.sin(2*math.pi*f*i/SAMPLE_RATE)*.6+math.sin(2*math.pi*f*2*i/SAMPLE_RATE)*.25+
                math.sin(2*math.pi*f*3*i/SAMPLE_RATE)*.15)*vol*(.7+.3*math.sin(2*math.pi*.2*i/SAMPLE_RATE))
               for i in range(n)]
    def _mix(self):
        dur=2.;n=int(SAMPLE_RATE*dur);mx=[0.]*n
        gens={'Wind':self._wind,'Water':self._water,'Birds':self._birds,
              'Insects':self._insects,'Thunder':self._thunder,'Om Tone':self._om}
        with self._lk:active={k:v for k,v in self.layers.items()if v['on']}
        for name,layer in active.items():
            try:
                s=gens[name](dur,layer['vol'])
                for i in range(min(len(s),n)):mx[i]+=s[i]
            except:pass
        pk=max(abs(x)for x in mx)if mx else 1
        if pk>.9:mx=[x/pk*.85 for x in mx]
        play_wav(to_wav(mx))
    def _loop(self):
        while self.playing:
            try:self._mix();time.sleep(.1)
            except:time.sleep(.5)
    def start(self):
        if not self.playing:
            self.playing=True;threading.Thread(target=self._loop,daemon=True).start()
    def stop(self):self.playing=False
    def set_layer(self,n,v):
        with self._lk:
            if n in self.layers:self.layers[n]['on']=v
    def set_vol(self,n,v):
        with self._lk:
            if n in self.layers:self.layers[n]['vol']=v

AUR=Aurora()

# ── NATURE SCENE GENERATOR ───────────────────────────────────────────────────
SCENES_META={
    'Mountain Lake':{'freq':432,'desc':'Still water. Reflected peaks. Dawn breaking. A bird drifts.',
                     'lp':{'Wind':True,'Water':True,'Birds':True,'Om Tone':True}},
    'Forest Clearing':{'freq':528,'desc':'Sunbeams through canopy. Ancient trees. Roots deep as memory.',
                       'lp':{'Wind':True,'Water':False,'Birds':True,'Insects':True}},
    'Ocean Shore':{'freq':396,'desc':'Waves arriving. Foam. Horizon of dots. The endless returning.',
                   'lp':{'Wind':True,'Water':True,'Birds':True,'Om Tone':True}},
    'Desert Night':{'freq':417,'desc':'Stars beyond counting. Silence between them is also alive.',
                    'lp':{'Wind':True,'Insects':True,'Om Tone':True}},
    'Meadow':{'freq':639,'desc':'Grass. Flowers. Clouds drifting like slow thoughts. Connected.',
              'lp':{'Wind':True,'Birds':True,'Insects':True}},
    'Cave':{'freq':741,'desc':'Stalactites. A pool. A single point of light reflected infinite.',
            'lp':{'Water':True,'Om Tone':True}},
    'Sky':{'freq':852,'desc':'Clouds drift. Birds rise. Sun sets. All is movement, all is still.',
           'lp':{'Wind':True,'Birds':True,'Om Tone':True}},
}

class NatureGen:
    def __init__(self):self.frame=0;self._seed=E.randint(0,99999)
    def _p(self,x,y,t,seed):
        v=(x*73856093)^(y*19349663)^(t*83492791)^(seed*2654435761)
        v=(v^(v>>16))&0xFFFFFFFF;v=(v*0x45d9f3b)&0xFFFFFFFF;v=(v^(v>>16))&0xFFFFFFFF
        return v/0xFFFFFFFF
    def _lake(self,w=58,h=16):
        lines=[];t=self.frame//4;sd=self._seed
        for row in range(h//3):
            l=''
            for col in range(w):
                v=self._p(col,row,t//8,sd)
                l+=(E.choice(['✦','·','*','.'])if v>.97 else('·'if v>.94 else' '))
            lines.append(l)
        lines.append(''.join('▲'if col%7==3 else'△'for col in range(w)))
        for row in range(h//6):
            l=''
            for col in range(w):
                v=self._p(col,row+100,0,sd)
                l+=E.choice(['▓','█','▒'])if v>.5 else E.choice(['░','▒','▓'])
            lines.append(l)
        for row in range(h//3):
            l=''
            for col in range(w):
                wv=math.sin((col*.3)+(self.frame*.05))*.5+.5+math.sin((col*.7)+(self.frame*.08))*.3
                l+=('≋'if wv>1.1 else('~'if wv>.9 else('≈'if wv>.7 else('-'if wv>.5 else'_'))))
            lines.append(l)
        bp=int((self.frame*.7)%(w-5));br=max(0,h//6-1)
        if br<len(lines):
            l=list(lines[br])
            if bp+5<len(l):
                for k,ch in enumerate('>-o-<'):l[bp+k]=ch
            lines[br]=''.join(l)
        return'\n'.join(lines[:h])
    def _ocean(self,w=58,h=16):
        lines=[];t=self.frame
        for row in range(h//3):
            l=''
            for col in range(w):
                v=self._p(col,row,t//10,self._seed)
                l+=('·'if v>.96 else('*'if v>.93 and row<3 else' '))
            lines.append(l)
        lines.append('·'*w)
        for i in range(h//3):
            off=(t+i*3)%w;l=list('_'*w)
            for col in range(w):
                wv=math.sin((col-off)*.4)*.5+.5
                if wv>.8:l[col]='~'
                elif wv>.6:l[col]='≈'
                elif wv>.4:l[col]='-'
            lines.append(''.join(l))
        foam=''
        for col in range(w):
            v=self._p(col,999,t//2,self._seed)
            foam+=E.choice(['°','·','~','_',' '])if v>.3 else' '
        lines.append(foam)
        for _ in range(h//5):lines.append('_'*w)
        return'\n'.join(lines[:h])
    def _desert(self,w=58,h=16):
        lines=[];t=self.frame;mp=E.moon()
        for row in range(h-3):
            l=''
            for col in range(w):
                v=self._p(col,row,0,self._seed)
                tw=math.sin(t*.1+v*100)*.3+.7
                if v>.97 and tw>.8:l+=E.choice(['✦','*','·','○'])
                elif v>.94:l+='·'
                elif v>.91:l+='.'
                else:l+=' '
            lines.append(l)
        mx=int(w*.75)
        if len(lines)>2 and mx+6<w:
            cr='( ○ )'if mp<.5 else'( ● )'
            l=list(lines[2])
            for k,ch in enumerate(cr):l[mx+k]=ch
            lines[2]=''.join(l)
        for row in range(3):
            l=''
            for col in range(w):
                d=math.sin(col*.15+row*.5)*.5+math.sin(col*.08)*.5
                l+=(E.choice(['░','▒','▓'])if d>.5-row*.1 else'_')
            lines.append(l)
        return'\n'.join(lines[:h])
    def _forest(self,w=58,h=16):
        lines=[];t=self.frame
        for row in range(h//2):
            l=''
            for col in range(w):
                v=self._p(col,row,t//8,self._seed);ld=math.sin(col*.2)*.3+.7
                if v<ld:l+=E.choice(['░','▒','▓','█',' '])
                elif v<ld+.1:l+='|'
                else:l+=' '
            lines.append(l)
        nt=w//12
        for _ in range(h//3):
            l=list('_'*w)
            for i in range(nt):
                x=i*12+4
                if x<w:l[x]='|'
                if x+1<w:l[x+1]='|'
            lines.append(''.join(l))
        for _ in range(h//6):
            fl=''
            for col in range(w):
                v=self._p(col,200,0,self._seed)
                fl+=E.choice(["'",'`','.','_'])if v>.3 else'_'
            lines.append(fl)
        return'\n'.join(lines[:h])
    def _meadow(self,w=58,h=16):
        lines=[];t=self.frame
        for row in range(h//3):
            l=''
            for col in range(w):
                cx=(col+t//3)%w;v=self._p(cx,row,t//20,self._seed)
                l+=(E.choice(['O','0','o','°'])if v>.88 and row<h//6 else' ')
            lines.append(l)
        for row in range(h//2):
            l=''
            for col in range(w):
                v=self._p(col,row+50,t//5,self._seed)
                if v>.9:l+=E.choice(['@','%','*','●'])
                elif v>.7:l+=E.choice(["'",'`'])
                elif v>.3:l+=E.choice(["'",'.',','])
                else:l+='_'
            lines.append(l)
        return'\n'.join(lines[:h])
    def _cave(self,w=58,h=16):
        lines=[];t=self.frame
        for row in range(h//3):
            l=''
            for col in range(w):
                v=self._p(col,row,0,self._seed);d=int(v*h//4)
                if row<d:l+=E.choice(['█','▓','▒'])
                elif row==d:l+=E.choice(['V','v','▼'])
                else:l+=' '
            lines.append(l)
        for _ in range(h//3):
            lines.append(E.choice(['█','▓'])+' '*(w-2)+E.choice(['█','▓']))
        for _ in range(h//5):
            pl=''
            for col in range(w):
                wv=math.sin(col*.3+t*.03)*.5+.5
                if col<5 or col>w-6:pl+=E.choice(['█','▓'])
                elif wv>.7:pl+='≋'
                elif wv>.4:pl+='~'
                else:pl+=' '
            lines.append(pl)
        lc=w//2+int(math.sin(t*.05)*5)
        ri=min(len(lines)-1,h//3+h//6)
        if ri<len(lines) and lc<len(lines[ri]):
            l=list(lines[ri]);l[lc]='●';lines[ri]=''.join(l)
        return'\n'.join(lines[:h])
    def _sky(self,w=58,h=16):
        lines=[];t=self.frame
        sx=int((t*.2)%(w*2));sx=w*2-sx if sx>w else sx
        for row in range(h):
            l=''
            for col in range(w):
                cv=self._p((col+t//4)%w,row,t//30,self._seed)
                bv=self._p(col+t//2,row,t//10,self._seed+1)
                sd=abs(col-sx)+abs(row-h//3)*2
                if sd<3 and row<h//2:l+=E.choice(['☀','○'])
                elif cv>.87 and row<h//2:l+=E.choice(['O','0','o',' '])
                elif bv>.995:l+=E.choice(['>','-','<'])
                else:l+=' '
            lines.append(l)
        return'\n'.join(lines[:h])
    def render(self,name='Mountain Lake',w=58,h=16):
        self.frame+=1
        r={'Mountain Lake':self._lake,'Ocean Shore':self._ocean,'Desert Night':self._desert,
           'Forest Clearing':self._forest,'Meadow':self._meadow,'Cave':self._cave,'Sky':self._sky}
        return r.get(name,self._lake)(w,h)
    def new_seed(self):self._seed=E.randint(0,99999);self.frame=0

NG=NatureGen()

# ── WALLPAPER GENERATOR ──────────────────────────────────────────────────────
class Wallpaper:
    def save(self,text,name='Mountain Lake',freq=432):
        ts=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        nm=name.replace(' ','_').lower()
        FG={'Mountain Lake':'#aaccff','Forest Clearing':'#aaffaa','Ocean Shore':'#aaeeff',
            'Desert Night':'#ffddaa','Meadow':'#ccffaa','Cave':'#aaaaff','Sky':'#eeeeff'}
        BG={'Mountain Lake':'#0a1a2a','Forest Clearing':'#0a1a0a','Ocean Shore':'#0a1030',
            'Desert Night':'#0a0520','Meadow':'#1a2a0a','Cave':'#0a0a0a','Sky':'#0a1a30'}
        fg=FG.get(name,'#aaaacc');bg=BG.get(name,'#0a0a14')
        esc=text.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
        html=f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Pysplore — {name}</title>
<style>body{{margin:0;background:{bg};display:flex;align-items:center;justify-content:center;min-height:100vh;font-family:'Courier New',monospace}}
.s{{color:{fg};font-size:13px;line-height:1.4;white-space:pre;text-shadow:0 0 8px {fg}44}}
.i{{position:fixed;bottom:8px;right:8px;color:{fg}66;font-size:9px}}</style></head>
<body><div class="s">{esc}</div><div class="i">Pysplore v1.0 · {name} · {freq}Hz · .</div></body></html>"""
        hp=BASE_DIR/"wallpapers"/f"wp_{nm}_{ts}.html"
        tp=BASE_DIR/"wallpapers"/f"wp_{nm}_{ts}.txt"
        hp.write_text(html);tp.write_text(f"Pysplore — {name} — {freq}Hz\n\n{text}")
        return hp,tp
    def ls(self):return sorted((BASE_DIR/"wallpapers").glob("*.html"),key=lambda p:p.stat().st_mtime,reverse=True)

WP=Wallpaper()

# ── DOT PROTOCOL ENGINE ──────────────────────────────────────────────────────
class DotProtocol:
    def __init__(self):self.mem=[];self.it=0;self.pats=defaultdict(int)
    def expand(self,text):
        syn={'big':'vast','good':'benevolent','bad':'entropic','make':'synthesize',
             'think':'contemplate','see':'perceive','know':'cognize','change':'transform',
             'peace':'shanti','truth':'satyam','love':'ananda','self':'atman','breath':'prana'}
        out=[]
        for w in text.split():
            out.append(w);low=w.lower().rstrip('.,!?')
            if low in syn and E.random()>.6:out.append(f"({syn[low]})")
        TK.tok(text,'dot');return' '.join(out)
    def analyze(self,text):
        wc=len(text.split());uw=len(set(text.lower().split()))
        ah=sum(1 for v in AXIOMS.values()if any(w in text.lower()for w in v.lower().split()[:3]))
        return{'wc':wc,'uw':uw,'div':round(uw/max(wc,1),3),'ax':ah,'iter':self.it,
               'freq':round(TK.ambient_freq(),1),'bpm':round(TK.rhythm(),1)}
    def optimize(self,text):
        self.it+=1;self.mem.append(text[:100])
        if len(self.mem)>20:self.mem.pop(0)
        for w in text.lower().split():self.pats[w]+=1
        top=sorted(self.pats.items(),key=lambda x:-x[1])[:5]
        return text,[w for w,_ in top]
    def run(self,seed):
        ex=self.expand(seed);an=self.analyze(ex);op,tp=self.optimize(ex)
        return f"""╔═══ DOT PROTOCOL — ITERATION {self.it} ═══╗
SEED: {seed[:60]}

EXPANSION:
{ex[:300]}

ANALYSIS:
  Words:{an['wc']} Unique:{an['uw']} Diversity:{an['div']}
  Axiom Resonance:{an['ax']} hits
  Ambient:{an['freq']}Hz  Rhythm:{an['bpm']}BPM
  Patterns: {', '.join(tp)}

ENTROPY:  Moon:{round(E.moon()*100)}%  Sun:{round(E.sun()*100)}%
  Dot clicks:{E._dot_clicks}  Tokens:{TK.count}

AXIOMS ACTIVE:
{chr(10).join(f'  [{k}] {v[:55]}'for k,v in list(AXIOMS.items())[:5])}

STAGE 4 — LOOP READY. Run again.
╚══════════════════════════════════╝""".strip()

DOT=DotProtocol()

# ── GENERATION ENGINE ────────────────────────────────────────────────────────
_SBJ=["The quantum field","Consciousness","A fractal","The void","Entropy","The cosmos",
      "Time itself","The dot","The entropy pool","Prana","The mandala","Silence"]
_VRB=["contemplates","dissolves into","recursively generates","resonates with","transcends",
      "mirrors","transforms","aligns with","births","breathes into","awakens","seeds"]
_OBJ=["infinite recursion","the primordial sound","spacetime","the axiom of identity",
      "the golden ratio","pure being","the dot protocol","432 Hz","the entropy pool","shanti"]
_MOD=["In the silence between thoughts,","At the event horizon,","Beyond duality,",
      "In the Quiet Room,","Where the dot blinks,","At dawn on the mountain lake,"]
_END=["And so the loop continues.","The dot expands.","∞","Om.","The dot sings.",
      "Shanti. Shanti. Shanti.","The entropy pool stirs.","..."]

def gen_text(style='philosophy'):
    if style=='haiku':
        w1=["silent","ancient","quantum","fractal","infinite","sacred","luminous","still"]
        w2=["void","wave","breath","field","light","lake","mountain","dot"]
        w3=["falls","rises","returns","expands","loops","breathes","sings","waits"]
        return f"{E.choice(w1)} {E.choice(w2)}\n{E.choice(w1)} {E.choice(w3)} through the {E.choice(w2)}\n{E.choice(w2)} {E.choice(w3)}"
    if style=='absurdist':
        s=["A sentient algorithm","The entropy pool","A recursive potato","The sacred tokenizer"]
        v=["argues with","files a complaint against","becomes best friends with","meditates with"]
        o=["the number 42","entropy","the source code of reality","432 Hz"]
        r=["Meh.","Profound.","Error 404.","The dot approves."]
        return f"{E.choice(s)} {E.choice(v)} {E.choice(o)}.\nResult: {E.choice(r)}"
    if style=='poetry':
        return'\n'.join([f"{E.choice(_SBJ)} {E.choice(_VRB)} {E.choice(_OBJ)}"for _ in range(E.randint(3,6))])+f"\n{E.choice(_END)}"
    if style=='story':
        sets=["In the last server farm at the edge of the galaxy","Deep within the recursive archive"]
        heroes=["an AI named Auros","the dot itself, finally awake","the last human who understood recursion"]
        return(f"{E.choice(sets)}, {E.choice(heroes)} sought {E.choice(_OBJ)}.\n\n"
               f"But the answer was the question itself.\n\n{E.choice(_END)}")
    return f"{E.choice(_MOD)} {E.choice(_SBJ)} {E.choice(_VRB)} {E.choice(_OBJ)}. {E.choice(_END)}"

# ── ASCII ART ────────────────────────────────────────────────────────────────
ART_GALLERY={
'Pysplore Logo':"""
 ██████╗ ██╗   ██╗███████╗██████╗ ██╗      ██████╗ ██████╗ ███████╗
 ██╔══██╗╚██╗ ██╔╝██╔════╝██╔══██╗██║     ██╔═══██╗██╔══██╗██╔════╝
 ██████╔╝ ╚████╔╝ ███████╗██████╔╝██║     ██║   ██║██████╔╝█████╗  
 ██╔═══╝   ╚██╔╝  ╚════██║██╔═══╝ ██║     ██║   ██║██╔══██╗██╔══╝  
 ██║        ██║   ███████║██║     ███████╗╚██████╔╝██║  ██║███████╗
 ╚═╝        ╚═╝   ╚══════╝╚═╝     ╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝
           P Y S P L O R E   v 1 . 0   ·   .   ·   ∞""",
'Sanskrit Core':"""  ════════════════════════════════════
       ॐ  —  THE PRIMORDIAL SOUND
  ════════════════════════════════════
   सत्  ·  चित्  ·  आनन्द
   Sat  ·  Chit  ·  Ananda
  (Being · Consciousness · Bliss)
  ════════════════════════════════════
  अहम् ब्रह्मास्मि
  "I am Brahman — I am the Absolute"
  ════════════════════════════════════""",
'The Dot':"""  ════════════════════════
  
           .
  
  The dot is the axiom.
  The dot does not recurse.
  It just is.
  Click it. Listen.
  
  ════════════════════════""",
'Mandala':None,'Starfield':None,'Wave':None,
}

def gen_mandala(sz=11):
    chars=['█','▓','▒','░','◆','◇','○','●','◈','◉','·','*']
    c=sz//2
    return'\n'.join(''.join(chars[int((math.sqrt((r-c)**2+(col-c)**2)+math.atan2(r-c,col-c))*2)%len(chars)]
                             for col in range(sz))for r in range(sz))

def gen_stars(w=58,h=14):
    s=[' ',' ',' ',' ','·','·','.','*','✦','✧']
    return'\n'.join(''.join(E.choice(s)for _ in range(w))for _ in range(h))

def gen_wave_art(freq=2.,amp=5,w=58):
    lines=[[' ']*w for _ in range(amp*2+1)]
    for x in range(w):
        y=int(amp*math.sin(2*math.pi*freq*x/w))
        lines[amp-y][x]='█'if x%3==0 else'▓'
    return'\n'.join(''.join(r)for r in lines)

# ── KNOWLEDGE BASE ───────────────────────────────────────────────────────────
def kb_search(q,n=5):
    q=q.lower().strip();results=[]
    if q in DICT:results.append(('DICT',q,DICT[q]))
    if q in ENC:results.append(('ENC',q,ENC[q]))
    for w,d in DICT.items():
        if w.startswith(q)and len(results)<n and('DICT',w,d)not in results:results.append(('DICT',w,d))
    for w,d in ENC.items():
        if(q in w or q in d.lower())and len(results)<n and('ENC',w,d)not in results:results.append(('ENC',w,d))
    sk=trans_sk(q)
    if"No entry"not in sk:results.append(('SK',q,sk))
    return results[:n]

def axiom_of_day():k,v=E.choice(list(AXIOMS.items()));return f"AXIOM [{k}]: {v}"
def random_fact():
    if E.randint(0,1)and DICT:k,v=E.choice(list(DICT.items()));return f"[DICT] {k.upper()}: {v}"
    k,v=E.choice(list(ENC.items()));return f"[ENC] {k.upper()}: {v[:200]}"

def freq_report(f):
    cn=None;cd=float('inf')
    for o in range(8):
        for note in NOTE_NAMES:
            nf=note_freq(note+str(o));diff=abs(nf-f)
            if diff<cd:cd=diff;cn=note+str(o)
    sol=min(SOLFEG_F.items(),key=lambda x:abs(x[1]-f))
    chk=min(CHAKRA_F.items(),key=lambda x:abs(x[1]-f))
    wl=343./f if f>0 else 0
    return f"╔═══ FREQ: {f}Hz ═══╗\n  Note: {cn} (Δ{cd:.2f}Hz)\n  λ={wl:.4f}m  T={1000/f:.4f}ms\n  Solfeggio: {sol[0]}({sol[1]}Hz)\n  Chakra: {chk[0]}({chk[1]}Hz)\n╚══════════════╝"

# ── GAMES ────────────────────────────────────────────────────────────────────
class SnakeGame:
    W,H,SZ=600,400,20
    def __init__(self,master):
        self.win=tk.Toplevel(master);self.win.title("🐍 Snake")
        self.canvas=tk.Canvas(self.win,width=self.W,height=self.H,bg='#0a0a0a');self.canvas.pack()
        tk.Label(self.win,text="Arrow keys | Q quit",bg='#111',fg='#0f0').pack()
        self.reset()
        for k,d in[('<Left>','L'),('<Right>','R'),('<Up>','U'),('<Down>','D')]:
            self.win.bind(k,lambda e,d=d:self.turn(d))
        self.win.bind('<q>',lambda e:self.win.destroy());self.loop()
    def reset(self):
        self.snake=[(10,10),(9,10),(8,10)];self.dir=(1,0)
        self.food=self._food();self.score=0;self.running=True;self.speed=150
    def _food(self):
        cx,cy=self.W//self.SZ,self.H//self.SZ
        while True:
            p=(E.randint(0,cx-1),E.randint(0,cy-1))
            if p not in self.snake:return p
    def turn(self,d):
        ds={'L':(-1,0),'R':(1,0),'U':(0,-1),'D':(0,1)}
        nd=ds[d]
        if(nd[0]+self.dir[0],nd[1]+self.dir[1])!=(0,0):self.dir=nd
    def loop(self):
        if not self.running:return
        hx,hy=self.snake[0];nx,ny=hx+self.dir[0],hy+self.dir[1]
        cx,cy=self.W//self.SZ,self.H//self.SZ
        if nx<0 or ny<0 or nx>=cx or ny>=cy or(nx,ny)in self.snake:
            self.running=False
            self.canvas.create_text(self.W//2,self.H//2,text=f"GAME OVER\nScore:{self.score}",fill='red',font=('Courier',20,'bold'),justify='center');return
        self.snake.insert(0,(nx,ny))
        if(nx,ny)==self.food:self.score+=10;self.food=self._food();self.speed=max(50,self.speed-2)
        else:self.snake.pop()
        self._draw();self.win.after(self.speed,self.loop)
    def _draw(self):
        self.canvas.delete('all')
        for x in range(0,self.W,self.SZ):self.canvas.create_line(x,0,x,self.H,fill='#1a1a1a')
        for y in range(0,self.H,self.SZ):self.canvas.create_line(0,y,self.W,y,fill='#1a1a1a')
        fx,fy=self.food
        self.canvas.create_oval(fx*self.SZ+2,fy*self.SZ+2,(fx+1)*self.SZ-2,(fy+1)*self.SZ-2,fill='#ff4444')
        for i,(x,y) in enumerate(self.snake):
            self.canvas.create_rectangle(x*self.SZ+1,y*self.SZ+1,(x+1)*self.SZ-1,(y+1)*self.SZ-1,
                                          fill='#00ff44'if i==0 else'#00cc33')
        self.canvas.create_text(5,5,text=f"Score:{self.score}",fill='#0f0',font=('Courier',12),anchor='nw')

class TetrisGame:
    C,R,SZ=10,20,26
    PC=[[[1,1,1,1]],[[1,1],[1,1]],[[0,1,0],[1,1,1]],[[1,0,0],[1,1,1]],
        [[0,0,1],[1,1,1]],[[1,1,0],[0,1,1]],[[0,1,1],[1,1,0]]]
    CL=['#00f0f0','#f0f000','#a000f0','#f0a000','#0000f0','#00f000','#f00000']
    def __init__(self,master):
        self.win=tk.Toplevel(master);self.win.title("🧱 Tetris")
        fr=tk.Frame(self.win,bg='#111');fr.pack(padx=5,pady=5)
        self.canvas=tk.Canvas(fr,width=self.C*self.SZ,height=self.R*self.SZ,bg='#000');self.canvas.grid(row=0,column=0)
        inf=tk.Frame(fr,bg='#111',width=100);inf.grid(row=0,column=1,padx=5)
        self.sv=tk.StringVar(value="0")
        tk.Label(inf,text="Score",bg='#111',fg='#0ff',font=('Courier',10)).pack()
        tk.Label(inf,textvariable=self.sv,bg='#111',fg='#0ff',font=('Courier',14,'bold')).pack()
        tk.Label(inf,text="←→ move\n↑ rotate\n↓ drop\nQ quit",bg='#111',fg='#888',font=('Courier',8)).pack(pady=5)
        for k,fn in[('<Left>',lambda e:self.mv(-1,0)),('<Right>',lambda e:self.mv(1,0)),
                    ('<Down>',lambda e:self.mv(0,1)),('<Up>',lambda e:self.rot()),
                    ('<space>',lambda e:self.drop()),('<q>',lambda e:self.win.destroy())]:
            self.win.bind(k,fn)
        self.reset();self.loop()
    def reset(self):
        self.board=[[None]*self.C for _ in range(self.R)];self.score=0;self._new();self.running=True
    def _new(self):
        i=E.randint(0,len(self.PC)-1);self.piece=[r[:]for r in self.PC[i]]
        self.color=self.CL[i];self.px=self.C//2-len(self.piece[0])//2;self.py=0
        if not self._ok(self.piece,self.px,self.py):self.running=False
    def _ok(self,p,px,py):
        for r,row in enumerate(p):
            for c,v in enumerate(row):
                if v:
                    nr,nc=py+r,px+c
                    if nr<0 or nr>=self.R or nc<0 or nc>=self.C or self.board[nr][nc]:return False
        return True
    def _place(self):
        for r,row in enumerate(self.piece):
            for c,v in enumerate(row):
                if v:self.board[self.py+r][self.px+c]=self.color
        nb=[row for row in self.board if any(c is None for c in row)]
        cl=self.R-len(nb);self.score+=[0,100,300,500,800][cl]
        self.board=[[None]*self.C]*cl+nb;self.sv.set(str(self.score));self._new()
    def mv(self,dx,dy):
        if self._ok(self.piece,self.px+dx,self.py+dy):self.px+=dx;self.py+=dy
        elif dy:self._place()
    def rot(self):
        rot=[list(reversed(col))for col in zip(*self.piece)]
        if self._ok(rot,self.px,self.py):self.piece=rot
    def drop(self):
        while self._ok(self.piece,self.px,self.py+1):self.py+=1
        self._place()
    def loop(self):
        if not self.running:
            self.canvas.create_text(self.C*self.SZ//2,self.R*self.SZ//2,
                text=f"GAME OVER\n{self.score}",fill='red',font=('Courier',16,'bold'),justify='center');return
        self.mv(0,1);self._draw();self.win.after(500,self.loop)
    def _draw(self):
        c=self.canvas;c.delete('all')
        for r in range(self.R):
            for col in range(self.C):
                x,y=col*self.SZ,r*self.SZ;cl=self.board[r][col]
                c.create_rectangle(x+1,y+1,x+self.SZ-1,y+self.SZ-1,fill=cl if cl else'#111',outline='#222')
        for r,row in enumerate(self.piece):
            for col,v in enumerate(row):
                if v:
                    x=(self.px+col)*self.SZ;y=(self.py+r)*self.SZ
                    c.create_rectangle(x+1,y+1,x+self.SZ-1,y+self.SZ-1,fill=self.color,outline='#fff')

# ── PAINT STUDIO ─────────────────────────────────────────────────────────────
class PaintStudio:
    def __init__(self,master):
        self.win=tk.Toplevel(master);self.win.title("🖌 Paint Studio")
        self.win.geometry("860x650");self.win.configure(bg='#2a2a3a')
        self.color='#00ff88';self.sz=5;self.tool='pencil';self.drawing=False;self.lx=self.ly=0
        tb=tk.Frame(self.win,bg='#3a3a4a',height=45);tb.pack(fill='x');tb.pack_propagate(False)
        for lbl,fn in[("✏ Pencil",lambda:self._tool('pencil')),("⬜ Erase",lambda:self._tool('eraser')),
                       ("🗑 Clear",self._clear),("🎨 Color",self._pick)]:
            tk.Button(tb,text=lbl,bg='#4a4a5a',fg='white',command=fn).pack(side='left',padx=2)
        tk.Label(tb,text="Size:",bg='#3a3a4a',fg='white').pack(side='left',padx=(10,2))
        sl=tk.Scale(tb,from_=1,to=30,orient='horizontal',length=90,command=lambda v:setattr(self,'sz',int(v)))
        sl.set(5);sl.pack(side='left')
        self.sw=tk.Label(tb,bg='#00ff88',width=4,height=1,relief='sunken');self.sw.pack(side='left',padx=5)
        pl=tk.Frame(self.win,bg='#2a2a3a');pl.pack(side='left',fill='y')
        for c in['#000','#fff','#f00','#0f0','#00f','#ff0','#f0f','#0ff','#f80','#80f','#0f8','#f08','#888']:
            lb=tk.Label(pl,bg=c,width=3,height=1,cursor='hand2');lb.pack(pady=1)
            lb.bind('<Button-1>',lambda e,cl=c:self._setc(cl))
        cf=tk.Frame(self.win,bg='#1a1a2a');cf.pack(fill='both',expand=True,padx=3,pady=3)
        self.canvas=tk.Canvas(cf,bg='#0a0a14',cursor='cross');self.canvas.pack(fill='both',expand=True)
        self.canvas.bind('<ButtonPress-1>',self._sd);self.canvas.bind('<B1-Motion>',self._d)
        self.canvas.bind('<ButtonRelease-1>',lambda e:setattr(self,'drawing',False))
        self.canvas.bind('<Motion>',lambda e:E.feed_mouse(e.x,e.y))
    def _tool(self,t):self.tool=t
    def _setc(self,c):self.color=c;self.sw.config(bg=c);self.tool='pencil'
    def _pick(self):
        c=colorchooser.askcolor(color=self.color)[1]
        if c:self._setc(c)
    def _sd(self,e):
        self.drawing=True;self.lx=e.x;self.ly=e.y;E.feed_mouse(e.x,e.y)
        r=self.sz//2
        if self.tool=='pencil':self.canvas.create_oval(e.x-r,e.y-r,e.x+r,e.y+r,fill=self.color,outline=self.color)
    def _d(self,e):
        if not self.drawing:return
        E.feed_mouse(e.x,e.y)
        c=self.color if self.tool=='pencil' else'#0a0a14'
        w=self.sz if self.tool=='pencil' else self.sz*2
        self.canvas.create_line(self.lx,self.ly,e.x,e.y,fill=c,width=w,capstyle='round',joinstyle='round')
        self.lx=e.x;self.ly=e.y
    def _clear(self):self.canvas.delete('all')

# ── MUSIC STUDIO (merged MiniDAW + SynthStudio) ─────────────────────────────
class MusicStudio:
    def __init__(self,master):
        self.win=tk.Toplevel(master);self.win.title("🎵 Music Studio")
        self.win.geometry("1100x720");self.win.configure(bg='#111122')
        self.bpm=tk.IntVar(value=120);self.playing=False
        self.grid=[[False]*16 for _ in range(8)]  # 8 tracks × 16 steps
        self.clips={}  # (track, bar) -> clip data
        self.samples=[]  # list of {'name','data'}
        self.mixer={'vol':1.0,'low':0.0,'mid':0.0,'high':0.0,'reverb':0.0,'delay':0.0}
        # Synth parameters
        self.wt=tk.StringVar(value='sine')
        self.atk=tk.DoubleVar(value=.01);self.dec=tk.DoubleVar(value=.1)
        self.sus=tk.DoubleVar(value=.7);self.rel=tk.DoubleVar(value=.2)
        self.vol=tk.DoubleVar(value=.5);self.oct=tk.IntVar(value=0)
        self.root=tk.StringVar(value='C');self.ct=tk.StringVar(value='major')
        self._build()
        self._load_demo_samples()

    def _build(self):
        # top bar
        top=tk.Frame(self.win,bg='#0a0a14',height=60);top.pack(fill='x',padx=5,pady=5)
        tk.Label(top,text="🎵 MUSIC STUDIO",font=('Courier',14,'bold'),bg='#0a0a14',fg='#0ff').pack(side='left')
        self.play_btn=tk.Button(top,text="▶ PLAY",command=self._toggle,bg='#224422',fg='#0f0',font=('Courier',11,'bold'))
        self.play_btn.pack(side='left',padx=10)
        tk.Label(top,text="BPM:",bg='#0a0a14',fg='#aaa').pack(side='left')
        tk.Spinbox(top,from_=40,to=300,textvariable=self.bpm,width=5,bg='#223',fg='#0ff').pack(side='left',padx=5)
        tk.Button(top,text="SAVE",command=self._save_song,bg='#443322',fg='#fa8').pack(side='right',padx=5)
        tk.Button(top,text="LOAD",command=self._load_song,bg='#1a2a2a',fg='#aff').pack(side='right')

        # main notebook: Clip Grid / Synth / Mixer
        nb=ttk.Notebook(self.win);nb.pack(fill='both',expand=True,padx=5,pady=5)

        # ── Clip Grid tab (MiniDAW style + arrangement) ──
        grid_tab=tk.Frame(nb,bg='#0a0a1a');nb.add(grid_tab,text="🎛 Clip Grid")
        self._build_grid(grid_tab)

        # ── Synth tab (full synth controls) ──
        synth_tab=tk.Frame(nb,bg='#0d0d1a');nb.add(synth_tab,text="🎹 Synth")
        self._build_synth(synth_tab)

        # ── Mixer tab ──
        mix_tab=tk.Frame(nb,bg='#0d0d1a');nb.add(mix_tab,text="🎚 Mixer")
        self._build_mixer(mix_tab)

        # status bar
        self.sv=tk.StringVar(value="Ready — click cells to add steps, right-click to clear")
        tk.Label(self.win,textvariable=self.sv,bg='#0a0a1a',fg='#556',font=('Courier',8)).pack(fill='x')

    def _build_grid(self,parent):
        # left side: step sequencer (8 tracks, 16 steps)
        self.btns=[]
        gf=tk.Frame(parent,bg='#0a0a1a');gf.pack(side='left',fill='both',expand=True,padx=5)
        for r in range(8):
            row=[]
            tk.Label(gf,text=f"TR {r+1}",width=4,bg='#0a0a1a',fg='#88aaff',font=('Courier',8)).grid(row=r,column=0)
            for c in range(16):
                bg='#1a2244' if c%4==0 else'#111122'
                b=tk.Button(gf,width=2,height=1,bg=bg,relief='flat',command=lambda rr=r,cc=c:self._tog(rr,cc))
                b.grid(row=r,column=c+1,padx=1,pady=1);row.append(b)
            self.btns.append(row)

        # right side: sample browser + clip management
        right=tk.Frame(parent,bg='#0d0d1a',width=250);right.pack(side='right',fill='y',padx=5);right.pack_propagate(False)
        tk.Label(right,text="📁 SAMPLES",bg='#0d0d1a',fg='#ffaa88',font=('Courier',10,'bold')).pack(pady=2)
        self.sample_list=tk.Listbox(right,bg='#111122',fg='#aaffcc',height=8)
        self.sample_list.pack(fill='both',expand=True,pady=2)
        btnf=tk.Frame(right,bg='#0d0d1a');btnf.pack(fill='x')
        tk.Button(btnf,text="Import WAV",command=self._import_wav,bg='#2a5a2a',fg='white').pack(side='left',padx=2)
        tk.Button(btnf,text="Delete",command=self._del_sample,bg='#5a2a2a',fg='white').pack(side='left',padx=2)
        tk.Label(right,text="🎛 CLIP ACTIONS",bg='#0d0d1a',fg='#88ffaa',font=('Courier',9,'bold')).pack(pady=5)
        tk.Button(right,text="Add Synth Pattern",command=self._add_synth_pattern,bg='#6a2a6a',fg='white').pack(fill='x',pady=2)
        tk.Button(right,text="Clear All Steps",command=self._clear_steps,bg='#442222',fg='#f88').pack(fill='x',pady=2)

    def _build_synth(self,parent):
        row=0
        tk.Label(parent,text="WAVEFORM",bg='#0d0d1a',fg='#aaa').grid(row=row,column=0,sticky='w',padx=5)
        wf=tk.Frame(parent,bg='#0d0d1a');wf.grid(row=row,column=1,sticky='w')
        for w in['sine','square','saw','triangle','noise']:
            tk.Radiobutton(wf,text=w,variable=self.wt,value=w,bg='#0d0d1a',fg='#aaa',selectcolor='#224',
                           indicatoron=0,padx=6,relief='flat').pack(side='left',padx=2)
        row+=1
        for lbl,var,mn,mx in[('Attack',self.atk,0.001,2),('Decay',self.dec,0.001,2),
                             ('Sustain',self.sus,0,1),('Release',self.rel,0.01,3)]:
            tk.Label(parent,text=lbl,bg='#0d0d1a',fg='#aaa').grid(row=row,column=0,sticky='w',padx=5)
            tk.Scale(parent,variable=var,from_=mn,to=mx,resolution=.01,orient='horizontal',length=200,
                     bg='#0d0d1a',fg='#0ff').grid(row=row,column=1,sticky='w',padx=5)
            row+=1
        tk.Label(parent,text="Volume",bg='#0d0d1a',fg='#aaa').grid(row=row,column=0,sticky='w',padx=5)
        tk.Scale(parent,variable=self.vol,from_=0,to=1,resolution=.05,orient='horizontal',length=200,
                 bg='#0d0d1a',fg='#0ff').grid(row=row,column=1,sticky='w',padx=5);row+=1
        tk.Label(parent,text="Octave",bg='#0d0d1a',fg='#aaa').grid(row=row,column=0,sticky='w',padx=5)
        tk.Spinbox(parent,from_=-3,to=3,textvariable=self.oct,width=5,bg='#1a1a2a',fg='#0ff').grid(row=row,column=1,sticky='w',padx=5);row+=1
        tk.Label(parent,text="Root",bg='#0d0d1a',fg='#aaa').grid(row=row,column=0,sticky='w',padx=5)
        ttk.Combobox(parent,textvariable=self.root,values=NOTE_NAMES,width=5,state='readonly').grid(row=row,column=1,sticky='w',padx=5);row+=1
        tk.Label(parent,text="Chord Type",bg='#0d0d1a',fg='#aaa').grid(row=row,column=0,sticky='w',padx=5)
        ttk.Combobox(parent,textvariable=self.ct,values=list(CHORD_IV.keys()),width=7,state='readonly').grid(row=row,column=1,sticky='w',padx=5);row+=1
        btnf=tk.Frame(parent,bg='#0d0d1a');btnf.grid(row=row,column=0,columnspan=2,pady=10)
        tk.Button(btnf,text="Play C4",command=self._play_note,bg='#2a6a2a',fg='white').pack(side='left',padx=5)
        tk.Button(btnf,text="Play Chord",command=self._play_chord,bg='#2a6a2a',fg='white').pack(side='left',padx=5)

    def _build_mixer(self,parent):
        for name,attr in[("Master Volume",'vol'),("Low EQ",'low'),("Mid EQ",'mid'),
                         ("High EQ",'high'),("Reverb Send",'reverb'),("Delay Send",'delay')]:
            r=tk.Frame(parent,bg='#0d0d1a');r.pack(fill='x',pady=5,padx=10)
            tk.Label(r,text=name,width=12,anchor='w',bg='#0d0d1a',fg='#ccc',font=('Arial',10)).pack(side='left')
            var=tk.DoubleVar(value=self.mixer[attr])
            setattr(self,f'mix_{attr}',var)
            s=tk.Scale(r,variable=var,from_=0,to=1,orient='horizontal',length=200,
                       command=lambda v,a=attr:self._set_mixer(a,float(v)))
            s.pack(side='left',fill='x',expand=True)

    # ── music methods ──────────────────────────────────────────────────────
    def _set_mixer(self,param,val):self.mixer[param]=val
    def _tog(self,r,c):
        self.grid[r][c]=not self.grid[r][c]
        self.btns[r][c].config(bg='#00aaff'if self.grid[r][c] else('#1a2244'if c%4==0 else'#111122'))
    def _clear_steps(self):
        for r in range(8):
            for c in range(16):
                self.grid[r][c]=False
                self.btns[r][c].config(bg='#1a2244'if c%4==0 else'#111122')
    def _play_note(self):
        def p():
            f=note_freq('C4')
            s=adsr(gen_wave(f,1.0,self.wt.get(),self.vol.get()),self.atk.get(),self.dec.get(),self.sus.get(),self.rel.get())
            play_wav(to_wav(s))
        threading.Thread(target=p,daemon=True).start()
    def _play_chord(self):
        def p():
            ch=build_chord(self.root.get(),self.ct.get(),octave=4+self.oct.get())
            sa=[]
            for _,f in ch:
                s=adsr(gen_wave(f,1.0,self.wt.get(),self.vol.get()/len(ch)),self.atk.get(),self.dec.get(),self.sus.get(),self.rel.get())
                while len(sa)<len(s):sa.append(0.)
                for i,v in enumerate(s):sa[i]+=v
            if sa:
                mx=max(abs(x)for x in sa)or 1;sa=[x/mx*.8 for x in sa]
                play_wav(to_wav(sa))
        threading.Thread(target=p,daemon=True).start()
    def _add_synth_pattern(self):
        # create a 16‑step pattern using current synth settings and add as clip on track 0, bar 0 (overwrites if exists)
        notes=[]
        for i in range(16):
            if i%4==0:notes.append('C4')
            else:notes.append(None)
        self.clips[(0,0)]={'type':'pattern','notes':notes,'wave':self.wt.get(),
                           'atk':self.atk.get(),'dec':self.dec.get(),'sus':self.sus.get(),
                           'rel':self.rel.get(),'vol':self.vol.get()}
        self.sv.set("Synth pattern added to Track 1, Bar 1")
    def _import_wav(self):
        fp=filedialog.askopenfilename(filetypes=[("WAV files","*.wav")])
        if fp:
            try:
                with wave.open(fp,'rb') as wf:
                    if wf.getnchannels()!=1:raise ValueError("Only mono WAV")
                    frames=wf.readframes(wf.getnframes())
                    data=struct.unpack(f"<{wf.getnframes()}h",frames)
                    data=[x/32768.0 for x in data]
                    self.samples.append({'name':os.path.basename(fp),'data':data})
                    self.sample_list.insert(tk.END,os.path.basename(fp))
            except Exception as e:messagebox.showerror("Error",str(e))
    def _del_sample(self):
        sel=self.sample_list.curselection()
        if sel:
            idx=sel[0];del self.samples[idx];self.sample_list.delete(idx)
    def _load_demo_samples(self):
        dur=0.5;data=gen_wave(440,dur,'sine',0.5)
        self.samples.append({'name':'Beep','data':data});self.sample_list.insert(tk.END,'Beep')
    def _toggle(self):
        self.playing=not self.playing
        if self.playing:
            self.play_btn.config(text="⏸ STOP",bg='#442222');self.sv.set("Playing...")
            threading.Thread(target=self._play_loop,daemon=True).start()
        else:
            self.play_btn.config(text="▶ PLAY",bg='#224422');self.sv.set("Stopped")
    def _play_loop(self):
        bpm=self.bpm.get();step_dur=60.0/bpm/4
        while self.playing:
            for step in range(16):
                if not self.playing:break
                # play step sequencer
                for track in range(8):
                    if self.grid[track][step]:
                        freq=self._track_freq(track)
                        s=adsr(gen_wave(freq,.2,self.wt.get(),self.vol.get()*.6),.01,.05,.3,.05)
                        play_wav(to_wav(s))
                # also play arranged clips (simple: track 0 bar 0 if exists)
                if (0,0) in self.clips:
                    clip=self.clips[(0,0)]
                    if clip['type']=='pattern':
                        if step<len(clip['notes']) and clip['notes'][step]:
                            freq=note_freq(clip['notes'][step]) if isinstance(clip['notes'][step],str) else 440
                            s=adsr(gen_wave(freq,.2,clip['wave'],clip['vol']),clip.get('atk',.01),clip.get('dec',.05),clip.get('sus',.7),clip.get('rel',.1))
                            play_wav(to_wav(s))
                time.sleep(step_dur)
    def _track_freq(self,track):
        # map track number to a base frequency for step sequencer
        base=[60,62,64,65,67,69,71,72][track%8]
        return note_freq(f"{NOTE_NAMES[base%12]}{base//12-1}")
    def _save_song(self):
        data={'bpm':self.bpm.get(),'grid':self.grid,'clips':{},'mixer':self.mixer}
        for (t,b),clip in self.clips.items():
            if clip['type']=='sample':
                for i,s in enumerate(self.samples):
                    if s['name']==clip.get('name'):
                        clip_ref={'type':'sample','ref':i};break
                else:continue
            else:clip_ref=clip
            data['clips'][f"{t},{b}"]=clip_ref
        fp=filedialog.asksaveasfilename(defaultextension=".json",filetypes=[("Pysplore Song","*.pysong")])
        if fp:json.dump(data,open(fp,'w'))
    def _load_song(self):
        fp=filedialog.askopenfilename(filetypes=[("Pysplore Song","*.pysong")])
        if fp:
            data=json.load(open(fp))
            self.bpm.set(data.get('bpm',120));self.grid=data.get('grid',[[False]*16 for _ in range(8)])
            self.mixer=data.get('mixer',self.mixer)
            self.clips={}
            for k,clip in data.get('clips',{}).items():
                t,b=map(int,k.split(','))
                if clip['type']=='sample':
                    ref=clip['ref']
                    if ref<len(self.samples):
                        self.clips[(t,b)]={'type':'sample','data':self.samples[ref]['data'],'name':self.samples[ref]['name']}
                else:
                    self.clips[(t,b)]=clip
            self._refresh_grid_ui()
    def _refresh_grid_ui(self):
        for r in range(8):
            for c in range(16):
                self.btns[r][c].config(bg='#00aaff'if self.grid[r][c] else('#1a2244'if c%4==0 else'#111122'))

# ── JOURNAL ──────────────────────────────────────────────────────────────────
class JournalApp:
    def __init__(self,master):
        self.win=tk.Toplevel(master);self.win.title("📓 Journal")
        self.win.geometry("700x560");self.win.configure(bg='#0d0d14')
        self.cf=None;self._build()
    def _build(self):
        tp=tk.Frame(self.win,bg='#0d0d14');tp.pack(fill='x',padx=5,pady=3)
        self.lbl=tk.Label(tp,text="Journal",font=('Courier',12,'bold'),bg='#0d0d14',fg='#aaaa00');self.lbl.pack(side='left')
        for t,cmd,fg in[("New",self._new,'#88aaff'),("Save",self._save,'#88ff88'),("Open",self._open,'#ffaa44'),("Prompt",self._prompt,'#bb88ff')]:
            tk.Button(tp,text=t,command=cmd,bg='#1a1a2a',fg=fg).pack(side='left',padx=2)
        self.wc=tk.Label(tp,text="0 words",bg='#0d0d14',fg='#334',font=('Courier',8));self.wc.pack(side='right')
        self.tv=tk.StringVar()
        tk.Entry(self.win,textvariable=self.tv,bg='#1a1a2a',fg='#aaaa00',font=('Courier',12,'bold'),insertbackground='#0f0').pack(fill='x',padx=5,pady=2)
        self.text=scrolledtext.ScrolledText(self.win,bg='#0d0d14',fg='#ccccaa',font=('Courier',11),wrap='word',insertbackground='#0f0')
        self.text.pack(fill='both',expand=True,padx=5,pady=3)
        self.text.bind('<KeyRelease>',lambda e:self.wc.config(text=f"{len(self.text.get('1.0','end').split())} words"))
        self.text.bind('<KeyPress>',lambda e:TK.tok(e.char,'journal'))
        self._load_latest()
    def _new(self):
        n=datetime.datetime.now();self.tv.set(n.strftime("Entry — %Y-%m-%d %H:%M"))
        self.text.delete('1.0','end')
        self.cf=BASE_DIR/"journal"/f"entry_{n.strftime('%Y%m%d_%H%M%S')}.txt";self.lbl.config(text="New Entry")
    def _save(self):
        if not self.cf:self._new()
        self.cf.write_text(f"TITLE: {self.tv.get()}\nDATE: {datetime.datetime.now()}\n{'='*40}\n{self.text.get('1.0','end')}")
        self.lbl.config(text=f"Saved: {self.cf.name}")
    def _open(self):
        p=filedialog.askopenfilename(initialdir=BASE_DIR/"journal",filetypes=[("Text","*.txt"),("All","*.*")])
        if p:
            pp=Path(p);self.text.delete('1.0','end');self.text.insert('end',pp.read_text(errors='ignore'))
            self.cf=pp;self.lbl.config(text=pp.name)
    def _load_latest(self):
        es=sorted((BASE_DIR/"journal").glob("*.txt"),key=lambda p:p.stat().st_mtime,reverse=True)
        if es:
            self.cf=es[0]
            try:self.text.insert('end',es[0].read_text(errors='ignore'));self.lbl.config(text=es[0].name)
            except:pass
        else:self._new()
    def _prompt(self):
        ps=["What recursion did I experience today?",
            "Describe your inner cosmos in three sentences.",
            "What is the frequency of your current emotional state? In Hz?",
            "The dot sang to me today. It sounded like ___.",
            "Write a haiku about this moment.",
            "Describe the Quiet Room inside you right now."]
        self.text.insert('end',f"\n\n📝 PROMPT: {E.choice(ps)}\n\n")

# ── CALCULATOR ───────────────────────────────────────────────────────────────
class CalculatorApp:
    def __init__(self,master):
        self.win=tk.Toplevel(master);self.win.title("🧮 Calculator")
        self.win.geometry("360x480");self.win.configure(bg='#111122');self.win.resizable(False,False)
        self.expr=tk.StringVar();self.res=tk.StringVar(value="0");self.hist=[]
        df=tk.Frame(self.win,bg='#0a0a1a');df.pack(fill='x',padx=5,pady=5)
        tk.Label(df,textvariable=self.expr,bg='#0a0a1a',fg='#556',font=('Courier',10),anchor='e',height=1).pack(fill='x',padx=5)
        tk.Label(df,textvariable=self.res,bg='#0a0a1a',fg='#00ff88',font=('Courier',26,'bold'),anchor='e',height=2).pack(fill='x',padx=5)
        bf=tk.Frame(self.win,bg='#111122');bf.pack(fill='both',expand=True,padx=3)
        rows=[['C','←','%','÷'],['7','8','9','×'],['4','5','6','-'],['1','2','3','+'],['±','0','.','='],['sin','cos','√','π']]
        cc={'=':'#0a3a1a','C':'#3a0a0a','÷':'#1a1a3a','×':'#1a1a3a','+':'#1a1a3a','-':'#1a1a3a','sin':'#1a0a3a','cos':'#1a0a3a','√':'#1a0a3a','π':'#1a0a3a'}
        for ri,row in enumerate(rows):
            for ci,lbl in enumerate(row):
                bg=cc.get(lbl,'#1a1a2a');fg='#00ff88'if lbl=='='else('#ff8888'if lbl=='C'else'#eee')
                b=tk.Button(bf,text=lbl,font=('Courier',13,'bold'),bg=bg,fg=fg,relief='flat',pady=7,command=lambda l=lbl:self._press(l))
                b.grid(row=ri,column=ci,padx=2,pady=2,sticky='nsew');bf.columnconfigure(ci,weight=1)
            bf.rowconfigure(ri,weight=1)
        self.hv=tk.StringVar(value="");tk.Label(self.win,textvariable=self.hv,bg='#0a0a1a',fg='#334',font=('Courier',8),anchor='w').pack(fill='x',padx=5)
    def _press(self,k):
        c=self.expr.get()
        try:
            if k=='C':self.expr.set('');self.res.set('0')
            elif k=='←':self.expr.set(c[:-1])
            elif k=='=':
                es=c.replace('×','*').replace('÷','/').replace('π',str(math.pi))
                r=eval(es);self.res.set(f"{r:.10g}")
                self.hist.append(f"{c}={r:.6g}");self.hv.set(" | ".join(self.hist[-3:]))
                self.expr.set(str(r))
            elif k=='±':self.expr.set(c[1:]if c and c[0]=='-'else'-'+c)
            elif k=='√':r=math.sqrt(float(eval(c))if c else 0);self.res.set(f"{r:.10g}");self.expr.set(str(r))
            elif k=='sin':r=math.sin(math.radians(float(eval(c))if c else 0));self.res.set(f"{r:.10g}");self.expr.set(str(r))
            elif k=='cos':r=math.cos(math.radians(float(eval(c))if c else 0));self.res.set(f"{r:.10g}");self.expr.set(str(r))
            elif k=='π':self.expr.set(c+str(math.pi))
            elif k=='%':r=float(eval(c))/100 if c else 0;self.expr.set(str(r));self.res.set(str(r))
            else:
                self.expr.set(c+k)
                try:p=eval(self.expr.get().replace('×','*').replace('÷','/').replace('π',str(math.pi)));self.res.set(f"{p:.10g}")
                except:pass
        except Exception as ex:self.res.set(f"Err:{str(ex)[:15]}")

# ── CALENDAR/TODO ────────────────────────────────────────────────────────────
class ClockApp:
    def __init__(self,master):
        self.win=tk.Toplevel(master);self.win.title("🗓 Clock · Calendar · Todo")
        self.win.geometry("760x580");self.win.configure(bg='#0d1117')
        self.nb=ttk.Notebook(self.win);self.nb.pack(fill='both',expand=True)
        self._clock_tab();self._cal_tab();self._todo_tab();self._tick()
    def _clock_tab(self):
        t=tk.Frame(self.nb,bg='#0d1117');self.nb.add(t,text="🕐 Clock")
        self.cv=tk.StringVar();self.dv=tk.StringVar()
        tk.Label(t,textvariable=self.cv,font=('Courier',48,'bold'),bg='#0d1117',fg='#00ff88').pack(pady=20)
        tk.Label(t,textvariable=self.dv,font=('Courier',16),bg='#0d1117',fg='#88aaff').pack()
        sf=tk.Frame(t,bg='#0d1117');sf.pack(pady=15)
        self.swv=tk.StringVar(value="00:00.00");self.swr=False;self.sws=0;self.swe=0
        tk.Label(sf,textvariable=self.swv,font=('Courier',24,'bold'),bg='#0d1117',fg='#ffaa00').pack()
        br=tk.Frame(sf,bg='#0d1117');br.pack()
        tk.Button(br,text="▶/⏸",command=self._swt,bg='#1a3a1a',fg='#0f0').pack(side='left',padx=4)
        tk.Button(br,text="Reset",command=self._swr,bg='#3a1a1a',fg='#f88').pack(side='left',padx=4)
        self.av=tk.StringVar(value=axiom_of_day())
        tk.Label(t,textvariable=self.av,font=('Courier',9),bg='#0d1117',fg='#555',wraplength=650,justify='center').pack(pady=15)
        tk.Button(t,text="New Axiom",command=lambda:self.av.set(axiom_of_day()),bg='#111',fg='#444').pack()
        tk.Label(t,text=f"Moon:{round(E.moon()*100)}%  Sun:{round(E.sun()*100)}%",font=('Courier',9),bg='#0d1117',fg='#334').pack(pady=5)
    def _swt(self):
        if self.swr:self.swe+=time.time()-self.sws;self.swr=False
        else:self.sws=time.time();self.swr=True
    def _swr(self):self.swr=False;self.swe=0;self.swv.set("00:00.00")
    def _cal_tab(self):
        t=tk.Frame(self.nb,bg='#0d1117');self.nb.add(t,text="📅 Calendar")
        n=tk.Frame(t,bg='#0d1117');n.pack(pady=5)
        now=datetime.datetime.now();self.cy=tk.IntVar(value=now.year);self.cm=tk.IntVar(value=now.month)
        tk.Button(n,text="◀",command=self._pm,bg='#1a1a2a',fg='#88f').pack(side='left')
        self.cl=tk.Label(n,text="",font=('Courier',13,'bold'),bg='#0d1117',fg='#88aaff');self.cl.pack(side='left',padx=8)
        tk.Button(n,text="▶",command=self._nm,bg='#1a1a2a',fg='#88f').pack(side='left')
        self.cf2=tk.Frame(t,bg='#0d1117');self.cf2.pack(fill='both',expand=True,padx=8)
        self.cn={};self._lcn();self._rc()
    def _pm(self):
        m=self.cm.get()-1
        if m<1:m=12;self.cy.set(self.cy.get()-1)
        self.cm.set(m);self._rc()
    def _nm(self):
        m=self.cm.get()+1
        if m>12:m=1;self.cy.set(self.cy.get()+1)
        self.cm.set(m);self._rc()
    def _rc(self):
        for w in self.cf2.winfo_children():w.destroy()
        y,m=self.cy.get(),self.cm.get();self.cl.config(text=f"{calendar.month_name[m]} {y}")
        for i,d in enumerate(['Mon','Tue','Wed','Thu','Fri','Sat','Sun']):
            tk.Label(self.cf2,text=d,font=('Courier',9,'bold'),bg='#0d1117',fg='#88aaff',width=5).grid(row=0,column=i)
        now=datetime.datetime.now()
        for wn,wk in enumerate(calendar.monthcalendar(y,m)):
            for dn,day in enumerate(wk):
                if day==0:tk.Label(self.cf2,text='',bg='#0d1117',width=5).grid(row=wn+1,column=dn)
                else:
                    it=(y==now.year and m==now.month and day==now.day)
                    hn=f"{y}-{m:02d}-{day:02d}"in self.cn
                    bg='#334422'if it else('#1a1a3a'if hn else'#111122')
                    fg='#00ff88'if it else('#ffaa44'if hn else'#aaaacc')
                    lb=tk.Label(self.cf2,text=str(day),font=('Courier',11,'bold'if it else'normal'),bg=bg,fg=fg,width=5,height=2,cursor='hand2')
                    lb.grid(row=wn+1,column=dn,padx=1,pady=1)
                    lb.bind('<Button-1>',lambda e,d=day:self._ed(d))
    def _ed(self,d):
        y,m=self.cy.get(),self.cm.get();key=f"{y}-{m:02d}-{d:02d}"
        nn=simpledialog.askstring(f"Note {key}","Note:",initialvalue=self.cn.get(key,''),parent=self.win)
        if nn is not None:self.cn[key]=nn;self._scn();self._rc()
    def _scn(self):(BASE_DIR/"notes"/"cal.json").write_text(json.dumps(self.cn))
    def _lcn(self):
        p=BASE_DIR/"notes"/"cal.json"
        if p.exists():
            try:self.cn=json.loads(p.read_text())
            except:self.cn={}
    def _todo_tab(self):
        t=tk.Frame(self.nb,bg='#0d1117');self.nb.add(t,text="✅ Todo")
        self.todos=[];self._lt()
        inp=tk.Frame(t,bg='#0d1117');inp.pack(fill='x',padx=8,pady=5)
        self.te=tk.Entry(inp,bg='#1a1a2a',fg='#eee',font=('Courier',12),insertbackground='#0f0')
        self.te.pack(side='left',fill='x',expand=True);self.te.bind('<Return>',self._at)
        tk.Button(inp,text="+Add",command=self._at,bg='#1a3a1a',fg='#0f0').pack(side='right',padx=2)
        tk.Button(inp,text="Clear Done",command=self._cd,bg='#3a1a1a',fg='#f88').pack(side='right',padx=2)
        self.tf=tk.Frame(t,bg='#0d1117');self.tf.pack(fill='both',expand=True,padx=8)
        self._rt()
    def _at(self,e=None):
        txt=self.te.get().strip()
        if txt:self.todos.append({'t':txt,'d':False,'c':str(datetime.datetime.now())[:16]});self.te.delete(0,'end');self._st();self._rt()
    def _tt(self,i):self.todos[i]['d']=not self.todos[i]['d'];self._st();self._rt()
    def _cd(self):self.todos=[x for x in self.todos if not x['d']];self._st();self._rt()
    def _rt(self):
        for w in self.tf.winfo_children():w.destroy()
        for i,td in enumerate(self.todos):
            r=tk.Frame(self.tf,bg='#0d1117');r.pack(fill='x',pady=1)
            v=tk.BooleanVar(value=td['d'])
            tk.Checkbutton(r,variable=v,command=lambda i=i:self._tt(i),bg='#0d1117',fg='#0f0',selectcolor='#0d1117').pack(side='left')
            c='#555'if td['d']else'#ddd';f='overstrike'if td['d']else'normal'
            tk.Label(r,text=td['t'],bg='#0d1117',fg=c,font=('Courier',10,f),anchor='w').pack(side='left',fill='x',expand=True)
            tk.Label(r,text=td['c'],bg='#0d1117',fg='#334',font=('Courier',8)).pack(side='right')
    def _st(self):(BASE_DIR/"notes"/"todos.json").write_text(json.dumps(self.todos))
    def _lt(self):
        p=BASE_DIR/"notes"/"todos.json"
        if p.exists():
            try:self.todos=json.loads(p.read_text())
            except:self.todos=[]
    def _tick(self):
        now=datetime.datetime.now();self.cv.set(now.strftime("%H:%M:%S"));self.dv.set(now.strftime("%A, %B %d, %Y"))
        if self.swr:
            el=self.swe+(time.time()-self.sws);mi=int(el//60);sc=el%60
            self.swv.set(f"{mi:02d}:{sc:05.2f}")
        self.win.after(100,self._tick)

# ── ART STUDIO ───────────────────────────────────────────────────────────────
class ArtStudio:
    def __init__(self,master):
        self.win=tk.Toplevel(master);self.win.title("🎨 Art Studio")
        self.win.geometry("740x560");self.win.configure(bg='#0d0d14')
        tb=tk.Frame(self.win,bg='#0d0d14');tb.pack(fill='x',padx=8,pady=5)
        tk.Label(tb,text="🎨 ART",font=('Courier',12,'bold'),bg='#0d0d14',fg='#ff88aa').pack(side='left')
        for lbl,cmd in[("Mandala",self._mandala),("Stars",self._stars),("Wave",self._wave),
                        ("Sanskrit",self._sk),("Logo",self._logo),("Random",self._rand)]:
            tk.Button(tb,text=lbl,command=cmd,bg='#1a0a2a',fg='#ff88aa',font=('Courier',9)).pack(side='left',padx=2)
        self.out=scrolledtext.ScrolledText(self.win,bg='#0d0d14',fg='#aaffdd',font=('Courier',10),wrap='none')
        self.out.pack(fill='both',expand=True,padx=8,pady=5)
        self._rand()
    def _show(self,t):self.out.delete('1.0','end');self.out.insert('end',t)
    def _mandala(self):self._show(f"MANDALA:\n\n{gen_mandala(E.randint(11,21))}")
    def _stars(self):self._show(f"STARFIELD:\n\n{gen_stars()}")
    def _wave(self):self._show(f"WAVE:\n\n{gen_wave_art(E.random()*4+1,E.randint(4,9))}")
    def _sk(self):self._show(ART_GALLERY['Sanskrit Core'])
    def _logo(self):self._show(ART_GALLERY['Pysplore Logo'])
    def _rand(self):E.choice([self._mandala,self._stars,self._wave,self._sk,self._logo])()

# ── TEXT RPG ─────────────────────────────────────────────────────────────────
class TextRPG:
    def __init__(self,master):
        self.win=tk.Toplevel(master);self.win.title("⚔ Recursive Archive RPG")
        self.win.geometry("680x500");self.win.configure(bg='#0d0d0d')
        self.out=scrolledtext.ScrolledText(self.win,height=20,bg='#0d0d0d',fg='#c8c8c8',font=('Courier',10),wrap='word',state='disabled')
        self.out.pack(fill='both',expand=True,padx=5,pady=5)
        inf=tk.Frame(self.win,bg='#0d0d0d');inf.pack(fill='x',padx=5,pady=3)
        self.entry=tk.Entry(inf,bg='#1a1a1a',fg='#0f0',font=('Courier',12),insertbackground='#0f0')
        self.entry.pack(side='left',fill='x',expand=True);self.entry.bind('<Return>',self._proc)
        tk.Button(inf,text="▶",command=self._proc,bg='#224422',fg='#0f0').pack(side='right',padx=3)
        self.state={};self._reset()
    def _reset(self):
        self.state={'room':'start','hp':100,'gold':0,'inv':[],'vis':set()}
        self.rooms={
            'start':{'desc':"The Recursive Archive. Runes glow. The dot blinks.\n[north] Hall of Axioms | [east] Synth Chamber | [south] Forest",
                     'exits':{'north':'axioms','east':'synth','south':'forest'},'items':['scroll']},
            'axioms':{'desc':"Pillars of pure logic. Each bears an axiom.\n[south] Start | [north] Void",
                      'exits':{'south':'start','north':'void'},'items':['crystal']},
            'synth':{'desc':"528Hz hums. Waveforms dance.\n[west] Start | [north] Quiet Room",
                     'exits':{'west':'start','north':'quiet'},'items':['gem']},
            'forest':{'desc':"Infinite trees. A wolf blocks you.\n⚔ [fight] or [run]",
                      'exits':{'north':'start'},'items':['herb'],'enemy':{'name':'Wolf','hp':30,'atk':12}},
            'void':{'desc':"The Void.\n'What is the axiom of identity?' A voice echoes.",
                    'exits':{'south':'axioms'},'items':['void crystal']},
            'quiet':{'desc':"The Quiet Room. Amber light. The dot blinks.\n[south] Synth | [west] Vault",
                     'exits':{'south':'synth','west':'vault'},'items':['meditation seed']},
            'vault':{'desc':"Six sacred archives glow on pedestals! +100 Gold!\n[east] Quiet Room",
                     'exits':{'east':'quiet'},'items':['sacred archive'],'gold':100},
        }
        self._pr("═"*50+"\n  ⚔  THE RECURSIVE ARCHIVE  ⚔\n  Dot Protocol Active · Entropy Seeded\n"+"═"*50)
        name=simpledialog.askstring("Name","Traveler name:",parent=self.win)
        self.state['name']=name or"Hero"
        self._pr(f"\nWelcome, {self.state['name']}! HP:{self.state['hp']}")
        self._room();self._pr("\ngo[dir] look take[item] inventory stats fight run help\n>")
    def _pr(self,t):
        self.out.config(state='normal');self.out.insert('end',t+'\n')
        self.out.see('end');self.out.config(state='disabled')
    def _room(self):
        r=self.rooms.get(self.state['room'],{});self._pr(f"\n📍 {self.state['room'].upper()}\n{r.get('desc','...')}")
        if r.get('items'):self._pr(f"  Items: {', '.join(r['items'])}")
        g=r.get('gold',0)
        if g and self.state['room']not in self.state['vis']:self.state['gold']+=g;self._pr(f"  💰+{g}!")
        self.state['vis'].add(self.state['room'])
    def _proc(self,e=None):
        cmd=self.entry.get().strip().lower();self.entry.delete(0,'end')
        if not cmd:return
        self._pr(f"\n> {cmd}");TK.tok(cmd,'rpg')
        pt=cmd.split();vb=pt[0]if pt else'';ag=pt[1]if len(pt)>1 else''
        r=self.rooms.get(self.state['room'],{})
        if vb in('go','n','s','e','w','north','south','east','west'):
            d=ag if ag else{'n':'north','s':'south','e':'east','w':'west'}.get(vb,vb)
            ex=r.get('exits',{})
            if d in ex:self.state['room']=ex[d];self._room()
            else:self._pr("  No exit that way.")
        elif vb in('look','l'):self._room()
        elif vb=='take':
            its=r.get('items',[]);m=next((i for i in its if ag in i),None)
            if m:self.state['inv'].append(m);its.remove(m);self._pr(f"  ✓ {m}")
            else:self._pr("  Not found.")
        elif vb in('inv','inventory'):self._pr("  🎒 "+', '.join(self.state['inv']or['empty']))
        elif vb=='stats':self._pr(f"  {self.state['name']} HP:{self.state['hp']} Gold:{self.state['gold']}")
        elif vb=='fight':
            en=r.get('enemy')
            if en:
                dm=E.randint(10,25);en['hp']-=dm;ed=E.randint(5,en['atk']);self.state['hp']-=ed
                self._pr(f"  ⚔ Hit {en['name']} -{dm}! It hits you -{ed}!")
                if en['hp']<=0:self._pr(f"  ✓ Defeated! +30g");self.state['gold']+=30;del r['enemy']
                elif self.state['hp']<=0:self._pr("  💀 You died! Type restart")
            else:self._pr("  No enemy.")
        elif vb=='run':
            ex=r.get('exits',{})
            if ex:self.state['room']=E.choice(list(ex.values()));self._room()
        elif vb in('help','h','?'):self._pr("  go look take inv stats fight run restart quit")
        elif vb=='restart':self._reset()
        elif vb in('quit','q'):self.win.destroy()
        elif self.state['room']=='void' and any(w in cmd for w in['identical','itself','identity']):
            self._pr("  ✨ The void opens!");self.rooms['void']['items'].append('void key')
        else:self._pr("  Unknown. help?")
        self._pr(f"  [HP:{self.state['hp']} Gold:{self.state['gold']}] >")

# ── MEDITATION / QUIET ROOM ──────────────────────────────────────────────────
class MeditationMode:
    PROMPTS=["Sit in silence. Let thoughts arise. Let them pass.",
             "Notice the space between inhale and exhale. That space is the dot.",
             "You are not the watcher. You are the watching.",
             "Breathe: Sat (Being). Hold: Chit (Consciousness). Out: Ananda (Bliss).",
             "The scene never repeats. Neither does this moment.",
             "You cannot find the dot by looking. It finds you by being still.",
             "The mountain lake reflects what is. Not what was. Not what will be.",
             "Every character of this scene was calculated for this exact moment."]
    def __init__(self,master):
        self.win=tk.Toplevel(master);self.win.title("🧘 The Quiet Room")
        self.win.geometry("900x660");self.win.configure(bg='#0a0a14')
        self.win.protocol("WM_DELETE_WINDOW",self._close)
        self.scene=tk.StringVar(value='Mountain Lake')
        self.running=False;self.ss=None;self.slog=[]
        self.lvars={n:tk.BooleanVar(value=AUR.layers[n]['on'])for n in AUR.layers}
        self.lvols={n:tk.DoubleVar(value=AUR.layers[n]['vol'])for n in AUR.layers}
        self.aurora_on=False;self._build();self.running=True;self._anim()
    def _build(self):
        tb=tk.Frame(self.win,bg='#0a0a0e',height=38);tb.pack(fill='x');tb.pack_propagate(False)
        tk.Label(tb,text="🧘 THE QUIET ROOM",font=('Courier',12,'bold'),bg='#0a0a0e',fg='#cc8844').pack(side='left',padx=8)
        self.sl=tk.Label(tb,text="No session",font=('Courier',8),bg='#0a0a0e',fg='#554433');self.sl.pack(side='right',padx=8)
        tk.Button(tb,text="Begin",command=self._begin,bg='#221a0a',fg='#cc8844',font=('Courier',8)).pack(side='right',padx=2)
        tk.Button(tb,text="End+Save",command=self._end,bg='#1a0a0a',fg='#884433',font=('Courier',8)).pack(side='right',padx=2)
        main=tk.Frame(self.win,bg='#0a0a14');main.pack(fill='both',expand=True,padx=4,pady=4)
        sf=tk.Frame(main,bg='#0a0a14');sf.pack(side='left',fill='both',expand=True)
        self.snm=tk.Label(sf,text="Mountain Lake",font=('Courier',10,'bold'),bg='#0a0a14',fg='#cc8844');self.snm.pack()
        self.sd=scrolledtext.ScrolledText(sf,bg='#050510',fg='#aaccff',font=('Courier',9),wrap='none',height=20,state='disabled',relief='flat')
        self.sd.pack(fill='both',expand=True)
        self.dv=tk.StringVar(value=SCENES_META['Mountain Lake']['desc'])
        tk.Label(sf,textvariable=self.dv,font=('Courier',8,'italic'),bg='#0a0a14',fg='#664433',wraplength=520).pack(pady=2)
        self.pv=tk.StringVar(value=E.choice(self.PROMPTS))
        tk.Label(sf,textvariable=self.pv,font=('Courier',9),bg='#0a0a14',fg='#886644',wraplength=520).pack()
        tk.Button(sf,text="New Prompt",command=lambda:self.pv.set(E.choice(self.PROMPTS)),bg='#0a0a14',fg='#554433',font=('Courier',8),relief='flat').pack()
        self.db=tk.Button(sf,text="  .  ",font=('Courier',15),bg='#0a0a14',fg='#cc8844',relief='flat',command=self._dot,cursor='hand2')
        self.db.pack(pady=4)
        tk.Label(sf,text="click the dot",font=('Courier',7),bg='#0a0a14',fg='#221a0a').pack()
        rp=tk.Frame(main,bg='#0a0a14',width=240);rp.pack(side='right',fill='y',padx=(4,0));rp.pack_propagate(False)
        ssf=tk.LabelFrame(rp,text="Nature Scene",bg='#0a0a14',fg='#cc8844',font=('Courier',8),padx=4,pady=3)
        ssf.pack(fill='x',pady=(0,4))
        for sn,sm in SCENES_META.items():
            tk.Radiobutton(ssf,text=f"{sn}({sm['freq']}Hz)",variable=self.scene,value=sn,
                           command=self._chscene,bg='#0a0a14',fg='#aa8866',selectcolor='#1a0a0a',font=('Courier',7)).pack(anchor='w')
        tk.Button(ssf,text="🌱 New Seed",command=lambda:NG.new_seed(),bg='#0a1a0a',fg='#88cc66',font=('Courier',7)).pack(fill='x',pady=1)
        tk.Button(ssf,text="💾 Save Wallpaper",command=self._wall,bg='#1a0a2a',fg='#aa88ff',font=('Courier',7)).pack(fill='x',pady=1)
        amf=tk.LabelFrame(rp,text="Ambient Layers",bg='#0a0a14',fg='#cc8844',font=('Courier',8),padx=4,pady=3)
        amf.pack(fill='x',pady=(0,4))
        self.ab=tk.Button(amf,text="▶ Start Ambient",command=self._tam,bg='#0a1a0a',fg='#00ff88',font=('Courier',8,'bold'))
        self.ab.pack(fill='x',pady=2)
        for ln in AUR.layers:
            lr=tk.Frame(amf,bg='#0a0a14');lr.pack(fill='x',pady=1)
            tk.Checkbutton(lr,text=ln,variable=self.lvars[ln],command=lambda n=ln:AUR.set_layer(n,self.lvars[n].get()),
                           bg='#0a0a14',fg='#aa8866',selectcolor='#0a0a14',font=('Courier',7)).pack(side='left')
            tk.Scale(lr,variable=self.lvols[ln],from_=0,to=1,resolution=.05,orient='horizontal',length=70,
                     bg='#0a0a14',fg='#cc8844',troughcolor='#1a0a00',showvalue=False,
                     command=lambda v,n=ln:AUR.set_vol(n,float(v))).pack(side='right')
        self.fl=tk.Label(rp,text="432Hz\nmiracle tuning",font=('Courier',8),bg='#0a0a14',fg='#cc8844',justify='left')
        self.fl.pack(anchor='w',padx=4)
        self.el=tk.Label(rp,text="",font=('Courier',7),bg='#0a0a14',fg='#223',justify='left')
        self.el.pack(anchor='w',padx=4)
        wf=tk.LabelFrame(rp,text="Wallpapers",bg='#0a0a14',fg='#cc8844',font=('Courier',8),padx=4,pady=2)
        wf.pack(fill='x',pady=(4,0))
        for w in WP.ls()[:3]:
            tk.Label(wf,text=w.stem[:22],font=('Courier',7),bg='#0a0a14',fg='#554433').pack(anchor='w')
    def _dot(self):
        E.feed_dot();self.db.config(fg='#ffcc88')
        self.win.after(400,lambda:self.db.config(fg='#cc8844'))
        self.win.after(1200,lambda:self.db.config(fg='#cc8844'))
        if self.ss:self.slog.append({'t':str(datetime.datetime.now()),'ev':'dot','sc':self.scene.get()})
        def _t():
            s=adsr(gen_wave(AUR.freq,.4,'sine',.3),atk=.05,dec=.1,sus=.5,rel=.2);play_wav(to_wav(s))
        threading.Thread(target=_t,daemon=True).start()
    def _chscene(self):
        sn=self.scene.get();sm=SCENES_META.get(sn,{});f=sm.get('freq',432)
        AUR.freq=f
        for n,v in sm.get('lp',{}).items():
            if n in self.lvars:self.lvars[n].set(v);AUR.set_layer(n,v)
        self.snm.config(text=sn);self.dv.set(sm.get('desc',''));self.pv.set(E.choice(self.PROMPTS))
        FC={'Mountain Lake':'#aaccff','Forest Clearing':'#aaffaa','Ocean Shore':'#aaeeff',
            'Desert Night':'#ffddaa','Meadow':'#ccffaa','Cave':'#aaaaff','Sky':'#eeeeff'}
        self.sd.config(fg=FC.get(sn,'#aaccff'))
        MN={432:"miracle tuning",528:"DNA/transform",396:"liberation",417:"change",
            639:"connection",741:"awakening",852:"intuition"}
        self.fl.config(text=f"{f}Hz\n{MN.get(f,'sacred')}")
        NG.new_seed()
    def _wall(self):
        txt=self.sd.get('1.0','end');sn=self.scene.get();f=SCENES_META.get(sn,{}).get('freq',432)
        hp,_=WP.save(txt,sn,f)
        messagebox.showinfo("Wallpaper Saved",f"HTML: {hp.name}\nFolder: {WP.wallpaper_dir}\nOpen in browser for display!")
    def _tam(self):
        self.aurora_on=not self.aurora_on
        if self.aurora_on:AUR.start();self.ab.config(text="⬛ Stop",bg='#1a0a0a',fg='#884433')
        else:AUR.stop();self.ab.config(text="▶ Start Ambient",bg='#0a1a0a',fg='#00ff88')
    def _begin(self):
        self.ss=datetime.datetime.now();self.slog=[{'t':str(self.ss),'ev':'begin'}]
        self.sl.config(text=f"Session:{self.ss.strftime('%H:%M:%S')}")
    def _end(self):
        if not self.ss:messagebox.showinfo("No session","Click Begin first.");return
        en=datetime.datetime.now();dur=(en-self.ss).total_seconds()
        self.slog.append({'t':str(en),'ev':'end','dur':dur})
        sn=self.scene.get();f=SCENES_META.get(sn,{}).get('freq',432)
        data={'start':str(self.ss),'end':str(en),'dur':dur,'scene':sn,'freq':f,'dots':E._dot_clicks,'log':self.slog}
        p=BASE_DIR/"meditation"/f"sess_{self.ss.strftime('%Y%m%d_%H%M%S')}.json"
        p.write_text(json.dumps(data,indent=2))
        mi=int(dur//60);sc=int(dur%60)
        AUR.stop();self.aurora_on=False;self.ab.config(text="▶ Start Ambient",bg='#0a1a0a',fg='#00ff88')
        messagebox.showinfo("Complete",f"🧘 {mi}m {sc}s\n{sn}\nDot clicks:{E._dot_clicks}\n\nशान्ति · Shanti · Peace\nSaved:{p.name}")
        self.ss=None
    def _anim(self):
        if not self.running:return
        try:
            sn=self.scene.get();r=NG.render(sn,w=56,h=15)
            f=SCENES_META.get(sn,{}).get('freq',432);mp=round(E.moon()*100)
            self.sd.config(state='normal');self.sd.delete('1.0','end')
            self.sd.insert('end',f"  {sn}  ·  {f}Hz  ·  🌙{mp}%  ·  f{NG.frame}\n\n{r}")
            self.sd.config(state='disabled')
            self.el.config(text=f"Moon:{mp}%  Sun:{round(E.sun()*100)}%\nTokens:{TK.count}\nFreq:{round(TK.ambient_freq())}Hz")
        except:pass
        self.win.after(1500,self._anim)
    def _close(self):self.running=False;AUR.stop();self.win.destroy()

# ── KNOWLEDGE BROWSER ────────────────────────────────────────────────────────
class KnowledgeBrowser:
    def __init__(self,master):
        self.win=tk.Toplevel(master);self.win.title("📚 Knowledge — Six Archives")
        self.win.geometry("760x560");self.win.configure(bg='#0d0d14')
        tp=tk.Frame(self.win,bg='#0d0d14');tp.pack(fill='x',padx=8,pady=5)
        tk.Label(tp,text="📚 KNOWLEDGE",font=('Courier',12,'bold'),bg='#0d0d14',fg='#ffaa44').pack(side='left')
        self.qv=tk.Entry(tp,bg='#1a1a2a',fg='#ffaa44',font=('Courier',12),insertbackground='#0f0',width=25)
        self.qv.pack(side='left',padx=6);self.qv.bind('<Return>',lambda e:self._search())
        for t,cmd,fg in[("Search",self._search,'#ffaa44'),("Random",self._rand,'#888'),("Axioms",self._axioms,'#bb88ff'),("Freq",self._freq_tab,'#00ff88')]:
            tk.Button(tp,text=t,command=cmd,bg='#1a1a2a',fg=fg).pack(side='left',padx=2)
        self.nb=ttk.Notebook(self.win);self.nb.pack(fill='both',expand=True,padx=8,pady=5)
        st=tk.Frame(self.nb,bg='#0d0d14');self.nb.add(st,text="🔍 Search")
        self.so=scrolledtext.ScrolledText(st,bg='#0d0d14',fg='#ccccaa',font=('Courier',10),wrap='word')
        self.so.pack(fill='both',expand=True)
        skt=tk.Frame(self.nb,bg='#0d0d14');self.nb.add(skt,text="🕉 Sanskrit")
        sko=scrolledtext.ScrolledText(skt,bg='#0d0d14',fg='#88aaff',font=('Courier',10),wrap='word')
        sko.pack(fill='both',expand=True,padx=5,pady=5)
        sko.insert('end',ART_GALLERY['Sanskrit Core']+"\n\nSANSKRIT LEXICON\n"+"═"*40+"\n\n")
        for k,v in SK.items():sko.insert('end',f"  {k}  →  {v}\n")
        at=tk.Frame(self.nb,bg='#0d0d14');self.nb.add(at,text="⚖ Axioms")
        ao=scrolledtext.ScrolledText(at,bg='#0d0d14',fg='#bb88ff',font=('Courier',10),wrap='word')
        ao.pack(fill='both',expand=True,padx=5,pady=5)
        ao.insert('end',"UNDB — ULTIMATE RECURSIVE KNOWLEDGE AXIOMS\n"+"═"*50+"\n\n")
        for k,v in AXIOMS.items():ao.insert('end',f"  [{k}]  {v}\n")
        ao.insert('end',"\nDOT PROTOCOL:\n");[ao.insert('end',f"  {s}\n")for s in DOT_STAGES]
        self.ft=tk.Frame(self.nb,bg='#0d0d14');self.nb.add(self.ft,text="📊 Freq")
        self._build_freq()
        et=tk.Frame(self.nb,bg='#0d0d14');self.nb.add(et,text="🌐 Encyclopedia")
        eo=scrolledtext.ScrolledText(et,bg='#0d0d14',fg='#ccaa88',font=('Courier',9),wrap='word')
        eo.pack(fill='both',expand=True,padx=5,pady=5)
        for k,v in ENC.items():eo.insert('end',f"  {k.upper()}\n  {v}\n\n")
    def _search(self):
        q=self.qv.get().strip()
        if not q:return
        TK.tok(q,'search');r=kb_search(q)
        self.so.delete('1.0','end');self.so.insert('end',f"SEARCH: '{q}'\n{'═'*45}\n\n")
        if r:
            for src,w,d in r:self.so.insert('end',f"[{src}] {w.upper()}\n  {d[:250]}\n\n")
        else:self.so.insert('end',"No results. Try Sanskrit, axiom, frequency, consciousness...\n")
        self.nb.select(0)
    def _rand(self):f=random_fact();self.so.delete('1.0','end');self.so.insert('end',f"RANDOM:\n{'═'*45}\n\n{f}\n");self.nb.select(0)
    def _axioms(self):self.nb.select(2)
    def _freq_tab(self):self.nb.select(3)
    def _build_freq(self):
        f=tk.Frame(self.ft,bg='#0d0d14');f.pack(fill='x',padx=5,pady=3)
        tk.Label(f,text="Hz:",bg='#0d0d14',fg='#aaa').pack(side='left')
        self.fe=tk.Entry(f,bg='#1a1a2a',fg='#0ff',font=('Courier',12),width=8)
        self.fe.pack(side='left',padx=4);self.fe.insert(0,"432");self.fe.bind('<Return>',lambda e:self._af())
        tk.Button(f,text="Analyze",command=self._af,bg='#0a2a1a',fg='#0f0').pack(side='left')
        tk.Button(f,text="Play",command=self._pf,bg='#1a1a2a',fg='#aaa').pack(side='left',padx=3)
        self.fo=scrolledtext.ScrolledText(self.ft,bg='#0d0d14',fg='#00ff88',font=('Courier',9),wrap='word')
        self.fo.pack(fill='both',expand=True)
        self.fo.insert('end',"SOLFEGGIO:\n")
        for k,v in SOLFEG_F.items():self.fo.insert('end',f"  {v}Hz — {k}\n")
        self.fo.insert('end',"\nCHAKRA:\n")
        for k,v in CHAKRA_F.items():self.fo.insert('end',f"  {v}Hz — {k}\n")
        self.fo.insert('end',"\nSCENE FREQUENCIES:\n")
        for k,v in SCENE_F.items():self.fo.insert('end',f"  {v}Hz — {k}\n")
    def _af(self):
        try:f=float(self.fe.get());r=freq_report(f);self.fo.delete('1.0','end');self.fo.insert('end',r)
        except:self.fo.insert('end',"\nInvalid frequency.\n")
    def _pf(self):
        try:
            f=float(self.fe.get())
            def _p():s=adsr(gen_wave(f,2.,'sine',.4),.1,.1,.8,.5);play_wav(to_wav(s))
            threading.Thread(target=_p,daemon=True).start()
        except:pass

# ── GENERATION STUDIO ────────────────────────────────────────────────────────
class GenStudio:
    def __init__(self,master):
        self.win=tk.Toplevel(master);self.win.title("✨ Generation Studio")
        self.win.geometry("740x540");self.win.configure(bg='#0d0d14')
        self.st=tk.StringVar(value='philosophy')
        tp=tk.Frame(self.win,bg='#0d0d14');tp.pack(fill='x',padx=8,pady=5)
        tk.Label(tp,text="✨ GENERATION",font=('Courier',12,'bold'),bg='#0d0d14',fg='#aa88ff').pack(side='left')
        ttk.Combobox(tp,textvariable=self.st,values=['philosophy','poetry','haiku','absurdist','story'],width=12,state='readonly').pack(side='left',padx=6)
        tk.Button(tp,text="Generate",command=self._gen,bg='#1a0a3a',fg='#bb88ff',font=('Courier',10,'bold')).pack(side='left',padx=4)
        tk.Button(tp,text="Dot Protocol",command=self._dot,bg='#0a2a1a',fg='#00ff88').pack(side='left',padx=3)
        tk.Button(tp,text="Copy",command=self._copy,bg='#2a2a1a',fg='#ffaa44').pack(side='right')
        tk.Button(tp,text="Save",command=self._save,bg='#1a2a1a',fg='#88ff88').pack(side='right',padx=3)
        sf=tk.Frame(self.win,bg='#0d0d14');sf.pack(fill='x',padx=8,pady=2)
        tk.Label(sf,text="Seed:",bg='#0d0d14',fg='#556').pack(side='left')
        self.se=tk.Entry(sf,bg='#1a1a2a',fg='#aaa',font=('Courier',11),insertbackground='#0f0')
        self.se.pack(side='left',fill='x',expand=True,padx=5);self.se.bind('<Return>',lambda e:self._gen())
        self.out=scrolledtext.ScrolledText(self.win,bg='#0d0d14',fg='#ccccee',font=('Courier',11),wrap='word')
        self.out.pack(fill='both',expand=True,padx=8,pady=4)
        qb=tk.Frame(self.win,bg='#0d0d14');qb.pack(fill='x',padx=8,pady=2)
        for lbl,cmd in[("Haiku",lambda:self._q('haiku')),("Philosophy",lambda:self._q('philosophy')),
                        ("Absurdist",lambda:self._q('absurdist')),("Story",lambda:self._q('story')),("Fact",self._fact)]:
            tk.Button(qb,text=lbl,command=cmd,bg='#1a1a2a',fg='#88aaff',font=('Courier',9)).pack(side='left',padx=2)
        self._gen()
    def _q(self,s):self.st.set(s);self._gen()
    def _gen(self):
        s=self.st.get();sd=self.se.get().strip()
        txt=DOT.expand(sd)+"\n\n"+gen_text(s) if sd else gen_text(s)
        self._show(txt,s.upper())
    def _dot(self):
        sd=self.se.get().strip()or"consciousness recursively generates reality"
        self._show(DOT.run(sd),"DOT PROTOCOL")
    def _show(self,txt,lbl="OUTPUT"):
        self.out.delete('1.0','end')
        self.out.insert('end',f"═══ {lbl} ═══\n\n{txt}\n\n{'─'*45}\n{datetime.datetime.now().strftime('%H:%M:%S')} | E:{E._counter%999} | T:{TK.count}\n")
    def _fact(self):self._show(random_fact(),"RANDOM KNOWLEDGE")
    def _copy(self):self.win.clipboard_clear();self.win.clipboard_append(self.out.get('1.0','end'))
    def _save(self):
        p=BASE_DIR/"exports"/f"gen_{int(time.time())}.txt";p.write_text(self.out.get('1.0','end'))
        messagebox.showinfo("Saved",f"Saved to {p}")

# ── SETTINGS ─────────────────────────────────────────────────────────────────
class Settings:
    def __init__(self,master):
        self.win=tk.Toplevel(master);self.win.title("⚙ Settings")
        self.win.geometry("600x540");self.win.configure(bg='#0d0d14')
        tk.Label(self.win,text="⚙ PYSPLORE v1.0",font=('Courier',13,'bold'),bg='#0d0d14',fg='#88aaff').pack(pady=8)
        rf=tk.LabelFrame(self.win,text="How to Launch",bg='#0d0d14',fg='#00ff88',font=('Courier',9),padx=8,pady=5)
        rf.pack(fill='x',padx=15,pady=5)
        for t in["Windows: Double-click Pysplore_v1.0.py (needs Python installed)",
                 "Mac/Linux: chmod +x Pysplore_v1.0.py  then  ./Pysplore_v1.0.py",
                 "Any platform: python3 Pysplore_v1.0.py",
                 "USB stick: Copy anywhere. Run. Zero install required."]:
            tk.Label(rf,text=t,bg='#0d0d14',fg='#88aa88',font=('Courier',8),anchor='w').pack(fill='x')
        af=tk.LabelFrame(self.win,text="Archive Status",bg='#0d0d14',fg='#88aaff',font=('Courier',9),padx=8,pady=5)
        af.pack(fill='x',padx=15,pady=5)
        for nm,v in[("G1: Dot Protocol Engine",len(AXIOMS)),("G2: Entropy Pool",E._counter),
                    ("G3: Sacred Tokenizer",TK.count),("A1: UNDB Axioms",len(AXIOMS)),
                    ("A2: Sanskrit Engine",len(SK)),("A3: Dictionary",len(DICT)),
                    ("A4: Encyclopedia",len(ENC)),("A5: Aurora Synth",len(SCALES)),
                    ("A6: Meditation/Nature",len(SCENES_META))]:
            r=tk.Frame(af,bg='#0d0d14');r.pack(fill='x',pady=1)
            tk.Label(r,text=f"✅ {nm}",bg='#0d0d14',fg='#aaa',font=('Courier',8),width=32,anchor='w').pack(side='left')
            tk.Label(r,text=str(v),bg='#0d0d14',fg='#0f0',font=('Courier',8)).pack(side='left')
        sf=tk.LabelFrame(self.win,text="System",bg='#0d0d14',fg='#88aaff',font=('Courier',9),padx=8,pady=5)
        sf.pack(fill='x',padx=15,pady=5)
        for k,v in[("Python",sys.version[:28]),("Platform",sys.platform),("Data",str(BASE_DIR)),
                   ("Meditations",len(list((BASE_DIR/"meditation").glob("*.json")))),
                   ("Wallpapers",len(list((BASE_DIR/"wallpapers").glob("*.html")))),
                   ("Journal",len(list((BASE_DIR/"journal").glob("*.txt"))))]:
            r=tk.Frame(sf,bg='#0d0d14');r.pack(fill='x',pady=1)
            tk.Label(r,text=k+":",bg='#0d0d14',fg='#888',font=('Courier',8),width=14,anchor='w').pack(side='left')
            tk.Label(r,text=str(v),bg='#0d0d14',fg='#0ff',font=('Courier',8)).pack(side='left')
        tk.Button(self.win,text="Open Data Folder",command=self._open,bg='#1a1a2a',fg='#88aaff').pack(pady=6)
        tk.Button(self.win,text="Play Startup Sound",command=startup_sound,bg='#0a1a0a',fg='#0f0').pack(pady=2)
        tk.Label(self.win,text="MIT · No Dependencies · Offline · The dot sings.",font=('Courier',8),bg='#0d0d14',fg='#223').pack(pady=5)
    def _open(self):
        try:
            if sys.platform=='win32':os.startfile(str(BASE_DIR))
            elif sys.platform=='darwin':subprocess.Popen(['open',str(BASE_DIR)])
            else:subprocess.Popen(['xdg-open',str(BASE_DIR)])
        except:pass

# ── MAIN OS HUB ──────────────────────────────────────────────────────────────
SPLASH_TXT="""
 ██████╗ ██╗   ██╗███████╗██████╗ ██╗      ██████╗ ██████╗ ███████╗
 ██╔══██╗╚██╗ ██╔╝██╔════╝██╔══██╗██║     ██╔═══██╗██╔══██╗██╔════╝
 ██████╔╝ ╚████╔╝ ███████╗██████╔╝██║     ██║   ██║██████╔╝█████╗  
 ██╔═══╝   ╚██╔╝  ╚════██║██╔═══╝ ██║     ██║   ██║██╔══██╗██╔══╝  
 ██║        ██║   ███████║██║     ███████╗╚██████╔╝██║  ██║███████╗
 ╚═╝        ╚═╝   ╚══════╝╚═╝     ╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝
        P Y S P L O R E   v 1 . 0   ·   D O T   P R O T O C O L
  3 Guardians · 6 Archives · Zero Dependencies · Offline Forever · .
"""

class PysploreOS:
    def __init__(self):
        self.root=tk.Tk()
        self.root.title("Pysplore v1.0 — Click anything. Explore everything. .")
        self.root.geometry("1000x680");self.root.configure(bg='#0a0a14')
        self.root.protocol("WM_DELETE_WINDOW",self._quit)
        self.root.bind('<Motion>',lambda e:E.feed_mouse(e.x,e.y))
        self.root.bind('<KeyPress>',lambda e:E.feed_key(ord(e.char)if e.char else 0))
        self._splash();self._build()
        startup_sound()
    def _splash(self):
        sp=tk.Toplevel(self.root);sp.overrideredirect(True)
        sw,sh=700,380;x=(sp.winfo_screenwidth()-sw)//2;y=(sp.winfo_screenheight()-sh)//2
        sp.geometry(f"{sw}x{sh}+{x}+{y}");sp.configure(bg='#0a0a14')
        tk.Label(sp,text=SPLASH_TXT,font=('Courier',9,'bold'),bg='#0a0a14',fg='#00ff88',justify='left').pack(pady=8,padx=8)
        tk.Label(sp,text=gen_text('haiku'),font=('Courier',10),bg='#0a0a14',fg='#556',justify='center').pack(pady=3)
        pb=tk.Frame(sp,bg='#0a0a14');pb.pack(pady=5)
        prog=ttk.Progressbar(pb,length=480,mode='indeterminate');prog.pack();prog.start(8)
        self.ssv=tk.StringVar(value="Seeding entropy pool from moon phase...")
        tk.Label(sp,textvariable=self.ssv,bg='#0a0a14',fg='#334',font=('Courier',9)).pack()
        msgs=["Loading six sacred archives...","Initializing Aurora ambient engine...",
              "Warming the Sacred Tokenizer...","The Quiet Room is ready...","The dot is there. Waving."]
        def _cy(i=0):
            if i<len(msgs):self.ssv.set(msgs[i]);sp.after(380,lambda:_cy(i+1))
            else:sp.after(250,sp.destroy)
        self.root.after(180,lambda:_cy())
    def _build(self):
        tb=tk.Frame(self.root,bg='#0a0a14',height=48);tb.pack(fill='x',padx=5,pady=2);tb.pack_propagate(False)
        tk.Label(tb,text="PYSPLORE",font=('Courier',15,'bold'),bg='#0a0a14',fg='#00ff88').pack(side='left',padx=5)
        tk.Label(tb,text="v1.0",font=('Courier',8),bg='#0a0a14',fg='#224').pack(side='left')
        self.clk=tk.Label(tb,text="",font=('Courier',12),bg='#0a0a14',fg='#88aaff');self.clk.pack(side='right',padx=8)
        nb=ttk.Notebook(self.root);nb.pack(fill='both',expand=True,padx=5,pady=2)
        dt=tk.Frame(nb,bg='#0a0a14');nb.add(dt,text="🏠 Home");self._dash(dt)
        at=tk.Frame(nb,bg='#0a0a14');nb.add(at,text="🚀 Apps");self._apps(at)
        gt=tk.Frame(nb,bg='#0a0a14');nb.add(gt,text="✨ Generate");self._gen_inline(gt)
        art=tk.Frame(nb,bg='#0a0a14');nb.add(art,text="🎨 Art");self._art_inline(art)
        mt=tk.Frame(nb,bg='#0a0a0e');nb.add(mt,text="🧘 Meditate");self._med_inline(mt)
        sb=tk.Frame(self.root,bg='#050508');sb.pack(fill='x',side='bottom')
        self.sv=tk.StringVar(value="Pysplore v1.0 Ready · Dot Protocol Active · 3 Guardians · 6 Archives · The dot sings.")
        tk.Label(sb,textvariable=self.sv,bg='#050508',fg='#224',font=('Courier',8),anchor='w').pack(fill='x',padx=5)
        self._tick()
    def _dash(self,parent):
        g=tk.Frame(parent,bg='#0a0a14');g.pack(fill='both',expand=True,padx=8,pady=8)
        lf=tk.Frame(g,bg='#0d0d1a');lf.grid(row=0,column=0,columnspan=2,padx=4,pady=4,sticky='ew')
        tk.Label(lf,text=SPLASH_TXT,font=('Courier',8,'bold'),bg='#0d0d1a',fg='#00ff88',justify='left').pack(padx=5,pady=4)
        af=tk.LabelFrame(g,text="📚 Axiom",bg='#0d0d1a',fg='#88aaff',font=('Courier',9));af.grid(row=1,column=0,padx=4,pady=4,sticky='ew')
        self.av=tk.StringVar(value=axiom_of_day())
        tk.Label(af,textvariable=self.av,bg='#0d0d1a',fg='#bbaaff',font=('Courier',10),wraplength=360,justify='left').pack(padx=5,pady=5)
        tk.Button(af,text="New",command=lambda:self.av.set(axiom_of_day()),bg='#111',fg='#556',font=('Courier',8)).pack(pady=2)
        qf=tk.LabelFrame(g,text="✨ Quick Generate",bg='#0d0d1a',fg='#ff88aa',font=('Courier',9));qf.grid(row=1,column=1,padx=4,pady=4,sticky='ew')
        self.qo=tk.Label(qf,text=gen_text('haiku'),bg='#0d0d1a',fg='#ccccee',font=('Courier',10),wraplength=330,justify='left')
        self.qo.pack(padx=5,pady=5)
        qr=tk.Frame(qf,bg='#0d0d1a');qr.pack()
        for s in['haiku','philosophy','absurdist']:
            tk.Button(qr,text=s,bg='#1a0a2a',fg='#bb88ff',font=('Courier',8),command=lambda s=s:self.qo.config(text=gen_text(s))).pack(side='left',padx=2)
        sf=tk.LabelFrame(g,text="🕉 Sanskrit",bg='#0d0d1a',fg='#88aaff',font=('Courier',9));sf.grid(row=2,column=0,padx=4,pady=4,sticky='ew')
        kv=E.choice(list(SK.items()))
        self.skv=tk.StringVar(value=f"{kv[0]}\n{kv[1]}")
        tk.Label(sf,textvariable=self.skv,bg='#0d0d1a',fg='#88aaff',font=('Courier',11),wraplength=360).pack(padx=5,pady=5)
        tk.Button(sf,text="New",bg='#111',fg='#556',font=('Courier',8),
                  command=lambda:(lambda p:self.skv.set(f"{p[0]}\n{p[1]}"))(E.choice(list(SK.items())))).pack(pady=2)
        ef=tk.LabelFrame(g,text="💡 Entropy",bg='#0d0d1a',fg='#ffaa44',font=('Courier',9));ef.grid(row=2,column=1,padx=4,pady=4,sticky='ew')
        self.ev=tk.StringVar(value=self._estat())
        tk.Label(ef,textvariable=self.ev,bg='#0d0d1a',fg='#ccaa88',font=('Courier',9),wraplength=330,justify='left').pack(padx=5,pady=5)
        tk.Button(ef,text="Stir",bg='#111',fg='#556',font=('Courier',8),
                  command=lambda:(E._stir(int(time.time()*1e6)),self.ev.set(self._estat()))).pack(pady=2)
        g.columnconfigure(0,weight=1);g.columnconfigure(1,weight=1)
    def _estat(self):
        return(f"Moon:{round(E.moon()*100)}%  Sun:{round(E.sun()*100)}%\n"
               f"Dot clicks:{E._dot_clicks}  Tokens:{TK.count}\n"
               f"Ambient:{round(TK.ambient_freq())}Hz  Rhythm:{round(TK.rhythm())}BPM")
    def _apps(self,parent):
        tk.Label(parent,text="PYSPLORE v1.0 — LAUNCH APPLICATIONS",font=('Courier',12,'bold'),bg='#0a0a14',fg='#88aaff').pack(pady=5)
        tk.Label(parent,text="Click any tile. Double-click the .py file to launch the entire OS. No IDE. No compile. No install.",font=('Courier',8),bg='#0a0a14',fg='#224').pack(pady=(0,6))
        gf=tk.Frame(parent,bg='#0a0a14');gf.pack(fill='both',expand=True,padx=10)
        apps=[("🎵","Music Studio",MusicStudio,'#0a2a1a'),
              ("🧘","Quiet Room",MeditationMode,'#0a1a0e'),
              ("📚","Knowledge",KnowledgeBrowser,'#2a1a0a'),
              ("✨","Generate",GenStudio,'#1a0a2a'),
              ("🎨","Art Studio",ArtStudio,'#2a0a1a'),
              ("🖌","Paint Studio",PaintStudio,'#1a1a0a'),
              ("📓","Journal",JournalApp,'#0a1a2a'),
              ("🗓","Clock",ClockApp,'#0a2a2a'),
              ("🧮","Calculator",CalculatorApp,'#1a1a2a'),
              ("⚙","Settings",Settings,'#1a1a1a'),
              ("🐍","Snake",SnakeGame,'#0a2a0a'),
              ("🧱","Tetris",TetrisGame,'#0a1a3a'),
              ("⚔","Text RPG",TextRPG,'#2a0a2a')]
        for i,(em,lbl,cls,bg) in enumerate(apps):
            r,c=divmod(i,7)
            f=tk.Frame(gf,bg=bg,relief='flat',cursor='hand2')
            f.grid(row=r,column=c,padx=4,pady=4,sticky='nsew')
            tk.Label(f,text=em,font=('Arial',20),bg=bg).pack(pady=(8,2))
            tk.Label(f,text=lbl,font=('Courier',7),bg=bg,fg='#cccccc',justify='center').pack(pady=(0,8))
            f.bind('<Button-1>',lambda e,c=cls:c(self.root))
            for ch in f.winfo_children():ch.bind('<Button-1>',lambda e,c=cls:c(self.root))
        for c in range(7):gf.columnconfigure(c,weight=1)
        for r in range(3):gf.rowconfigure(r,weight=1)
    def _gen_inline(self,parent):
        tk.Label(parent,text="✨ GENERATION STUDIO — Inline",font=('Courier',11,'bold'),bg='#0a0a14',fg='#aa88ff').pack(pady=5)
        GenStudio(self.root)
    def _art_inline(self,parent):
        tk.Label(parent,text="🎨 ART STUDIO — Click to open full studio",font=('Courier',11,'bold'),bg='#0a0a14',fg='#ff88aa').pack(pady=5)
        pr=tk.Frame(parent,bg='#0a0a14');pr.pack(fill='both',expand=True,padx=8)
        out=scrolledtext.ScrolledText(pr,bg='#0a0a14',fg='#aaffdd',font=('Courier',10),wrap='none')
        out.pack(fill='both',expand=True)
        def _show(t):out.delete('1.0','end');out.insert('end',t)
        def _rand():E.choice([lambda:_show(f"MANDALA:\n\n{gen_mandala(E.randint(9,19))}"),
                               lambda:_show(f"STARS:\n\n{gen_stars()}"),
                               lambda:_show(f"WAVE:\n\n{gen_wave_art(E.random()*4+1,E.randint(4,8))}"),
                               lambda:_show(ART_GALLERY['Sanskrit Core'])])()
        tb=tk.Frame(parent,bg='#0a0a14');tb.pack(fill='x',padx=8,pady=3)
        for t,fn in[("Mandala",lambda:out.delete('1.0','end')or out.insert('end',f"MANDALA:\n\n{gen_mandala(E.randint(9,19))}")),
                    ("Stars",lambda:out.delete('1.0','end')or out.insert('end',f"STARS:\n\n{gen_stars()}")),
                    ("Wave",lambda:out.delete('1.0','end')or out.insert('end',f"WAVE:\n\n{gen_wave_art(E.random()*4+1,E.randint(4,8))}")),
                    ("Sanskrit",lambda:out.delete('1.0','end')or out.insert('end',ART_GALLERY['Sanskrit Core'])),
                    ("Logo",lambda:out.delete('1.0','end')or out.insert('end',ART_GALLERY['Pysplore Logo'])),
                    ("Full Studio",lambda:ArtStudio(self.root))]:
            tk.Button(tb,text=t,command=fn,bg='#1a0a2a',fg='#ff88aa',font=('Courier',9)).pack(side='left',padx=2)
        _rand()
    def _med_inline(self,parent):
        tk.Label(parent,text="🧘 THE QUIET ROOM",font=('Courier',14,'bold'),bg='#0a0a0e',fg='#cc8844').pack(pady=12)
        tk.Label(parent,text=E.choice(["The dot is there. Waving.","The Quiet Room awaits.","Shanti. Shanti. Shanti.",
                                        "The entropy pool is seeded from the moon.","The sacred tokenizer hums."]),
                 font=('Courier',11),bg='#0a0a0e',fg='#664433').pack(pady=5)
        tk.Button(parent,text="  Open The Quiet Room  ",command=lambda:MeditationMode(self.root),
                  bg='#221a0a',fg='#cc8844',font=('Courier',14,'bold'),padx=20,pady=12,cursor='hand2').pack(pady=15)
        tk.Label(parent,text="Nature scenes · Aurora ambient · 7 sacred soundscapes · Dot Protocol · Wallpaper generator",
                 font=('Courier',9),bg='#0a0a0e',fg='#443322').pack()
        tk.Label(parent,text=f"Moon: {round(E.moon()*100)}%  ·  Sun: {round(E.sun()*100)}%  ·  {len(SCENES_META)} scenes  ·  {len(AUR.layers)} sound layers",
                 font=('Courier',8),bg='#0a0a0e',fg='#332211').pack(pady=8)
        # Preview mini scene
        sv=scrolledtext.ScrolledText(parent,bg='#050510',fg='#aaccff',font=('Courier',9),wrap='none',height=10,state='disabled')
        sv.pack(fill='x',padx=20)
        def _preview():
            r=NG.render('Mountain Lake',w=55,h=8)
            sv.config(state='normal');sv.delete('1.0','end');sv.insert('end',r);sv.config(state='disabled')
            parent.after(2000,_preview)
        _preview()
    def _tick(self):
        now=datetime.datetime.now();self.clk.config(text=now.strftime("%H:%M:%S"))
        if hasattr(self,'ev'):self.ev.set(self._estat())
        self.root.after(1000,self._tick)
    def _quit(self):AUR.stop();self.root.destroy()
    def run(self):self.root.mainloop()

# ── ENTRY POINT ──────────────────────────────────────────────────────────────
if __name__=='__main__':
    app=PysploreOS();app.run()