#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     P Y S P L O R E   v 1 . 1 Alpha                        ║
║  Zero Hard Dependencies · Offline Forever · Any Python 3.7+ · All Devices  ║
║  Full DAW · Media Player · PyAmby Ambient · Paint · Journal · Clock        ║
║  Calculator · Chess · Checkers · Solitaire · On-Screen KB                  ║
║  Touch-optimised · High-precision rhythm engine · Equal Access for All     ║
║  MIT 2026 · The dot sings ∞                                                ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import os, sys, gc, threading, time, math, random, json, struct
import wave, io, tempfile, subprocess, shutil, datetime, calendar
from pathlib import Path
from collections import deque

try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext, messagebox, simpledialog, filedialog, colorchooser
except ImportError:
    print("Pysplore needs tkinter.\n  Ubuntu/Debian: sudo apt-get install python3-tk\n  Brew: brew install python-tk")
    sys.exit(1)

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

VERSION = "4.0"
SR      = 44100
BASE_DIR = Path.home() / "Pysplore_Data"
for _d in ["journal", "songs", "patterns", "samples", "exports", "saves", "media"]:
    (BASE_DIR / _d).mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# PALETTE & FONTS
# ─────────────────────────────────────────────────────────────────────────────
C = {
    "bg":      "#07080f", "bg2":    "#0d0e1a", "bg3":    "#13152a",
    "border":  "#1e2040", "dim":    "#282a44", "acc":    "#00e5a0",
    "acc2":    "#4f9eff", "acc3":   "#9b6dff", "warn":   "#ff9a44",
    "danger":  "#ff3355", "ok":     "#00d96e", "text":   "#d8daf0",
    "muted":   "#5a5e80", "white":  "#ffffff", "black":  "#000000",
    "daw_bg":  "#080a10", "daw_grid":"#12162a","daw_beat":"#1a1e34",
    "daw_bar": "#242840", "daw_step_on":"#00e5a0","daw_step_off":"#131528",
    "daw_head":"#0d0f1e","daw_play":"#00d96e","daw_rec":"#ff3355",
    "daw_track":"#0f1120","gdk":"#0a0b14",
}

def fnt(f="Courier", s=10, w="normal"): return (f, s, w)
FN = {
    "title": fnt("Courier",14,"bold"), "head":  fnt("Courier",11,"bold"),
    "body":  fnt("Courier",10),        "small": fnt("Courier",9),
    "tiny":  fnt("Courier",8),         "clock": fnt("Courier",36,"bold"),
    "mono":  fnt("Courier",10),        "daw":   fnt("Courier",9,"bold"),
}

# ─────────────────────────────────────────────────────────────────────────────
# ENTROPY POOL  (no stdlib random dependency)
# ─────────────────────────────────────────────────────────────────────────────
class EntropyPool:
    __slots__ = ("_p","_dot","_kt","_mt","_last","_ctr")
    def __init__(self):
        self._p = list(range(256)); self._dot = 0
        self._kt = deque(maxlen=64); self._mt = deque(maxlen=64)
        self._last = time.time(); self._ctr = 0
        for v in (int(time.time()*1e9) % (2**32), id(self), os.getpid()):
            self._stir(v)

    def _stir(self, val):
        v = int(val) & 0xFFFFFFFF
        for i in range(255, 0, -1):
            j = (v ^ (i * 6364136223846793005)) % (i + 1)
            self._p[i], self._p[j] = self._p[j], self._p[i]
            v = (v * 1664525 + 1013904223) & 0xFFFFFFFF

    def feed_mouse(self, x, y):
        n = time.time(); d = (n - self._last) * 1e6; self._last = n
        self._mt.append(int(d) ^ (x * 31337) ^ (y * 7919))
        if self._mt: self._stir(sum(self._mt))

    def feed_key(self, k):
        n = time.time(); d = (n - self._last) * 1e6; self._last = n
        self._kt.append(int(d) ^ k)
        if self._kt: self._stir(sum(self._kt))

    def moon(self):
        d = datetime.datetime.now()
        return ((d - datetime.datetime(2000,1,6)).days % 29.53059) / 29.53059

    def randint(self, lo, hi):
        if lo >= hi: return lo
        self._ctr += 1
        self._stir(self._ctr ^ int(time.time()*1e9) % 99991)
        idx = (self._p[self._ctr % 256] ^ int(self.moon() * 1000)) % 256
        return lo + (self._p[idx] % (hi - lo + 1))

    def random(self): return self.randint(0, 999999) / 1_000_000.0
    def choice(self, s): return s[self.randint(0, len(s) - 1)]
    def rand_hex_color(self):
        return "#{:02x}{:02x}{:02x}".format(
            self.randint(0,255), self.randint(0,255), self.randint(0,255))

E = EntropyPool()

# ─────────────────────────────────────────────────────────────────────────────
# AUDIO ENGINE
# ─────────────────────────────────────────────────────────────────────────────
NOTE_NAMES = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
SCALES = {
    "major":     [0,2,4,5,7,9,11],
    "minor":     [0,2,3,5,7,8,10],
    "pentatonic":[0,2,4,7,9],
    "blues":     [0,3,5,6,7,10],
    "chromatic": list(range(12)),
}
CHORD_TYPES = {
    "maj":[0,4,7], "min":[0,3,7], "maj7":[0,4,7,11],
    "min7":[0,3,7,10], "sus4":[0,5,7], "dim":[0,3,6],
}

def midi_to_freq(n): return 440.0 * 2.0 ** ((n - 69) / 12.0)

def note_to_midi(name):
    nm = {"C":0,"D":2,"E":4,"F":5,"G":7,"A":9,"B":11}
    sm = {"C#":1,"D#":3,"F#":6,"G#":8,"A#":10,"Bb":10}
    try:
        if len(name) >= 3 and name[1] in "#b":
            k, o = name[:2], int(name[2:])
        else:
            k, o = name[0], int(name[1:])
        return (o + 1) * 12 + sm.get(k, nm.get(k, 0))
    except:
        return 60

def gen_wave(freq, dur, wtype="sine", vol=0.5):
    n = int(SR * dur); inc = 2 * math.pi * freq / SR; p = 0.0
    if wtype == "noise":
        return [E.random() * 2 * vol - vol for _ in range(n)]
    out = []
    for _ in range(n):
        p += inc
        if   wtype == "sine":     s = math.sin(p)
        elif wtype == "square":   s = 1.0 if math.sin(p) >= 0 else -1.0
        elif wtype == "saw":      s = 2.0*(p%(2*math.pi))/(2*math.pi) - 1.0
        elif wtype == "triangle": s = 2.0*abs(2.0*(p%(2*math.pi))/(2*math.pi)-1.0) - 1.0
        else:                     s = math.sin(p)
        out.append(s * vol)
    return out

def adsr(s, atk=.01, dec=.05, sus=.7, rel=.1):
    n = len(s); a = int(atk*SR); d = int(dec*SR); r = int(rel*SR)
    sl = max(0, n - a - d - r); out = []
    for i, v in enumerate(s):
        if   i < a:       env = i / max(a, 1)
        elif i < a+d:     env = 1.0 - (1.0-sus)*((i-a)/max(d,1))
        elif i < a+d+sl:  env = sus
        else:             env = sus * ((n-i)/max(r,1))
        out.append(v * max(0.0, env))
    return out

def mix_samples(a, b):
    la, lb = len(a), len(b)
    if la < lb: a = a + [0.0]*(lb-la)
    if lb < la: b = b + [0.0]*(la-lb)
    return [min(1.0, max(-1.0, x+y)) for x,y in zip(a,b)]

def normalize(s, peak=0.85):
    if not s: return s
    mx = max(abs(x) for x in s)
    if mx < 1e-6: return s
    return [x/mx*peak for x in s]

def to_wav_bytes(samp, channels=1):
    buf = bytearray()
    for s in samp:
        buf += struct.pack("<h", int(max(-1.0, min(1.0, s)) * 32767))
    w = io.BytesIO()
    with wave.open(w, "wb") as wf:
        wf.setnchannels(channels); wf.setsampwidth(2)
        wf.setframerate(SR); wf.writeframes(bytes(buf))
    return w.getvalue()

def find_player():
    for pl, ex in [
        ("aplay",  []),
        ("paplay", []),
        ("play",   []),
        ("ffplay", ["-nodisp","-autoexit","-loglevel","quiet"]),
        ("mpv",    ["--no-video","--really-quiet"]),
        ("mplayer",["-really-quiet"]),
    ]:
        if shutil.which(pl): return pl, ex
    return None, []

def play_raw(data, block=False):
    def _go():
        tmp = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as t:
                t.write(data); tmp = t.name
            if sys.platform == "win32":
                import winsound
                flags = winsound.SND_FILENAME | (0 if block else winsound.SND_ASYNC)
                winsound.PlaySound(tmp, flags)
            elif sys.platform == "darwin":
                subprocess.Popen(["afplay", tmp],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).wait()
            else:
                pl, ex = find_player()
                if pl:
                    subprocess.Popen([pl]+ex+[tmp],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).wait()
        except:
            pass
        finally:
            if tmp:
                try: os.unlink(tmp)
                except: pass
    if block: _go()
    else: threading.Thread(target=_go, daemon=True).start()

def startup_chime():
    def _g():
        mix = []
        for note, v in [("C3",.35),("E3",.28),("G3",.28)]:
            s = adsr(gen_wave(midi_to_freq(note_to_midi(note)), .6, "sine", v),
                     atk=.1, dec=.1, sus=.8, rel=.2)
            mix = mix_samples(mix, s)
        for n in ["C4","E4","G4","C5"]:
            mix.extend(adsr(gen_wave(midi_to_freq(note_to_midi(n)), .12, "sine", .4),
                            atk=.01, dec=.04, sus=.5, rel=.06))
        play_raw(to_wav_bytes(normalize(mix)))
    threading.Thread(target=_g, daemon=True).start()

# ─────────────────────────────────────────────────────────────────────────────
# MP3 / AUDIO CODEC BRIDGE
# ─────────────────────────────────────────────────────────────────────────────
class MP3Codec:
    @staticmethod
    def _tool():
        for t in ["ffmpeg","lame","sox"]:
            if shutil.which(t): return t
        return None

    @classmethod
    def can_encode(cls): return cls._tool() is not None

    @classmethod
    def wav_to_mp3(cls, wav_path, mp3_path, bitrate="192k"):
        t = cls._tool()
        if not t: return False, "No encoder (install ffmpeg/lame)"
        try:
            if t == "ffmpeg":
                r = subprocess.run(
                    ["ffmpeg","-y","-i",str(wav_path),"-ab",bitrate,str(mp3_path)],
                    capture_output=True, timeout=120)
            elif t == "lame":
                r = subprocess.run(
                    ["lame",f"--preset",bitrate[:-1],str(wav_path),str(mp3_path)],
                    capture_output=True, timeout=120)
            else:
                r = subprocess.run(
                    ["sox",str(wav_path),"-C","192",str(mp3_path)],
                    capture_output=True, timeout=120)
            return r.returncode == 0, r.stderr.decode(errors="ignore")[:200]
        except Exception as e: return False, str(e)

    @classmethod
    def mp3_to_wav(cls, mp3_path, wav_path):
        t = cls._tool()
        if not t: return False, "No decoder (install ffmpeg)"
        try:
            if t == "ffmpeg":
                cmd = ["ffmpeg","-y","-i",str(mp3_path),str(wav_path)]
            elif t == "sox":
                cmd = ["sox",str(mp3_path),str(wav_path)]
            else:
                cmd = ["lame","--decode",str(mp3_path),str(wav_path)]
            r = subprocess.run(cmd, capture_output=True, timeout=120)
            return r.returncode == 0, r.stderr.decode(errors="ignore")[:200]
        except Exception as e: return False, str(e)

    @classmethod
    def load_any_audio(cls, path):
        p = Path(path)
        if p.suffix.lower() in (".mp3",".ogg",".flac",".aac",".m4a"):
            tmp = tempfile.mktemp(suffix=".wav")
            ok, _ = cls.mp3_to_wav(p, tmp)
            if not ok: return None
            path = tmp
        try:
            with wave.open(str(path), "r") as wf:
                n   = wf.getnframes()
                raw = wf.readframes(n)
                ch  = wf.getnchannels()
                sr  = wf.getframerate()
                vals = struct.unpack("<" + ("h"*n*ch), raw)
                if ch == 2:
                    vals = [(vals[i]+vals[i+1])/2 for i in range(0,len(vals),2)]
                return [v/32768.0 for v in vals], sr
        except:
            return None

# ─────────────────────────────────────────────────────────────────────────────
# ON-SCREEN KEYBOARD
# ─────────────────────────────────────────────────────────────────────────────
class OSK:
    ROWS = [
        list("1234567890-="),
        list("qwertyuiop[]"),
        list("asdfghjkl;'"),
        list("zxcvbnm,./"),
    ]

    def __init__(self, root):
        self.root = root; self.target = None
        self.shift = False; self.visible = False
        self._win = None; self._build()
        root.bind("<FocusIn>", self._on_focus, add=True)

    def _build(self):
        self._win = tk.Toplevel(self.root)
        self._win.overrideredirect(True)
        self._win.configure(bg=C["bg2"])
        self._win.attributes("-topmost", True)
        self._win.withdraw()
        outer = tk.Frame(self._win, bg=C["bg2"], pady=4)
        outer.pack(fill="both", expand=True)
        for row in self.ROWS:
            f = tk.Frame(outer, bg=C["bg2"]); f.pack(fill="x", padx=4, pady=1)
            for k in row:
                tk.Button(f, text=k, width=3, bg=C["bg3"], fg=C["text"],
                    font=FN["body"], relief="flat", bd=0, padx=8, pady=10,
                    cursor="hand2", command=lambda c=k: self._press(c)).pack(side="left", padx=1)
        sf = tk.Frame(outer, bg=C["bg2"]); sf.pack(fill="x", padx=4, pady=1)
        for txt, cmd in [
            ("⇧", self._tog_shift),
            ("      Space      ", lambda: self._press(" ")),
            ("⌫", self._backspace),
            ("↩", lambda: self._press("\n")),
            ("✕", self.hide),
        ]:
            w = 10 if "Space" in txt else 4
            tk.Button(sf, text=txt, width=w, bg=C["bg3"], fg=C["text"],
                font=FN["body"], relief="flat", bd=0, padx=8, pady=10,
                cursor="hand2", command=cmd).pack(side="left", padx=1)

    def _on_focus(self, event):
        if isinstance(event.widget, (tk.Entry, tk.Text)):
            self.target = event.widget

    def _press(self, c):
        c2 = c.upper() if self.shift and c.isalpha() else c
        if self.target:
            try: self.target.insert(tk.INSERT, c2)
            except: pass
        if self.shift and c.isalpha(): self._tog_shift()

    def _backspace(self):
        if not self.target: return
        try:
            if isinstance(self.target, tk.Text):
                pos = self.target.index(tk.INSERT)
                if pos != "1.0": self.target.delete(f"{pos}-1c", pos)
            else:
                idx = self.target.index(tk.INSERT)
                if idx > 0: self.target.delete(idx-1, idx)
        except: pass

    def _tog_shift(self): self.shift = not self.shift
    def show(self): self._position(); self._win.deiconify(); self.visible = True
    def hide(self): self._win.withdraw(); self.visible = False
    def toggle(self):
        if self.visible: self.hide()
        else: self.show()

    def _position(self):
        try:
            w  = self.root.winfo_width()
            x  = self.root.winfo_rootx()
            y  = self.root.winfo_rooty()
            h  = self.root.winfo_height()
            self._win.geometry(f"{w}x220+{x}+{y+h-220}")
        except: pass

# ─────────────────────────────────────────────────────────────────────────────
# BASE APP FRAME
# ─────────────────────────────────────────────────────────────────────────────
class AppFrame(tk.Frame):
    def __init__(self, master, **kw):
        super().__init__(master, bg=C["bg"], **kw)

    def _hdr(self, text, fg=None):
        f = tk.Frame(self, bg=C["bg2"]); f.pack(fill="x")
        tk.Label(f, text=text, font=FN["head"],
                 fg=fg or C["acc"], bg=C["bg2"]).pack(side="left", padx=10, pady=8)
        return f

    def on_destroy(self): pass

# ─────────────────────────────────────────────────────────────────────────────
# DAW — DATA LAYER
# ─────────────────────────────────────────────────────────────────────────────
class DAWNote:
    __slots__ = ("midi","start_step","length_steps","vel")
    def __init__(self, midi=60, start=0, length=1, vel=100):
        self.midi=midi; self.start_step=start; self.length_steps=length; self.vel=vel

class DAWPattern:
    def __init__(self, name="Pattern 1", steps=32):
        self.name = name; self.steps = steps
        self.step_data = [False]*steps; self.notes = []; self.color = "#00e5a0"

    def to_dict(self):
        return {"name":self.name,"steps":self.steps,"step_data":self.step_data,
                "notes":[[n.midi,n.start_step,n.length_steps,n.vel] for n in self.notes],
                "color":self.color}

    @classmethod
    def from_dict(cls, d):
        p = cls(d.get("name","Pattern"), d.get("steps",32))
        p.step_data = d.get("step_data",[False]*p.steps)
        p.notes = [DAWNote(x[0],x[1],x[2],x[3]) for x in d.get("notes",[])]
        p.color = d.get("color","#00e5a0"); return p

class DAWTrack:
    SYNTH_PRESETS = {
        "Kick":  {"wave":"sine",    "freq_base":55,   "atk":.001,"dec":.25,"sus":.0,"rel":.05,"pitch_env":50},
        "Snare": {"wave":"noise",   "freq_base":200,  "atk":.001,"dec":.15,"sus":.0,"rel":.04,"pitch_env":0},
        "HiHat": {"wave":"noise",   "freq_base":8000, "atk":.001,"dec":.04,"sus":.0,"rel":.02,"pitch_env":0},
        "Bass":  {"wave":"saw",     "freq_base":0,    "atk":.005,"dec":.10,"sus":.6,"rel":.15,"pitch_env":0},
        "Lead":  {"wave":"square",  "freq_base":0,    "atk":.01, "dec":.15,"sus":.5,"rel":.20,"pitch_env":0},
        "Pad":   {"wave":"sine",    "freq_base":0,    "atk":.20, "dec":.30,"sus":.7,"rel":.50,"pitch_env":0},
        "Piano": {"wave":"triangle","freq_base":0,    "atk":.005,"dec":.25,"sus":.3,"rel":.30,"pitch_env":0},
    }

    def __init__(self, idx, name=None):
        self.idx = idx
        self.name = name or f"Track {idx+1}"
        self.preset = list(self.SYNTH_PRESETS.keys())[idx % len(self.SYNTH_PRESETS)]
        self.patterns = {}; self.muted = False; self.solo = False
        self.vol = 0.75; self.pan = 0.0
        self.sample_path = None; self.sample_data = None

    def synth_params(self): return dict(self.SYNTH_PRESETS.get(self.preset, self.SYNTH_PRESETS["Lead"]))

    def render_note(self, midi_note, duration_sec, vel=100):
        vol = self.vol * (vel / 127.0)
        if self.sample_data:
            n = min(int(SR*duration_sec), len(self.sample_data))
            s = self.sample_data[:n] + [0.0]*max(0, int(SR*duration_sec)-n)
            return [x*vol for x in s]
        p = self.synth_params()
        freq = p["freq_base"] if p["freq_base"] > 0 else (
               midi_to_freq(midi_note) if midi_note else 261.63)
        raw = gen_wave(freq, duration_sec + p["rel"], p["wave"], vol)
        if p.get("pitch_env",0) > 0:
            pe = p["pitch_env"]
            for i in range(len(raw)):
                t_  = i/SR; env = math.exp(-t_*15)
                f2  = freq*(1 + pe*env)
                raw[i] = math.sin(2*math.pi*f2*i/SR)*vol*max(0, 1-t_/duration_sec)
        return adsr(raw, p["atk"], p["dec"], p["sus"], p["rel"])

    def load_sample(self, path):
        result = MP3Codec.load_any_audio(path)
        if result:
            self.sample_data, _ = result
            self.sample_path = str(path); return True
        return False

    def to_dict(self):
        return {"idx":self.idx,"name":self.name,"preset":self.preset,
                "muted":self.muted,"solo":self.solo,"vol":self.vol,"pan":self.pan,
                "sample_path":self.sample_path,
                "patterns":{k:v.to_dict() for k,v in self.patterns.items()}}

    @classmethod
    def from_dict(cls, d):
        t = cls(d["idx"], d.get("name"))
        t.preset = d.get("preset","Lead")
        t.muted  = d.get("muted",False); t.solo = d.get("solo",False)
        t.vol    = d.get("vol",.75);     t.pan  = d.get("pan",0.)
        t.sample_path = d.get("sample_path")
        t.patterns = {k:DAWPattern.from_dict(v) for k,v in d.get("patterns",{}).items()}
        if t.sample_path:
            try: t.load_sample(t.sample_path)
            except: pass
        return t

class DAWProject:
    N_TRACKS = 8

    def __init__(self):
        self.bpm = 120; self.steps_per_bar = 16; self.bars_per_loop = 4
        self.loop_count = 8; self.swing = 0.0
        self.tracks = [DAWTrack(i) for i in range(self.N_TRACKS)]
        self.arrangement = []; self.active_pats = [None]*self.N_TRACKS

    def total_steps(self): return self.steps_per_bar * self.bars_per_loop
    def step_duration(self): return 60.0 / self.bpm / (self.steps_per_bar / 4)

    def render_loop(self, progress_cb=None):
        total_steps = self.total_steps()
        step_dur    = self.step_duration()
        loop_dur    = total_steps * step_dur
        n_samples   = int(SR * loop_dur)
        mix         = [0.0] * n_samples
        any_solo    = any(t.solo for t in self.tracks)

        for ti, track in enumerate(self.tracks):
            if track.muted or (any_solo and not track.solo): continue
            pat_name = self.active_pats[ti]
            pat = (track.patterns.get(pat_name) if pat_name else
                   (list(track.patterns.values())[0] if track.patterns else None))
            if not pat: continue

            # step grid notes
            for step_idx, active in enumerate(pat.step_data[:total_steps]):
                if not active: continue
                t_start = step_idx * step_dur
                if self.swing > 0 and step_idx % 2 == 1:
                    t_start += step_dur * self.swing * 0.5
                samples = track.render_note(60, step_dur + track.synth_params()["rel"])
                i_start = int(t_start * SR)
                for i, v in enumerate(samples):
                    idx = i_start + i
                    if idx < n_samples:
                        mix[idx] = min(1.0, max(-1.0, mix[idx] + v * track.vol))

            # piano roll notes
            for note in pat.notes:
                t_start = note.start_step * step_dur
                if self.swing > 0 and note.start_step % 2 == 1:
                    t_start += step_dur * self.swing * 0.5
                n_dur   = note.length_steps * step_dur
                samples = track.render_note(note.midi, n_dur + track.synth_params()["rel"], note.vel)
                i_start = int(t_start * SR)
                for i, v in enumerate(samples):
                    idx = i_start + i
                    if idx < n_samples:
                        mix[idx] = min(1.0, max(-1.0, mix[idx] + v * track.vol))

            if progress_cb: progress_cb(ti+1, self.N_TRACKS)
        return normalize(mix, 0.88)

    def to_dict(self):
        return {"bpm":self.bpm,"steps_per_bar":self.steps_per_bar,
                "bars_per_loop":self.bars_per_loop,"loop_count":self.loop_count,
                "swing":self.swing,"tracks":[t.to_dict() for t in self.tracks],
                "arrangement":self.arrangement,"active_pats":self.active_pats}

    @classmethod
    def from_dict(cls, d):
        proj = cls()
        proj.bpm           = d.get("bpm",120)
        proj.steps_per_bar = d.get("steps_per_bar",16)
        proj.bars_per_loop = d.get("bars_per_loop",4)
        proj.loop_count    = d.get("loop_count",8)
        proj.swing         = d.get("swing",0.)
        proj.tracks        = [DAWTrack.from_dict(td) for td in d.get("tracks",[])]
        while len(proj.tracks) < proj.N_TRACKS:
            proj.tracks.append(DAWTrack(len(proj.tracks)))
        proj.arrangement   = d.get("arrangement",[])
        proj.active_pats   = d.get("active_pats",[None]*proj.N_TRACKS)
        return proj

# ─────────────────────────────────────────────────────────────────────────────
# PIANO ROLL EDITOR
# ─────────────────────────────────────────────────────────────────────────────
class PianoRollEditor(tk.Toplevel):
    PITCH_MIN=36; PITCH_MAX=96; CELL_W=18; KEY_W=36; ROW_H=12

    def __init__(self, master, pattern, track, on_close=None):
        super().__init__(master)
        self.title(f"Piano Roll — {track.name} / {pattern.name}")
        self.geometry("900x520"); self.configure(bg=C["bg"]); self.resizable(True,True)
        self.pat=pattern; self.track=track; self.on_close=on_close
        self._mode="draw"; self._drag_note=None
        self._build(); self.protocol("WM_DELETE_WINDOW",self._close); self._redraw()

    def _build(self):
        tb = tk.Frame(self, bg=C["bg2"]); tb.pack(fill="x", padx=4, pady=2)
        tk.Label(tb, text=f"Piano Roll · {self.track.name} · {self.pat.name}",
                 font=FN["head"], fg=C["acc"], bg=C["bg2"]).pack(side="left",padx=8,pady=4)
        for txt, mode, fg2 in [("✏ Draw","draw",C["ok"]),("⬜ Erase","erase",C["danger"]),
                                ("▶ Play",None,C["acc2"])]:
            cmd = (lambda m=mode: setattr(self,"_mode",m)) if mode else self._play
            tk.Button(tb, text=txt, command=cmd, bg=C["bg3"], fg=fg2,
                      font=FN["small"], relief="flat", bd=0, padx=8, pady=4).pack(side="left",padx=2)
        tk.Button(tb, text="✕", command=self._close, bg=C["bg3"], fg=C["muted"],
                  font=FN["small"], relief="flat", bd=0, padx=8, pady=4).pack(side="right",padx=4)

        cf = tk.Frame(self, bg=C["bg"]); cf.pack(fill="both", expand=True, padx=4, pady=4)
        hs = tk.Scrollbar(cf, orient="horizontal"); hs.pack(side="bottom", fill="x")
        vs = tk.Scrollbar(cf, orient="vertical");   vs.pack(side="right",  fill="y")
        self.canvas = tk.Canvas(cf, bg=C["daw_bg"],
                                xscrollcommand=hs.set, yscrollcommand=vs.set,
                                highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        hs.config(command=self.canvas.xview); vs.config(command=self.canvas.yview)
        self.canvas.bind("<ButtonPress-1>",   self._mdown)
        self.canvas.bind("<B1-Motion>",       self._mmove)
        self.canvas.bind("<ButtonRelease-1>", self._mup)
        self.canvas.bind("<Button-3>",        self._rclick)

    def _pitch_to_y(self,midi): return (self.PITCH_MAX - midi) * self.ROW_H
    def _y_to_pitch(self,y):    return self.PITCH_MAX - int(y // self.ROW_H)
    def _step_to_x(self,step):  return self.KEY_W + step * self.CELL_W
    def _x_to_step(self,x):     return max(0, int((x - self.KEY_W) // self.CELL_W))

    def _redraw(self):
        self.canvas.delete("all")
        n_steps = self.pat.steps
        total_w = self.KEY_W + n_steps*self.CELL_W + 20
        total_h = (self.PITCH_MAX - self.PITCH_MIN + 1)*self.ROW_H + 20
        self.canvas.config(scrollregion=(0, 0, total_w, total_h))
        black_keys = {1,3,6,8,10}

        for midi in range(self.PITCH_MIN, self.PITCH_MAX+1):
            y = self._pitch_to_y(midi); note_oct = midi % 12
            is_black = note_oct in black_keys
            kbg = "#1a1a1a" if is_black else "#f0f0f0"
            kfg = "#ffffff" if is_black else "#000000"
            self.canvas.create_rectangle(0, y, self.KEY_W, y+self.ROW_H, fill=kbg, outline="#333")
            if midi % 12 == 0:
                self.canvas.create_text(self.KEY_W-4, y+self.ROW_H//2,
                    text=f"C{midi//12-1}", fill=kfg, font=FN["tiny"], anchor="e")

        for step in range(n_steps+1):
            x   = self._step_to_x(step)
            col = (C["daw_bar"] if step%self.pat.steps==0 else
                   C["daw_beat"] if step%4==0 else C["daw_grid"])
            for midi in range(self.PITCH_MIN, self.PITCH_MAX+1):
                y = self._pitch_to_y(midi)
                bg = "#0c0e20" if midi%12 in black_keys else C["daw_grid"]
                if step < n_steps:
                    self.canvas.create_rectangle(x, y, x+self.CELL_W, y+self.ROW_H,
                                                 fill=bg, outline=col)
            self.canvas.create_line(x, 0, x, total_h, fill=col,
                                    width=2 if step%4==0 else 1)

        for note in self.pat.notes:
            x1 = self._step_to_x(note.start_step)
            x2 = self._step_to_x(note.start_step + note.length_steps)
            y1 = self._pitch_to_y(note.midi); y2 = y1 + self.ROW_H
            bright = int(200 * note.vel / 127)
            col = f"#{bright:02x}ff{bright//2:02x}"
            self.canvas.create_rectangle(x1+1, y1+1, x2-1, y2-1, fill=col, outline=C["white"])

    def _mdown(self, e):
        cx = self.canvas.canvasx(e.x); cy = self.canvas.canvasy(e.y)
        step = self._x_to_step(cx); pitch = self._y_to_pitch(cy)
        if cx < self.KEY_W:
            threading.Thread(
                target=lambda: play_raw(to_wav_bytes(adsr(self.track.render_note(pitch,.4,100)))),
                daemon=True).start(); return
        if self.PITCH_MIN <= pitch <= self.PITCH_MAX and 0 <= step < self.pat.steps:
            if self._mode == "draw":
                note = DAWNote(pitch, step, 1, 100)
                self.pat.notes.append(note); self._drag_note = note
            elif self._mode == "erase":
                self.pat.notes = [n for n in self.pat.notes
                    if not (n.midi==pitch and n.start_step<=step<n.start_step+n.length_steps)]
            self._redraw()

    def _mmove(self, e):
        if not self._drag_note: return
        step = self._x_to_step(self.canvas.canvasx(e.x))
        self._drag_note.length_steps = max(1, step - self._drag_note.start_step + 1)
        self._redraw()

    def _mup(self, e): self._drag_note = None

    def _rclick(self, e):
        cx = self.canvas.canvasx(e.x); cy = self.canvas.canvasy(e.y)
        step = self._x_to_step(cx); pitch = self._y_to_pitch(cy)
        self.pat.notes = [n for n in self.pat.notes
            if not (n.midi==pitch and n.start_step<=step<n.start_step+n.length_steps)]
        self._redraw()

    def _play(self):
        def _g():
            from copy import deepcopy
            proj = DAWProject(); proj.tracks[0] = deepcopy(self.track)
            proj.tracks[0].patterns = {"pr": self.pat}; proj.active_pats[0] = "pr"
            play_raw(to_wav_bytes(proj.render_loop()))
        threading.Thread(target=_g, daemon=True).start()

    def _close(self):
        if self.on_close: self.on_close()
        self.destroy()

# ─────────────────────────────────────────────────────────────────────────────
# METRONOME ENGINE  (high-precision perf_counter loop)
# ─────────────────────────────────────────────────────────────────────────────
class MetronomeEngine:
    def __init__(self, project):
        self.project = project
        self.running  = False
        self._beat_cb = None
        self._thread  = None
        self._stop_ev = threading.Event()

    def start(self, beat_cb=None):
        self.stop()                          # ensure no ghost thread
        self._beat_cb = beat_cb
        self.running  = True
        self._stop_ev.clear()
        self._thread  = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False
        self._stop_ev.set()
        if self._thread:
            self._thread.join(timeout=0.5)
        self._thread = None

    def _loop(self):
        step_dur  = self.project.step_duration()
        total     = self.project.total_steps()
        step      = 0
        next_time = time.perf_counter()

        while self.running and not self._stop_ev.is_set():
            is_down  = (step % total == 0)
            is_beat  = (step % 4 == 0)
            if is_down or is_beat:
                freq = 880 if is_down else 660
                vol  = .45 if is_down else .25
                threading.Thread(
                    target=lambda f=freq,v=vol: play_raw(to_wav_bytes(
                        adsr(gen_wave(f,.06,"sine",v),atk=.001,dec=.05,sus=.0,rel=.01))),
                    daemon=True).start()
            if self._beat_cb:
                self._beat_cb(step, total)
            step = (step + 1) % total
            next_time += step_dur
            sleep_time = next_time - time.perf_counter()
            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                next_time = time.perf_counter()  # re-sync if behind

# ─────────────────────────────────────────────────────────────────────────────
# DAW — MUSIC STUDIO UI
# ─────────────────────────────────────────────────────────────────────────────
class MusicStudioApp(AppFrame):
    def __init__(self, master):
        super().__init__(master)
        self.proj  = DAWProject()
        self.metro = MetronomeEngine(self.proj)
        self._playing   = False
        self._metro_on  = False
        self._cur_step  = 0
        self._play_stop = threading.Event()
        for i, t in enumerate(self.proj.tracks):
            p = DAWPattern("P1", self.proj.total_steps())
            t.patterns["P1"] = p; self.proj.active_pats[i] = "P1"
        self._build()

    # ── top-level layout ──────────────────────────────────────────────────────
    def _build(self):
        tb = tk.Frame(self, bg=C["daw_head"]); tb.pack(fill="x")
        tk.Label(tb, text="🎵 DAW", font=FN["title"],
                 fg=C["acc"], bg=C["daw_head"]).pack(side="left",padx=8,pady=4)

        self._play_btn = tk.Button(tb, text="▶ PLAY", command=self._toggle_play,
            bg=C["bg3"], fg=C["daw_play"], font=FN["head"],
            relief="flat", bd=0, padx=10, pady=4)
        self._play_btn.pack(side="left", padx=3, pady=4)

        self._metro_btn = tk.Button(tb, text="🎹 Metro", command=self._toggle_metro,
            bg=C["bg3"], fg=C["muted"], font=FN["small"],
            relief="flat", bd=0, padx=8, pady=4)
        self._metro_btn.pack(side="left", padx=2)

        tk.Label(tb, text="BPM:", fg=C["muted"], bg=C["daw_head"], font=FN["small"]).pack(side="left",padx=(10,2))
        self._bpm_var = tk.IntVar(value=self.proj.bpm)
        bspin = tk.Spinbox(tb, from_=40, to=300, textvariable=self._bpm_var,
                           width=5, bg=C["bg3"], fg=C["acc"], font=FN["body"],
                           command=self._update_bpm)
        bspin.pack(side="left",padx=2); bspin.bind("<Return>",lambda e: self._update_bpm())

        tk.Label(tb, text="Bars:", fg=C["muted"], bg=C["daw_head"], font=FN["small"]).pack(side="left",padx=(8,2))
        self._bars_var = tk.IntVar(value=self.proj.bars_per_loop)
        tk.Spinbox(tb, from_=1, to=32, textvariable=self._bars_var, width=4,
                   bg=C["bg3"], fg=C["acc"], font=FN["body"],
                   command=self._update_bars).pack(side="left",padx=2)

        tk.Label(tb, text="×", fg=C["muted"], bg=C["daw_head"], font=FN["small"]).pack(side="left",padx=2)
        self._loops_var = tk.IntVar(value=self.proj.loop_count)
        tk.Spinbox(tb, from_=1, to=999, textvariable=self._loops_var, width=4,
                   bg=C["bg3"], fg=C["acc"], font=FN["body"]).pack(side="left",padx=2)

        tk.Label(tb, text="Swing:", fg=C["muted"], bg=C["daw_head"], font=FN["small"]).pack(side="left",padx=(8,2))
        self._swing_var = tk.DoubleVar(value=0.0)
        tk.Scale(tb, variable=self._swing_var, from_=0, to=0.6, resolution=0.05,
                 orient="horizontal", length=70, bg=C["daw_head"], fg=C["acc"],
                 troughcolor=C["dim"], showvalue=False, highlightthickness=0,
                 command=lambda v: setattr(self.proj,"swing",float(v))).pack(side="left",padx=2)

        for txt,cmd,fg2 in [("💾 Save",self._save,C["acc2"]),("📂 Load",self._load,C["acc"]),
                             ("⬇ WAV",self._export_wav,C["acc3"]),("⬇ MP3",self._export_mp3,C["warn"])]:
            tk.Button(tb, text=txt, command=cmd, bg=C["bg3"], fg=fg2,
                      font=FN["small"], relief="flat", bd=0, padx=6, pady=4).pack(side="right",padx=1,pady=4)

        self._pos_var    = tk.StringVar(value="· "*16)
        self._status_var = tk.StringVar(value="Ready")
        tk.Label(tb, textvariable=self._pos_var,    fg=C["dim"],   bg=C["daw_head"], font=FN["small"]).pack(side="left",padx=4)
        tk.Label(tb, textvariable=self._status_var, fg=C["muted"], bg=C["daw_head"], font=FN["small"]).pack(side="left",padx=6)

        nb = ttk.Notebook(self); nb.pack(fill="both", expand=True, padx=2, pady=2)
        seq_f = tk.Frame(nb, bg=C["daw_bg"]); nb.add(seq_f, text="  🎛 Step Seq  ")
        arr_f = tk.Frame(nb, bg=C["daw_bg"]); nb.add(arr_f, text="  📐 Arrange  ")
        syn_f = tk.Frame(nb, bg=C["daw_bg"]); nb.add(syn_f, text="  🔧 Synth  ")
        gen_f = tk.Frame(nb, bg=C["daw_bg"]); nb.add(gen_f, text="  ✨ Generate  ")
        self._build_step_seq(seq_f)
        self._build_arranger(arr_f)
        self._build_synth(syn_f)
        self._build_generator(gen_f)

    # ── step sequencer ────────────────────────────────────────────────────────
    def _build_step_seq(self, parent):
        hdr = tk.Frame(parent, bg=C["daw_bg"]); hdr.pack(fill="x",padx=2,pady=1)
        tk.Label(hdr, text="Track / Pattern", width=16, bg=C["daw_bg"],
                 fg=C["muted"], font=FN["small"], anchor="w").pack(side="left",padx=2)
        tk.Label(hdr, text="Pat", width=4, bg=C["daw_bg"],
                 fg=C["muted"], font=FN["small"]).pack(side="left")
        slbl = tk.Frame(hdr, bg=C["daw_bg"]); slbl.pack(side="left",padx=2)
        for i in range(16):
            col = (C["daw_bar"] if i%16==0 else C["daw_beat"] if i%4==0 else C["daw_bg"])
            tk.Label(slbl, text=str(i+1), width=2, bg=col,
                     fg=C["muted"], font=FN["tiny"]).pack(side="left")

        self._track_rows = []
        for ti, track in enumerate(self.proj.tracks):
            self._track_rows.append(self._build_track_row(parent, ti, track))

        pmf = tk.Frame(parent, bg=C["bg2"]); pmf.pack(fill="x",padx=4,pady=4)
        self._global_pat_var = tk.StringVar(value="P1")
        tk.Label(pmf, text="Pattern:", fg=C["muted"], bg=C["bg2"], font=FN["small"]).pack(side="left",padx=4)
        tk.Entry(pmf, textvariable=self._global_pat_var, width=8, bg=C["bg3"],
                 fg=C["acc"], font=FN["body"], insertbackground=C["acc"],
                 relief="flat", bd=2).pack(side="left",padx=4)
        for txt, cmd in [("Set All →",self._set_all_pats),
                         ("Save Pat",self._save_pattern),
                         ("Load Pat",self._load_pattern)]:
            tk.Button(pmf, text=txt, command=cmd, bg=C["bg3"], fg=C["acc"],
                      font=FN["small"], relief="flat", bd=0, padx=6, pady=3).pack(side="left",padx=4)

    def _build_track_row(self, parent, ti, track):
        rf = tk.Frame(parent, bg=C["daw_track"], height=30)
        rf.pack(fill="x", padx=2, pady=1); rf.pack_propagate(False)

        nl = tk.Label(rf, text=track.name, width=10, bg=C["daw_track"],
                      fg=C["text"], font=FN["daw"], anchor="w", cursor="hand2")
        nl.pack(side="left",padx=(4,2))
        nl.bind("<Double-Button-1>", lambda e,i=ti: self._rename_track(i))

        m_var = tk.BooleanVar(value=track.muted)
        tk.Checkbutton(rf, text="M", variable=m_var,
            command=lambda i=ti,v=m_var: setattr(self.proj.tracks[i],"muted",v.get()),
            bg=C["daw_track"], fg=C["warn"], selectcolor=C["warn"],
            font=FN["tiny"], indicatoron=0, padx=3, pady=1, relief="flat").pack(side="left",padx=1)

        s_var = tk.BooleanVar(value=track.solo)
        tk.Checkbutton(rf, text="S", variable=s_var,
            command=lambda i=ti,v=s_var: setattr(self.proj.tracks[i],"solo",v.get()),
            bg=C["daw_track"], fg=C["acc2"], selectcolor=C["acc2"],
            font=FN["tiny"], indicatoron=0, padx=3, pady=1, relief="flat").pack(side="left",padx=1)

        vol_v = tk.DoubleVar(value=track.vol)
        tk.Scale(rf, variable=vol_v, from_=0, to=1, resolution=.02,
                 orient="horizontal", length=50, bg=C["daw_track"], fg=C["acc"],
                 troughcolor=C["dim"], showvalue=False, highlightthickness=0,
                 command=lambda v,i=ti: setattr(self.proj.tracks[i],"vol",float(v))).pack(side="left",padx=2)

        pat_names = list(track.patterns.keys()) or ["P1"]
        pat_var   = tk.StringVar(value=self.proj.active_pats[ti] or pat_names[0])
        pat_cb    = ttk.Combobox(rf, textvariable=pat_var, values=pat_names,
                                 width=5, state="readonly", font=FN["tiny"])
        pat_cb.pack(side="left",padx=2)
        pat_cb.bind("<<ComboboxSelected>>",
                    lambda e,i=ti,v=pat_var: self._switch_pat(i,v.get()))

        tk.Button(rf, text="🎹", command=lambda i=ti: self._open_pianoroll(i),
                  bg=C["daw_track"], fg=C["acc3"], font=FN["tiny"],
                  relief="flat", bd=0, padx=4, pady=1).pack(side="left",padx=1)
        tk.Button(rf, text="🔊", command=lambda i=ti: self._import_sample(i),
                  bg=C["daw_track"], fg=C["acc2"], font=FN["tiny"],
                  relief="flat", bd=0, padx=4, pady=1).pack(side="left",padx=1)

        step_frame = tk.Frame(rf, bg=C["daw_track"]); step_frame.pack(side="left",padx=2)
        steps      = self.proj.total_steps()
        step_btns  = []
        for si in range(min(steps,16)):
            pat    = track.patterns.get(self.proj.active_pats[ti], DAWPattern())
            active = pat.step_data[si] if si < len(pat.step_data) else False
            bg     = (C["daw_step_on"] if active else
                      C["daw_beat"]    if si%4==0 else C["daw_step_off"])
            b = tk.Button(step_frame, text="", width=2, height=1, bg=bg,
                          relief="flat", bd=0,
                          command=lambda i=ti,s=si: self._toggle_step(i,s))
            b.grid(row=0, column=si, padx=0, pady=0); step_btns.append(b)

        return {"frame":rf,"step_btns":step_btns,"pat_var":pat_var,
                "pat_cb":pat_cb,"vol_v":vol_v,"m_var":m_var,"s_var":s_var}

    def _toggle_step(self, ti, si):
        pname = self.proj.active_pats[ti]
        if not pname: return
        pat = self.proj.tracks[ti].patterns.get(pname)
        if not pat or si >= len(pat.step_data): return
        pat.step_data[si] = not pat.step_data[si]
        self._refresh_step_row(ti)
        if pat.step_data[si]:
            threading.Thread(
                target=lambda: play_raw(to_wav_bytes(
                    self.proj.tracks[ti].render_note(60,.15))),
                daemon=True).start()

    def _refresh_step_row(self, ti):
        row  = self._track_rows[ti]
        pat  = self.proj.tracks[ti].patterns.get(self.proj.active_pats[ti])
        for si, b in enumerate(row["step_btns"]):
            active = pat.step_data[si] if pat and si < len(pat.step_data) else False
            b.config(bg=C["daw_step_on"] if active else
                       (C["daw_beat"] if si%4==0 else C["daw_step_off"]))

    def _refresh_all_steps(self):
        for ti in range(self.proj.N_TRACKS): self._refresh_step_row(ti)

    def _switch_pat(self, ti, pname):
        self.proj.active_pats[ti] = pname
        self._refresh_step_row(ti)
        self._track_rows[ti]["pat_cb"].config(
            values=list(self.proj.tracks[ti].patterns.keys()))

    def _rename_track(self, ti):
        n = simpledialog.askstring("Rename","New name:",
            initialvalue=self.proj.tracks[ti].name, parent=self)
        if n: self.proj.tracks[ti].name = n

    def _set_all_pats(self):
        pname = self._global_pat_var.get().strip()
        if not pname: return
        for ti, track in enumerate(self.proj.tracks):
            if pname not in track.patterns:
                track.patterns[pname] = DAWPattern(pname, self.proj.total_steps())
            self.proj.active_pats[ti] = pname
        self._refresh_all_steps(); self._update_all_pat_cbs()

    def _update_all_pat_cbs(self):
        for ti, row in enumerate(self._track_rows):
            row["pat_cb"].config(values=list(self.proj.tracks[ti].patterns.keys()))
            if self.proj.active_pats[ti]: row["pat_var"].set(self.proj.active_pats[ti])

    def _save_pattern(self):
        ti = 0; pname = self.proj.active_pats[ti]
        if not pname: return
        pat = self.proj.tracks[ti].patterns.get(pname)
        if not pat: return
        fp = filedialog.asksaveasfilename(defaultextension=".pypat",
                                          initialdir=BASE_DIR/"patterns",
                                          filetypes=[("Pattern","*.pypat")])
        if fp: Path(fp).write_text(json.dumps(pat.to_dict())); self._status_var.set(f"Saved: {Path(fp).name}")

    def _load_pattern(self):
        fp = filedialog.askopenfilename(initialdir=BASE_DIR/"patterns",
                                         filetypes=[("Pattern","*.pypat"),("All","*.*")])
        if not fp: return
        try:
            pat = DAWPattern.from_dict(json.loads(Path(fp).read_text()))
            self.proj.tracks[0].patterns[pat.name] = pat
            self.proj.active_pats[0] = pat.name
            self._refresh_step_row(0); self._update_all_pat_cbs()
            self._status_var.set(f"Loaded: {pat.name}")
        except Exception as e: messagebox.showerror("Error",str(e))

    def _open_pianoroll(self, ti):
        track  = self.proj.tracks[ti]
        pname  = self.proj.active_pats[ti]
        if not pname: messagebox.showinfo("No Pattern","Select or create a pattern first."); return
        pat = track.patterns.setdefault(pname, DAWPattern(pname, self.proj.total_steps()))
        PianoRollEditor(self, pat, track)

    def _import_sample(self, ti):
        fp = filedialog.askopenfilename(
            filetypes=[("Audio","*.wav *.mp3 *.ogg *.flac"),("WAV","*.wav"),("All","*.*")],
            title=f"Import sample for {self.proj.tracks[ti].name}")
        if fp:
            ok = self.proj.tracks[ti].load_sample(fp)
            self._status_var.set(f"T{ti+1}: {'loaded' if ok else 'FAILED'} {Path(fp).name}")

    # ── arranger ─────────────────────────────────────────────────────────────
    def _build_arranger(self, parent):
        tk.Label(parent, text="Left-click cell → set pattern.  Right-click → clear.",
                 fg=C["muted"], bg=C["daw_bg"], font=FN["small"]).pack(anchor="w",padx=8,pady=4)
        gf = tk.Frame(parent, bg=C["daw_bg"]); gf.pack(fill="both",expand=True,padx=6)
        N_BARS = 16
        tk.Label(gf, text="", width=10, bg=C["daw_bg"]).grid(row=0,column=0)
        for b in range(N_BARS):
            tk.Label(gf, text=str(b+1), width=4,
                     bg=C["daw_bar"] if b%4==0 else C["daw_bg"],
                     fg=C["muted"], font=FN["tiny"]).grid(row=0,column=b+1,padx=1)
        self._arr_btns = []
        for ti, track in enumerate(self.proj.tracks):
            row_btns = []
            tk.Label(gf, text=track.name, width=10, bg=C["daw_track"],
                     fg=C["text"], font=FN["small"], anchor="w").grid(
                         row=ti+1, column=0, sticky="ew", padx=1, pady=1)
            for b in range(N_BARS):
                cur = self._get_arr(ti,b)
                btn = tk.Button(gf, text=cur or "", width=4, height=1,
                    bg=C["ok"] if cur else C["bg3"],
                    fg=C["black"] if cur else C["muted"],
                    font=FN["tiny"], relief="flat", bd=0,
                    command=lambda i=ti,bb=b: self._arr_click(i,bb))
                btn.grid(row=ti+1, column=b+1, padx=1, pady=1)
                btn.bind("<Button-3>", lambda e,i=ti,bb=b: self._arr_clear(i,bb))
                row_btns.append(btn)
            self._arr_btns.append(row_btns)

    def _get_arr(self, ti, bar):
        for e in self.proj.arrangement:
            if e.get("track_idx")==ti and e.get("bar_start")==bar:
                return e.get("pat_name","")
        return None

    def _set_arr(self, ti, bar, pname):
        self.proj.arrangement = [e for e in self.proj.arrangement
            if not (e.get("track_idx")==ti and e.get("bar_start")==bar)]
        if pname: self.proj.arrangement.append({"track_idx":ti,"bar_start":bar,"pat_name":pname})

    def _arr_click(self, ti, bar):
        cur = self._get_arr(ti,bar) or (list(self.proj.tracks[ti].patterns.keys())[0]
              if self.proj.tracks[ti].patterns else "")
        new = simpledialog.askstring("Pattern",f"Pattern for T{ti+1} Bar{bar+1}:",
                                     initialvalue=cur, parent=self)
        if new is not None: self._set_arr(ti, bar, new.strip()); self._refresh_arr()

    def _arr_clear(self, ti, bar): self._set_arr(ti,bar,None); self._refresh_arr()

    def _refresh_arr(self):
        if not hasattr(self,"_arr_btns"): return
        for ti in range(self.proj.N_TRACKS):
            for bar in range(16):
                cur = self._get_arr(ti,bar); btn = self._arr_btns[ti][bar]
                btn.config(text=cur or "",
                           bg=C["ok"] if cur else C["bg3"],
                           fg=C["black"] if cur else C["muted"])

    # ── synth panel ───────────────────────────────────────────────────────────
    def _build_synth(self, parent):
        nb2 = ttk.Notebook(parent); nb2.pack(fill="both",expand=True,padx=4,pady=4)
        for ti, track in enumerate(self.proj.tracks):
            tf = tk.Frame(nb2, bg=C["bg"]); nb2.add(tf,text=f"T{ti+1}")
            self._build_track_synth(tf, ti, track)

    def _build_track_synth(self, parent, ti, track):
        tk.Label(parent,text=f"Track {ti+1}: {track.name}",
                 fg=C["acc"],font=FN["head"],bg=C["bg"]).pack(anchor="w",padx=8,pady=6)
        pf = tk.Frame(parent,bg=C["bg"]); pf.pack(fill="x",padx=8,pady=2)
        tk.Label(pf,text="Preset:",fg=C["muted"],bg=C["bg"],font=FN["small"]).pack(side="left")
        p_var = tk.StringVar(value=track.preset)
        p_cb  = ttk.Combobox(pf,textvariable=p_var,
                              values=list(DAWTrack.SYNTH_PRESETS.keys()),
                              width=12,state="readonly")
        p_cb.pack(side="left",padx=6)
        p_cb.bind("<<ComboboxSelected>>",lambda e,i=ti,v=p_var: setattr(self.proj.tracks[i],"preset",v.get()))

        for label,attr,lo,hi,res,fg2 in [("Vol","vol",0,1,.02,C["acc"]),("Pan","pan",-1,1,.05,C["acc2"])]:
            f = tk.Frame(parent,bg=C["bg"]); f.pack(fill="x",padx=8,pady=2)
            tk.Label(f,text=f"{label}:",fg=C["muted"],bg=C["bg"],font=FN["small"]).pack(side="left")
            v = tk.DoubleVar(value=getattr(track,attr))
            tk.Scale(f,variable=v,from_=lo,to=hi,resolution=res,orient="horizontal",
                     length=180,bg=C["bg"],fg=fg2,troughcolor=C["dim"],showvalue=True,
                     highlightthickness=0,
                     command=lambda val,i=ti,a=attr: setattr(self.proj.tracks[i],a,float(val))
                     ).pack(side="left",padx=6)

        tk.Button(parent,text="▶ Test Note",
            command=lambda i=ti: threading.Thread(
                target=lambda: play_raw(to_wav_bytes(self.proj.tracks[i].render_note(60,.6,100))),
                daemon=True).start(),
            bg=C["bg3"],fg=C["ok"],font=FN["small"],relief="flat",bd=0,padx=10,pady=4
        ).pack(anchor="w",padx=8,pady=4)

        sif = tk.Frame(parent,bg=C["bg"]); sif.pack(fill="x",padx=8,pady=2)
        lbl = tk.Label(sif,
            text=f"Sample: {Path(track.sample_path).name if track.sample_path else 'None'}",
            fg=C["muted"],bg=C["bg"],font=FN["small"])
        lbl.pack(side="left")
        tk.Button(sif,text="Import Audio",
            command=lambda i=ti,l=lbl: self._import_sample_syn(i,l),
            bg=C["bg3"],fg=C["acc2"],font=FN["small"],relief="flat",bd=0,padx=6,pady=2
        ).pack(side="left",padx=6)
        tk.Button(sif,text="Clear",
            command=lambda i=ti,l=lbl: (
                setattr(self.proj.tracks[i],"sample_data",None),
                setattr(self.proj.tracks[i],"sample_path",None),
                l.config(text="Sample: None")),
            bg=C["bg3"],fg=C["danger"],font=FN["small"],relief="flat",bd=0,padx=6,pady=2
        ).pack(side="left")

    def _import_sample_syn(self, ti, lbl):
        fp = filedialog.askopenfilename(
            filetypes=[("Audio","*.wav *.mp3 *.ogg *.flac"),("All","*.*")])
        if fp:
            ok = self.proj.tracks[ti].load_sample(fp)
            lbl.config(text=f"Sample: {Path(fp).name}" if ok else "Sample: LOAD FAILED")

    # ── pattern generator ─────────────────────────────────────────────────────
    def _build_generator(self, parent):
        tk.Label(parent, text="Auto-generate patterns using scales & rhythms",
                 fg=C["muted"],bg=C["daw_bg"],font=FN["small"]).pack(anchor="w",padx=8,pady=6)
        cf = tk.Frame(parent,bg=C["daw_bg"]); cf.pack(fill="x",padx=8,pady=4)
        fields = [
            ("Track:",    ttk.Combobox,
             {"values":[f"T{i+1} {self.proj.tracks[i].name}" for i in range(self.proj.N_TRACKS)],
              "width":14,"state":"readonly"}, "T1 Track 1"),
            ("Pat Name:", tk.Entry,
             {"width":10,"bg":C["bg3"],"fg":C["acc"],"font":FN["body"],
              "insertbackground":C["acc"],"relief":"flat","bd":2}, "Gen1"),
            ("Style:",    ttk.Combobox,
             {"values":["Drums (4-on-floor)","Drums (breakbeat)","Bass (pentatonic)",
                        "Melody (major)","Melody (minor)","Melody (blues)",
                        "Chord Stabs","Random"],"width":18,"state":"readonly"},
             "Drums (4-on-floor)"),
            ("Root:",     ttk.Combobox, {"values":NOTE_NAMES,"width":6,"state":"readonly"}, "C"),
            ("Octave:",   ttk.Combobox, {"values":["2","3","4","5","6"],"width":5,"state":"readonly"}, "4"),
        ]
        self._gen_w = {}
        for ri,(label,wtype,kw,default) in enumerate(fields):
            tk.Label(cf,text=label,fg=C["muted"],bg=C["daw_bg"],font=FN["small"]).grid(
                row=ri,column=0,sticky="w",padx=4,pady=3)
            w = wtype(cf,**kw); w.grid(row=ri,column=1,sticky="w",padx=4,pady=3)
            if hasattr(w,"set"):    w.set(default)
            elif hasattr(w,"insert"): w.insert(0,default)
            self._gen_w[label] = w

        tk.Label(cf,text="Density:",fg=C["muted"],bg=C["daw_bg"],font=FN["small"]).grid(
            row=len(fields),column=0,sticky="w",padx=4,pady=3)
        self._gen_dens = tk.Scale(cf,from_=0.1,to=1.0,resolution=.05,orient="horizontal",
                                   length=160,bg=C["daw_bg"],fg=C["acc"],troughcolor=C["dim"],
                                   showvalue=True,highlightthickness=0)
        self._gen_dens.set(0.6); self._gen_dens.grid(row=len(fields),column=1,sticky="w",padx=4,pady=3)

        tk.Button(cf,text="✨ Generate",command=self._do_generate,
                  bg=C["bg3"],fg=C["acc"],font=FN["head"],relief="flat",bd=0,padx=12,pady=6
                  ).grid(row=len(fields)+1,column=0,columnspan=2,pady=8)

        self._gen_status = tk.Label(parent,text="",fg=C["ok"],bg=C["daw_bg"],font=FN["small"])
        self._gen_status.pack(anchor="w",padx=8)

    def _do_generate(self):
        t_str  = self._gen_w["Track:"].get()
        t_idx  = int(t_str[1]) - 1
        track  = self.proj.tracks[t_idx]
        pname  = self._gen_w["Pat Name:"].get().strip() or "Gen1"
        style  = self._gen_w["Style:"].get()
        root   = self._gen_w["Root:"].get()
        octave = int(self._gen_w["Octave:"].get())
        dens   = self._gen_dens.get()
        steps  = self.proj.total_steps()
        pat    = DAWPattern(pname, steps)
        root_midi = octave*12 + NOTE_NAMES.index(root)

        if "4-on-floor" in style:
            for i in range(steps):
                if i%4 == 0: pat.step_data[i] = True
        elif "breakbeat" in style:
            for i in range(steps):
                if E.random() < dens*0.5: pat.step_data[i] = True
        elif "Bass" in style:
            scale = SCALES["pentatonic"]
            for i in range(steps):
                if E.random() < dens*0.4:
                    pat.step_data[i] = True
                    pat.notes.append(DAWNote(root_midi+E.choice(scale),i,2,90))
        elif "Melody" in style:
            sc = "blues" if "blues" in style else ("minor" if "minor" in style else "major")
            scale = SCALES[sc]
            for i in range(steps):
                if E.random() < dens*0.35:
                    pat.notes.append(DAWNote(root_midi+12+E.choice(scale),i,
                                             E.randint(1,4), 80+E.randint(-10,10)))
        elif "Chord" in style:
            chord = CHORD_TYPES["maj"]
            for i in range(0,steps,4):
                if E.random() < dens:
                    for iv in chord: pat.notes.append(DAWNote(root_midi+iv,i,2,75))
        else:
            for i in range(steps):
                if E.random() < dens*0.3:
                    pat.step_data[i] = True
                    pat.notes.append(DAWNote(root_midi+E.randint(0,11),i,
                                             E.randint(1,3), 70+E.randint(0,30)))

        track.patterns[pname] = pat
        self.proj.active_pats[t_idx] = pname
        self._refresh_step_row(t_idx); self._update_all_pat_cbs(); self._refresh_arr()
        self._gen_status.config(text=f"✅ Generated '{pname}' on {track.name}")

    # ── high-precision playback loop ──────────────────────────────────────────
    def _toggle_play(self):
        self._playing = not self._playing
        if self._playing:
            self._play_btn.config(text="⏸ STOP", fg=C["danger"])
            self._play_stop.clear()
            threading.Thread(target=self._play_loop_thread, daemon=True).start()
        else:
            self._play_stop.set()
            self._playing = False
            self._play_btn.config(text="▶ PLAY", fg=C["daw_play"])

    def _play_loop_thread(self):
        loop_count  = self._loops_var.get()
        step_dur    = self.proj.step_duration()
        total_steps = self.proj.total_steps()
        any_solo    = any(t.solo for t in self.proj.tracks)
        next_time   = time.perf_counter()

        for _ in range(loop_count):
            if self._play_stop.is_set(): break
            for step in range(total_steps):
                if self._play_stop.is_set(): break
                self._cur_step = step
                self.after(0, self._update_step_indicator, step, total_steps)

                for ti, track in enumerate(self.proj.tracks):
                    if track.muted or (any_solo and not track.solo): continue
                    pat = track.patterns.get(self.proj.active_pats[ti])
                    if not pat: continue
                    # step-grid trigger
                    if step < len(pat.step_data) and pat.step_data[step]:
                        threading.Thread(
                            target=lambda i=ti: play_raw(to_wav_bytes(
                                self.proj.tracks[i].render_note(60, step_dur*1.5))),
                            daemon=True).start()
                    # piano-roll notes at this step
                    for note in pat.notes:
                        if note.start_step == step:
                            threading.Thread(
                                target=lambda i=ti,m=note.midi,ls=note.length_steps,vel=note.vel:
                                    play_raw(to_wav_bytes(
                                        self.proj.tracks[i].render_note(m, step_dur*ls, vel))),
                                daemon=True).start()

                next_time += step_dur
                sleep_time = next_time - time.perf_counter()
                if sleep_time > 0:
                    time.sleep(sleep_time)
                else:
                    next_time = time.perf_counter()  # re-sync on overrun

        self._playing = False
        self.after(0, lambda: self._play_btn.config(text="▶ PLAY", fg=C["daw_play"]))
        self.after(0, self._update_step_indicator, -1, total_steps)

    def _update_step_indicator(self, step, total):
        bars = self.proj.bars_per_loop; spb = self.proj.steps_per_bar
        parts = []
        for bar in range(bars):
            bar_steps = ["●" if bar*spb+si==step else "·" for si in range(spb)]
            parts.append(" ".join(bar_steps))
        self._pos_var.set("  |  ".join(parts))
        for ti, row in enumerate(self._track_rows):
            pat = self.proj.tracks[ti].patterns.get(self.proj.active_pats[ti])
            for si, btn in enumerate(row["step_btns"]):
                active = pat.step_data[si] if pat and si < len(pat.step_data) else False
                if si == step: btn.config(bg=C["warn"])
                else: btn.config(bg=C["daw_step_on"] if active else
                                    (C["daw_beat"] if si%4==0 else C["daw_step_off"]))

    def _toggle_metro(self):
        self._metro_on = not self._metro_on
        if self._metro_on:
            self.proj.bpm = self._bpm_var.get(); self.metro.project = self.proj
            self.metro.start(lambda s,t: self.after(0,self._update_step_indicator,s,t))
            self._metro_btn.config(fg=C["warn"])
        else:
            self.metro.stop(); self._metro_btn.config(fg=C["muted"])

    def _update_bpm(self):
        try: self.proj.bpm = int(self._bpm_var.get())
        except: pass

    def _update_bars(self):
        try:
            bars = int(self._bars_var.get()); self.proj.bars_per_loop = bars
            new_steps = self.proj.total_steps()
            for track in self.proj.tracks:
                for pat in track.patterns.values():
                    if len(pat.step_data) < new_steps:
                        pat.step_data.extend([False]*(new_steps-len(pat.step_data)))
                    else:
                        pat.step_data = pat.step_data[:new_steps]
                    pat.steps = new_steps
            self._refresh_all_steps()
        except: pass

    def _save(self):
        fp = filedialog.asksaveasfilename(defaultextension=".pysong",
            initialdir=BASE_DIR/"songs",
            filetypes=[("Pysplore Song","*.pysong"),("JSON","*.json")])
        if fp: Path(fp).write_text(json.dumps(self.proj.to_dict(),indent=2))
        if fp: self._status_var.set(f"Saved: {Path(fp).name}")

    def _load(self):
        fp = filedialog.askopenfilename(initialdir=BASE_DIR/"songs",
            filetypes=[("Pysplore Song","*.pysong"),("JSON","*.json")])
        if not fp: return
        try:
            self.proj = DAWProject.from_dict(json.loads(Path(fp).read_text()))
            self.metro.project = self.proj
            self._bpm_var.set(self.proj.bpm)
            self._bars_var.set(self.proj.bars_per_loop)
            self._loops_var.set(self.proj.loop_count)
            self._refresh_all_steps(); self._refresh_arr()
            self._status_var.set(f"Loaded: {Path(fp).name}")
        except Exception as e: messagebox.showerror("Load Error",str(e))

    def _export_wav(self):
        fp = filedialog.asksaveasfilename(defaultextension=".wav",
            initialdir=BASE_DIR/"exports", filetypes=[("WAV","*.wav")])
        if not fp: return
        self._status_var.set("Rendering…")
        def _g():
            try:
                loops  = self._loops_var.get()
                single = self.proj.render_loop()
                all_s  = normalize(single * loops)
                Path(fp).write_bytes(to_wav_bytes(all_s))
                self.after(0, lambda: self._status_var.set(f"Exported WAV: {Path(fp).name}"))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Export Error",str(e)))
        threading.Thread(target=_g, daemon=True).start()

    def _export_mp3(self):
        if not MP3Codec.can_encode():
            messagebox.showinfo("MP3 Export",
                "No encoder found.\nInstall ffmpeg (recommended) for MP3 export.\nExporting as WAV instead.")
            self._export_wav(); return
        fp = filedialog.asksaveasfilename(defaultextension=".mp3",
            initialdir=BASE_DIR/"exports", filetypes=[("MP3","*.mp3")])
        if not fp: return
        self._status_var.set("Rendering → MP3…")
        def _g():
            try:
                loops = self._loops_var.get(); single = self.proj.render_loop()
                wav_b = to_wav_bytes(normalize(single*loops))
                tmp   = tempfile.mktemp(suffix=".wav"); Path(tmp).write_bytes(wav_b)
                ok, msg = MP3Codec.wav_to_mp3(tmp, fp)
                try: os.unlink(tmp)
                except: pass
                if ok: self.after(0,lambda: self._status_var.set(f"Exported MP3: {Path(fp).name}"))
                else:  self.after(0,lambda: messagebox.showerror("MP3 Error",msg))
            except Exception as e:
                self.after(0,lambda: messagebox.showerror("Export Error",str(e)))
        threading.Thread(target=_g, daemon=True).start()

    def on_destroy(self):
        self._play_stop.set(); self._playing = False; self.metro.stop()

# ─────────────────────────────────────────────────────────────────────────────
# MEDIA PLAYER
# ─────────────────────────────────────────────────────────────────────────────
class MediaPlayerApp(AppFrame):
    def __init__(self, master):
        super().__init__(master)
        self._playlist = []; self._idx = 0; self._playing = False
        self._proc = None; self._stop_ev = threading.Event()
        self._build()

    def _build(self):
        self._hdr("📻  Media Player")
        ctrl = tk.Frame(self,bg=C["bg2"]); ctrl.pack(fill="x",padx=8,pady=4)
        for txt,cmd in [("📂 Add Files",self._add),("🗑 Clear",self._clear),
                        ("▶ Play",self._play),("⏸ Pause/Stop",self._stop),
                        ("⏮ Prev",self._prev),("⏭ Next",self._next)]:
            tk.Button(ctrl,text=txt,command=cmd,bg=C["bg3"],fg=C["acc"],
                      font=FN["small"],relief="flat",bd=0,padx=8,pady=6
                      ).pack(side="left",padx=2,pady=2)

        self._now = tk.StringVar(value="No media loaded")
        tk.Label(self,textvariable=self._now,fg=C["acc2"],bg=C["bg"],
                 font=FN["body"],wraplength=600).pack(padx=8,pady=4)

        lf = tk.Frame(self,bg=C["bg"]); lf.pack(fill="both",expand=True,padx=8,pady=4)
        sb = tk.Scrollbar(lf); sb.pack(side="right",fill="y")
        self._lb = tk.Listbox(lf,bg=C["bg2"],fg=C["text"],font=FN["body"],
                              yscrollcommand=sb.set,selectbackground=C["acc3"],
                              selectforeground=C["white"],relief="flat",bd=0)
        self._lb.pack(fill="both",expand=True); sb.config(command=self._lb.yview)
        self._lb.bind("<Double-Button-1>",lambda e: self._play_idx(self._lb.curselection()[0] if self._lb.curselection() else 0))

    def _add(self):
        files = filedialog.askopenfilenames(
            filetypes=[("Audio/Video","*.mp3 *.wav *.ogg *.flac *.mp4 *.mkv *.avi *.m4a *.aac"),("All","*.*")])
        for f in files:
            self._playlist.append(Path(f))
            self._lb.insert(tk.END, Path(f).name)

    def _clear(self):
        self._stop(); self._playlist.clear(); self._lb.delete(0,tk.END)
        self._now.set("Playlist cleared")

    def _play(self):
        if not self._playlist: return
        self._play_idx(self._idx)

    def _play_idx(self, idx):
        self._stop(); self._idx = idx
        p = self._playlist[idx]
        self._now.set(f"▶ {p.name}")
        self._lb.selection_clear(0,tk.END); self._lb.selection_set(idx); self._lb.see(idx)
        self._playing = True; self._stop_ev.clear()
        threading.Thread(target=self._play_thread, args=(p,), daemon=True).start()

    def _play_thread(self, path):
        try:
            pl, ex = find_player()
            if pl:
                self._proc = subprocess.Popen(
                    [pl]+ex+[str(path)],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self._proc.wait()
            else:
                # fallback: load as wav and play
                result = MP3Codec.load_any_audio(path)
                if result:
                    data, _ = result
                    play_raw(to_wav_bytes(data), block=True)
        except: pass
        if not self._stop_ev.is_set():
            self.after(100, self._next)

    def _stop(self):
        self._playing = False; self._stop_ev.set()
        if self._proc:
            try: self._proc.terminate()
            except: pass
            self._proc = None

    def _prev(self):
        if not self._playlist: return
        self._play_idx((self._idx - 1) % len(self._playlist))

    def _next(self):
        if not self._playlist: return
        self._play_idx((self._idx + 1) % len(self._playlist))

    def on_destroy(self): self._stop()

# ─────────────────────────────────────────────────────────────────────────────
# PAINT APP (Sky Blue Gradient Canvas + Lime Green Brush)
# ─────────────────────────────────────────────────────────────────────────────
class PaintApp(AppFrame):
    def __init__(self, master):
        super().__init__(master)
        self._color = "#8BC34A"      # Lime green brush
        self._size = 4
        self._tool = "pen"
        self._last = None
        self._build()

    def _build(self):
        tb = tk.Frame(self, bg=C["bg2"])
        tb.pack(fill="x")
        for txt, t in [("✏ Pen","pen"), ("○ Circle","circle"), ("□ Rect","rect"),
                       ("⬡ Fill","fill"), ("⬜ Erase","erase")]:
            tk.Button(tb, text=txt, command=lambda x=t: setattr(self, "_tool", x),
                      bg=C["bg3"], fg=C["acc"], font=FN["small"], relief="flat",
                      bd=0, padx=6, pady=4).pack(side="left", padx=2, pady=3)
        tk.Button(tb, text="🎨 Color", command=self._pick_color,
                  bg=C["bg3"], fg=C["acc2"], font=FN["small"], relief="flat",
                  bd=0, padx=6, pady=4).pack(side="left", padx=2)
        tk.Button(tb, text="🗑 Clear", command=self._clear,
                  bg=C["bg3"], fg=C["danger"], font=FN["small"], relief="flat",
                  bd=0, padx=6, pady=4).pack(side="left", padx=2)
        tk.Button(tb, text="💾 Save", command=self._save,
                  bg=C["bg3"], fg=C["ok"], font=FN["small"], relief="flat",
                  bd=0, padx=6, pady=4).pack(side="left", padx=2)
        tk.Label(tb, text="Size:", fg=C["muted"], bg=C["bg2"], font=FN["small"]).pack(
            side="left", padx=(8, 2))
        self._sz_var = tk.IntVar(value=4)
        tk.Spinbox(tb, from_=1, to=50, textvariable=self._sz_var, width=4,
                   bg=C["bg3"], fg=C["acc"], font=FN["body"],
                   command=lambda: setattr(self, "_size", self._sz_var.get())).pack(
            side="left", padx=2)

        # Canvas with gradient background
        self.canvas = tk.Canvas(self, cursor="crosshair", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=4, pady=4)
        self._draw_gradient()  # initial gradient

        self.canvas.bind("<ButtonPress-1>", self._mdown)
        self.canvas.bind("<B1-Motion>", self._mmove)
        self.canvas.bind("<ButtonRelease-1>", self._mup)
        self.canvas.bind("<Configure>", lambda e: self._draw_gradient())

    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _draw_gradient(self):
        """Create vertical gradient from #E1F5FE to #81D4FA."""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width <= 1 or height <= 1:
            return
        self.canvas.delete("gradient")
        top = self._hex_to_rgb("#E1F5FE")
        bottom = self._hex_to_rgb("#81D4FA")
        steps = 100
        for i in range(steps):
            ratio = i / steps
            r = int(top[0] + (bottom[0] - top[0]) * ratio)
            g = int(top[1] + (bottom[1] - top[1]) * ratio)
            b = int(top[2] + (bottom[2] - top[2]) * ratio)
            fill = f'#{r:02x}{g:02x}{b:02x}'
            y0 = int(i * height / steps)
            y1 = int((i + 1) * height / steps)
            self.canvas.create_rectangle(0, y0, width, y1, fill=fill, outline="",
                                         tags="gradient")
        self.canvas.tag_lower("gradient")

    def _pick_color(self):
        c = colorchooser.askcolor(title="Pick colour", color=self._color)
        if c[1]:
            self._color = c[1]

    def _clear(self):
        self.canvas.delete("all")
        self._draw_gradient()

    def _save(self):
        if not HAS_PIL:
            messagebox.showinfo("Save", "Pillow not installed – cannot save.")
            return
        fp = filedialog.asksaveasfilename(defaultextension=".png",
                                          initialdir=BASE_DIR/"saves",
                                          filetypes=[("PNG", "*.png")])
        if not fp:
            return
        try:
            self.canvas.postscript(file=fp+".ps", colormode='color')
            img = Image.open(fp+".ps")
            img.save(fp, 'png')
            os.unlink(fp+".ps")
            messagebox.showinfo("Saved", f"Saved to {fp}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def _mdown(self, e):
        self._last = (e.x, e.y)
        if self._tool == "fill":
            self.canvas.create_rectangle(0, 0, self.canvas.winfo_width(),
                                         self.canvas.winfo_height(),
                                         fill=self._color, outline="")

    def _mmove(self, e):
        if not self._last:
            return
        x0, y0 = self._last
        x1, y1 = e.x, e.y
        if self._tool in ("pen", "erase"):
            col = "#E1F5FE" if self._tool == "erase" else self._color
            self.canvas.create_line(x0, y0, x1, y1, fill=col,
                                    width=self._size, capstyle="round", smooth=True)
            self._last = (x1, y1)

    def _mup(self, e):
        if not self._last:
            return
        x0, y0 = self._last
        x1, y1 = e.x, e.y
        if self._tool == "circle":
            self.canvas.create_oval(x0, y0, x1, y1, outline=self._color, width=self._size)
        elif self._tool == "rect":
            self.canvas.create_rectangle(x0, y0, x1, y1, outline=self._color, width=self._size)
        self._last = None

# ─────────────────────────────────────────────────────────────────────────────
# JOURNAL
# ─────────────────────────────────────────────────────────────────────────────
class JournalApp(AppFrame):
    def __init__(self, master):
        super().__init__(master)
        self._entries = {}; self._cur = None; self._load_all(); self._build()

    def _load_all(self):
        for f in (BASE_DIR/"journal").glob("*.txt"):
            self._entries[f.stem] = f.read_text(encoding="utf-8")

    def _build(self):
        self._hdr("📓  Journal")
        top = tk.Frame(self,bg=C["bg2"]); top.pack(fill="x",padx=8,pady=4)
        for txt,cmd in [("✨ New",self._new),("💾 Save",self._save_cur),
                        ("🗑 Delete",self._delete)]:
            tk.Button(top,text=txt,command=cmd,bg=C["bg3"],fg=C["acc"],
                      font=FN["small"],relief="flat",bd=0,padx=8,pady=6
                      ).pack(side="left",padx=2)
        pane = tk.PanedWindow(self,orient="horizontal",bg=C["bg"],sashwidth=4)
        pane.pack(fill="both",expand=True,padx=6,pady=4)
        lf = tk.Frame(pane,bg=C["bg2"]); pane.add(lf,minsize=160)
        sb  = tk.Scrollbar(lf); sb.pack(side="right",fill="y")
        self._lb = tk.Listbox(lf,bg=C["bg2"],fg=C["text"],font=FN["body"],
                              yscrollcommand=sb.set,selectbackground=C["acc3"],
                              selectforeground=C["white"],relief="flat",bd=0,width=20)
        self._lb.pack(fill="both",expand=True); sb.config(command=self._lb.yview)
        self._lb.bind("<<ListboxSelect>>",self._on_select)
        rf = tk.Frame(pane,bg=C["bg"]); pane.add(rf,minsize=400)
        self._title_var = tk.StringVar()
        tk.Entry(rf,textvariable=self._title_var,bg=C["bg3"],fg=C["acc"],
                 font=FN["head"],insertbackground=C["acc"],relief="flat",bd=4
                 ).pack(fill="x",padx=4,pady=4)
        self._txt = scrolledtext.ScrolledText(rf,bg=C["bg2"],fg=C["text"],
                                              font=FN["body"],insertbackground=C["acc"],
                                              relief="flat",bd=0,wrap="word")
        self._txt.pack(fill="both",expand=True,padx=4,pady=4)
        self._refresh_list()

    def _refresh_list(self):
        self._lb.delete(0,tk.END)
        for k in sorted(self._entries.keys(),reverse=True):
            self._lb.insert(tk.END,k)

    def _on_select(self, _e):
        sel = self._lb.curselection()
        if not sel: return
        key = self._lb.get(sel[0]); self._cur = key
        self._title_var.set(key)
        self._txt.delete("1.0",tk.END)
        self._txt.insert("1.0",self._entries.get(key,""))

    def _new(self):
        key = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self._entries[key] = ""; self._cur = key
        self._title_var.set(key); self._txt.delete("1.0",tk.END)
        self._refresh_list()

    def _save_cur(self):
        if self._cur is None: self._new()
        key     = self._title_var.get().strip() or self._cur
        content = self._txt.get("1.0",tk.END)
        if self._cur != key and self._cur in self._entries:
            del self._entries[self._cur]
        self._entries[key] = content; self._cur = key
        (BASE_DIR/"journal"/f"{key}.txt").write_text(content,encoding="utf-8")
        self._refresh_list()

    def _delete(self):
        if self._cur is None: return
        if messagebox.askyesno("Delete",f"Delete '{self._cur}'?"):
            f = BASE_DIR/"journal"/f"{self._cur}.txt"
            if f.exists(): f.unlink()
            del self._entries[self._cur]; self._cur = None
            self._title_var.set(""); self._txt.delete("1.0",tk.END)
            self._refresh_list()

# ─────────────────────────────────────────────────────────────────────────────
# CLOCK
# ─────────────────────────────────────────────────────────────────────────────
class ClockApp(AppFrame):
    def __init__(self, master):
        super().__init__(master); self._running = True; self._alarm = None
        self._sw_running = False; self._sw_start = 0.0; self._sw_elapsed = 0.0
        self._build(); self._tick()

    def _build(self):
        self._hdr("🕐  Clock")
        cf = tk.Frame(self,bg=C["bg"]); cf.pack(pady=20)
        self._time_lbl = tk.Label(cf,text="",font=FN["clock"],fg=C["acc"],bg=C["bg"])
        self._time_lbl.pack()
        self._date_lbl = tk.Label(cf,text="",font=FN["body"],fg=C["muted"],bg=C["bg"])
        self._date_lbl.pack()

        cal_f = tk.Frame(self,bg=C["bg"]); cal_f.pack(pady=8)
        self._cal_lbl = tk.Label(cal_f,text="",font=FN["small"],fg=C["text"],bg=C["bg"],justify="left")
        self._cal_lbl.pack()

        af = tk.Frame(self,bg=C["bg2"]); af.pack(fill="x",padx=20,pady=8)
        tk.Label(af,text="⏰ Alarm (HH:MM):",fg=C["muted"],bg=C["bg2"],font=FN["small"]).pack(side="left",padx=6)
        self._alarm_var = tk.StringVar()
        tk.Entry(af,textvariable=self._alarm_var,width=8,bg=C["bg3"],fg=C["acc"],
                 font=FN["body"],insertbackground=C["acc"],relief="flat",bd=2).pack(side="left",padx=4)
        tk.Button(af,text="Set",command=self._set_alarm,
                  bg=C["bg3"],fg=C["ok"],font=FN["small"],relief="flat",bd=0,padx=6,pady=3
                  ).pack(side="left",padx=2)
        tk.Button(af,text="Clear",command=lambda: (setattr(self,"_alarm",None),
                                                     self._alarm_var.set("")),
                  bg=C["bg3"],fg=C["danger"],font=FN["small"],relief="flat",bd=0,padx=6,pady=3
                  ).pack(side="left",padx=2)
        self._alarm_lbl = tk.Label(af,text="",fg=C["warn"],bg=C["bg2"],font=FN["small"])
        self._alarm_lbl.pack(side="left",padx=6)

        swf = tk.Frame(self,bg=C["bg2"]); swf.pack(fill="x",padx=20,pady=6)
        tk.Label(swf,text="⏱ Stopwatch:",fg=C["muted"],bg=C["bg2"],font=FN["small"]).pack(side="left",padx=6)
        self._sw_lbl = tk.Label(swf,text="00:00.0",fg=C["acc2"],bg=C["bg2"],font=FN["head"])
        self._sw_lbl.pack(side="left",padx=6)
        for txt,cmd in [("▶ Start",self._sw_start_),("⏸ Stop",self._sw_stop),("↺ Reset",self._sw_reset)]:
            tk.Button(swf,text=txt,command=cmd,
                      bg=C["bg3"],fg=C["acc"],font=FN["small"],relief="flat",bd=0,padx=6,pady=3
                      ).pack(side="left",padx=2)

    def _tick(self):
        if not self._running: return
        now  = datetime.datetime.now()
        self._time_lbl.config(text=now.strftime("%H:%M:%S"))
        self._date_lbl.config(text=now.strftime("%A, %d %B %Y"))
        # mini calendar
        cal_txt = calendar.month(now.year, now.month)
        self._cal_lbl.config(text=cal_txt)
        # alarm check
        if self._alarm and now.strftime("%H:%M") == self._alarm:
            self._alarm_lbl.config(text=f"🔔 ALARM {self._alarm}!")
            startup_chime()
            self._alarm = None
        # stopwatch
        if self._sw_running:
            elapsed = self._sw_elapsed + time.time() - self._sw_start
            mins = int(elapsed)//60; secs = elapsed % 60
            self._sw_lbl.config(text=f"{mins:02d}:{secs:04.1f}")
        self.after(500, self._tick)

    def _set_alarm(self):
        self._alarm = self._alarm_var.get().strip()
        self._alarm_lbl.config(text=f"Set for {self._alarm}")

    def _sw_start_(self):
        if not self._sw_running:
            self._sw_running = True; self._sw_start = time.time()

    def _sw_stop(self):
        if self._sw_running:
            self._sw_elapsed += time.time() - self._sw_start
            self._sw_running = False

    def _sw_reset(self):
        self._sw_running = False; self._sw_elapsed = 0.0
        self._sw_lbl.config(text="00:00.0")

    def on_destroy(self): self._running = False

# ─────────────────────────────────────────────────────────────────────────────
# CALCULATOR
# ─────────────────────────────────────────────────────────────────────────────
class CalcApp(AppFrame):
    def __init__(self, master):
        super().__init__(master); self._expr = ""; self._build()

    def _build(self):
        self._hdr("🧮  Calculator")
        self._disp = tk.Label(self,text="0",font=fnt("Courier",24,"bold"),
                              fg=C["acc"],bg=C["bg2"],anchor="e",padx=12)
        self._disp.pack(fill="x",padx=10,pady=8)
        self._sub  = tk.Label(self,text="",font=FN["small"],fg=C["muted"],bg=C["bg"],anchor="e",padx=12)
        self._sub.pack(fill="x",padx=10)

        grid = [
            ["C","±","%","÷"],
            ["7","8","9","×"],
            ["4","5","6","−"],
            ["1","2","3","+"],
            ["0","0",".","="],
        ]
        bf = tk.Frame(self,bg=C["bg"]); bf.pack(fill="both",expand=True,padx=10,pady=6)
        for r,row in enumerate(grid):
            for c,lbl in enumerate(row):
                if r==4 and c in (0,1): continue   # "0" spans two cells below
                fg2 = (C["acc"] if lbl in "÷×−+" else C["ok"] if lbl=="=" else C["text"])
                bg2 = (C["bg3"] if lbl not in ("=",) else C["acc3"])
                b   = tk.Button(bf,text=lbl,font=FN["head"],fg=fg2,bg=bg2,
                                relief="flat",bd=0,padx=4,pady=14,cursor="hand2",
                                command=lambda l=lbl: self._press(l))
                if r==4 and c==0:
                    b.grid(row=r,column=0,columnspan=2,sticky="nsew",padx=2,pady=2)
                else:
                    b.grid(row=r,column=c,sticky="nsew",padx=2,pady=2)
                bf.columnconfigure(c,weight=1)
            bf.rowconfigure(r,weight=1)

    def _press(self, k):
        op_map = {"÷":"/","×":"*","−":"-","+":"+"}
        if k == "C":
            self._expr = ""; self._disp.config(text="0"); self._sub.config(text=""); return
        if k == "=":
            try:
                self._sub.config(text=self._expr)
                result = eval(self._expr.replace("^","**"))   # safe: only numbers+operators
                self._expr = str(result); self._disp.config(text=result)
            except:
                self._disp.config(text="Error"); self._expr = ""
            return
        if k == "±":
            try:
                val = eval(self._expr)
                self._expr = str(-val); self._disp.config(text=self._expr)
            except: pass
            return
        if k == "%":
            try:
                val = eval(self._expr)
                self._expr = str(val/100); self._disp.config(text=self._expr)
            except: pass
            return
        self._expr += op_map.get(k,k)
        self._disp.config(text=self._expr[-20:])

# ─────────────────────────────────────────────────────────────────────────────
# CHECKERS
# ─────────────────────────────────────────────────────────────────────────────
class CheckersApp(AppFrame):
    SZ=60
    def __init__(self, master):
        super().__init__(master)
        self._board=None; self._sel=None; self._turn="r"; self._build()

    def _new_board(self):
        b=[[None]*8 for _ in range(8)]
        for r in range(3):
            for c in range(8):
                if (r+c)%2==1: b[r][c]="b"
        for r in range(5,8):
            for c in range(8):
                if (r+c)%2==1: b[r][c]="r"
        return b

    def _build(self):
        self._hdr("⬛  Checkers")
        ctrl=tk.Frame(self,bg=C["bg2"]); ctrl.pack(fill="x",padx=8,pady=2)
        tk.Button(ctrl,text="▶ New Game",command=self._new_game,
                  bg=C["bg3"],fg=C["ok"],font=FN["small"],relief="flat",bd=0,padx=8,pady=4).pack(side="left",padx=4)
        self._status_lbl=tk.Label(ctrl,text="Red's turn",fg=C["acc"],bg=C["bg2"],font=FN["head"])
        self._status_lbl.pack(side="left",padx=10)
        self.canvas=tk.Canvas(self,bg=C["bg"],width=8*self.SZ,height=8*self.SZ,
                              highlightthickness=0)
        self.canvas.pack(pady=8)
        self.canvas.bind("<ButtonPress-1>",self._click)
        self._new_game()

    def _new_game(self):
        self._board=self._new_board(); self._sel=None; self._turn="r"; self._draw()
        self._status_lbl.config(text="Red's turn")

    def _draw(self):
        self.canvas.delete("all")
        for r in range(8):
            for c in range(8):
                bg="#8B4513" if (r+c)%2==1 else "#F0D9B5"
                self.canvas.create_rectangle(c*self.SZ,r*self.SZ,
                    (c+1)*self.SZ,(r+1)*self.SZ,fill=bg,outline="")
                p=self._board[r][c]
                if p:
                    col=("#cc2222" if p in "rR" else "#111111")
                    self.canvas.create_oval(c*self.SZ+5,r*self.SZ+5,
                        (c+1)*self.SZ-5,(r+1)*self.SZ-5,fill=col,outline="#ffffff",width=2)
                    if p in "RB":  # king
                        self.canvas.create_text(c*self.SZ+self.SZ//2,r*self.SZ+self.SZ//2,
                            text="♛",fill="#FFD700",font=FN["head"])
        if self._sel:
            sr,sc=self._sel
            self.canvas.create_rectangle(sc*self.SZ,sr*self.SZ,
                (sc+1)*self.SZ,(sr+1)*self.SZ,outline=C["acc"],width=3)

    def _click(self,e):
        c,r=e.x//self.SZ,e.y//self.SZ
        if not(0<=r<8 and 0<=c<8): return
        p=self._board[r][c]
        if self._sel is None:
            if p and p.lower()==self._turn: self._sel=(r,c)
        else:
            sr,sc=self._sel
            sp=self._board[sr][sc]
            if self._try_move(sr,sc,r,c,sp):
                self._sel=None; self._turn="r" if self._turn=="b" else "b"
                self._status_lbl.config(text=f"{'Red' if self._turn=='r' else 'Black'}'s turn")
            elif p and p.lower()==self._turn:
                self._sel=(r,c)
            else:
                self._sel=None
        self._draw()

    def _try_move(self,sr,sc,er,ec,p):
        dr=er-sr; dc=ec-sc; is_king=p in "RB"
        fwd = (-1 if p=="r" else 1)
        if abs(dc)==1 and (dr==fwd or is_king) and self._board[er][ec] is None:
            self._board[er][ec]=p; self._board[sr][sc]=None
            self._promote(er,ec); return True
        if abs(dc)==2 and abs(dr)==2:
            mr,mc=(sr+er)//2,(sc+ec)//2; mp=self._board[mr][mc]
            if mp and mp.lower()!=self._turn and self._board[er][ec] is None:
                self._board[er][ec]=p; self._board[sr][sc]=None; self._board[mr][mc]=None
                self._promote(er,ec); return True
        return False

    def _promote(self,r,c):
        p=self._board[r][c]
        if p=="r" and r==0: self._board[r][c]="R"
        elif p=="b" and r==7: self._board[r][c]="B"

# ─────────────────────────────────────────────────────────────────────────────
# CHESS  (basic rules, no AI)
# ─────────────────────────────────────────────────────────────────────────────
class ChessApp(AppFrame):
    SZ=64
    INIT=[
        ["r","n","b","q","k","b","n","r"],
        ["p"]*8,
        [None]*8,[None]*8,[None]*8,[None]*8,
        ["P"]*8,
        ["R","N","B","Q","K","B","N","R"],
    ]
    UNICODE={"K":"♔","Q":"♕","R":"♖","B":"♗","N":"♘","P":"♙",
             "k":"♚","q":"♛","r":"♜","b":"♝","n":"♞","p":"♟"}

    def __init__(self, master):
        super().__init__(master)
        self._board=None; self._sel=None; self._turn="w"; self._build()

    def _build(self):
        self._hdr("♟  Chess")
        ctrl=tk.Frame(self,bg=C["bg2"]); ctrl.pack(fill="x",padx=8,pady=2)
        tk.Button(ctrl,text="▶ New Game",command=self._new_game,
                  bg=C["bg3"],fg=C["ok"],font=FN["small"],relief="flat",bd=0,padx=8,pady=4).pack(side="left",padx=4)
        self._status_lbl=tk.Label(ctrl,text="White's turn",fg=C["acc"],bg=C["bg2"],font=FN["head"])
        self._status_lbl.pack(side="left",padx=10)
        self.canvas=tk.Canvas(self,bg=C["bg"],width=8*self.SZ,height=8*self.SZ,
                              highlightthickness=0)
        self.canvas.pack(pady=8)
        self.canvas.bind("<ButtonPress-1>",self._click)
        self._new_game()

    def _new_game(self):
        import copy
        self._board=[list(r) for r in copy.deepcopy(self.INIT)]
        self._sel=None; self._turn="w"; self._draw()
        self._status_lbl.config(text="White's turn")

    def _draw(self):
        self.canvas.delete("all")
        for r in range(8):
            for c in range(8):
                bg="#F0D9B5" if (r+c)%2==0 else "#B58863"
                self.canvas.create_rectangle(c*self.SZ,r*self.SZ,
                    (c+1)*self.SZ,(r+1)*self.SZ,fill=bg,outline="")
                p=self._board[r][c]
                if p:
                    col="#FFFFFF" if p.isupper() else "#1a1a1a"
                    self.canvas.create_text(c*self.SZ+self.SZ//2,r*self.SZ+self.SZ//2,
                        text=self.UNICODE.get(p,"?"),fill=col,
                        font=fnt("Arial",int(self.SZ*.55),"bold"))
        if self._sel:
            sr,sc=self._sel
            self.canvas.create_rectangle(sc*self.SZ,sr*self.SZ,
                (sc+1)*self.SZ,(sr+1)*self.SZ,outline=C["acc"],width=3)
            for mr,mc in self._legal_moves(sr,sc):
                self.canvas.create_oval(mc*self.SZ+22,mr*self.SZ+22,
                    (mc+1)*self.SZ-22,(mr+1)*self.SZ-22,fill=C["acc"],outline="")

    def _click(self,e):
        c,r=e.x//self.SZ,e.y//self.SZ
        if not(0<=r<8 and 0<=c<8): return
        p=self._board[r][c]
        if self._sel:
            if (r,c) in self._legal_moves(*self._sel):
                self._do_move(self._sel,r,c)
                self._sel=None; self._turn="b" if self._turn=="w" else "w"
                self._status_lbl.config(text=f"{'White' if self._turn=='w' else 'Black'}'s turn")
            else:
                self._sel=None
                if p and (p.isupper()==(self._turn=="w")): self._sel=(r,c)
        else:
            if p and (p.isupper()==(self._turn=="w")): self._sel=(r,c)
        self._draw()

    def _do_move(self,sel,er,ec):
        sr,sc=sel; p=self._board[sr][sc]
        self._board[er][ec]=p; self._board[sr][sc]=None
        # pawn promotion
        if p=="P" and er==0: self._board[er][ec]="Q"
        if p=="p" and er==7: self._board[er][ec]="q"

    def _legal_moves(self,r,c):
        p=self._board[r][c]; moves=[]
        if not p: return moves
        is_white=p.isupper(); pt=p.lower()

        def add(nr,nc):
            if 0<=nr<8 and 0<=nc<8:
                target=self._board[nr][nc]
                if target is None or (target.isupper()!=is_white):
                    moves.append((nr,nc))

        if pt=="p":
            dr=-1 if is_white else 1
            if 0<=r+dr<8 and self._board[r+dr][c] is None:
                moves.append((r+dr,c))
                start_row=6 if is_white else 1
                if r==start_row and self._board[r+2*dr][c] is None:
                    moves.append((r+2*dr,c))
            for dc in(-1,1):
                nr2,nc2=r+dr,c+dc
                if 0<=nr2<8 and 0<=nc2<8 and self._board[nr2][nc2] and self._board[nr2][nc2].isupper()!=is_white:
                    moves.append((nr2,nc2))
        elif pt=="r":
            for dr,dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                nr2,nc2=r+dr,c+dc
                while 0<=nr2<8 and 0<=nc2<8:
                    tgt=self._board[nr2][nc2]
                    if tgt:
                        if tgt.isupper()!=is_white: moves.append((nr2,nc2)); break
                        else: break
                    moves.append((nr2,nc2)); nr2+=dr; nc2+=dc
        elif pt=="b":
            for dr,dc in [(1,1),(1,-1),(-1,1),(-1,-1)]:
                nr2,nc2=r+dr,c+dc
                while 0<=nr2<8 and 0<=nc2<8:
                    tgt=self._board[nr2][nc2]
                    if tgt:
                        if tgt.isupper()!=is_white: moves.append((nr2,nc2)); break
                        else: break
                    moves.append((nr2,nc2)); nr2+=dr; nc2+=dc
        elif pt=="q":
            for dr,dc in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
                nr2,nc2=r+dr,c+dc
                while 0<=nr2<8 and 0<=nc2<8:
                    tgt=self._board[nr2][nc2]
                    if tgt:
                        if tgt.isupper()!=is_white: moves.append((nr2,nc2)); break
                        else: break
                    moves.append((nr2,nc2)); nr2+=dr; nc2+=dc
        elif pt=="n":
            for dr,dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
                add(r+dr,c+dc)
        elif pt=="k":
            for dr in(-1,0,1):
                for dc in(-1,0,1):
                    if dr or dc: add(r+dr,c+dc)
        return moves

    def on_destroy(self): pass

# ─────────────────────────────────────────────────────────────────────────────
# PYAMBY AMBIENCE
# ─────────────────────────────────────────────────────────────────────────────
class AmbienceApp(AppFrame):
    PRESETS = {
        "Rain":       {"freqs":[60,120,250,500],"wave":"noise","rate":0.3,"vol":0.18},
        "Forest":     {"freqs":[330,440,550,660],"wave":"sine","rate":0.4,"vol":0.14},
        "Ocean":      {"freqs":[80,160,320],"wave":"sine","rate":0.2,"vol":0.20},
        "Fire":       {"freqs":[100,200,400],"wave":"noise","rate":0.5,"vol":0.15},
        "White Noise":{"freqs":[1000],"wave":"noise","rate":0.0,"vol":0.25},
        "Space":      {"freqs":[55,110,220,440,880],"wave":"sine","rate":0.1,"vol":0.12},
        "City":       {"freqs":[200,400,800,1600],"wave":"noise","rate":0.6,"vol":0.16},
    }

    def __init__(self, master):
        super().__init__(master)
        self._running = False; self._stop_ev = threading.Event()
        self._preset  = "Rain"; self._vol = 0.5; self._build()

    def _build(self):
        self._hdr("🌿  PyAmby Ambience")
        cfg = tk.Frame(self,bg=C["bg2"]); cfg.pack(fill="x",padx=12,pady=8)
        tk.Label(cfg,text="Preset:",fg=C["muted"],bg=C["bg2"],font=FN["small"]).pack(side="left",padx=4)
        self._preset_var = tk.StringVar(value=self._preset)
        p_cb = ttk.Combobox(cfg,textvariable=self._preset_var,
                             values=list(self.PRESETS.keys()),
                             width=14,state="readonly")
        p_cb.pack(side="left",padx=6)
        tk.Label(cfg,text="Vol:",fg=C["muted"],bg=C["bg2"],font=FN["small"]).pack(side="left",padx=(12,2))
        self._vol_var = tk.DoubleVar(value=0.5)
        tk.Scale(cfg,variable=self._vol_var,from_=0,to=1,resolution=.02,
                 orient="horizontal",length=120,bg=C["bg2"],fg=C["acc"],
                 troughcolor=C["dim"],showvalue=False,highlightthickness=0,
                 command=lambda v: setattr(self,"_vol",float(v))).pack(side="left",padx=4)
        bf = tk.Frame(self,bg=C["bg"]); bf.pack(pady=8)
        tk.Button(bf,text="▶ Start",command=self._start,
                  bg=C["bg3"],fg=C["ok"],font=FN["head"],relief="flat",bd=0,padx=16,pady=10
                  ).pack(side="left",padx=6)
        tk.Button(bf,text="⏹ Stop",command=self._stop,
                  bg=C["bg3"],fg=C["danger"],font=FN["head"],relief="flat",bd=0,padx=16,pady=10
                  ).pack(side="left",padx=6)
        self._status_lbl = tk.Label(self,text="Idle",fg=C["muted"],bg=C["bg"],font=FN["small"])
        self._status_lbl.pack(pady=4)

    def _start(self):
        if self._running: self._stop()
        self._preset = self._preset_var.get()
        self._running = True; self._stop_ev.clear()
        self._status_lbl.config(text=f"♪ Playing: {self._preset}")
        threading.Thread(target=self._loop, daemon=True).start()

    def _stop(self):
        self._running = False; self._stop_ev.set()
        self._status_lbl.config(text="Stopped")

    def _loop(self):
        cfg = self.PRESETS[self._preset]
        while self._running and not self._stop_ev.is_set():
            vol = self._vol * cfg["vol"]
            freqs = cfg["freqs"]
            freq  = E.choice(freqs) * (1 + (E.random()-0.5)*0.05)
            dur   = 0.4 + E.random()*0.4
            raw   = gen_wave(freq, dur, cfg["wave"], vol)
            snd   = adsr(raw, atk=0.05, dec=0.1, sus=0.7, rel=0.15)
            play_raw(to_wav_bytes(snd))
            delay = max(0.05, 0.5*(1-cfg["rate"])*E.random())
            self._stop_ev.wait(timeout=delay)

    def on_destroy(self): self._stop()

# ─────────────────────────────────────────────────────────────────────────────
# SETTINGS
# ─────────────────────────────────────────────────────────────────────────────
class SettingsApp(AppFrame):
    def __init__(self, master):
        super().__init__(master); self._build()

    def _build(self):
        self._hdr("⚙  Settings")
        info = [
            ("Version",        VERSION),
            ("Python",         sys.version.split()[0]),
            ("Data directory", str(BASE_DIR)),
            ("PIL / Pillow",   "Available" if HAS_PIL else "Not installed"),
            ("Audio player",   find_player()[0] or "None found"),
            ("MP3 encoder",    MP3Codec._tool() or "None found"),
        ]
        for label, val in info:
            f = tk.Frame(self,bg=C["bg2"]); f.pack(fill="x",padx=12,pady=3)
            tk.Label(f,text=f"{label}:",width=20,fg=C["muted"],bg=C["bg2"],
                     font=FN["small"],anchor="w").pack(side="left")
            tk.Label(f,text=val,fg=C["acc"],bg=C["bg2"],font=FN["body"]).pack(side="left",padx=6)

        tk.Label(self,text="Keyboard Shortcuts",fg=C["acc2"],bg=C["bg"],
                 font=FN["head"]).pack(anchor="w",padx=12,pady=(16,4))
        shortcuts = [
            ("DAW Play/Stop",  "Click ▶ PLAY button"),
            ("Metronome",      "Click 🎹 Metro button"),
            ("Chess/Checkers", "Click pieces"),
            ("Solitaire",      "Drag cards / Double-click to foundation"),
        ]
        for action, key in shortcuts:
            f = tk.Frame(self,bg=C["bg"]); f.pack(fill="x",padx=16,pady=1)
            tk.Label(f,text=action,width=22,fg=C["text"],bg=C["bg"],
                     font=FN["small"],anchor="w").pack(side="left")
            tk.Label(f,text=key,fg=C["muted"],bg=C["bg"],font=FN["small"]).pack(side="left")

        tk.Label(self,text="Data Folders",fg=C["acc2"],bg=C["bg"],
                 font=FN["head"]).pack(anchor="w",padx=12,pady=(16,4))
        for d in ["journal","songs","patterns","samples","exports","saves","media"]:
            path = BASE_DIR/d
            f = tk.Frame(self,bg=C["bg"]); f.pack(fill="x",padx=16,pady=1)
            tk.Label(f,text=str(path),fg=C["muted"],bg=C["bg"],font=FN["tiny"]).pack(side="left")
            tk.Button(f,text="Open",command=lambda p=path: self._open_dir(p),
                      bg=C["bg3"],fg=C["acc2"],font=FN["tiny"],relief="flat",bd=0,
                      padx=4,pady=1).pack(side="right",padx=4)

    @staticmethod
    def _open_dir(path):
        try:
            if sys.platform=="win32":  os.startfile(path)
            elif sys.platform=="darwin": subprocess.Popen(["open",str(path)])
            else: subprocess.Popen(["xdg-open",str(path)])
        except: pass

# ─────────────────────────────────────────────────────────────────────────────
# SPLASH SCREEN
# ─────────────────────────────────────────────────────────────────────────────
def show_splash(root):
    sp = tk.Toplevel(root); sp.overrideredirect(True)
    sp.configure(bg=C["bg"]); sp.attributes("-topmost",True)
    w,h=500,280; x=(root.winfo_screenwidth()-w)//2; y=(root.winfo_screenheight()-h)//2
    sp.geometry(f"{w}x{h}+{x}+{y}")
    tk.Label(sp,text="P Y S P L O R E",font=fnt("Courier",28,"bold"),
             fg=C["acc"],bg=C["bg"]).pack(pady=(30,4))
    tk.Label(sp,text=f"v{VERSION}",font=FN["body"],fg=C["muted"],bg=C["bg"]).pack()
    tk.Label(sp,text="DAW · Media · Paint · Journal · Clock\n"
                     "Calculator · Chess · Checkers · Solitaire · Ambience",
             font=FN["small"],fg=C["text"],bg=C["bg"],justify="center").pack(pady=10)
    bar = tk.Canvas(sp,bg=C["bg2"],height=6,width=400,highlightthickness=0); bar.pack(pady=10)
    prog = bar.create_rectangle(0,0,0,6,fill=C["acc"],outline="")
    msg  = tk.Label(sp,text="Initialising…",font=FN["small"],fg=C["muted"],bg=C["bg"]); msg.pack()
    steps=[("Loading audio engine…",0.25),("Warming up entropy…",0.55),
           ("Building apps…",0.80),("Ready!",1.0)]
    def _step(i=0):
        if i >= len(steps): sp.destroy(); return
        txt,pct=steps[i]; msg.config(text=txt)
        bar.coords(prog,0,0,int(400*pct),6)
        sp.after(300,_step,i+1)
    _step()

# ─────────────────────────────────────────────────────────────────────────────
# KLONDIKE SOLITAIRE
# ─────────────────────────────────────────────────────────────────────────────
_SOL_SUITS  = ['♠','♥','♦','♣']
_SOL_RANKS  = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']
_SOL_COLOR  = {'♠':'black','♣':'black','♥':'red','♦':'red'}

class _SolCard:
    __slots__ = ('r','s','f')
    def __init__(self, r, su, f=0): self.r=r; self.s=su; self.f=f
    def col(self): return _SOL_COLOR[self.s]
    def __repr__(self): return f"{self.r}{self.s}"

class _SolDeck:
    def __init__(self):
        self.c = [_SolCard(r,su) for su in _SOL_SUITS for r in _SOL_RANKS]
        random.shuffle(self.c)
    def deal(self): return self.c.pop() if self.c else None

class _SolGame:
    def __init__(self):
        self.tb=[[] for _ in range(7)]
        self.fd={su:[] for su in _SOL_SUITS}
        self.w=[]; self.st=[]; self.h=[]
        self.ng()

    def _snap(self):
        import copy
        self.h.append({
            'tb': [p[:] for p in self.tb],
            'fd': {su: f[:] for su,f in self.fd.items()},
            'w':  self.w[:], 'st': self.st[:]
        })
        if len(self.h) > 60: self.h.pop(0)

    def undo(self):
        if len(self.h) > 1:
            self.h.pop()
            st = self.h[-1]
            self.tb = [p[:] for p in st['tb']]
            self.fd = {su: f[:] for su,f in st['fd'].items()}
            self.w  = st['w'][:]; self.st = st['st'][:]
            return True
        return False

    def ng(self):
        d = _SolDeck()
        self.tb = [[] for _ in range(7)]
        for i in range(7):
            for j in range(i+1):
                c = d.deal(); c.f = (j == i); self.tb[i].append(c)
        self.st = [d.deal() for _ in range(len(d.c))]
        self.w = []; self.fd = {su:[] for su in _SOL_SUITS}
        self.h.clear(); self._snap()

    def can_tb(self, c, t):
        if t:
            return (t[-1].f and
                    _SOL_RANKS.index(c.r) == _SOL_RANKS.index(t[-1].r)-1 and
                    c.col() != t[-1].col())
        return c.r == 'K'

    def can_fd(self, c, su):
        p = self.fd[su]
        if p: return _SOL_RANKS.index(c.r) == _SOL_RANKS.index(p[-1].r)+1 and c.s==su
        return c.r == 'A' and c.s == su

    def draw(self):
        if self.st:
            c = self.st.pop(); c.f=1; self.w.append(c); self._snap(); return True
        elif self.w:
            self.st = self.w[::-1]
            for c in self.st: c.f=0
            self.w=[]; self._snap(); return True
        return False

    def won(self): return all(len(p)==13 for p in self.fd.values())

    def auto_moves(self):
        """Return list of (src_desc, card) that can go to foundation."""
        moves = []
        for p in self.tb:
            if p and p[-1].f and self.can_fd(p[-1], p[-1].s):
                moves.append(('tableau', p[-1]))
        if self.w and self.can_fd(self.w[-1], self.w[-1].s):
            moves.append(('waste', self.w[-1]))
        return moves

class SolitaireApp(AppFrame):
    CW=72; CH=100; XO=20; YO=20; YT=140; XS=82; YS=25

    def __init__(self, master):
        super().__init__(master)
        self.g = _SolGame()
        self._dg = {'src':None, 'cs':[], 'ox':0, 'oy':0}
        self._build()

    def _build(self):
        self._hdr("🂡  Solitaire")
        ctrl = tk.Frame(self, bg=C["bg2"]); ctrl.pack(fill="x", padx=8, pady=2)
        for txt, cmd in [("▶ New", self._new), ("↩ Undo", self._undo),
                         ("💡 Hint", self._hint), ("⚡ Auto", self._auto)]:
            tk.Button(ctrl, text=txt, command=cmd,
                      bg=C["bg3"], fg=C["acc"], font=FN["small"],
                      relief="flat", bd=0, padx=10, pady=4).pack(side="left", padx=3)
        self._msg = tk.Label(ctrl, text="Draw from stock or drag cards",
                             fg=C["muted"], bg=C["bg2"], font=FN["small"])
        self._msg.pack(side="left", padx=12)

        cf = tk.Frame(self, bg=C["bg"]); cf.pack(fill="both", expand=True)
        self.cv = tk.Canvas(cf, bg="#0a5a1e", highlightthickness=0)
        self.cv.pack(fill="both", expand=True)
        self.cv.bind("<Button-1>",        self._click)
        self.cv.bind("<B1-Motion>",       self._drag)
        self.cv.bind("<ButtonRelease-1>", self._drop)
        self.cv.bind("<Double-1>",        self._dbl)
        self.cv.bind("<Configure>",       lambda e: self._draw())
        self._draw()

    # ── drawing ───────────────────────────────────────────────────────────────
    def _draw(self):
        cv = self.cv; cv.delete("all")
        W = cv.winfo_width() or 800
        # layout constants scaled to canvas width
        xo = max(10, (W - 7*self.XS - self.CW) // 2)

        self._draw_stock(xo)
        self._draw_waste(xo)
        self._draw_foundations(xo, W)
        self._draw_tableaux(xo)
        if self.g.won():
            cv.create_text(W//2, 300, text="🎉 YOU WIN! 🎉",
                           fill="#ffd700", font=fnt("Courier",28,"bold"))

    def _slot(self, x, y):
        self.cv.create_rectangle(x, y, x+self.CW, y+self.CH,
                                  fill="#085a15", outline="#1a7a2a", dash=(4,3))

    def _card(self, x, y, card, ghost=False):
        cv = self.cv
        if ghost:
            cv.create_rectangle(x,y,x+self.CW,y+self.CH,
                                  fill="", outline=C["acc"], dash=(4,2), width=2)
            return
        if not card.f:
            cv.create_rectangle(x,y,x+self.CW,y+self.CH,
                                  fill="#0d4a1a", outline="#2a7a3a", width=1)
            cv.create_text(x+self.CW//2, y+self.CH//2, text="✦",
                           font=fnt("Courier",18), fill="#1a6a2a")
            return
        col  = "#cc2233" if card.col()=="red" else "#111122"
        cv.create_rectangle(x,y,x+self.CW,y+self.CH,
                              fill="#f8f8f2", outline="#aaaaaa", width=1)
        cv.create_text(x+5, y+5,  text=card.r, anchor="nw",
                       font=fnt("Courier",11,"bold"), fill=col)
        cv.create_text(x+5, y+16, text=card.s, anchor="nw",
                       font=fnt("Courier",12),      fill=col)
        cv.create_text(x+self.CW-5, y+self.CH-5, text=card.s, anchor="se",
                       font=fnt("Courier",14),      fill=col)

    def _draw_stock(self, xo):
        x, y = xo, self.YO
        if self.g.st:
            self.cv.create_rectangle(x,y,x+self.CW,y+self.CH,
                                      fill="#0d4a1a", outline="#2a8a3a", width=2)
            self.cv.create_text(x+self.CW//2, y+self.CH//2, text="🂠",
                                 font=fnt("Courier",22), fill="#3aaa5a")
        else:
            self._slot(x, y)
            self.cv.create_text(x+self.CW//2, y+self.CH//2, text="↺",
                                 font=fnt("Courier",22), fill="#1a7a2a")
        self.cv.create_text(x+self.CW//2, y-12, text="Stock",
                             fill=C["muted"], font=FN["tiny"])

    def _draw_waste(self, xo):
        x, y = xo+self.XS, self.YO
        if self.g.w:
            if len(self.g.w) > 1:
                self._card(x-4, y-3, self.g.w[-2], ghost=False)
                # slightly offset peek card is face-down style
                self.cv.create_rectangle(x-4,y-3,x-4+self.CW,y-3+self.CH,
                                          fill="#f0f0ea", outline="#999", width=1)
            self._card(x, y, self.g.w[-1])
        else:
            self._slot(x, y)
        self.cv.create_text(x+self.CW//2, y-12, text="Waste",
                             fill=C["muted"], font=FN["tiny"])

    def _draw_foundations(self, xo, W):
        fx = xo + 3*self.XS
        for i, su in enumerate(_SOL_SUITS):
            x = fx + i*self.XS; y = self.YO
            p = self.g.fd[su]
            if p:
                self._card(x, y, p[-1])
            else:
                self._slot(x, y)
                self.cv.create_text(x+self.CW//2, y+self.CH//2, text=su,
                                     font=fnt("Courier",18), fill="#2a8a4a")
            self.cv.create_text(x+self.CW//2, y-12, text=su,
                                 fill=C["muted"], font=FN["tiny"])

    def _draw_tableaux(self, xo):
        for i, pile in enumerate(self.g.tb):
            x = xo + i*self.XS; y = self.YT
            if pile:
                for j, card in enumerate(pile):
                    self._card(x, y + j*self.YS, card)
            else:
                self._slot(x, y)

    # ── hit-testing ───────────────────────────────────────────────────────────
    def _xo(self):
        W = self.cv.winfo_width() or 800
        return max(10, (W - 7*self.XS - self.CW) // 2)

    def _hit(self, mx, my):
        xo = self._xo()
        # stock
        x,y = xo, self.YO
        if x<=mx<=x+self.CW and y<=my<=y+self.CH: return ('stock', None)
        # waste
        x = xo+self.XS
        if x<=mx<=x+self.CW and y<=my<=y+self.CH: return ('waste', None)
        # foundations
        fx = xo+3*self.XS
        for i in range(4):
            x = fx+i*self.XS
            if x<=mx<=x+self.CW and y<=my<=y+self.CH: return ('fd', i)
        # tableaux
        for i, pile in enumerate(self.g.tb):
            x = xo+i*self.XS
            if not (x<=mx<=x+self.CW): continue
            if pile:
                for j in range(len(pile)-1, -1, -1):
                    y2 = self.YT + j*self.YS
                    if my >= y2:
                        return ('tb', (i, j))
            elif self.YT<=my<=self.YT+self.CH:
                return ('tb', (i, -1))
        return (None, None)

    # ── interactions ──────────────────────────────────────────────────────────
    def _click(self, e):
        area, idx = self._hit(e.x, e.y)
        if area == 'stock':
            self.g.draw(); self._draw(); return
        if area == 'waste' and self.g.w:
            self._dg = {'src':('waste',None), 'cs':[self.g.w[-1]], 'ox':e.x, 'oy':e.y}
        elif area == 'tb':
            pi, ci = idx
            if ci >= 0 and self.g.tb[pi][ci].f:
                self._dg = {'src':('tb',pi,ci), 'cs':self.g.tb[pi][ci:], 'ox':e.x, 'oy':e.y}
        elif area == 'fd':
            su = _SOL_SUITS[idx]; p = self.g.fd[su]
            if p:
                self._dg = {'src':('fd',idx), 'cs':[p[-1]], 'ox':e.x, 'oy':e.y}

    def _drag(self, e):
        if not self._dg['cs']: return
        self.cv.delete("drag_tag")
        dx = e.x - self._dg['ox']; dy = e.y - self._dg['oy']
        # find original card position
        xo = self._xo()
        src = self._dg['src']
        if src[0]=='waste': bx,by = xo+self.XS, self.YO
        elif src[0]=='tb':  bx = xo+src[1]*self.XS; by = self.YT+src[2]*self.YS
        elif src[0]=='fd':  bx = xo+3*self.XS+src[1]*self.XS; by = self.YO
        else: return
        for j, card in enumerate(self._dg['cs']):
            x = bx+dx; y = by+dy+j*self.YS
            col = "#cc2233" if card.col()=="red" else "#111122"
            self.cv.create_rectangle(x,y,x+self.CW,y+self.CH,
                                      fill="#f8f8f2",outline="#333",width=1,tags="drag_tag")
            self.cv.create_text(x+5,y+5, text=card.r, anchor="nw",
                                font=fnt("Courier",11,"bold"), fill=col, tags="drag_tag")
            self.cv.create_text(x+5,y+16, text=card.s, anchor="nw",
                                font=fnt("Courier",12), fill=col, tags="drag_tag")

    def _drop(self, e):
        self.cv.delete("drag_tag")
        if not self._dg['cs']: return
        area, idx = self._hit(e.x, e.y)
        src = self._dg['src']; cs = self._dg['cs']
        moved = False

        if area == 'tb':
            pi = idx[0]; t = self.g.tb[pi]
            if self.g.can_tb(cs[0], t):
                if src[0]=='tb':
                    sp = self.g.tb[src[1]]
                    self.g.tb[pi].extend(sp[src[2]:]); del sp[src[2]:]
                    if sp and not sp[-1].f: sp[-1].f=1
                elif src[0]=='waste':
                    self.g.tb[pi].append(self.g.w.pop())
                elif src[0]=='fd':
                    self.g.tb[pi].append(self.g.fd[_SOL_SUITS[src[1]]].pop())
                moved = True

        elif area == 'fd' and len(cs)==1:
            su = _SOL_SUITS[idx]
            if self.g.can_fd(cs[0], su):
                if src[0]=='tb':
                    sp = self.g.tb[src[1]]
                    self.g.fd[su].append(sp.pop())
                    if sp and not sp[-1].f: sp[-1].f=1
                elif src[0]=='waste':
                    self.g.fd[su].append(self.g.w.pop())
                elif src[0]=='fd' and src[1]!=idx:
                    self.g.fd[su].append(self.g.fd[_SOL_SUITS[src[1]]].pop())
                moved = True

        if moved: self.g._snap()
        self._dg = {'src':None,'cs':[],'ox':0,'oy':0}
        self._draw()
        if self.g.won():
            self._msg.config(text="🎉 You win! Deal again?", fg=C["ok"])

    def _dbl(self, e):
        area, idx = self._hit(e.x, e.y)
        moved = False
        if area == 'tb':
            pi, ci = idx
            if ci >= 0:
                p = self.g.tb[pi]
                if p and p[ci].f:
                    c = p[ci]
                    if self.g.can_fd(c, c.s):
                        self.g.fd[c.s].append(p.pop(ci))
                        if p and not p[-1].f: p[-1].f=1
                        moved = True
        elif area == 'waste' and self.g.w:
            c = self.g.w[-1]
            if self.g.can_fd(c, c.s):
                self.g.fd[c.s].append(self.g.w.pop()); moved = True
        if moved: self.g._snap(); self._draw()

    def _new(self):
        self.g.ng(); self._dg={'src':None,'cs':[],'ox':0,'oy':0}
        self._msg.config(text="New game — good luck!", fg=C["muted"]); self._draw()

    def _undo(self):
        ok = self.g.undo(); self._draw()
        self._msg.config(text="Undo" if ok else "Nothing to undo",
                         fg=C["muted"] if ok else C["warn"])

    def _hint(self):
        moves = self.g.auto_moves()
        if moves:
            src, c = moves[0]
            self._msg.config(text=f"Hint: move {c} to foundation", fg=C["acc2"])
        else:
            for i, p in enumerate(self.g.tb):
                if p and p[-1].f:
                    c = p[-1]
                    for j, p2 in enumerate(self.g.tb):
                        if i!=j and self.g.can_tb(c, p2):
                            self._msg.config(text=f"Hint: move {c} to pile {j+1}", fg=C["acc2"])
                            return
            if self.g.w:
                c = self.g.w[-1]
                for j, p2 in enumerate(self.g.tb):
                    if self.g.can_tb(c, p2):
                        self._msg.config(text=f"Hint: play waste {c} to pile {j+1}", fg=C["acc2"])
                        return
            self._msg.config(text="No obvious move — try drawing", fg=C["warn"])

    def _auto(self):
        """Auto-move all eligible cards to foundation."""
        moved = True
        while moved:
            moved = False
            for p in self.g.tb:
                if p and p[-1].f and self.g.can_fd(p[-1], p[-1].s):
                    self.g.fd[p[-1].s].append(p.pop())
                    if p and not p[-1].f: p[-1].f=1
                    self.g._snap(); moved=True; break
            if not moved and self.g.w and self.g.can_fd(self.g.w[-1], self.g.w[-1].s):
                c=self.g.w[-1]; self.g.fd[c.s].append(self.g.w.pop())
                self.g._snap(); moved=True
        self._draw()
        if self.g.won():
            self._msg.config(text="🎉 Auto-complete! You win!", fg=C["ok"])

    def on_destroy(self): pass

# ─────────────────────────────────────────────────────────────────────────────
# MAIN SHELL
# ─────────────────────────────────────────────────────────────────────────────
APPS = [
    ("🎵 DAW",      MusicStudioApp),
    ("📻 Media",    MediaPlayerApp),
    ("🌿 Ambience", AmbienceApp),
    ("🎨 Paint",    PaintApp),
    ("📓 Journal",  JournalApp),
    ("🕐 Clock",    ClockApp),
    ("🧮 Calc",     CalcApp),
    ("♟ Chess",     ChessApp),
    ("⬛ Checkers", CheckersApp),
    ("🂡 Solitaire",SolitaireApp),
    ("⚙ Settings",  SettingsApp),
]

class PysploreShell:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"Pysplore v{VERSION}")
        self.root.configure(bg=C["bg"])
        self.root.geometry("1100x760")
        self.root.minsize(800,550)
        self._current_app = None
        self._active_btn  = None
        self.osk = OSK(self.root)
        self._style()
        self._build()
        show_splash(self.root)
        startup_chime()
        self.root.after(1400, lambda: self._open(0))
        self.root.bind_all("<Motion>",self._feed_mouse)
        self.root.bind_all("<KeyPress>",self._feed_key)
        self.root.protocol("WM_DELETE_WINDOW",self._quit)

    def _style(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook",     background=C["bg2"], borderwidth=0)
        style.configure("TNotebook.Tab", background=C["bg3"], foreground=C["muted"],
                        font=FN["small"], padding=[8,4])
        style.map("TNotebook.Tab",
            background=[("selected",C["bg"])],
            foreground=[("selected",C["acc"])])
        style.configure("TCombobox", fieldbackground=C["bg3"],
                        background=C["bg3"], foreground=C["acc"],
                        selectbackground=C["acc3"], arrowcolor=C["acc"])

    def _build(self):
        # sidebar
        sidebar = tk.Frame(self.root,bg=C["bg2"],width=110); sidebar.pack(side="left",fill="y")
        sidebar.pack_propagate(False)
        tk.Label(sidebar,text="∞",font=fnt("Courier",22,"bold"),
                 fg=C["acc"],bg=C["bg2"]).pack(pady=(12,4))
        tk.Label(sidebar,text="PYSPLORE",font=fnt("Courier",7,"bold"),
                 fg=C["muted"],bg=C["bg2"]).pack()

        self._nav_btns = []
        for i,(label,_) in enumerate(APPS):
            b = tk.Button(sidebar,text=label,font=FN["small"],fg=C["text"],
                          bg=C["bg2"],relief="flat",bd=0,padx=4,pady=10,
                          anchor="w",cursor="hand2",
                          command=lambda idx=i: self._open(idx))
            b.pack(fill="x",padx=4,pady=1); self._nav_btns.append(b)

        # OSK toggle
        tk.Button(sidebar,text="⌨ KB",font=FN["tiny"],fg=C["muted"],bg=C["bg2"],
                  relief="flat",bd=0,padx=4,pady=8,cursor="hand2",
                  command=self.osk.toggle).pack(fill="x",padx=4,pady=(8,2),side="bottom")

        # close button
        tk.Button(sidebar,text="✕ Quit",font=FN["tiny"],fg=C["danger"],bg=C["bg2"],
                  relief="flat",bd=0,padx=4,pady=8,cursor="hand2",
                  command=self._quit).pack(fill="x",padx=4,pady=2,side="bottom")

        # main area
        self._main = tk.Frame(self.root,bg=C["bg"]); self._main.pack(side="left",fill="both",expand=True)

    def _open(self, idx):
        if self._current_app:
            try: self._current_app.on_destroy()
            except: pass
            self._current_app.destroy()
        if self._active_btn:
            self._active_btn.config(bg=C["bg2"],fg=C["text"])
        b = self._nav_btns[idx]; b.config(bg=C["acc"],fg=C["black"])
        self._active_btn = b
        app_cls = APPS[idx][1]
        app = app_cls(self._main); app.pack(fill="both",expand=True)
        self._current_app = app
        gc.collect()

    def _feed_mouse(self, e): E.feed_mouse(e.x,e.y)
    def _feed_key(self, e):
        try: E.feed_key(ord(e.char) if e.char else 0)
        except: pass

    def _quit(self):
        if self._current_app:
            try: self._current_app.on_destroy()
            except: pass
        try: self.osk._win.destroy()
        except: pass
        self.root.destroy()

    def run(self): self.root.mainloop()

# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    PysploreShell().run()



