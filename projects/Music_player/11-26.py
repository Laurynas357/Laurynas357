import os
import json
import random
import tkinter as tk
from tkinter import filedialog
from mutagen import File
from pyllist import dllist
from collections import deque


class MusicPlayerPlaylist:
    def __init__(self):
        self.songs = dllist()
        self.current_node = None

    def is_empty(self):
        return len(self.songs) == 0

    def add_song(self, song):
        if song.playlist_id is None:
            song.playlist_id = len(self.songs) + 1
        self.songs.append(song)
        if self.current_node is None:
            self.current_node = self.songs.first

    def play(self):
        if self.is_empty():
            print("Grojaraštis tuščias.")
        else:
            print(f"Dabar groja: {self.current_song()}")

    def next_song(self):
        if self.is_empty():
            return None
        self.current_node = self.current_node.next or self.songs.first
        return self.current_song()

    def prev_song(self):
        if self.is_empty():
            return None
        self.current_node = self.current_node.prev or self.songs.last
        return self.current_song()

    def current_song(self):
        if self.is_empty():
            return None
        return self.current_node.value

    def save_playlist(self, filename):
        if self.is_empty():
            print("Grojaraštis tuščias.")
            return
        data = [{
            "artist": s.artist,
            "album": s.album,
            "year": s.year,
            "track_number": s.track_number,
            "title": s.title,
            "format": s.format,
            "length": s.length,
            "path": s.path,
            "playlist_id": s.playlist_id
        } for s in self.to_list()]
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Išsaugota {filename}.")

    def load_playlist(self, filename):
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.clear()
        for s in data:
            song = Song(
                s["artist"], s["album"], s["year"],
                s["track_number"], s["title"], s["format"], s["path"],
                s.get("length", "Unknown")
            )
            song.playlist_id = s.get("playlist_id", None)
            self.add_song(song)
        self.current_node = self.songs.first
        print(f"Grojaraštis įkeltas iš {filename}.")

    def _rebuild_from_list(self, songs):
        self.clear()
        for s in songs:
            self.add_song(s)

    def clear(self):
        node = self.songs.first
        while node is not None:
            next_node = node.next
            self.songs.remove(node)
            node = next_node
        self.current_node = None

    def remove_song(self, song):
        node = self.songs.first
        while node is not None:
            if node.value == song:
                if self.current_node==node:
                    if node.next:
                        self.current_node=node.next
                    elif node.prev:
                        self.current_node=node.prev
                    else:
                        self.current_node=None
                self.songs.remove(node)
                return True
            node = node.next
        return False
    def to_list(self):
        return [node for node in self.songs]


class Stack:
    def __init__(self, maxsize=50):
        self._items = deque(maxlen=maxsize)

    def push(self, item):
        self._items.append(item)

    def pop(self):
        if not self.is_empty():
            return self._items.pop()
        return None

    def peek(self):
        if not self.is_empty():
            return self._items[-1]
        return None

    def is_empty(self):
        return len(self._items) == 0

    def size(self):
        return len(self._items)

    def to_list(self):
        return list(self._items)

class Song:
    def __init__(self, artist, album, year, track_number, title, format, path, length=None):
        self.artist = artist
        self.album = album
        self.year = year
        self.track_number = track_number
        self.title = title
        self.format = format
        self.path = path
        self.playlist_id = None

        if length is not None:
            self.length = length
        else:
            try:
                audio = File(path)
                if audio and audio.info:
                    seconds = int(audio.info.length)
                    mins = seconds // 60
                    secs = seconds % 60
                    self.length = f"{mins}:{secs:02d}"
                else:
                    self.length = "Unknown"
            except Exception:
                self.length = "Unknown"

    def __str__(self):
        return f"{self.artist} - {self.title} | {self.album} | {self.length}"


history_stack = Stack(maxsize=50)
playlist = MusicPlayerPlaylist()
is_playing = False
play_mode = "sequential"

root = tk.Tk()
root.title("Muzikos grotuvas")
root.geometry("900x500")
root.configure(bg="#121212")

playlist_display = tk.Listbox(
    root,
    width=70,
    height=15,
    bg="#181818",
    fg="white",
    selectbackground="#1DB954",
    font=("Segoe UI", 10),
    highlightthickness=0,
    borderwidth=0,
)
playlist_display.pack(pady=15)

current_song_label = tk.Label(
    root,
    text="Nėra grojančios dainos",
    bg="#121212",
    fg="white",
    font=("Segoe UI", 12, "bold"),
)
current_song_label.pack(pady=5)

control_frame = tk.Frame(root, bg="#121212")
control_frame.pack(side="bottom", pady=10)

def add_to_history(song):
    if song:
        history_stack.push(song)
def update_playlist_display():
    playlist_display.delete(0, tk.END)
    songs = playlist.to_list()
    for idx, song in enumerate(songs):
        display_text = f"{idx + 1}. [{song.playlist_id}] {song}"
        playlist_display.insert(tk.END, display_text)
        if playlist.current_node and song == playlist.current_song():
            playlist_display.itemconfig(idx, {'bg': '#1DB954', 'fg': 'black'})
            playlist_display.see(idx)


def toggle_play():
    global is_playing
    if not is_playing:
        play_button.config(text="⏸️")
        if not playlist.is_empty():
            current_song_label.config(text=f"Grojama: {playlist.current_song()}")
            add_to_history(playlist.current_song())
        else:
            current_song_label.config(text="Grojaraštis tuščias.")
        is_playing = True
    else:
        play_button.config(text="▶️")
        current_song_label.config(text="Sustabdyta")
        is_playing = False

def next_song():
    global play_mode
    if playlist.is_empty():
        return

    songs = playlist.to_list()

    if play_mode == "sequential":
        playlist.next_song()

    elif play_mode == "random":
        if len(songs) > 1:
            current = playlist.current_song()
            new_song = current
            while new_song == current:
                new_song = random.choice(songs)

            node = playlist.songs.first
            while node.value != new_song:
                node = node.next
            playlist.current_node = node

    add_to_history(playlist.current_song())
    current_song_label.config(text=f"{playlist.current_song()}")
    update_playlist_display()


def prev_song():
    if playlist.is_empty():
        return
    playlist.prev_song()
    add_to_history(playlist.current_song())
    current_song_label.config(text=f"{playlist.current_song()}")
    update_playlist_display()


def load_album_gui():
    folder = filedialog.askdirectory(title="Pasirinkite albumo aplanką")
    if not folder:
        return

    song_queue = deque()
    files = sorted(os.listdir(folder))

    for filename in files:
        if filename.lower().endswith(('.mp3', '.flac')):
            full_path = os.path.join(folder, filename)
            name_part, extension = os.path.splitext(filename)
            parts = name_part.split(" - ")

            if len(parts) >= 5:
                song = Song(*parts[:5], extension[1:], full_path)
            else:
                song = Song("Unknown", "Unknown", "????", "?", filename, extension[1:], full_path)

            song_queue.append(song)


    while song_queue:
        playlist.add_song(song_queue.popleft())

    playlist.current_node = playlist.songs.first
    update_playlist_display()

    if playlist.current_node:
        current_song_label.config(text=f"{playlist.current_node.value}")


def load_single_song_gui():
    file_path = filedialog.askopenfilename(title="Pasirinkite dainą", filetypes=[("Garso failai", "*.mp3 *.flac")])
    if not file_path:
        return
    filename = os.path.basename(file_path)
    name_part, extension = os.path.splitext(filename)
    parts = name_part.split(" - ")
    if len(parts) >= 5:
        artist, album, year, track_number, title = parts[:5]
    else:
        artist, album, year, track_number, title = "Nežinoma", "Nežinoma", "????", "?", filename
    song = Song(artist, album, year, track_number, title, extension[1:], file_path)
    playlist.add_song(song)
    update_playlist_display()
    if playlist.current_node:
        current_song_label.config(text=f"{playlist.current_song()}")


def load_playlist_gui():
    filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if filename:
        playlist.load_playlist(filename)
        update_playlist_display()
        if playlist.current_node:
            current_song_label.config(text=f"{playlist.current_song()}")


def save_playlist_gui():
    filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if filename:
        playlist.save_playlist(filename)


def delete_selected_song():
    sel = playlist_display.curselection()
    if not sel:
        return

    index = sel[0]
    songs = playlist.to_list()
    song_to_delete = songs[index]

    removed = playlist.remove_song(song_to_delete)
    if removed:
        for idx, song in enumerate(playlist.to_list(), start=1):
            song.playlist_id = idx

        update_playlist_display()
        if playlist.current_node:
            current_song_label.config(text=f"{playlist.current_song()}")
        else:
            current_song_label.config(text="Nėra grojančios dainos")
def delete_all_songs():
    playlist.clear()
    update_playlist_display()
    current_song_label.config(text="Grojaraštis išvalytas")


def quicksort(songs, key_func):
    if len(songs) <= 1:
        return songs

    piv_i = len(songs) // 2
    piv_song = songs[piv_i]
    piv_val = key_func(piv_song)

    maz = []
    lyg = []
    daug = []

    for song in songs:
        value = key_func(song)
        if value < piv_val:
            maz.append(song)
        elif value > piv_val:
            daug.append(song)
        else:
            lyg.append(song)

    return quicksort(maz, key_func) + lyg + quicksort(daug, key_func)


def sort_playlist_by(key):
    if playlist.is_empty():
        print("Grojaraštis tuščias, nėra ką rikiuoti.")
        return

    songs = playlist.to_list()

    if key == "artist":
        key_func = lambda s: s.artist.lower()
    elif key == "title":
        key_func = lambda s: s.title.lower()
    elif key == "album":
        key_func = lambda s: s.album.lower()
    elif key == "track":
        key_func = lambda s: s.playlist_id
    elif key == "length":
        def parse_len(l):
            try:
                m, s = l.split(":")
                return int(m) * 60 + int(s)
            except:
                return 0
        key_func = lambda s: parse_len(s.length)
    else:
        key_func = lambda s: s.title.lower()

    sorted_songs = quicksort(songs, key_func)
    playlist._rebuild_from_list(sorted_songs)
    update_playlist_display()
    current_song_label.config(text=f"Surikiuota pagal {key}.")


def show_history():
    if history_stack.is_empty():
        current_song_label.config(text="Istorija tuščia")
        return

    history_window = tk.Toplevel(root)
    history_window.title("Grojimo istorija")
    history_window.geometry("600x400")
    history_window.configure(bg="#121212")

    history_listbox = tk.Listbox(
        history_window,
        width=70,
        height=20,
        bg="#181818",
        fg="white",
        font=("Segoe UI", 10),
        highlightthickness=0,
        borderwidth=0,
    )
    history_listbox.pack(pady=15, padx=15, fill="both", expand=True)

    for idx, song in enumerate(reversed(history_stack.to_list()), start=1):
        history_listbox.insert(tk.END, f"{idx}. {song}")

btn_prev = tk.Button(control_frame, text="⏮️",command=prev_song, bg="#1DB954", fg="white", width=6, relief="flat")
play_button = tk.Button(control_frame, text="▶️", command=toggle_play, bg="#1DB954", fg="white", width=6, relief="flat")
btn_next = tk.Button(control_frame, text="⏭️", command=next_song, bg="#1DB954", fg="white", width=6, relief="flat")
btn_save = tk.Button(control_frame, text="Išsaugoti", command=save_playlist_gui, bg="#333333", fg="white", width=10, relief="flat")

btn_prev.pack(side="left", padx=5)
play_button.pack(side="left", padx=5)
btn_next.pack(side="left", padx=5)
btn_save.pack(side="left", padx=20)


load_menu = tk.Menu(root, tearoff=0, bg="#333333",fg="white", activebackground="#1DB954", activeforeground="black")
load_menu.add_command(label="Įkelti dainą", command=load_single_song_gui)
load_menu.add_command(label="Įkelti albumą", command=load_album_gui)
load_menu.add_command(label="Įkelti grojaraštį (.json)", command=load_playlist_gui)
btn_load = tk.Button(control_frame, text="Įkelti", bg="#333333", fg="white", width=10, relief="flat")
btn_load.pack(side="left", padx=20)
btn_load.bind("<Button-1>", lambda e: load_menu.post(e.x_root, e.y_root))


sort_menu = tk.Menu(root, tearoff=0, bg="#333333", fg="white",activebackground="#1DB954", activeforeground="black")
sort_menu.add_command(label="Pagal atlikėją", command=lambda: sort_playlist_by("artist"))
sort_menu.add_command(label="Pagal pavadinimą", command=lambda: sort_playlist_by("title"))
sort_menu.add_command(label="Pagal albumą", command=lambda: sort_playlist_by("album"))
sort_menu.add_command(label="Pagal numerį", command=lambda: sort_playlist_by("track"))
sort_menu.add_command(label="Pagal trukmę", command=lambda: sort_playlist_by("length"))
btn_sort = tk.Button(control_frame, text="Rikiuoti", bg="#333333", fg="white", width=10, relief="flat")
btn_sort.pack(side="left", padx=10)
btn_sort.bind("<Button-1>", lambda e: sort_menu.post(e.x_root, e.y_root))


play_mode_menu = tk.Menu(root, tearoff=0, bg="#333333", fg="white",activebackground="#1DB954", activeforeground="black")
play_mode_menu.add_command(label="Iš eilės", command=lambda: set_play_mode("sequential"))
play_mode_menu.add_command(label="Atsitiktinai", command=lambda: set_play_mode("random"))
btn_mode = tk.Button(control_frame, text="Grojimo režimas",bg="#333333", fg="white", width=15, relief="flat")
btn_mode.pack(side="left", padx=10)
btn_mode.bind("<Button-1>", lambda e: play_mode_menu.post(e.x_root, e.y_root))

delete_menu = tk.Menu(root, tearoff=0, bg="#333333", fg="white", activebackground="#1DB954", activeforeground="black")
delete_menu.add_command(label="Ištrinti pasirinktą dainą", command=lambda: delete_selected_song())
delete_menu.add_command(label="Ištrinti visas dainas", command=lambda: delete_all_songs())

btn_delete = tk.Button(control_frame, text="Ištrinti",bg="#333333", fg="white", width=10, relief="flat")
btn_delete.pack(side="left", padx=10)
btn_delete.bind("<Button-1>", lambda e: delete_menu.post(e.x_root, e.y_root))

def set_play_mode(mode):
    global play_mode
    play_mode = mode
    current_song_label.config(text=f"Grojimo režimas: {mode.capitalize()}")

btn_history = tk.Button(control_frame, text="Istorija", command=show_history, bg="#333333", fg="white", width=10, relief="flat")
btn_history.pack(side="left",padx=10)

root.mainloop()
