import ctypes as ct
import os
import threading
from tkinter import *
from tkinter.ttk import Combobox, Progressbar

import tkinterdnd2
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.icons import Icon

from MangaUp import manga_up


def detect_dark_mode():
    try:
        import winreg
    except ImportError:
        return False
    registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
    reg_keypath = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize'
    try:
        reg_key = winreg.OpenKey(registry, reg_keypath)
    except FileNotFoundError:
        return False

    for i in range(1024):
        try:
            value_name, value, _ = winreg.EnumValue(reg_key, i)
            if value_name == 'AppsUseLightTheme':
                return value == 0
        except OSError:
            break
    return False


def dark_title_bar(window, use_dark_mode=False):
    """
    MORE INFO:
    https://learn.microsoft.com/en-us/windows/win32/api/dwmapi/ne-dwmapi-dwmwindowattribute
    """
    window.update()
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    set_window_attribute = ct.windll.dwmapi.DwmSetWindowAttribute
    get_parent = ct.windll.user32.GetParent
    hwnd = get_parent(window.winfo_id())
    rendering_policy = DWMWA_USE_IMMERSIVE_DARK_MODE
    value = 1 if use_dark_mode else 0  # 1 for dark mode, 0 for light mode
    value = ct.c_int(value)
    set_window_attribute(hwnd, rendering_policy, ct.byref(value), ct.sizeof(value))


dark_mode = detect_dark_mode()


def tk_window():
    theme_name = 'minty' if not dark_mode else 'darkly'
    _root = ttk.Window(themename=theme_name)

    tkinterdnd2.TkinterDnD._require(_root)
    _root.title('Manga2x GUI')
    _root.geometry('600x400')
    _root.resizable(False, False)
    icon_image = PhotoImage(data=Icon.info)

    dark_title_bar(_root,use_dark_mode=dark_mode)

    # Style
    style = ttk.Style()
    style.configure('TLabel', font=('Helvetica', 12))
    style.configure('TButton', font=('Helvetica', 11))
    style.configure('TCombobox', font=('Helvetica', 11))

    # Drag and drop label
    ttk.Label(_root, text='Drag and drop files below to add into queue.').pack(pady=10)

    # Method selector
    method_frame = ttk.Frame(_root)
    method_frame.pack(pady=5)
    ttk.Label(method_frame, text='Select method:').pack(side=LEFT, padx=10)
    method_var = StringVar(value='Moderate')
    method_combobox = Combobox(method_frame, textvariable=method_var, values=['Moderate', 'Sharp'],
                               font=('Helvetica', 11))
    method_combobox.pack(side=LEFT, padx=10)

    # Buttons
    button_frame = ttk.Frame(_root)
    button_frame.pack(pady=10)
    ttk.Button(button_frame, text='Clear Queue', bootstyle=(INFO, OUTLINE),
               command=lambda: on_clear_click(canvas)).pack(side=LEFT, padx=5)
    ttk.Button(button_frame, text='Start Queue',
               command=lambda: start_queue(canvas.filenames.values(), method_var.get(), _progress=_progress),
               bootstyle=SUCCESS).pack(side=LEFT, padx=5)

    _root.file_icon = PhotoImage(data=(
        'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAALtJREFUWEdjZBhgwDjA9jNgdYDrJOmE//8Z5oMc5+QmQrEbGRkYfjIw/G+v1LzUiG4YVge4TJT+D1NIDQeAzAI5olLzIseAOQBkcZXmRQwP0y0ERh0wGgKjITAaAqMhMBoCoyEwGgKjITAaAiSFgFaP2f9rP3Qp7g9gGFAzl7hWMUNL8v9mPSOGAEU7qjpCV1eXeAe0GLkx+MtqDZADWpPqGf4zNlDVdsb/iQzV8xYQ1TOiqsUEDBvw3jEALRZ5IUHwOukAAAAASUVORK5CYII='))
    # https://icon-sets.iconify.design/fluent-emoji-flat/
    _root.folder_icon = PhotoImage(data=(
        'R0lGODlhGAAYAKECAAAAAPD/gP///////yH+EUNyZWF0ZWQgd2l0aCBHSU1QA'
        'CH5BAEKAAIALAAAAAAYABgAAAJClI+pK+DvGINQKhCyztEavGmd5IQmYJXmhi7UC8frH'
        'EL0Hdj4rO/n41v1giIgkWU8cpLK4dFJhAalvpj1is16toICADs='))

    # Canvas for drag-and-drop
    main_frame = ttk.Frame(_root)
    main_frame.pack(fill=BOTH, expand=True)

    canvas = Canvas(main_frame, name='dnd_canvas', takefocus=True, width=580, height=200)
    canvas.pack(side=LEFT, fill=BOTH, expand=True)

    scrollbar = ttk.Scrollbar(main_frame, orient=VERTICAL, command=canvas.yview)
    # scrollbar.pack(side=RIGHT, fill=Y)
    scrollbar.pack_forget()
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.filenames = {}
    canvas.nextcoords = [50, 20]
    canvas.dragging = False

    def on_mousewheel(event):
        if event.delta > 0:
            canvas.yview_scroll(-1, "units")
        else:
            canvas.yview_scroll(1, "units")

    color_fill = 'white' if dark_mode else 'black'

    def add_file(filename):
        icon = _root.file_icon  # Use the icon stored in the root window
        if os.path.isdir(filename):
            icon = _root.folder_icon  # Use the icon stored in the root window
        id1 = canvas.create_image(canvas.nextcoords[0], canvas.nextcoords[1],
                                  image=icon, anchor='n', tags=('file',))
        id2 = canvas.create_text(canvas.nextcoords[0], canvas.nextcoords[1] + 30,
                                 text=os.path.basename(filename), anchor='n',
                                 justify='center', width=90, fill=color_fill)

        canvas.filenames[id1] = filename
        if canvas.nextcoords[0] > 450:
            canvas.nextcoords = [50, canvas.nextcoords[1] + 80]
        else:
            canvas.nextcoords = [canvas.nextcoords[0] + 100, canvas.nextcoords[1]]

        canvas.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        update_scrollbar()

    def update_scrollbar():
        bbox = canvas.bbox("all")
        if bbox is None:
            scrollbar.pack_forget()
        else:
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()
            if bbox[3] > canvas_height or bbox[2] > canvas_width:
                scrollbar.pack(side=RIGHT, fill=Y)
            else:
                scrollbar.pack_forget()

    def on_clear_click(_canvas):
        clear_queue(_canvas)
        update_scrollbar()

    def drop_enter(event):
        event.widget.focus_force()
        return event.action

    def drop_position(event):
        return event.action

    def drop_leave(event):
        return event.action

    def drop(event):
        if canvas.dragging:
            return tkinterdnd2.REFUSE_DROP
        if event.data:
            files = canvas.tk.splitlist(event.data)
            for f in files:
                add_file(f)
        return event.action

    def drag_init(event):
        data = ()
        sel = canvas.select_item()
        if sel:
            data = (canvas.filenames[sel],)
            canvas.dragging = True
            return (tkinterdnd2.ASK, tkinterdnd2.COPY), (tkinterdnd2.DND_FILES, tkinterdnd2.DND_TEXT), data
        else:
            return 'break'

    def drag_end(event):
        canvas.dragging = False

    canvas.drop_target_register(tkinterdnd2.DND_FILES)
    canvas.dnd_bind('<<DropEnter>>', drop_enter)
    canvas.dnd_bind('<<DropPosition>>', drop_position)
    canvas.dnd_bind('<<DropLeave>>', drop_leave)
    canvas.dnd_bind('<<Drop>>', drop)

    canvas.drag_source_register(1, tkinterdnd2.DND_FILES)
    canvas.dnd_bind('<<DragInitCmd>>', drag_init)
    canvas.dnd_bind('<<DragEndCmd>>', drag_end)

    canvas.bind("<MouseWheel>", on_mousewheel)

    # Progress bar
    _progress = Progressbar(_root, orient=HORIZONTAL, length=580, mode='determinate', bootstyle="success-striped")
    _progress.pack(pady=10)

    _root.protocol("WM_DELETE_WINDOW", lambda: os._exit(0))
    _root.wm_iconphoto(True, icon_image)

    return _root, _progress


def init_tk_window(_root):
    _root.mainloop()


def run_manga_up(epub_path, method):
    directory = os.path.dirname(epub_path)
    base_name = os.path.splitext(os.path.basename(epub_path))[0]

    output_epub_path = os.path.join(directory, f"{base_name}_{method}2x")
    manga_up(epub_path, output_epub_path + '.epub', _method=method)


def start_queue(file_list, method, _progress=None):
    print(method)
    total_files = len(file_list)
    if total_files != 0:
        _progress['value'] = 1
        _progress['maximum'] = total_files + 1

        def process_files():
            for idx, file in enumerate(file_list):
                run_manga_up(file, method)
                _progress['value'] = idx + 1
                root.update_idletasks()
            _progress['value'] = _progress['maximum']

        thread = threading.Thread(target=process_files)
        thread.start()


def clear_queue(canvas):
    canvas.delete('all')
    canvas.filenames = {}
    canvas.nextcoords = [50, 20]
    progress['value'] = 0
    progress['maximum'] = 0


if __name__ == "__main__":
    root, progress = tk_window()
    init_tk_window(root)
