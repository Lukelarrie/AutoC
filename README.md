# 🖱️ AutoC v2.0 - Advanced Auto Clicker

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

AutoC is a modern, highly customizable auto-clicker built in Python. Designed with a sleek **Dark Mode UI** and **hardware-level input simulation**, it provides advanced anti-detection features and precision targeting for power users and gamers alike.

---

## 📸 Preview
> [!TIP]
> *Insert a high-quality screenshot or a short GIF of the AutoC dashboard here to showcase the "Modern Aesthetic".*

---

## 📑 Table of Contents
- [Why AutoC?](#-why-autoc)
- [Features](#-features)
- [Installation](#-installation)
- [Building the Executable](#-building-the-executable)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🚀 Why AutoC?
Most auto-clickers available today either look like they belong in Windows 95, are packed with ads, or fail to work in modern full-screen games because they use high-level software click simulation.

AutoC v2.0 solves these problems by providing:
1. **Modern Aesthetic:** A clean, flat-design dashboard using `customtkinter`.
2. **Anti-Detection Mechanics:** Built-in randomization to simulate human clicking behavior.
3. **Maximum Compatibility:** Utilizes low-level Windows API (`ctypes` SendInput) to ensure clicks register in any application, including DirectX/full-screen games.
4. **Performance:** Highly optimized with UI throttling to prevent memory leaks and CPU spikes, even at 1000+ clicks per second.

---

## ✨ Features

### 🖱️ Click Options
* **Customizable Hotkeys:** Set a global start/stop hotkey (Default: `F8`) that works even when the app is minimized.
* **Button & Type Selection:** Choose between Left, Right, or Middle clicks; set actions to Single, Double, or Triple clicks.
* **Click Limits:** Automatically stop clicking after a precise number of clicks.

### ⏱️ Delay & Timing (Anti-Detection)
* **Base Interval:** Set exact millisecond delays between clicks.
* **Interval Randomization:** Add a `± ms` range (e.g., 100ms ± 20ms) so your click speed fluctuates naturally.
* **Hold Duration:** Control exactly how long the mouse button is physically held down.

### 🎯 Precision Targeting
* **Current Cursor:** Clicks wherever your mouse is, with a live X/Y coordinate tracker.
* **Fixed Location:** Input precise X/Y screen coordinates manually.
* **Location Picker:** Use the built-in screen overlay to click a spot and capture its coordinates.
* **Area Randomization:** Set a pixel radius around your target to prevent robotic single-pixel clicking.

### 💾 Quality of Life
* **Profile Management:** Save and load complex configurations via `.json` files.
* **Always on Top:** Keep the dashboard pinned above your games or workspaces.

---

## 🛠️ Installation

### Requirements
* **Python 3.10+**
* **Windows OS** (Required for hardware-level `ctypes` clicking)

### Setup Steps
1. **Clone the repository:**
   ```bash
   git clone https://github.com/Lukelarrie/AutoC.git
   cd AutoC
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

---

## 📦 Building the Executable (.exe)
Want to share the app without requiring Python? We've included an automated build script.

1. Double-click the **`build.bat`** file in the project folder.
2. The script will automatically install `PyInstaller` and compile the app.
3. Find your portable app in the `dist/` folder as **`AutoC_v2.0.exe`**.

---

## 🤝 Contributing
Contributions are welcome! If you have ideas for new features or find a bug:
1. Fork the Project.
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the Branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---

## ⚖️ License
Distributed under the **MIT License**. See `LICENSE` for more information.

---

> [!WARNING]  
> **Disclaimer:** Use responsibly. The creators are not responsible for bans or penalties incurred while using this software in competitive gaming environments.
