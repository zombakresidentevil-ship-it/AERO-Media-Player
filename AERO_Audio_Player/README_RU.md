# AERO Audio Player
Standalone Windows audio player. Tkinter UI, pygame/SDL_mixer playback, Mutagen tags. No VLC or separately installed codec pack is required: runtime libraries are bundled into one EXE by PyInstaller.

Formats: MP3, WAV, OGG, FLAC, MIDI, MOD, XM, IT, S3M (actual support depends on bundled SDL_mixer build).

Features: add files/folders, play/pause/stop, previous/next, shuffle, repeat, volume, seek, audio tags, M3U playlists.

Build on Windows 10/11 x64 with Python 3.12 by running build_win.bat. GitHub Actions produces one portable EXE; size is printed in the build log.
