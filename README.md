# Source Soundscape Editor

A single-file desktop editor for **Source engine** soundscape and soundscript `.txt` files.

Built with **PySide6**, with an optional fallback to **PyQt6**.  
Audio preview uses **QtMultimedia** when available.

---

## Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Running](#running)
- [Usage](#usage)
- [Supported File Types](#supported-file-types)
- [File Format Notes](#file-format-notes)
- [Audio Preview](#audio-preview)
- [History, Undo and Redo](#history-undo-and-redo)
- [Settings](#settings)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [Project Structure](#project-structure)
- [Packaging with PyInstaller](#packaging-with-pyinstaller)
- [Troubleshooting](#troubleshooting)
- [Development Notes](#development-notes)

---

## Overview

`SoundScapeEditor.py` is a compact GUI tool for editing Source engine soundscape scripts commonly used with `env_soundscape`, and soundscript files used with `ambient_generic`.

The editor is designed to stay in one file, avoid unnecessary dependencies, and provide a practical workflow for level designers and modders:

- open existing `.txt` scripts;
- edit soundscape entries visually;
- manage looping and random sounds;
- preview audio directly from the editor;
- undo/redo changes through a visual history panel;
- save files back in a Source-friendly quoted format.

---

## Features

### Editing

- Edit **soundscape** files:
  - general properties:
    - soundscape name;
    - DSP room type;
    - DSP spatial;
    - DSP volume;
    - attenuation;
  - positional sounds:
    - `position0` … `position7`;
  - global sounds:
    - `playlooping`;
    - `playrandom`;
    - `rndwave` sound lists.

- Edit **soundscript** files:
  - script name;
  - channel;
  - wave path;
  - volume range;
  - pitch range;
  - soundlevel.

- Add, delete, copy and paste entries.
- Search/filter the entry list.
- Drag and drop `.txt` files into the window.
- Drag and drop audio files into wave path fields.

### Audio Preview

- Preview a single sound from any wave field.
- Browse game/mod `sound` folders from inside the editor.
- Preview a full soundscape:
  - looping sounds are started together;
  - random sounds are scheduled using their `time` ranges.
- Master volume slider for all preview playback.
- Preview stops automatically when switching entries or closing the app.

### History and Undo/Redo

- Standard undo/redo support.
- Visual history dock with step-by-step changes.
- Click a history step to roll back to that state.
- Diff summary for each history entry.
- Undo stack limited to 50 states.

### Interface

- Dark Valve-inspired UI palette.
- Russian and English UI.
- Custom animated splash screen.
- Floating/dockable history panel.
- Dark Windows title bar where supported.
- Generated PNG icons for arrows, spinners, close/float buttons and resize grip.

---

## Requirements

### Python

Python **3.10 or newer** is required.

PySide6 6.11.1 currently supports:

```txt
Python >=3.10,<3.15
```

### GUI Framework

Recommended:

```txt
PySide6==6.11.1
```

Optional fallback:

```txt
PyQt6==6.11.1
```

The script first tries to import PySide6. If PySide6 is unavailable, it falls back to PyQt6.

### Audio Preview

Audio preview is optional.

It uses:

```python
QtMultimedia.QMediaPlayer
QtMultimedia.QAudioOutput
```

These modules are normally available in standard PySide6/PyQt6 installations.  
If QtMultimedia cannot be imported, the editor still works, but audio preview buttons are disabled.

### Other Dependencies

No other external Python dependencies are required.

---

## Installation

### 1. Clone or download the repository

```bash
git clone <your-repository-url>
cd <repository-folder>
```

Or simply download `SoundScapeEditor.py`.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

#### Windows

```powershell
.venv\Scripts\activate
```

#### Linux / macOS

```bash
source .venv/bin/activate
```

### 3. Install PySide6

```bash
python -m pip install --upgrade pip
python -m pip install PySide6==6.11.1
```

### Optional: install PyQt6 fallback

Only needed if PySide6 cannot be used on your system:

```bash
python -m pip install PyQt6==6.11.1
```

---

## Running

From the project folder:

```bash
python SoundScapeEditor.py
```

The editor will create `settings.json` beside the script on first run.

If packaged with PyInstaller, settings are stored beside the executable.

---

## Usage

### Creating a New File

Use:

```text
File → New file
```

This creates an empty document.

The default type is **soundscape**.

### Opening a File

Use:

```text
File → Open...
```

Or drag a `.txt` file into the editor window.

The editor detects the file type from the file name:

- if the file name contains `_level_sounds`, it is treated as a **soundscript** file;
- otherwise it is treated as a **soundscape** file.

### Saving a File

Use:

```text
File → Save
```

or:

```text
File → Save as...
```

Saving writes the current document back to disk in a Source-style quoted key/value format.

### Editing a Soundscape

After selecting an entry in the left list, use the tabs on the right:

#### General

Editable fields:

- Soundscape name;
- DSP room type;
- DSP spatial;
- DSP volume;
- Attenuation.

#### Positions

Contains eight positional sound blocks:

```text
position0
position1
...
position7
```

Each position can contain:

- wave path;
- volume;
- pitch;
- soundlevel;
- attenuation.

#### Global Sounds

Contains:

- `playlooping` blocks;
- `playrandom` blocks.

Random blocks can contain a `rndwave` list with multiple wave paths.

### Editing a Soundscript

For files detected as soundscripts, the editor shows a single **Soundscripts** tab.

Editable fields:

- script name;
- channel;
- wave path;
- volume range;
- pitch range;
- soundlevel.

Volume and pitch can be single values or ranges, for example:

```txt
"volume" "1.0"
"volume" "0.8,1.2"
"pitch" "95,105"
```

---

## Supported File Types

### Soundscape Files

Typical use:

```txt
env_soundscape
```

Example:

```txt
"my_soundscape"
{
    "dsp" "1"
    "attenuation" "0.8"

    "position0"
    {
        "wave" "ambient/levels/canals/windhowl1.wav"
        "volume" "1.0"
        "pitch" "100"
        "soundlevel" "SNDLVL_75dB"
        "attenuation" "0.8"
    }

    "playlooping"
    {
        "wave" "ambient/music/loop_track1.wav"
        "volume" "0.7"
        "pitch" "100"
        "soundlevel" "SNDLVL_70dB"
        "position" "0"
    }

    "playrandom"
    {
        "time" "10,30"
        "volume" "0.5,0.8"
        "pitch" "95,105"
        "soundlevel" "SNDLVL_65dB"
        "position" "random"

        "rndwave"
        {
            "wave" "ambient/nature/birds/bird1.wav"
            "wave" "ambient/nature/birds/bird2.wav"
            "wave" "ambient/nature/birds/bird3.wav"
        }
    }
}
```

### Soundscript Files

Typical use:

```txt
ambient_generic
```

Files whose name contains `_level_sounds` are treated as soundscript files.

Example:

```txt
"my_level_sound"
{
    "channel" "CHAN_AUTO"
    "wave" "ambient/machines/machine_hum_loop1.wav"
    "volume" "0.8,1.0"
    "pitch" "95,105"
    "soundlevel" "SNDLVL_75dB"
}
```

---

## File Format Notes

The editor reads and writes Valve-style quoted blocks:

```txt
"key" "value"
```

and nested objects:

```txt
"key"
{
    "nested_key" "nested_value"
}
```

### Preserved Behavior

The serializer aims to keep the usual Source script structure:

- quoted keys;
- quoted string values;
- nested blocks;
- repeated keys for list-like blocks;
- stable dictionary/key order where possible.

### Normalized Output

The editor writes normalized indentation:

```txt
    "key" "value"
```

It does **not** attempt to preserve original whitespace exactly.

### Comments

Comments are understood during parsing but are **not preserved on save**.

Supported comment styles during reading:

```txt
// single-line comment
/* multi-line
   comment */
```

After saving, comments are removed.

---

## Audio Preview

### Single Sound Preview

Every wave field has a preview button:

```text
▶
```

Clicking it plays the selected sound.

Clicking again stops it if the same sound is currently playing.

### Sound Browser

The `...` button opens a file browser rooted at the detected `sound` directory.

The editor looks for a `sound` folder in these locations relative to the opened file:

```text
<file_folder>/sound
<parent_of_file_folder>/sound
```

Typical layout:

```text
game/
├── sound/
│   └── ambient/
└── scripts/
    └── my_soundscape.txt
```

### Full Soundscape Preview

The top preview bar contains:

```text
▶  ■
```

- `▶` starts preview for the currently selected soundscape;
- `■` stops all preview playback.

Full preview supports:

- positional looping sounds;
- `playlooping` blocks;
- `playrandom` blocks with scheduled random playback.

### Soundscript Preview Limitation

Whole-file preview is not available for soundscript files because they are individual `ambient_generic` scripts, not complete soundscape definitions.

### Master Volume

The slider in the preview bar controls global preview volume.

The value is saved in `settings.json`.

---

## History, Undo and Redo

The editor maintains a visual history of document states.

Open the history panel with:

```text
History
```

in the top bar.

### History Panel

The history panel shows:

- initial state;
- added entries;
- deleted entries;
- edited values;
- structural changes.

Each item has a tooltip with a diff summary.

Clicking a history step rolls the document back to that state.

### Undo and Redo

Undo and redo are available through standard shortcuts.

The undo stack stores snapshots of:

- document data;
- currently selected entry;
- detected file type.

The undo stack is limited to 50 states.

### Important Behavior

Undo/redo shortcuts are intentionally ignored while a text field, combo box or spin box has focus.

This prevents accidental history jumps while typing.

To use undo/redo safely:

- click outside the active field;
- or use the history panel.

---

## Settings

Settings are stored in:

```text
settings.json
```

Location:

- beside `SoundScapeEditor.py` when running from source;
- beside the executable when packaged with PyInstaller.

Example:

```json
{
  "lang": "en",
  "last_dir": "C:/Game/csgo/scripts",
  "master_volume": 1.0
}
```

### Supported Settings

| Key | Description |
|---|---|
| `lang` | UI language: `ru` or `en` |
| `last_dir` | Last used file dialog directory |
| `master_volume` | Global preview volume from `0.0` to `1.0` |

The file is created automatically on first run.

---

## Keyboard Shortcuts

| Action | Shortcut |
|---|---|
| Undo | `Ctrl+Z` / `Cmd+Z` |
| Redo | `Ctrl+Shift+Z`, `Ctrl+Y` / platform standard |
| Copy selected entry | `Ctrl+C` / `Cmd+C` |
| Paste entry | `Ctrl+V` / `Cmd+V` |
| Delete selected entry | `Del` |

Shortcuts may vary slightly depending on operating system and Qt standard key mappings.

---

## Project Structure

The project is intentionally kept as a single Python file:

```text
SoundScapeEditor.py
```

Main components:

| Component | Purpose |
|---|---|
| `VLV` | Color palette |
| `LANGS` | Russian and English UI strings |
| `STYLE` | Qt stylesheet |
| `SplashScreen` | Custom animated splash screen |
| `SoundBrowser` | Audio file browser dialog |
| `SoundscapeEditor` | Main application window and editor logic |

### UI Strings

All translatable UI strings must go through:

```python
self.t("key")
```

and be defined in:

```python
LANGS["ru"]
LANGS["en"]
```

### Colors

All colors should come from:

```python
VLV
```

Do not hardcode new colors directly in widgets unless absolutely necessary.

---

## Packaging with PyInstaller

The editor can be packaged into a standalone executable.

Install PyInstaller:

```bash
python -m pip install pyinstaller
```

Basic build:

```bash
pyinstaller --noconfirm --onedir --windowed --name "SourceSoundscapeEditor" SoundScapeEditor.py
```

With icon:

```bash
pyinstaller --noconfirm --onedir --windowed --name "SourceSoundscapeEditor" --icon soundscape.ico SoundScapeEditor.py
```

If you want to bundle an icon file beside the executable or inside the bundle:

```bash
pyinstaller --noconfirm --onedir --windowed --name "SourceSoundscapeEditor" --icon soundscape.ico --add-data "soundscape.ico;." SoundScapeEditor.py
```

On Linux/macOS use `:` instead of `;`:

```bash
--add-data "soundscape.ico:."
```

### Optional Boot Splash

The code supports PyInstaller’s splash screen through `pyi_splash`.

If you want to use it, build with:

```bash
pyinstaller --noconfirm --onedir --windowed --name "SourceSoundscapeEditor" --icon soundscape.ico --splash splash.png SoundScapeEditor.py
```

Where `splash.png` is your splash image.

The internal Qt splash screen is shown after the application has initialized.

---

## Troubleshooting

### The editor does not start

Make sure PySide6 or PyQt6 is installed:

```bash
python -m pip show PySide6
```

or:

```bash
python -m pip show PyQt6
```

If neither is installed, install PySide6:

```bash
python -m pip install PySide6==6.11.1
```

### Audio preview does not work

Check that QtMultimedia is available.

Try importing it manually:

```bash
python -c "from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput; print('OK')"
```

If this fails, audio preview is disabled.

On some Linux systems, additional system multimedia packages may be required by Qt.

### Sound browser cannot find sounds

The editor expects a `sound` folder near the `scripts` folder.

Valid layouts include:

```text
mod/
├── scripts/
│   └── my_soundscape.txt
└── sound/
    └── ...
```

or:

```text
mod/
└── scripts/
    ├── my_soundscape.txt
    └── sound/
        └── ...
```

### Undo does not work while typing

This is intentional.

Undo/redo shortcuts are ignored while a line edit, combo box or spin box has focus.

Click outside the field or use the history panel.

### Comments disappear after saving

This is expected.

The parser removes comments, and the serializer does not store them.

### File is treated as the wrong type

File type detection is based on the file name.

If the file name contains:

```text
_level_sounds
```

it is treated as a soundscript file.

Otherwise it is treated as a soundscape file.

Rename the file if needed.

---

## Development Notes

### Single-file Architecture

This project is designed to remain a single-file editor.

Avoid introducing new external dependencies unless absolutely necessary.

### Fallback Import Pattern

The GUI import pattern is:

```python
try:
    from PySide6.QtWidgets import *
    from PySide6.QtCore import *
    from PySide6.QtGui import *
except ImportError:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
```

Multimedia import is optional:

```python
try:
    from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
except ImportError:
    try:
        from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
    except ImportError:
        QMediaPlayer = None
        QAudioOutput = None
```

### Adding a New Language

To add a new language:

1. Add a new dictionary to `LANGS`.
2. Use the same keys as `ru` and `en`.
3. Add the language option to the language menu in `setup_menu_and_ui()`.

Example:

```python
"de": {
    "file": "Datei",
    "save": "Speichern",
}
```

### Adding a New UI String

Add the key to both language dictionaries:

```python
LANGS["ru"]["my_new_string"] = "Новая строка"
LANGS["en"]["my_new_string"] = "New string"
```

Then use it:

```python
self.t("my_new_string")
```

### Adding a New Color

Add it to `VLV`:

```python
VLV["my_color"] = "#rrggbb"
```

Then reference it in styles or code:

```python
VLV["my_color"]
```

---

## License

This repository does not currently include a license file.

If you plan to publish the project publicly, add an explicit license before distribution.
