# ezUIMaker

Native desktop application for visually designing Tkinter interfaces and generating runnable Python scripts. It uses Python's standard-library Tkinter; no browser or third-party UI framework is needed. English is the default language, and French is available from the language selector. The language choice is saved in `~/.ezuimaker.json`.

## Run

```sh
python -m pip install -r requirements.txt
python app.py
```

Add labels, buttons, inputs, frames, checkboxes, text areas, images, and videos from the component palette. Drag items on the canvas, resize the selected item from its corner handle, and edit its content, position, size, font, and colors in the inspector. Select a frame before adding an item to nest it. Use the canvas zoom and grid snapping controls, arrow keys to nudge, `Delete` to remove, and `Ctrl+D` to duplicate. Double-click a video to preview it. The generated Tkinter code updates live.

Generated scripts that use images or video require Pillow and OpenCV as well. Keep source media files available at their saved paths when running the generated script.

**Export Python** saves the generated `.py` file. **Build .exe** saves the Python script and prepares a Windows build file when run on another operating system. On Windows, the app can invoke PyInstaller directly when it is installed. An executable must be built on Windows for Windows.
