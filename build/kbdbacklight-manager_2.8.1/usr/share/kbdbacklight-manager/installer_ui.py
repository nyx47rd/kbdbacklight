import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gio, Gdk
import subprocess
import os
import utils
import config
import i18n
from i18n import _
import threading

class InstallerWindow(Gtk.Window):
    def __init__(self, on_complete_callback):
        super().__init__(title=_("app_title"))
        self.set_default_size(600, 450)
        self.set_border_width(0) # Modern look, no border
        self.set_position(Gtk.WindowPosition.CENTER)
        self.on_complete_callback = on_complete_callback
        
        # Modern Styling
        screen = Gdk.Screen.get_default()
        provider = Gtk.CssProvider()
        style_data = b"""
        .title { font-size: 24px; font-weight: bold; color: #ffffff; }
        .subtitle { font-size: 14px; color: #aaaaaa; }
        .success { color: #2ecc71; font-weight: bold; }
        .warning { color: #f39c12; font-weight: bold; }
        .error { color: #e74c3c; font-weight: bold; }
        .lang-btn { padding: 10px 20px; font-size: 16px; margin: 5px; background: #444; color: white; border: 1px solid #555; }
        .card { background-color: #3d3d3d; padding: 20px; border-radius: 10px; color: #eee; }
        GtkWindow { background-color: #2d2d2d; color: #eeeeee; }
        GtkLabel { color: #eeeeee; }
        GtkButton { background-color: #444; color: white; border: 1px solid #555; }
        .suggested-action { background-color: #2ecc71; color: white; border-color: #27ae60; }
        .destructive-action { background-color: #e74c3c; color: white; border-color: #c0392b; }
        """
        provider.load_from_data(style_data)
        Gtk.StyleContext.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(400)
        self.add(self.stack)

        self.create_lang_page() # Step 1
        self.create_welcome_page() # Step 2
        self.create_os_check_page() # Step 3 (renamed logic to hw check)
        self.create_deps_page() # Step 4
        self.create_final_page() # Step 5
        
        self.show_all()

    def create_lang_page(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=30)
        vbox.set_valign(Gtk.Align.CENTER)
        vbox.set_halign(Gtk.Align.CENTER)
        
        lbl = Gtk.Label(label="Select Language / Dil Seçimi")
        lbl.get_style_context().add_class("title")
        vbox.pack_start(lbl, False, False, 0)
        
        hbox_btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        vbox.pack_start(hbox_btns, False, False, 0)
        
        btn_tr = Gtk.Button(label="🇹🇷 Türkçe")
        btn_tr.get_style_context().add_class("lang-btn")
        btn_tr.connect("clicked", self.on_lang_selected, "tr")
        
        btn_en = Gtk.Button(label="🇬🇧 English")
        btn_en.get_style_context().add_class("lang-btn")
        btn_en.connect("clicked", self.on_lang_selected, "en")
        
        hbox_btns.pack_start(btn_tr, True, True, 0)
        hbox_btns.pack_start(btn_en, True, True, 0)
        
        self.stack.add_named(vbox, "lang_select")

    def on_lang_selected(self, btn, lang_code):
        i18n.set_lang_override(lang_code)
        self.selected_lang = lang_code
        self.refresh_ui_text()
        self.stack.set_visible_child_name("welcome")

    def refresh_ui_text(self):
        # Refresh title
        self.set_title(_("app_title") + " - Installer")
        # Trigger rebuild of pages or update labels (simpler to rebuild next pages dynamically, but for now just update what we can or rely on just-in-time creation? 
        # Actually simplest is to rebuild the stack content except lang page.
        # But for reliability, let's just update the welcome page text specifically as it's next.
        # Ideally, we should construct pages AFTER lang selection. 
        # Refactoring approach: create_welcome_page etc will be called/refreshed here.
        
        # Remove old pages to be safe
        for child in self.stack.get_children():
            if self.stack.child_get_property(child, "name") != "lang_select":
                self.stack.remove(child)
        
        self.create_welcome_page()
        self.create_os_check_page()
        self.create_deps_page()
        self.create_final_page()
        self.stack.show_all()

    def create_welcome_page(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        vbox.set_border_width(40)
        
        icon = Gtk.Image.new_from_icon_name("system-run-symbolic", Gtk.IconSize.DIALOG)
        icon.set_pixel_size(64)
        vbox.pack_start(icon, False, False, 10)
        
        label = Gtk.Label(label=_("welcome"))
        label.get_style_context().add_class("title")
        vbox.pack_start(label, False, False, 0)
        
        desc = Gtk.Label(label=_("welcome_desc"))
        desc.set_line_wrap(True)
        desc.set_max_width_chars(50)
        desc.set_justify(Gtk.Justification.CENTER)
        vbox.pack_start(desc, False, False, 0)
        
        # Universal Support Badge
        univ_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        univ_box.get_style_context().add_class("card")
        univ_lbl = Gtk.Label(label="✨ Universal Support / Evrensel Destek")
        univ_lbl.get_style_context().add_class("success")
        univ_box.pack_start(univ_lbl, False, False, 0)
        
        compat_lbl = Gtk.Label(label="ASUS, MSI, HP, Dell...\n" + _("compat_systems"))
        compat_lbl.set_justify(Gtk.Justification.CENTER)
        univ_box.pack_start(compat_lbl, False, False, 0)
        vbox.pack_start(univ_box, False, False, 10)
        
        btn = Gtk.Button(label=_("lets_start"))
        btn.get_style_context().add_class("suggested-action")
        btn.set_size_request(-1, 50)
        btn.connect("clicked", lambda w: self.stack.set_visible_child_name("os_check"))
        vbox.pack_end(btn, False, False, 0)
        
        self.stack.add_named(vbox, "welcome")

    def create_os_check_page(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        vbox.set_valign(Gtk.Align.CENTER)
        
        self.os_label = Gtk.Label(label=_("os_check"))
        self.os_label.get_style_context().add_class("title")
        vbox.pack_start(self.os_label, True, True, 0)
        
        self.os_spinner = Gtk.Spinner()
        self.os_spinner.set_size_request(32, 32)
        vbox.pack_start(self.os_spinner, False, False, 0)
        self.os_spinner.start()
        
        self.stack.add_named(vbox, "os_check")
        self.stack.connect("notify::visible-child-name", self.on_os_page_visible)

    def on_os_page_visible(self, stack, param):
        if stack.get_visible_child_name() == "os_check":
            GLib.timeout_add(1500, self.perform_os_check) # Little delay for effect

    def perform_os_check(self):
        # We act generous now, it is universal
        self.os_label.set_markup(f"<span color='#2ecc71'>✔ Universal Mode Active!</span>")
        self.os_spinner.stop()
        GLib.timeout_add(800, lambda: self.stack.set_visible_child_name("deps"))
        return False

    def create_deps_page(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        vbox.set_border_width(30)
        
        self.deps_label = Gtk.Label()
        self.deps_label.set_markup(f"<span size='large' weight='bold'>{_('configuring')}</span>")
        vbox.pack_start(self.deps_label, False, False, 5)
        
        self.deps_list = Gtk.ListBox()
        self.deps_list.set_selection_mode(Gtk.SelectionMode.NONE)
        self.deps_list.get_style_context().add_class("card")
        vbox.pack_start(self.deps_list, True, True, 0)
        
        self.btn_install = Gtk.Button(label=_("start_config"))
        self.btn_install.get_style_context().add_class("suggested-action")
        self.btn_install.set_size_request(-1, 50)
        self.btn_install.connect("clicked", self.on_install_clicked)
        vbox.pack_end(self.btn_install, False, False, 0)
        
        self.stack.add_named(vbox, "deps")
        self.stack.connect("notify::visible-child-name", self.on_deps_page_visible)

    def on_deps_page_visible(self, stack, param):
        if stack.get_visible_child_name() == "deps":
            self.refresh_deps()

    def refresh_deps(self):
        for child in self.deps_list.get_children():
            self.deps_list.remove(child)
            
        deps = utils.get_installed_dependencies()
        all_pkgs_ok = all(deps.values())
        perms_ok = utils.check_permissions()
        
        friendly_names = {
            "brightnessctl": _("hardware_tool"),
            "python3-pynput": _("keyboard_driver"),
            "gir1.2-xapp-1.0": _("tray_support")
        }
        
        for name, status in deps.items():
            if name == "gir1.2-keybinder-3.0": continue # we removed shortcuts
            row = Gtk.ListBoxRow()
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            row.add(hbox)
            label = Gtk.Label(label=friendly_names.get(name, name), xalign=0)
            hbox.pack_start(label, True, True, 10)
            icon_name = "emblem-ok-symbolic" if status else "emblem-important-symbolic"
            icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.MENU)
            hbox.pack_end(icon, False, False, 10)
            self.deps_list.add(row)
            
        # Permissions
        row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        row.add(hbox)
        hbox.pack_start(Gtk.Label(label=_("permissions"), xalign=0), True, True, 10)
        icon_name = "emblem-ok-symbolic" if perms_ok else "emblem-important-symbolic"
        hbox.pack_end(Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.MENU), False, False, 10)
        self.deps_list.add(row)

        self.deps_list.show_all()
        
        if all_pkgs_ok and perms_ok:
            self.stack.set_visible_child_name("final")
        else:
            self.btn_install.set_label(_("auto_config"))

    def on_install_clicked(self, btn):
        btn.set_sensitive(False)
        # Note: Added -y to apt install to ensure non-interactive
        # We redirect stderr to stdout to capture everything
        script = f"""pkexec sh -c "apt update && apt install -y brightnessctl python3-pynput gir1.2-xapp-1.0 && {os.path.abspath('setup_permissions.sh')}" """
        
        def run_thread():
            # dim: capture_output=True requires python 3.7+
            try:
                res = subprocess.run(script, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                output = res.stdout
                code = res.returncode
            except Exception as e:
                code = 1
                output = str(e)
            
            GLib.idle_add(self.on_install_done, code, output)
            
        threading.Thread(target=run_thread).start()

    def on_install_done(self, code, output):
        if code == 0:
            # Save selected language to config before finishing
            if hasattr(self, 'selected_lang'):
                settings = config.load_settings()
                settings['language'] = self.selected_lang
                config.save_settings(settings)
            self.stack.set_visible_child_name("final")
        else:
            # Show error log
            dialog = Gtk.MessageDialog(transient_for=self, flags=0, message_type=Gtk.MessageType.ERROR,
                                       buttons=Gtk.ButtonsType.OK, text=_("config_fail"))
            
            # Create a scrolling area for the log
            # Standard MessageDialog doesn't support complex widgets easily in secondary area,
            # but we can format the secondary text or add a custom content area.
            
            # Truncate if too long (to avoid super huge dialog)
            if len(output) > 2000:
                output = output[-2000:] + "\n...(truncated)"
                
            scroll = Gtk.ScrolledWindow()
            scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            scroll.set_size_request(400, 200)
            
            tv = Gtk.TextView()
            tv.set_editable(False)
            tv.set_wrap_mode(Gtk.WrapMode.WORD)
            tv.get_buffer().set_text(output)
            scroll.add(tv)
            
            content_area = dialog.get_content_area()
            content_area.pack_start(scroll, True, True, 10)
            scroll.show_all()
            
            dialog.run()
            dialog.destroy()
            self.btn_install.set_sensitive(True)

    def create_final_page(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        vbox.set_valign(Gtk.Align.CENTER)
        
        icon = Gtk.Image.new_from_icon_name("emblem-success-symbolic", Gtk.IconSize.DIALOG)
        icon.set_pixel_size(96)
        vbox.pack_start(icon, False, False, 10)
        
        label = Gtk.Label()
        label.set_markup(f"<span size='xx-large' weight='bold' color='#2ecc71'>{_('all_ready')}</span>")
        vbox.pack_start(label, False, False, 0)
        
        desc = Gtk.Label(label=_("final_desc"))
        desc.set_justify(Gtk.Justification.CENTER)
        vbox.pack_start(desc, False, False, 0)
        
        btn = Gtk.Button(label=_("launch_app"))
        btn.get_style_context().add_class("suggested-action")
        btn.set_size_request(-1, 60)
        btn.connect("clicked", self.on_finish)
        vbox.pack_end(btn, False, False, 20)
        
        self.stack.add_named(vbox, "final")

    def on_finish(self, btn):
        settings = config.load_settings()
        settings["is_installed"] = True
        config.save_settings(settings)
        
        if os.path.exists("/usr/bin/kbdbacklight"):
            subprocess.Popen(["kbdbacklight"])
        else:
            subprocess.Popen(["python3", os.path.abspath("main.py")])
            
        self.destroy()
        Gtk.main_quit()
