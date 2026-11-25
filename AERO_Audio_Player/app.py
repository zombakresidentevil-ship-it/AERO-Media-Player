from __future__ import annotations
import random, tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import pygame
from mutagen import File as AudioFile

APP="AERO Audio Player"
EXTS={".mp3",".wav",".ogg",".flac",".mid",".midi",".mod",".xm",".it",".s3m"}
BG,PANEL,EDGE,CYAN,TEXT,MUTED="#111820","#1c2935","#34495a","#35d7e8","#e6f0f5","#91a7b6"

def info(path):
    title,artist,duration=Path(path).stem,"",0
    try:
        media=AudioFile(path,easy=True)
        if media:
            title=str((media.tags or {}).get("title",[title])[0])
            artist=str((media.tags or {}).get("artist",[""])[0])
            duration=int(getattr(media.info,"length",0) or 0)
    except Exception: pass
    return {"path":str(path),"title":title,"artist":artist,"duration":duration}

class Player(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP); self.geometry("780x510"); self.minsize(650,430); self.configure(bg=BG)
        pygame.mixer.init()
        self.items=[]; self.current=-1; self.paused=False; self.shuffle=False; self.repeat=False; self.offset=0
        self.ui(); self.after(200,self.tick); self.protocol("WM_DELETE_WINDOW",self.close)
    def button(self,parent,label,cmd,small=False,primary=False):
        return tk.Button(parent,text=label,command=cmd,bg=CYAN if primary else "#263746",fg="#071218" if primary else CYAN,
          activebackground="#176071",activeforeground="white",relief="flat",bd=0,font=("Segoe UI",8 if small else 11,"bold"),
          padx=11 if small else 14,pady=7 if small else 9,cursor="hand2")
    def ui(self):
        head=tk.Frame(self,bg=BG); head.pack(fill="x",padx=18,pady=(14,8))
        tk.Label(head,text="AERO",font=("Segoe UI",25,"bold"),fg=CYAN,bg=BG).pack(side="left")
        tk.Label(head,text="AUDIO PLAYER  /  CLASSIC EDITION",font=("Segoe UI",9,"bold"),fg=MUTED,bg=BG).pack(side="left",padx=12,pady=(12,0))
        self.status=tk.Label(head,text="READY",fg=CYAN,bg=BG,font=("Consolas",10)); self.status.pack(side="right",pady=14)
        now=tk.Frame(self,bg=PANEL,highlightbackground=EDGE,highlightthickness=1); now.pack(fill="x",padx=18,pady=5)
        self.title_label=tk.Label(now,text="Добавьте музыку в плейлист",bg=PANEL,fg=TEXT,font=("Segoe UI",13,"bold"),anchor="w")
        self.title_label.pack(fill="x",padx=14,pady=(10,1))
        self.artist_label=tk.Label(now,text="AERO • ВАШ МУЗЫКАЛЬНЫЙ ПЛЕЕР",bg=PANEL,fg=MUTED,font=("Segoe UI",9),anchor="w"); self.artist_label.pack(fill="x",padx=14)
        row=tk.Frame(now,bg=PANEL); row.pack(fill="x",padx=12,pady=(8,2))
        self.elapsed=tk.Label(row,text="00:00",bg=PANEL,fg=MUTED,font=("Consolas",9)); self.elapsed.pack(side="left")
        self.pos=tk.DoubleVar(); self.seek=ttk.Scale(row,from_=0,to=100,variable=self.pos); self.seek.pack(side="left",fill="x",expand=True,padx=10); self.seek.bind("<ButtonRelease-1>",self.seek_to)
        self.total=tk.Label(row,text="00:00",bg=PANEL,fg=MUTED,font=("Consolas",9)); self.total.pack(side="right")
        tk.Frame(now,bg=CYAN,height=2).pack(fill="x",padx=14,pady=(5,10))
        ctl=tk.Frame(self,bg=BG); ctl.pack(fill="x",padx=18,pady=8)
        self.button(ctl,"⏮",self.previous).pack(side="left",padx=(0,5))
        self.playbtn=self.button(ctl,"▶",self.play_pause,primary=True); self.playbtn.pack(side="left",padx=5)
        self.button(ctl,"⏭",self.next_track).pack(side="left",padx=5); self.button(ctl,"■",self.stop).pack(side="left",padx=5)
        self.shufbtn=self.button(ctl,"SHUFFLE",self.toggle_shuffle,True); self.shufbtn.pack(side="left",padx=(15,4))
        self.repbtn=self.button(ctl,"REPEAT",self.toggle_repeat,True); self.repbtn.pack(side="left",padx=4)
        tk.Label(ctl,text="VOL",bg=BG,fg=MUTED,font=("Segoe UI",8,"bold")).pack(side="left",padx=(15,5))
        self.vol=tk.DoubleVar(value=75); ttk.Scale(ctl,from_=0,to=100,variable=self.vol,command=lambda v:pygame.mixer.music.set_volume(float(v)/100)).pack(side="left",fill="x",expand=True)
        bar=tk.Frame(self,bg=BG); bar.pack(fill="x",padx=18,pady=(4,6))
        for label,cmd in [("＋ ДОБАВИТЬ ФАЙЛЫ",self.add_files),("＋ ПАПКА",self.add_folder),("ОТКРЫТЬ M3U",self.open_list),("СОХРАНИТЬ",self.save_list)]:
            self.button(bar,label,cmd,True).pack(side="left",padx=(0,6))
        self.button(bar,"ОЧИСТИТЬ",self.clear,True).pack(side="right")
        frame=tk.Frame(self,bg=PANEL,highlightbackground=EDGE,highlightthickness=1); frame.pack(fill="both",expand=True,padx=18,pady=(0,14))
        self.list=tk.Listbox(frame,bg="#101820",fg=TEXT,selectbackground="#176071",selectforeground="white",activestyle="none",font=("Segoe UI",10),bd=0,highlightthickness=0)
        sb=ttk.Scrollbar(frame,orient="vertical",command=self.list.yview); self.list.configure(yscrollcommand=sb.set)
        self.list.pack(side="left",fill="both",expand=True,padx=(6,0),pady=6); sb.pack(side="right",fill="y",padx=5,pady=6)
        self.list.bind("<Double-Button-1>",lambda e:self.play(self.list.curselection()[0]) if self.list.curselection() else None)
        self.bind("<space>",lambda e:self.play_pause()); self.bind("<Right>",lambda e:self.next_track()); self.bind("<Left>",lambda e:self.previous())
    def add_paths(self,paths):
        known={x["path"].casefold() for x in self.items}
        for p in paths:
            if Path(p).suffix.lower() in EXTS and str(p).casefold() not in known:
                x=info(p); self.items.append(x); known.add(str(p).casefold())
                self.list.insert("end",f'{x["artist"]} — {x["title"]}' if x["artist"] else x["title"])
        if self.current<0 and self.items:self.list.selection_set(0)
    def add_files(self):
        p=filedialog.askopenfilenames(filetypes=[("Аудио","*.mp3 *.wav *.ogg *.flac *.mid *.midi *.mod *.xm *.it *.s3m"),("Все файлы","*.*")]); self.add_paths(p)
    def add_folder(self):
        p=filedialog.askdirectory()
        if p:self.add_paths([str(x) for x in Path(p).rglob("*") if x.is_file() and x.suffix.lower() in EXTS])
    def play(self,i):
        if not 0<=i<len(self.items):return
        x=self.items[i]
        try:
            pygame.mixer.music.load(x["path"]); pygame.mixer.music.set_volume(self.vol.get()/100); pygame.mixer.music.play()
            self.current=i; self.paused=False; self.offset=0; self.playbtn.configure(text="Ⅱ")
            self.title_label.configure(text=x["title"]); self.artist_label.configure(text=x["artist"] or Path(x["path"]).name)
            self.total.configure(text=self.fmt(x["duration"])); self.elapsed.configure(text="00:00"); self.pos.set(0)
            self.list.selection_clear(0,"end"); self.list.selection_set(i); self.list.see(i); self.status.configure(text="PLAYING")
        except Exception as e:messagebox.showerror("Ошибка воспроизведения",f"Не удалось открыть файл:\n{x['path']}\n\n{e}")
    def play_pause(self):
        if self.current<0:
            if self.items:self.play(0)
        elif self.paused:pygame.mixer.music.unpause(); self.paused=False; self.playbtn.configure(text="Ⅱ")
        elif pygame.mixer.music.get_busy():pygame.mixer.music.pause(); self.paused=True; self.playbtn.configure(text="▶")
        else:self.play(self.current)
    def stop(self):
        pygame.mixer.music.stop(); self.paused=False; self.playbtn.configure(text="▶"); self.pos.set(0); self.elapsed.configure(text="00:00")
    def next_track(self):
        if self.items:self.play(random.randrange(len(self.items)) if self.shuffle and len(self.items)>1 else (self.current+1)%len(self.items))
    def previous(self):
        if self.items:self.play(max(0,self.current-1))
    def toggle_shuffle(self):
        self.shuffle=not self.shuffle; self.shufbtn.configure(fg="white" if self.shuffle else CYAN)
    def toggle_repeat(self):
        self.repeat=not self.repeat; self.repbtn.configure(fg="white" if self.repeat else CYAN)
    def seek_to(self,event=None):
        if self.current>=0:
            try:
                target=max(0,min(self.items[self.current]["duration"],self.pos.get())); pygame.mixer.music.set_pos(target); self.offset=target
            except pygame.error:pass
    def tick(self):
        if self.current>=0:
            x=self.items[self.current]; dur=x["duration"]
            if pygame.mixer.music.get_busy() and not self.paused:
                p=pygame.mixer.music.get_pos()/1000
                if p>=0:
                    sec=int(self.offset+p); self.elapsed.configure(text=self.fmt(sec))
                    if dur:self.pos.set(min(dur,sec))
            elif not self.paused and self.elapsed.cget("text")!="00:00":
                if self.repeat:self.play(self.current)
                elif self.current<len(self.items)-1 or self.shuffle:self.next_track()
                else:self.stop(); self.status.configure(text="FINISHED")
        self.after(200,self.tick)
    def fmt(self,n):return f"{int(n)//60:02d}:{int(n)%60:02d}"
    def open_list(self):
        p=filedialog.askopenfilename(filetypes=[("M3U","*.m3u *.m3u8")])
        if p:
            try:
                entries=[]
                for line in Path(p).read_text(encoding="utf-8-sig",errors="replace").splitlines():
                    line=line.strip()
                    if line and not line.startswith("#"):entries.append(str((Path(p).parent/line).resolve()) if not Path(line).is_absolute() and "://" not in line else line)
                self.clear(); self.add_paths(entries)
            except Exception as e:messagebox.showerror("Плейлист",str(e))
    def save_list(self):
        p=filedialog.asksaveasfilename(defaultextension=".m3u",filetypes=[("M3U","*.m3u")])
        if p:Path(p).write_text("#EXTM3U\n"+"\n".join(x["path"] for x in self.items)+"\n",encoding="utf-8")
    def clear(self):
        pygame.mixer.music.stop(); self.items.clear(); self.current=-1; self.list.delete(0,"end")
        self.title_label.configure(text="Добавьте музыку в плейлист"); self.artist_label.configure(text="AERO • ВАШ МУЗЫКАЛЬНЫЙ ПЛЕЕР")
        self.playbtn.configure(text="▶"); self.status.configure(text="READY")
    def close(self):
        pygame.mixer.music.stop(); pygame.mixer.quit(); self.destroy()

if __name__=="__main__": Player().mainloop()
