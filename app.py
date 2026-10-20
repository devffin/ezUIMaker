import json
import os
import re
import subprocess
import sys
import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox, ttk

try:
    import cv2
except ImportError:
    cv2 = None

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = ImageTk = None


TEXT = {
    "en": {
        "title": "ezUIMaker | Python UI Builder", "project": "My interface", "language": "Language",
        "python": "Export Python", "exe": "Build .exe", "components": "COMPONENTS", "layers": "LAYERS",
        "canvas": "DESIGN CANVAS", "inspector": "INSPECTOR", "code": "GENERATED PYTHON",
        "label": "Label", "button": "Button", "entry": "Input", "frame": "Frame", "checkbox": "Checkbox", "text": "Text area", "image": "Image", "video": "Video", "play_preview": "Play preview",
        "add_image": "Add image...", "add_video": "Add video...", "replace_media": "Replace file...", "media_source": "Media source", "media_missing": "Media preview needs Pillow. Install the optional media dependencies.", "video_missing": "Video preview needs OpenCV and Pillow. Install the optional media dependencies.", "file_missing": "This media file could not be opened.", "play_video": "Double-click a video to preview it.",
        "hint": "Select a frame to nest an item. Drag to move; use the corner handle to resize.", "empty": "Add a component to get started", "snap": "Snap to grid",
        "window_size": "Window size", "clear": "Clear", "select_hint": "Select a component to edit its properties.",
        "element": "Element", "content": "Content", "position": "Position", "size": "Size", "x": "X", "y": "Y", "width": "Width", "height": "Height",
        "typography": "Typography", "font": "Font", "font_size": "Size (px)", "weight": "Weight", "regular": "Regular", "bold": "Bold",
        "colors": "Colors", "text_color": "Text", "background": "Background", "duplicate": "Duplicate", "delete": "Delete",
        "default_label": "Your text", "default_button": "Click me", "default_entry": "Enter text...", "default_frame": "Frame",
        "default_checkbox": "Enable this option", "default_text": "Text area", "default_image": "Image", "default_video": "Video", "layers_empty": "No elements yet",
        "ready": "Ready", "items": "{count} component(s)", "copied": "Python code copied", "saved": "Python script saved",
        "save_python": "Save Python script", "save_exe": "Save project for .exe build", "python_files": "Python files",
        "exe_prepared": "The Python script and Windows build file were saved. Run the .bat file on Windows to create the .exe.",
        "pyinstaller_missing": "PyInstaller is not installed. Install it with: python -m pip install pyinstaller",
        "dependencies_missing": "Install the required packages first: python -m pip install {packages}",
        "build_running": "Building Windows executable...", "build_success": "Executable created in dist.",
        "build_failed": "PyInstaller could not create the executable. Check the build log next to your script.",
        "no_components": "Add components before exporting.", "clipboard_error": "Clipboard access is unavailable.",
    },
    "fr": {
        "title": "ezUIMaker | Atelier Python", "project": "Mon interface", "language": "Langue",
        "python": "Exporter Python", "exe": "Créer .exe", "components": "COMPOSANTS", "layers": "CALQUES",
        "canvas": "ESPACE DE CRÉATION", "inspector": "INSPECTEUR", "code": "CODE PYTHON GÉNÉRÉ",
        "label": "Texte", "button": "Bouton", "entry": "Champ", "frame": "Frame", "checkbox": "Case à cocher", "text": "Zone de texte", "image": "Image", "video": "Vidéo", "play_preview": "Lire l’aperçu",
        "add_image": "Ajouter une image...", "add_video": "Ajouter une vidéo...", "replace_media": "Remplacer le fichier...", "media_source": "Source du média", "media_missing": "L’aperçu des images nécessite Pillow. Installez les dépendances média facultatives.", "video_missing": "L’aperçu vidéo nécessite OpenCV et Pillow. Installez les dépendances média facultatives.", "file_missing": "Impossible d’ouvrir ce fichier média.", "play_video": "Double-cliquez sur une vidéo pour la prévisualiser.",
        "hint": "Sélectionnez une frame pour y imbriquer un élément. Glissez pour déplacer, utilisez la poignée pour redimensionner.", "empty": "Ajoutez un composant pour commencer", "snap": "Aligner sur la grille",
        "window_size": "Taille de la fenêtre", "clear": "Effacer", "select_hint": "Sélectionnez un élément pour modifier ses propriétés.",
        "element": "Élément", "content": "Contenu", "position": "Position", "size": "Taille", "x": "X", "y": "Y", "width": "Largeur", "height": "Hauteur",
        "typography": "Typographie", "font": "Police", "font_size": "Taille (px)", "weight": "Graisse", "regular": "Normale", "bold": "Gras",
        "colors": "Couleurs", "text_color": "Texte", "background": "Fond", "duplicate": "Dupliquer", "delete": "Supprimer",
        "default_label": "Votre texte", "default_button": "Cliquer ici", "default_entry": "Saisir du texte...", "default_frame": "Frame",
        "default_checkbox": "Activer cette option", "default_text": "Zone de texte", "default_image": "Image", "default_video": "Vidéo", "layers_empty": "Aucun élément pour le moment",
        "ready": "Prêt", "items": "{count} composant(s)", "copied": "Code Python copié", "saved": "Script Python enregistré",
        "save_python": "Enregistrer le script Python", "save_exe": "Préparer le projet .exe", "python_files": "Fichiers Python",
        "exe_prepared": "Le script Python et le fichier de compilation Windows sont enregistrés. Lancez le fichier .bat sous Windows pour créer le .exe.",
        "pyinstaller_missing": "PyInstaller n’est pas installé. Installez-le avec : python -m pip install pyinstaller",
        "dependencies_missing": "Installez d’abord les dépendances nécessaires : python -m pip install {packages}",
        "build_running": "Compilation de l’exécutable Windows...", "build_success": "Exécutable créé dans dist.",
        "build_failed": "PyInstaller n’a pas pu créer l’exécutable. Consultez le journal de compilation à côté du script.",
        "no_components": "Ajoutez des composants avant l’export.", "clipboard_error": "Le presse-papiers est indisponible.",
    },
}

COMPONENTS = ("label", "button", "entry", "frame", "checkbox", "text", "image", "video")
DEFAULTS = {
    "label": {"x": 38, "y": 38, "w": 190, "h": 34, "fg": "#20231f", "bg": "#ffffff", "size": 16, "bold": False, "font": "Segoe UI"},
    "button": {"x": 38, "y": 38, "w": 150, "h": 42, "fg": "#ffffff", "bg": "#27351f", "size": 13, "bold": True, "font": "Segoe UI"},
    "entry": {"x": 38, "y": 38, "w": 230, "h": 34, "fg": "#20231f", "bg": "#ffffff", "size": 12, "bold": False, "font": "Segoe UI"},
    "frame": {"x": 28, "y": 28, "w": 320, "h": 205, "fg": "#343b30", "bg": "#f2f4ef", "size": 12, "bold": True, "font": "Segoe UI"},
    "checkbox": {"x": 38, "y": 38, "w": 205, "h": 30, "fg": "#20231f", "bg": "#ffffff", "size": 12, "bold": False, "font": "Segoe UI"},
    "text": {"x": 38, "y": 38, "w": 240, "h": 105, "fg": "#20231f", "bg": "#ffffff", "size": 12, "bold": False, "font": "Segoe UI"},
    "image": {"x": 38, "y": 38, "w": 260, "h": 180, "fg": "#20231f", "bg": "#e8ebe3", "size": 11, "bold": False, "font": "Segoe UI"},
    "video": {"x": 38, "y": 38, "w": 320, "h": 200, "fg": "#ffffff", "bg": "#20231f", "size": 11, "bold": False, "font": "Segoe UI"},
}


def generate_python(project_name, width, height, components):
    """Generate a runnable Tkinter script from a flat component list."""
    by_id = {item["id"]: item for item in components}
    roots = [item for item in components if not item.get("parent")]
    has_images = any(item["type"] == "image" for item in components)
    has_videos = any(item["type"] == "video" for item in components)
    lines = ["import tkinter as tk"]
    if has_images or has_videos:
        lines.extend(["from PIL import Image, ImageTk"])
    if has_videos:
        lines.append("import cv2")
    lines.extend([
        "", "", "class GeneratedUI(tk.Tk):", "    def __init__(self):",
        "        super().__init__()", f"        self.title({project_name!r})",
        f"        self.geometry({(str(width) + 'x' + str(height))!r})", "        self._build_ui(self)", "",
        "    def _build_ui(self, parent):",
    ])
    if not roots:
        lines.append("        pass")

    def emit(item, parent_name, indent):
        pad = " " * indent
        variable = "widget_" + re.sub(r"\W", "_", item["id"])
        weight = "bold" if item["bold"] else "normal"
        font = f"({item['font']!r}, {item['size']}, {weight!r})"
        if item["type"] == "frame":
            lines.append(f"{pad}{variable} = tk.Frame({parent_name}, bg={item['bg']!r}, highlightbackground={item['fg']!r}, highlightthickness=1)")
            lines.append(f"{pad}{variable}.place(x={item['x']}, y={item['y']}, width={item['w']}, height={item['h']})")
            title = f"{variable}_title"
            lines.append(f"{pad}{title} = tk.Label({variable}, text={item['text']!r}, bg={item['bg']!r}, fg={item['fg']!r}, font={font}, anchor='w')")
            lines.append(f"{pad}{title}.place(x=8, y=4)")
            for child_id in item.get("children", []):
                child = by_id.get(child_id)
                if child:
                    emit(child, variable, indent)
            return
        if item["type"] == "image":
            lines.append(f"{pad}image_{variable} = Image.open({item['path']!r})")
            lines.append(f"{pad}image_{variable}.thumbnail(({item['w']}, {item['h']}), Image.Resampling.LANCZOS)")
            lines.append(f"{pad}self.{variable}_photo = ImageTk.PhotoImage(image_{variable})")
            lines.append(f"{pad}{variable} = tk.Label({parent_name}, image=self.{variable}_photo, bg={item['bg']!r}, bd=0)")
            lines.append(f"{pad}{variable}.place(x={item['x']}, y={item['y']}, width={item['w']}, height={item['h']})")
            return
        if item["type"] == "video":
            video_title = f"▶  {os.path.basename(item['path'])}"
            lines.append(f"{pad}{variable} = tk.Label({parent_name}, text={video_title!r}, bg='#20231f', fg='#ffffff', font=('Segoe UI', 11), compound='center')")
            lines.append(f"{pad}{variable}.place(x={item['x']}, y={item['y']}, width={item['w']}, height={item['h']})")
            lines.append(f"{pad}self.{variable}_capture = cv2.VideoCapture({item['path']!r})")
            lines.append(f"{pad}{variable}.bind('<Button-1>', lambda _event: self._play_{variable}())")
            return
        options = f"bg={item['bg']!r}, fg={item['fg']!r}, font={font}"
        if item["type"] == "label":
            lines.append(f"{pad}{variable} = tk.Label({parent_name}, text={item['text']!r}, {options}, anchor='w', bd=0)")
        elif item["type"] == "button":
            lines.append(f"{pad}{variable} = tk.Button({parent_name}, text={item['text']!r}, {options}, relief='flat', bd=0, cursor='hand2')")
        elif item["type"] == "entry":
            lines.append(f"{pad}{variable} = tk.Entry({parent_name}, {options}, relief='solid', bd=1)")
            if item["text"]:
                lines.append(f"{pad}{variable}.insert(0, {item['text']!r})")
        elif item["type"] == "checkbox":
            lines.append(f"{pad}self.{variable}_value = tk.BooleanVar(value=True)")
            lines.append(f"{pad}{variable} = tk.Checkbutton({parent_name}, text={item['text']!r}, variable=self.{variable}_value, {options}, selectcolor={item['bg']!r})")
        elif item["type"] == "text":
            lines.append(f"{pad}{variable} = tk.Text({parent_name}, {options}, relief='solid', bd=1, wrap='word')")
            if item["text"]:
                lines.append(f"{pad}{variable}.insert('1.0', {item['text']!r})")
        lines.append(f"{pad}{variable}.place(x={item['x']}, y={item['y']}, width={item['w']}, height={item['h']})")

    for component in roots:
        emit(component, "parent", 8)
    for item in components:
        if item["type"] != "video":
            continue
        variable = "widget_" + re.sub(r"\W", "_", item["id"])
        lines.extend([
            "", f"    def _play_{variable}(self):",
            f"        capture = self.{variable}_capture",
            "        success, frame = capture.read()",
            "        if not success:",
            "            capture.set(cv2.CAP_PROP_POS_FRAMES, 0)",
            "            self.after(10, lambda: self._play_" + variable + "())",
            "            return",
            "        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)",
            "        image = Image.fromarray(frame)",
            f"        image.thumbnail(({item['w']}, {item['h']}), Image.Resampling.LANCZOS)",
            "        photo = ImageTk.PhotoImage(image)",
            f"        self.{variable}.configure(image=photo, text='')",
            f"        self.{variable}.image = photo",
            "        self.after(33, lambda: self._play_" + variable + "())",
        ])
    lines.extend(["", "", 'if __name__ == "__main__":', "    app = GeneratedUI()", "    app.mainloop()", ""])
    return "\n".join(lines)


class UIBuilder(tk.Tk):
    def __init__(self):
        super().__init__()
        self.config_path = os.path.join(os.path.expanduser("~"), ".ezuimaker.json")
        self.language = self._load_language()
        self.project_name = self.tr("project")
        self.project_name_default = True
        self.width = 900
        self.height = 560
        self.components = []
        self.selected_id = None
        self.next_id = 1
        self.drag_state = None
        self.zoom = 1.0
        self.snap_enabled = True
        self.media_cache = {}
        self.media_refs = {}
        self.active_video = None

        self.configure(bg="#f3f4ef")
        self.geometry("1440x900")
        self.minsize(1050, 680)
        self._setup_style()
        self._build_shell()
        self.refresh_language()

    def tr(self, key, **values):
        return TEXT[self.language][key].format(**values)

    def _load_language(self):
        try:
            with open(self.config_path, encoding="utf-8") as config_file:
                return "fr" if json.load(config_file).get("language") == "fr" else "en"
        except (OSError, ValueError, TypeError):
            return "en"

    def _save_language(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as config_file:
                json.dump({"language": self.language}, config_file)
        except OSError:
            pass

    def _setup_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background="#ffffff")
        style.configure("TLabel", background="#ffffff", foreground="#20231f", font=("Segoe UI", 9))
        style.configure("Panel.TLabel", background="#ffffff", foreground="#777c73", font=("Segoe UI", 9, "bold"))
        style.configure("TButton", padding=(9, 6), font=("Segoe UI", 9))
        style.configure("Primary.TButton", padding=(10, 7), background="#b8f36b", foreground="#20231f", font=("Segoe UI", 9, "bold"))
        style.map("Primary.TButton", background=[("active", "#a9e65c")])
        style.configure("TEntry", padding=5)
        style.configure("TCombobox", padding=4)
        style.configure("Treeview", background="#fafbf8", fieldbackground="#fafbf8", foreground="#20231f", rowheight=27, font=("Segoe UI", 9), borderwidth=0, relief="flat")
        style.map("Treeview", background=[("selected", "#e4f1d7")], foreground=[("selected", "#263a16")])

    def _build_shell(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.topbar = ttk.Frame(self, padding=(14, 10))
        self.topbar.grid(row=0, column=0, sticky="ew")
        self.topbar.columnconfigure(1, weight=1)
        self.brand = ttk.Label(self.topbar, text="ezUIMaker", font=("Segoe UI", 14, "bold"))
        self.brand.grid(row=0, column=0, padx=(0, 18))
        self.project_var = tk.StringVar(value=self.project_name)
        self.project_entry = ttk.Entry(self.topbar, textvariable=self.project_var, width=28)
        self.project_entry.grid(row=0, column=1, sticky="w")
        self.project_var.trace_add("write", self._project_changed)
        self.language_var = tk.StringVar(value="EN" if self.language == "en" else "FR")
        self.language_box = ttk.Combobox(self.topbar, textvariable=self.language_var, values=("EN", "FR"), state="readonly", width=5)
        self.language_box.grid(row=0, column=2, padx=(12, 8))
        self.language_box.bind("<<ComboboxSelected>>", self._language_changed)
        self.python_button = ttk.Button(self.topbar, command=self.export_python)
        self.python_button.grid(row=0, column=3, padx=4)
        self.exe_button = ttk.Button(self.topbar, style="Primary.TButton", command=self.build_exe)
        self.exe_button.grid(row=0, column=4, padx=(4, 0))

        self.panes = ttk.Panedwindow(self, orient="horizontal")
        self.panes.grid(row=1, column=0, sticky="nsew")
        self.left_panel = ttk.Frame(self.panes, padding=12, width=205)
        self.center_panel = ttk.Frame(self.panes, padding=10)
        self.right_panel = ttk.Frame(self.panes, padding=12, width=270)
        self.panes.add(self.left_panel, weight=0)
        self.panes.add(self.center_panel, weight=1)
        self.panes.add(self.right_panel, weight=0)
        self.left_panel.pack_propagate(False)
        self.right_panel.pack_propagate(False)
        self._build_left_panel()
        self._build_center_panel()
        self._build_right_panel()

        self.status_var = tk.StringVar()
        self.status = ttk.Label(self, textvariable=self.status_var, anchor="w", padding=(14, 5))
        self.status.grid(row=2, column=0, sticky="ew")

    def _build_left_panel(self):
        self.palette_heading = ttk.Label(self.left_panel, style="Panel.TLabel")
        self.palette_heading.pack(anchor="w", pady=(2, 10))
        self.palette = ttk.Frame(self.left_panel)
        self.palette.pack(fill="x")
        self.palette_buttons = {}
        for index, kind in enumerate(COMPONENTS):
            button = ttk.Button(self.palette, command=lambda component_type=kind: self.add_component(component_type))
            button.grid(row=index // 2, column=index % 2, sticky="ew", padx=2, pady=3)
            self.palette_buttons[kind] = button
        self.palette.columnconfigure(0, weight=1)
        self.palette.columnconfigure(1, weight=1)
        self.hint = ttk.Label(self.left_panel, wraplength=175, foreground="#777c73")
        self.hint.pack(anchor="w", pady=(8, 18))
        self.layers_heading = ttk.Label(self.left_panel, style="Panel.TLabel")
        self.layers_heading.pack(anchor="w", pady=(0, 7))
        self.layer_tree = ttk.Treeview(self.left_panel, show="tree", selectmode="browse", height=12)
        self.layer_tree.pack(fill="both", expand=True)
        self.layer_tree.bind("<<TreeviewSelect>>", self._layer_selected)

    def _build_center_panel(self):
        self.center_panel.columnconfigure(0, weight=1)
        self.center_panel.rowconfigure(1, weight=1)
        self.canvas_bar = ttk.Frame(self.center_panel)
        self.canvas_bar.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.canvas_heading = ttk.Label(self.canvas_bar, style="Panel.TLabel")
        self.canvas_heading.pack(side="left")
        controls = ttk.Frame(self.canvas_bar)
        controls.pack(side="right")
        self.size_label = ttk.Label(controls)
        self.size_label.pack(side="left", padx=(0, 6))
        self.width_var = tk.StringVar(value=str(self.width))
        self.width_box = ttk.Spinbox(controls, from_=240, to=1920, increment=10, width=6, textvariable=self.width_var, command=self._canvas_size_changed)
        self.width_box.pack(side="left")
        ttk.Label(controls, text="×").pack(side="left", padx=4)
        self.height_var = tk.StringVar(value=str(self.height))
        self.height_box = ttk.Spinbox(controls, from_=180, to=1200, increment=10, width=6, textvariable=self.height_var, command=self._canvas_size_changed)
        self.height_box.pack(side="left")
        self.width_box.bind("<FocusOut>", self._canvas_size_changed)
        self.height_box.bind("<FocusOut>", self._canvas_size_changed)
        self.clear_button = ttk.Button(controls, command=self.clear_canvas)
        self.clear_button.pack(side="left", padx=(8, 0))
        self.snap_var = tk.BooleanVar(value=True)
        self.snap_toggle = ttk.Checkbutton(controls, variable=self.snap_var, text="Snap", command=self._snap_changed)
        self.snap_toggle.pack(side="left", padx=(10, 3))
        self.zoom_out = ttk.Button(controls, text="−", width=3, command=lambda: self._set_zoom(self.zoom - 0.1))
        self.zoom_out.pack(side="left", padx=(6, 0))
        self.zoom_value = ttk.Label(controls, width=5, anchor="center")
        self.zoom_value.pack(side="left")
        self.zoom_in = ttk.Button(controls, text="+", width=3, command=lambda: self._set_zoom(self.zoom + 0.1))
        self.zoom_in.pack(side="left")

        canvas_wrap = ttk.Frame(self.center_panel)
        canvas_wrap.grid(row=1, column=0, sticky="nsew")
        canvas_wrap.rowconfigure(0, weight=1)
        canvas_wrap.columnconfigure(0, weight=1)
        self.canvas = tk.Canvas(canvas_wrap, width=900, height=500, bg="#e8ebe3", highlightthickness=0, takefocus=True, scrollregion=(0, 0, self.width, self.height))
        self.canvas.grid(row=0, column=0, sticky="nsew")
        xscroll = ttk.Scrollbar(canvas_wrap, orient="horizontal", command=self.canvas.xview)
        yscroll = ttk.Scrollbar(canvas_wrap, orient="vertical", command=self.canvas.yview)
        xscroll.grid(row=1, column=0, sticky="ew")
        yscroll.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(xscrollcommand=xscroll.set, yscrollcommand=yscroll.set)
        self.canvas.bind("<Button-1>", self._canvas_background_click)
        self.canvas.bind("<ButtonPress-2>", lambda event: self.canvas.scan_mark(event.x, event.y))
        self.canvas.bind("<B2-Motion>", lambda event: self.canvas.scan_dragto(event.x, event.y, gain=1))
        self.bind_all("<Delete>", self._delete_selected)
        self.bind_all("<Control-d>", self._duplicate_selected)
        self.bind_all("<Control-D>", self._duplicate_selected)
        for key in ("Left", "Right", "Up", "Down"):
            self.bind_all(f"<{key}>", self._nudge_selected)

        self.code_bar = ttk.Frame(self.center_panel)
        self.code_bar.grid(row=2, column=0, sticky="ew", pady=(10, 5))
        self.code_heading = ttk.Label(self.code_bar, style="Panel.TLabel")
        self.code_heading.pack(side="left")
        self.copy_button = ttk.Button(self.code_bar, command=self.copy_code)
        self.copy_button.pack(side="right")
        self.code_view = tk.Text(self.center_panel, height=10, bg="#20231f", fg="#d7e3ce", insertbackground="#b8f36b", relief="flat", padx=12, pady=9, font=("DejaVu Sans Mono", 9), wrap="none", state="disabled")
        self.code_view.tag_configure("keyword", foreground="#f2a980")
        self.code_view.tag_configure("string", foreground="#b8f36b")
        self.code_view.tag_configure("call", foreground="#8fc7f3")
        self.code_view.grid(row=3, column=0, sticky="ew")

    def _build_right_panel(self):
        self.inspector_heading = ttk.Label(self.right_panel, style="Panel.TLabel")
        self.inspector_heading.pack(anchor="w", pady=(2, 12))
        self.inspector = ttk.Frame(self.right_panel)
        self.inspector.pack(fill="both", expand=True)

    def refresh_language(self):
        self.title(self.tr("title"))
        self.language_var.set("EN" if self.language == "en" else "FR")
        if self.project_name_default:
            self.project_name = self.tr("project")
            self.project_var.set(self.project_name)
        self.palette_heading.configure(text=self.tr("components"))
        self.layers_heading.configure(text=self.tr("layers"))
        self.canvas_heading.configure(text=self.tr("canvas"))
        self.inspector_heading.configure(text=self.tr("inspector"))
        self.code_heading.configure(text=self.tr("code"))
        self.size_label.configure(text=self.tr("window_size"))
        self.clear_button.configure(text=self.tr("clear"))
        self.snap_toggle.configure(text=self.tr("snap"))
        self.zoom_value.configure(text=f"{round(self.zoom * 100)}%")
        self.copy_button.configure(text="Copy" if self.language == "en" else "Copier")
        self.python_button.configure(text=self.tr("python"))
        self.exe_button.configure(text=self.tr("exe"))
        self.hint.configure(text=self.tr("hint"))
        for kind, button in self.palette_buttons.items():
            button.configure(text=self.tr(kind))
        self._refresh_layers()
        self._refresh_inspector()
        self.redraw()
        self.update_code()

    def _language_changed(self, _event=None):
        self.language = "fr" if self.language_var.get() == "FR" else "en"
        self._save_language()
        self.refresh_language()

    def _project_changed(self, *_args):
        if not hasattr(self, "project_var"):
            return
        current = self.project_var.get()
        self.project_name = current
        self.project_name_default = current == TEXT[self.language]["project"]
        self.update_code()

    def _canvas_size_changed(self, _event=None):
        try:
            self.width = max(240, min(1920, int(self.width_var.get())))
            self.height = max(180, min(1200, int(self.height_var.get())))
        except ValueError:
            return
        self.width_var.set(str(self.width))
        self.height_var.set(str(self.height))
        self.canvas.configure(scrollregion=(0, 0, self.width * self.zoom, self.height * self.zoom))
        self.redraw()
        self.update_code()

    def add_component(self, kind):
        if kind in ("image", "video"):
            self.add_media(kind)
            return
        parent = self._find(self.selected_id)
        if not parent or parent["type"] != "frame":
            parent = None
        item = {
            "id": f"item-{self.next_id}", "type": kind, "parent": parent["id"] if parent else None,
            "children": [], "text": self.tr(f"default_{kind}"), "default_text": True, **DEFAULTS[kind],
        }
        self.next_id += 1
        if parent:
            item["x"] = 16
            item["y"] = 28 + len(parent["children"]) * 38
            parent["children"].append(item["id"])
        self.components.append(item)
        self.selected_id = item["id"]
        self._refresh_layers()
        self._refresh_inspector()
        self.redraw()
        self.update_code()

    def add_media(self, kind):
        image_types = (("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"), ("All files", "*.*"))
        video_types = (("Video files", "*.mp4 *.mov *.avi *.mkv *.webm"), ("All files", "*.*"))
        path = filedialog.askopenfilename(parent=self, title=self.tr(f"add_{kind}"), filetypes=image_types if kind == "image" else video_types)
        if not path:
            return
        parent = self._find(self.selected_id)
        if not parent or parent["type"] != "frame":
            parent = None
        item = {
            "id": f"item-{self.next_id}", "type": kind, "parent": parent["id"] if parent else None,
            "children": [], "text": os.path.basename(path), "path": os.path.abspath(path), "default_text": False,
            **DEFAULTS[kind],
        }
        self.next_id += 1
        if parent:
            item["x"] = 16
            item["y"] = 28 + len(parent["children"]) * 38
            parent["children"].append(item["id"])
        self.components.append(item)
        self.selected_id = item["id"]
        self._refresh_layers()
        self._refresh_inspector()
        self.redraw()
        self.update_code()

    def _find(self, component_id):
        return next((item for item in self.components if item["id"] == component_id), None)

    def _refresh_layers(self):
        if not hasattr(self, "layer_tree"):
            return
        self.layer_tree.delete(*self.layer_tree.get_children())

        def insert_children(parent_id="", parent_item=None):
            children = [item for item in self.components if item.get("parent") == parent_id]
            for item in children:
                tree_id = self.layer_tree.insert(parent_id, "end", iid=item["id"], text=f"{self.tr(item['type'])}  ·  {item['text']}", open=True)
                insert_children(tree_id, item)

        insert_children()
        if self.selected_id and self.layer_tree.exists(self.selected_id):
            self.layer_tree.selection_set(self.selected_id)

    def _layer_selected(self, _event=None):
        selection = self.layer_tree.selection()
        if selection:
            self.selected_id = selection[0]
            self._refresh_inspector()
            self.redraw()

    def _refresh_inspector(self):
        for child in self.inspector.winfo_children():
            child.destroy()
        item = self._find(self.selected_id)
        if not item:
            ttk.Label(self.inspector, text=self.tr("select_hint"), wraplength=225, foreground="#777c73").pack(anchor="w")
            return
        ttk.Label(self.inspector, text=f"{self.tr('element')} · {self.tr(item['type']).upper()}", style="Panel.TLabel").pack(anchor="w", pady=(0, 10))
        if item["type"] in ("image", "video"):
            self._add_media_field(item)
        else:
            self._add_text_field(item)
        self._add_section(self.tr("position"))
        self._add_number_row(item, "x", "x", 0, 1920)
        self._add_number_row(item, "y", "y", 0, 1200)
        self._add_section(self.tr("size"))
        self._add_number_row(item, "width", "w", 24, 1920)
        self._add_number_row(item, "height", "h", 20, 1200)
        self._add_section(self.tr("typography"))
        self._add_number_row(item, "font_size", "size", 8, 96)
        self._add_choice(item, "font", "font", ("Segoe UI", "Arial", "Helvetica", "Times New Roman", "Courier New"))
        self._add_choice(item, "weight", "bold", (self.tr("regular"), self.tr("bold")), boolean=True)
        self._add_section(self.tr("colors"))
        self._add_color(item, "text_color", "fg")
        self._add_color(item, "background", "bg")
        actions = ttk.Frame(self.inspector)
        actions.pack(fill="x", pady=(14, 0))
        ttk.Button(actions, text=self.tr("duplicate"), command=lambda: self.duplicate_component(item["id"])).pack(side="left", expand=True, fill="x", padx=(0, 4))
        ttk.Button(actions, text=self.tr("delete"), command=lambda: self.delete_component(item["id"])).pack(side="left", expand=True, fill="x", padx=(4, 0))

    def _add_media_field(self, item):
        ttk.Label(self.inspector, text=self.tr("media_source")).pack(anchor="w", pady=(0, 4))
        ttk.Label(self.inspector, text=item["path"], wraplength=225, foreground="#777c73").pack(anchor="w")
        ttk.Button(self.inspector, text=self.tr("replace_media"), command=lambda: self._replace_media(item)).pack(anchor="w", pady=(6, 0))
        if item["type"] == "video":
            ttk.Button(self.inspector, text=self.tr("play_preview"), command=lambda: self._toggle_video(item["id"])).pack(anchor="w", pady=(6, 0))

    def _replace_media(self, item):
        kind = item["type"]
        filetypes = (("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"), ("All files", "*.*")) if kind == "image" else (("Video files", "*.mp4 *.mov *.avi *.mkv *.webm"), ("All files", "*.*"))
        path = filedialog.askopenfilename(parent=self, title=self.tr(f"add_{kind}"), filetypes=filetypes)
        if path:
            item["path"] = os.path.abspath(path)
            item["text"] = os.path.basename(path)
            self.media_cache.clear()
            self._refresh_layers()
            self._refresh_inspector()
            self.redraw()
            self.update_code()

    def _add_section(self, title):
        ttk.Label(self.inspector, text=title.upper(), style="Panel.TLabel").pack(anchor="w", pady=(12, 5))

    def _add_text_field(self, item):
        ttk.Label(self.inspector, text=self.tr("content")).pack(anchor="w", pady=(0, 4))
        text_box = tk.Text(self.inspector, height=3, wrap="word", font=("Segoe UI", 9), relief="solid", bd=1, padx=5, pady=4)
        text_box.pack(fill="x")
        text_box.insert("1.0", item["text"])
        text_box.edit_modified(False)

        def changed(_event=None):
            if text_box.edit_modified():
                item["text"] = text_box.get("1.0", "end-1c")
                item["default_text"] = False
                text_box.edit_modified(False)
                self._refresh_layers()
                self.redraw()
                self.update_code()

        text_box.bind("<<Modified>>", changed)

    def _add_number_row(self, item, label_key, key, minimum, maximum):
        row = ttk.Frame(self.inspector)
        row.pack(fill="x", pady=2)
        ttk.Label(row, text=self.tr(label_key)).pack(side="left")
        value = tk.StringVar(value=str(item[key]))
        spin = ttk.Spinbox(row, from_=minimum, to=maximum, textvariable=value, width=8)
        spin.pack(side="right")

        def changed(*_args):
            try:
                item[key] = max(minimum, min(maximum, int(value.get())))
            except ValueError:
                return
            self.redraw()
            self.update_code()

        value.trace_add("write", changed)

    def _add_choice(self, item, label_key, key, options, boolean=False):
        row = ttk.Frame(self.inspector)
        row.pack(fill="x", pady=2)
        ttk.Label(row, text=self.tr(label_key)).pack(side="left")
        if boolean:
            value = tk.StringVar(value=self.tr("bold" if item[key] else "regular"))
            choices = options
        else:
            value = tk.StringVar(value=item[key])
            choices = options
        box = ttk.Combobox(row, textvariable=value, values=choices, state="readonly", width=17)
        box.pack(side="right")

        def changed(_event=None):
            item[key] = value.get() == self.tr("bold") if boolean else value.get()
            self.redraw()
            self.update_code()

        box.bind("<<ComboboxSelected>>", changed)

    def _add_color(self, item, label_key, key):
        row = ttk.Frame(self.inspector)
        row.pack(fill="x", pady=3)
        ttk.Label(row, text=self.tr(label_key)).pack(side="left")
        swatch = tk.Button(row, bg=item[key], width=7, relief="flat", command=lambda: self._choose_color(item, key, swatch))
        swatch.pack(side="right")

    def _choose_color(self, item, key, swatch):
        chosen = colorchooser.askcolor(color=item[key], parent=self)
        if chosen and chosen[1]:
            item[key] = chosen[1]
            swatch.configure(bg=item[key])
            self.redraw()
            self.update_code()

    def _component_bounds(self, item):
        x, y = item["x"], item["y"]
        parent = self._find(item.get("parent"))
        while parent:
            x += parent["x"]
            y += parent["y"]
            parent = self._find(parent.get("parent"))
        return x, y

    def _media_preview(self, item, width, height):
        path = item.get("path", "")
        cache_key = (item["type"], path, width, height)
        if cache_key in self.media_cache:
            return self.media_cache[cache_key]
        if item["type"] == "image":
            try:
                if Image and ImageTk:
                    with Image.open(path) as source:
                        preview = source.copy()
                    preview.thumbnail((max(width - 4, 1), max(height - 4, 1)), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(preview)
                else:
                    photo = tk.PhotoImage(file=path)
                    scale = max(1, (photo.width() + width - 1) // max(width, 1), (photo.height() + height - 1) // max(height, 1))
                    if scale > 1:
                        photo = photo.subsample(scale, scale)
            except (OSError, tk.TclError, ValueError):
                return None
        else:
            if not cv2 or not Image or not ImageTk:
                return None
            capture = cv2.VideoCapture(path)
            success, frame = capture.read()
            capture.release()
            if not success:
                return None
            preview = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            preview.thumbnail((max(width - 4, 1), max(height - 4, 1)), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(preview)
        self.media_cache[cache_key] = photo
        return photo

    def _toggle_video(self, component_id):
        if self.active_video and self.active_video["id"] == component_id:
            self._stop_video()
            self.redraw()
            return
        if not cv2 or not Image or not ImageTk:
            messagebox.showinfo("ezUIMaker", self.tr("video_missing"), parent=self)
            return
        item = self._find(component_id)
        if not item:
            return
        self._stop_video()
        capture = cv2.VideoCapture(item["path"])
        if not capture.isOpened():
            capture.release()
            messagebox.showerror("ezUIMaker", self.tr("file_missing"), parent=self)
            return
        self.active_video = {"id": component_id, "capture": capture, "after": None, "photo": None}
        self._play_video_frame()

    def _play_video_frame(self):
        active = self.active_video
        if not active:
            return
        item = self._find(active["id"])
        canvas_items = self.canvas.find_withtag(f"media:{active['id']}")
        if not item or not canvas_items:
            self._stop_video()
            return
        success, frame = active["capture"].read()
        if not success:
            active["capture"].set(cv2.CAP_PROP_POS_FRAMES, 0)
            active["after"] = self.after(10, self._play_video_frame)
            return
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        preview = Image.fromarray(frame)
        x, y = self._component_bounds(item)
        preview.thumbnail((max(round(item["w"] * self.zoom) - 4, 1), max(round(item["h"] * self.zoom) - 4, 1)), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(preview)
        active["photo"] = photo
        self.canvas.itemconfigure(canvas_items[0], image=photo)
        fps = active["capture"].get(cv2.CAP_PROP_FPS) or 30
        active["after"] = self.after(max(1, round(1000 / fps)), self._play_video_frame)

    def _stop_video(self):
        if not self.active_video:
            return
        if self.active_video["after"]:
            self.after_cancel(self.active_video["after"])
        self.active_video["capture"].release()
        self.active_video = None

    def _set_zoom(self, zoom):
        self.zoom = max(0.5, min(1.5, round(zoom, 1)))
        self.zoom_value.configure(text=f"{round(self.zoom * 100)}%")
        self.redraw()

    def _snap_changed(self):
        self.snap_enabled = bool(self.snap_var.get())

    def _delete_selected(self, event):
        if self.selected_id and not isinstance(event.widget, (tk.Text, tk.Entry, ttk.Entry, ttk.Spinbox, ttk.Combobox)):
            self.delete_component(self.selected_id)

    def _duplicate_selected(self, _event):
        if isinstance(self.focus_get(), (tk.Text, tk.Entry, ttk.Entry, ttk.Spinbox, ttk.Combobox)):
            return
        if self.selected_id:
            self.duplicate_component(self.selected_id)
            return "break"

    def _nudge_selected(self, event):
        if not self.selected_id or event.widget is not self.canvas:
            return
        item = self._find(self.selected_id)
        if not item:
            return
        step = 10 if event.state & 0x0001 else 1
        item["x"] = max(0, item["x"] + (step if event.keysym == "Right" else -step if event.keysym == "Left" else 0))
        item["y"] = max(0, item["y"] + (step if event.keysym == "Down" else -step if event.keysym == "Up" else 0))
        self._refresh_inspector()
        self.redraw()
        self.update_code()
        return "break"

    def redraw(self):
        if not hasattr(self, "canvas"):
            return
        self._stop_video()
        self.canvas.delete("all")
        self.media_refs.clear()
        self.canvas.configure(scrollregion=(0, 0, self.width * self.zoom, self.height * self.zoom))
        stage_width, stage_height = self.width * self.zoom, self.height * self.zoom
        self.canvas.create_rectangle(0, 0, stage_width, stage_height, fill="#ffffff", outline="#cbd0c5", width=1, tags=("stage",))
        grid_step = max(4, round(20 * self.zoom))
        for grid_x in range(grid_step, int(stage_width), grid_step):
            self.canvas.create_line(grid_x, 0, grid_x, stage_height, fill="#f0f2ed", tags=("stage",))
        for grid_y in range(grid_step, int(stage_height), grid_step):
            self.canvas.create_line(0, grid_y, stage_width, grid_y, fill="#f0f2ed", tags=("stage",))
        roots = [item for item in self.components if not item.get("parent")]
        if not roots:
            self.canvas.create_text(stage_width / 2, stage_height / 2, text=self.tr("empty"), fill="#9b9f96", font=("Courier", 11), tags=("stage",))
        for item in roots:
            self._draw_component(item)

    def _draw_component(self, item):
        x, y = self._component_bounds(item)
        x, y = round(x * self.zoom), round(y * self.zoom)
        width, height = max(1, round(item["w"] * self.zoom)), max(1, round(item["h"] * self.zoom))
        x2, y2 = x + width, y + height
        tag = f"component:{item['id']}"
        selected = item["id"] == self.selected_id
        outline = "#5d8b37" if selected else (item["fg"] if item["type"] == "frame" else "#c7cbc2")
        fill = item["bg"]
        if item["type"] == "frame":
            self.canvas.create_rectangle(x, y, x2, y2, fill=fill, outline=outline, width=2 if selected else 1, tags=(tag,))
            self.canvas.create_text(x + round(9 * self.zoom), y + round(8 * self.zoom), text=item["text"], anchor="nw", fill=item["fg"], font=(item["font"], max(7, round(item["size"] * self.zoom)), "bold" if item["bold"] else "normal"), tags=(tag,))
            for child_id in item["children"]:
                child = self._find(child_id)
                if child:
                    self._draw_component(child)
        elif item["type"] in ("image", "video"):
            self.canvas.create_rectangle(x, y, x2, y2, fill=fill, outline=outline, width=2 if selected else 1, tags=(tag,))
            photo = self._media_preview(item, width, height)
            if photo:
                self.media_refs[item["id"]] = photo
                self.canvas.create_image(x + width // 2, y + height // 2, image=photo, tags=(tag, f"media:{item['id']}"))
            else:
                label = self.tr("media_missing") if item["type"] == "image" else self.tr("video_missing")
                self.canvas.create_text(x + width / 2, y + height / 2, text=f"{item['text']}\n\n{label}", width=max(width - 18, 40), fill="#778071", font=("Segoe UI", 9), tags=(tag,))
            if item["type"] == "video":
                self.canvas.create_text(x + width / 2, y + height / 2, text="▶", fill="#b8f36b", font=("Segoe UI", 28, "bold"), tags=(tag,))
                self.canvas.tag_bind(tag, "<Double-Button-1>", lambda event, component_id=item["id"]: self._toggle_video(component_id))
        elif item["type"] in ("button", "entry", "text"):
            self.canvas.create_rectangle(x, y, x2, y2, fill=fill if item["type"] == "button" else "#ffffff", outline=outline, width=2 if selected else 1, tags=(tag,))
            label = item["text"]
            anchor = "center" if item["type"] == "button" else "nw"
            tx, ty = ((x + width / 2, y + height / 2) if item["type"] == "button" else (x + 8, y + 7))
            if item["type"] == "text":
                label = label[:160]
            self.canvas.create_text(tx, ty, text=label, width=max(width - 16, 12), anchor=anchor, fill=item["fg"] if item["type"] != "button" else "#ffffff", font=(item["font"], max(7, round(item["size"] * self.zoom)), "bold" if item["bold"] else "normal"), tags=(tag,))
        elif item["type"] == "checkbox":
            self.canvas.create_rectangle(x, y + 5, x + 18, y + 23, fill="#ffffff", outline=outline, tags=(tag,))
            self.canvas.create_text(x + 27, y + item["h"] / 2, text=item["text"], anchor="w", fill=item["fg"], font=(item["font"], item["size"], "bold" if item["bold"] else "normal"), tags=(tag,))
        else:
            self.canvas.create_text(x, y, text=item["text"], anchor="nw", fill=item["fg"], font=(item["font"], item["size"], "bold" if item["bold"] else "normal"), tags=(tag,))
        self.canvas.tag_bind(tag, "<ButtonPress-1>", lambda event, component_id=item["id"]: self._start_drag(event, component_id))
        self.canvas.tag_bind(tag, "<B1-Motion>", self._drag)
        self.canvas.tag_bind(tag, "<ButtonRelease-1>", self._end_drag)
        if selected:
            handle = f"resize:{item['id']}"
            self.canvas.create_rectangle(x2 - 5, y2 - 5, x2 + 5, y2 + 5, fill="#5d8b37", outline="#ffffff", tags=(handle,))
            self.canvas.tag_bind(handle, "<ButtonPress-1>", lambda event, component_id=item["id"]: self._start_resize(event, component_id))
            self.canvas.tag_bind(handle, "<B1-Motion>", self._drag)
            self.canvas.tag_bind(handle, "<ButtonRelease-1>", self._end_drag)

    def _start_drag(self, event, component_id):
        self.canvas.focus_set()
        self.selected_id = component_id
        item = self._find(component_id)
        self.drag_state = {
            "id": component_id, "x": self.canvas.canvasx(event.x) / self.zoom, "y": self.canvas.canvasy(event.y) / self.zoom,
            "origin_x": item["x"], "origin_y": item["y"], "origin_w": item["w"], "origin_h": item["h"], "mode": "move",
        }
        self._refresh_layers()
        self._refresh_inspector()
        self.redraw()
        return "break"

    def _start_resize(self, event, component_id):
        self.selected_id = component_id
        item = self._find(component_id)
        self.drag_state = {
            "id": component_id, "x": self.canvas.canvasx(event.x) / self.zoom, "y": self.canvas.canvasy(event.y) / self.zoom,
            "origin_x": item["x"], "origin_y": item["y"], "origin_w": item["w"], "origin_h": item["h"], "mode": "resize",
        }
        return "break"

    def _drag(self, event):
        if not self.drag_state:
            return
        item = self._find(self.drag_state["id"])
        if not item:
            return
        x = self.canvas.canvasx(event.x) / self.zoom
        y = self.canvas.canvasy(event.y) / self.zoom
        dx = round(x - self.drag_state["x"])
        dy = round(y - self.drag_state["y"])
        if self.drag_state["mode"] == "resize":
            item["w"] = max(24, self.drag_state["origin_w"] + dx)
            item["h"] = max(20, self.drag_state["origin_h"] + dy)
        else:
            item["x"] = max(0, self.drag_state["origin_x"] + dx)
            item["y"] = max(0, self.drag_state["origin_y"] + dy)
            if self.snap_enabled:
                item["x"] = max(0, round(item["x"] / 10) * 10)
                item["y"] = max(0, round(item["y"] / 10) * 10)
        self.redraw()
        self.update_code()

    def _end_drag(self, _event=None):
        if self.drag_state:
            self.drag_state = None
            self._refresh_inspector()
            self._refresh_layers()

    def _canvas_background_click(self, event):
        current = self.canvas.find_withtag("current")
        if current and any(tag.startswith(("component:", "resize:")) for tag in self.canvas.gettags(current[0])):
            return
        self.selected_id = None
        self._refresh_inspector()
        self._refresh_layers()
        self.redraw()

    def duplicate_component(self, component_id):
        source = self._find(component_id)
        if not source:
            return

        def clone_tree(original, parent_id):
            clone = {**original, "id": f"item-{self.next_id}", "parent": parent_id, "children": [], "x": original["x"] + 18, "y": original["y"] + 18}
            self.next_id += 1
            self.components.append(clone)
            if parent_id:
                self._find(parent_id)["children"].append(clone["id"])
            for child_id in original["children"]:
                child = self._find(child_id)
                if child:
                    clone_tree(child, clone["id"])
            return clone

        parent_id = source.get("parent")
        clone = clone_tree(source, parent_id)
        self.selected_id = clone["id"]
        self._refresh_layers()
        self._refresh_inspector()
        self.redraw()
        self.update_code()

    def delete_component(self, component_id):
        item = self._find(component_id)
        if not item:
            return
        removed = {component_id}
        changed = True
        while changed:
            changed = False
            for component in self.components:
                if component.get("parent") in removed and component["id"] not in removed:
                    removed.add(component["id"])
                    changed = True
        parent = self._find(item.get("parent"))
        if parent and component_id in parent["children"]:
            parent["children"].remove(component_id)
        self.components = [component for component in self.components if component["id"] not in removed]
        self.selected_id = None
        self._refresh_layers()
        self._refresh_inspector()
        self.redraw()
        self.update_code()

    def clear_canvas(self):
        self.components.clear()
        self.selected_id = None
        self._refresh_layers()
        self._refresh_inspector()
        self.redraw()
        self.update_code()

    def build_python(self):
        return generate_python(self.project_name or self.tr("project"), self.width, self.height, self.components)

    def update_code(self):
        if not hasattr(self, "code_view"):
            return
        code = self.build_python()
        self.code_view.configure(state="normal")
        self.code_view.delete("1.0", "end")
        self.code_view.insert("1.0", code)
        for match in re.finditer(r"\b(import|from|class|def|if|else|return|for|in|self|True|False|None)\b", code):
            self.code_view.tag_add("keyword", f"1.0+{match.start()}c", f"1.0+{match.end()}c")
        for match in re.finditer(r"(['\"])(?:\\.|(?!\1).)*?\1", code):
            self.code_view.tag_add("string", f"1.0+{match.start()}c", f"1.0+{match.end()}c")
        for match in re.finditer(r"\b(?:tk\.[A-Z]\w*|ImageTk\.PhotoImage|cv2\.VideoCapture)\b", code):
            self.code_view.tag_add("call", f"1.0+{match.start()}c", f"1.0+{match.end()}c")
        self.code_view.configure(state="disabled")
        self.status_var.set(self.tr("items", count=len(self.components)))

    def copy_code(self):
        try:
            self.clipboard_clear()
            self.clipboard_append(self.build_python())
            self.status_var.set(self.tr("copied"))
        except tk.TclError:
            messagebox.showerror("ezUIMaker", self.tr("clipboard_error"), parent=self)

    def export_python(self):
        if not self.components:
            messagebox.showinfo("ezUIMaker", self.tr("no_components"), parent=self)
            return
        path = filedialog.asksaveasfilename(parent=self, title=self.tr("save_python"), defaultextension=".py", initialfile=self._safe_project_name() + ".py", filetypes=((self.tr("python_files"), "*.py"),))
        if not path:
            return
        with open(path, "w", encoding="utf-8") as output:
            output.write(self.build_python())
        self.status_var.set(self.tr("saved"))

    def _safe_project_name(self):
        return re.sub(r"[^a-zA-Z0-9_-]+", "_", self.project_name.strip()).strip("_") or "my_interface"

    def build_exe(self):
        if not self.components:
            messagebox.showinfo("ezUIMaker", self.tr("no_components"), parent=self)
            return
        path = filedialog.asksaveasfilename(parent=self, title=self.tr("save_exe"), defaultextension=".py", initialfile=self._safe_project_name() + ".py", filetypes=((self.tr("python_files"), "*.py"),))
        if not path:
            return
        with open(path, "w", encoding="utf-8") as output:
            output.write(self.build_python())
        if sys.platform != "win32":
            batch_path = os.path.splitext(path)[0] + "_build_windows.bat"
            executable_name = os.path.splitext(os.path.basename(path))[0]
            packages = ["pyinstaller"]
            if any(item["type"] in ("image", "video") for item in self.components):
                packages.append("Pillow")
            if any(item["type"] == "video" for item in self.components):
                packages.append("opencv-python")
            with open(batch_path, "w", encoding="utf-8", newline="\r\n") as output:
                output.write("@echo off\npython -m pip install " + " ".join(packages) + "\nif errorlevel 1 (\n  pause\n  exit /b 1\n)\n")
                output.write(f'python -m PyInstaller --noconfirm --onefile --windowed --name "{executable_name}" "{os.path.basename(path)}"\npause\n')
            messagebox.showinfo("ezUIMaker", self.tr("exe_prepared"), parent=self)
            return
        try:
            import importlib.util
            modules = {"PyInstaller": "pyinstaller"}
            if any(item["type"] in ("image", "video") for item in self.components):
                modules["PIL"] = "Pillow"
            if any(item["type"] == "video" for item in self.components):
                modules["cv2"] = "opencv-python"
            missing = [package for module, package in modules.items() if not importlib.util.find_spec(module)]
            if missing:
                messagebox.showwarning("ezUIMaker", self.tr("dependencies_missing", packages=" ".join(missing)), parent=self)
                return
        except (ImportError, ValueError):
            messagebox.showwarning("ezUIMaker", self.tr("pyinstaller_missing"), parent=self)
            return
        output_dir = os.path.dirname(path) or os.getcwd()
        build_log = os.path.splitext(path)[0] + "_build.log"
        log_file = open(build_log, "w", encoding="utf-8")
        process = subprocess.Popen([sys.executable, "-m", "PyInstaller", "--noconfirm", "--onefile", "--windowed", "--name", os.path.splitext(os.path.basename(path))[0], path], cwd=output_dir, stdout=log_file, stderr=subprocess.STDOUT)
        self.status_var.set(self.tr("build_running"))

        def check_build():
            if process.poll() is None:
                self.after(400, check_build)
                return
            log_file.close()
            if process.returncode == 0:
                messagebox.showinfo("ezUIMaker", self.tr("build_success"), parent=self)
            else:
                messagebox.showerror("ezUIMaker", self.tr("build_failed"), parent=self)

        self.after(400, check_build)


if __name__ == "__main__":
    UIBuilder().mainloop()