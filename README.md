# AccessiFight

## Introduction

Welcome to AccessiFight, the accessibility companion for fighting games.

All the classic fighting games we know and love are fast-paced, high-energy heart pounders. But for totally blind players, the on-screen information that sighted players take for granted, things like health bars, super meters, round timers and menus, is completely invisible.

What if there was a way to get all of that visual information described to you, so you can focus on fighting the game's characters rather than the game itself? Introducing AccessiFight!

AccessiFight is a lightweight tool for Windows that captures your game screen on demand and describes what it sees, using your choice of offline OCR, Google Gemini, or Cloudflare Workers AI. It runs quietly in the background and responds to global hotkeys, so you never have to leave your game.

## System requirements

AccessiFight requires at least Windows 7 or higher in order to run. Both 32-bit and 64-bit Windows editions are supported. A compatible screen reader is required for screen reader output mode. SAPI 5 speech output works with any voice installed on the system.

## Download and installation

### From source

Here are the instructions for running AccessiFight from its source code on Windows.

1. Download and install [Git for Windows](https://github.com/git-for-windows/git/releases/download/v2.53.0.windows.2/Git-2.53.0.2-64-bit.exe).
2. Press Windows + R, type powershell and hit enter.
3. Install [UV](https://docs.astral.sh/uv/), a lightning fast, modern package manager for Python written in Rust.
    ```powershell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```
4. Use UV to install Python if it is not already installed.
    ```
    uv python install
    ```
5. Clone the repository and switch to its directory.
    ```
    git clone https://github.com/seedy60/AccessiFight.git
    cd AccessiFight
    ``    `
6. Install the required libraries.
    ```
    uv sync
    ```
7. Run the program.
    ```
    uv run python apm.py
    ```

### Compiled

1. [Download the latest release](https://github.com/seedy60/AccessiFight/releases/latest/download/afight.zip).
2. Extract the zip file with your zip archiver of choice.
3. Navigate to the extracted program folder and run afight.exe. If file extensions don't show on your system, the filename will just be afight.

## First-launch setup

When you launch AccessiFight for the first time, a setup wizard will appear. This wizard lets you configure two things: how AccessiFight speaks to you, and how it describes what's on screen.

### Speech output

You can choose between two speech output modes:

### Screen reader

AccessiFight speaks through your screen reader, such as NVDA or JAWS. This is the default setting.

### SAPI 5

AccessiFight speaks through SAPI 5, the text to speech synthesizer built into Windows, using any of your installed system voices. If you select this option, a dropdown will appear listing all your installed SAPI 5 voices.

### Description method

This is how AccessiFight analyses your game screen. There are three options:

### Offline OCR (Tesseract).

AccessiFight extracts visible text from the screen using Tesseract OCR. This is completely offline and free, but can only read text, such as menu items and on-screen pop-ups. It cannot interpret graphical data like health bars or meters that turn from green to red.
Tesseract must be installed separately. You can [download it here](https://github.com/UB-Mannheim/tesseract/wiki). If Tesseract isn't in your PATH, you can set its location in the settings.

### Google Gemini.

AccessiFight sends a screenshot to Google's Gemini AI for a detailed description. This requires a free API key from [Google AI Studio](https://aistudio.google.com/apikey). Once you enter your key, you can click List Models in AccessiFight's settings to choose from all available Gemini models.

### Cloudflare Workers AI.

AccessiFight sends a screenshot to Cloudflare's Workers AI platform. This requires a Cloudflare account ID and API token, both available from the [Cloudflare dashboard](https://dash.cloudflare.com). You can choose from a curated list of vision-capable models, or enter a custom model name. Some Cloudflare models require a one-time license agreement; AccessiFight handles this automatically on first use.

When you're done, click Save & Start and AccessiFight will begin running in the background.

## Changing settings

You can open the settings dialog at any time using the settings hotkey, Windows+Shift+Control+P. Your settings are stored in a JSON file at `%APPDATA%\AccessiFight\config.json`.

## Hotkeys

AccessiFight uses 7 global hotkeys. These hotkeys work from anywhere within Windows, so you never need to switch away from your game.

* Windows+Shift+Control+M: describe any menus visible on screen. Reports the menu title, all visible items in order, and which item is currently highlighted.
* Windows+Shift+Control+H: describe health/life bars. Reports which player each bar belongs to, its approximate fill percentage, and its on-screen position, top left or top right.
* Windows+Shift+Control+S: describe super meters, EX gauges, or other special move resources. Reports which player each meter belongs to and its fill level.
* Windows+Shift+Control+O: describe an options or settings screen. Lists all visible items, the highlighted item, and any slider or adjustable values.
* Windows+Shift+Control+R: describe the round timer. Reports the remaining time and its position on screen.
* Windows+Shift+Control+P: open the settings dialog.
* Windows+Shift+Control+Q: quit AccessiFight.

When you press a description hotkey, AccessiFight will say "Scanning", take a screenshot of  the active game window, send it to your chosen description backend, and then speak the result.

## How it works

AccessiFight captures only the currently active foreground window, not your entire screen. The captured image is then processed by whichever description method you've configured. For Gemini and Cloudflare, the image is sent as a base64-encoded PNG along with a specialised prompt tailored to the type of information you requested (menus, health bars, meters, etc). For OCR, the image is passed directly to Tesseract for text extraction.
