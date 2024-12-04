
# Manga2x GUI

## Overview
_Manga2x GUI_ is a graphical user interface (GUI) application designed with [Tcl/Tk GUI toolkit](https://docs.python.org/3.12/library/tkinter.html) to up-scale images within EPUB manga files using [Waifu2x](https://github.com/nagadomi/waifu2x) or [Realesrgan](https://github.com/xinntao/ESRGAN) using [NCNN](https://github.com/Tencent/ncnn) with Vulkan to call GPU acceleration, recommending 4GB of VRAM or more, or enabling shared VRAM in NVIDIA settings.

## Image preview
<img height="200" src="https://raw.githubusercontent.com/puff-dayo/Manga2x/fba715067f8ddc43a0a73b1e250db8307a650a83/preview.png"/>

## Requirements
- Python 3.10+
- Python packages (requirements.txt )
- Windows 11 Build 22000+ 
- GPU with Vulkan support

## Installation

   ```bash
   git clone https://github.com/puff-dayo/Manga2x.git
   cd Manga2x
   ```

Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

Run:
   ```bash
   python MangaUpGUI.py
   ```

## Output
- The up-scaled EPUB files will be saved in the same directory as the original files, with a suffix indicating the up-scaling method (e.g., `_Moderate2x.epub`).
