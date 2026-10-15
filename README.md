# Source Soundscape Editor

A desktop editor for Source engine soundscape and soundscript files. Edit Valve KeyValues-style **.txt** files, browse sounds from game folders or VPK archives, and preview audio in the app.

<img width="1922" height="1415" alt="Source Soundscape Editor screenshot" src="https://github.com/user-attachments/assets/f06382d3-93cd-444c-a11f-8ea96060ccbd" />

## Features

- Edit soundscape entries, including DSP settings, eight positional sound slots, looping sounds, and random sound groups.
- Switch between **position0–position7** using a dedicated tab for each slot.
- Edit soundscripts with channel, wave, volume, pitch, and soundlevel fields.
- Search entries; add, rename, copy, paste, and delete them.
- Open and save **.txt** files, or drag files into the editor.
- Browse audio files in a local **sound/** directory and in mounted VPK archives.
- Mount VPK files from Settings or by dropping them into the VPK list. Split archives are supported; select the matching **_dir.vpk** and sibling parts are found automatically.
- Preview individual sounds or a complete soundscape. Adjust master preview volume.
- Use undo/redo and the dockable edit history.
- Switch the interface between English and Russian.

## Requirements

- Python 3.10 or newer
- PySide6 6.11.1 (listed in **requirements.txt**)

Qt Multimedia is used for playback. If its components are unavailable in the PySide6 installation, editing still works but audio preview is unavailable.

## Run from source

From the repository directory:

    python -m venv .venv

Activate the environment, then install the dependencies:

    # Windows PowerShell
    .venv\Scripts\Activate.ps1

    # macOS/Linux
    source .venv/bin/activate

    python -m pip install -r requirements.txt
    python SoundScapeEditor.py

The editor creates **settings.json** beside the script on first launch.

## Open and edit files

Use **File → Open** or drag a **.txt** file into the window. The editor treats a filename containing **_level_sounds** (case-insensitive) as a soundscript; other **.txt** files open as soundscapes.

Select an entry in the left panel to edit it. Soundscape fields are split across **General**, **Positions**, and **Global Sounds**. The Positions tab has one sub-tab for each slot, **0** through **7**. Soundscripts use their own editing tab.

Use **File → Save** or **Save As** to write the document. The editor writes normalized indentation and quoted KeyValues blocks.

### Sound browser and VPK archives

The sound browser combines files from a local **sound/** folder with sounds found in mounted VPKs. Local files take precedence when the same path exists in both sources. Mount or unmount archives from **Settings → VPK**; mounted paths are saved in **settings.json** and restored at the next launch.

For a split VPK set, choose its **_dir.vpk** file. The matching numbered archive parts must be alongside it.

### Audio preview

Use the preview button beside a wave field to audition one sound. The main preview controls play or stop the selected soundscape, including its looping and scheduled random sounds. Preview audio can come from disk or a mounted VPK.

Soundscript entries can be previewed by wave, but the editor does not play a soundscript as a complete soundscape. Playback depends on codecs supported by the system's Qt Multimedia backend.

## File format notes

The editor reads and writes quoted KeyValues-style blocks, including nested blocks and repeated keys used by **rndwave** lists. Comments (**//** and **/* ... */**) are accepted while reading, but are not preserved when saving. Original whitespace is normalized.

Soundscape example:

    "my_soundscape"
    {
        "dsp" "1"
        "position0"
        {
            "wave" "ambient/levels/canals/windhowl1.wav"
            "volume" "1.0"
            "pitch" "100"
            "soundlevel" "SNDLVL_75dB"
        }
        "playlooping"
        {
            "wave" "ambient/music/loop_track1.wav"
            "volume" "0.7"
            "position" "0"
        }
    }

## Settings and shortcuts

**settings.json** stores the interface language, last folder, recent files, master preview volume, and mounted VPK paths. It is created beside the script, or beside the executable in a packaged build.

| Action | Shortcut |
| --- | --- |
| Undo | Ctrl+Z |
| Redo | Ctrl+Shift+Z or Ctrl+Y |
| Copy selected entry | Ctrl+C |
| Paste entry | Ctrl+V |
| Delete selected entry | Delete |

Qt may map standard shortcuts differently on some platforms. Undo/redo shortcuts are ignored while an editor field has focus; use the history panel or move focus out of the field.

## Build with PyInstaller

Install PyInstaller in the active environment:

    python -m pip install pyinstaller

Then run the project build script:

    pyinstaller --noconfirm SoundScapeEditor.spec

On Windows, **compile.bat** runs this command. The spec uses **splash.png** and **soundscape.ico**; run the build from the repository directory.

## Project files

| File | Purpose |
| --- | --- |
| **SoundScapeEditor.py** | Main Qt application |
| **vpk_reader.py** | VPK reader, sound index, and temporary extraction |
| **requirements.txt** | Runtime dependency |
| **SoundScapeEditor.spec** | PyInstaller build configuration |
| **compile.bat** | Windows build shortcut |
| **settings.json** | User settings, generated at runtime |

## Troubleshooting

**The app does not start:** activate the environment where dependencies were installed and run **python -m pip install -r requirements.txt**.

**Preview is silent:** check that the sound path is valid and that the system's Qt Multimedia backend supports the file's codec. Audio preview is optional; file editing does not depend on it.

**A sound is missing from the browser:** check that the archive is mounted or that the game folder contains a **sound/** directory. For a split VPK, select the **_dir.vpk** file.

**Comments disappear after saving:** this is expected; comments are parsed but not retained by the editor.

## License

This repository does not currently include a **LICENSE** file. Add the license you choose to the repository before publishing or redistributing it.

