import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gio
import subprocess
import os
import utils
import config
from i18n import _
import threading

class InstallerWindow(Gtk.Window):
    def __init__(self, on_complete_callback):
        super().__init__(title=_("app_title") + " - " + _("welcome"))
        self.set_default_size(500, 400)
        self.set_border_width(20)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.on_complete_callback = on_complete_callback
        
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(500)
        self.add(self.stack)

        self.create_welcome_page()
        self.create_os_check_page()
        self.create_deps_page()
        self.create_final_page()
        
        self.show_all()

    def create_welcome_page(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        
        icon = Gtk.Image.new_from_icon_name("system-run-symbolic", Gtk.IconSize.DIALOG)
        vbox.pack_start(icon, False, False, 10)
        
        label = Gtk.Label()
        label.set_markup(f"<span size='xx-large' weight='bold'>{_('welcome')}</span>")
        vbox.pack_start(label, False, False, 0)
        
        desc = Gtk.Label(label=_("welcome_desc"))
        desc.set_line_wrap(True)
        desc.set_justify(Gtk.Justification.CENTER)
        vbox.pack_start(desc, False, False, 0)
        
        compat = Gtk.Label()
        compat.set_markup(_("compat_systems"))
        vbox.pack_start(compat, False, False, 10)
        
        btn = Gtk.Button(label=_("lets_start"))
        btn.get_style_context().add_class("suggested-action")
        btn.connect("clicked", lambda w: self.stack.set_visible_child_name("os_check"))
        vbox.pack_end(btn, False, False, 0)
        
        self.stack.add_named(vbox, "welcome")

    def create_os_check_page(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        
        self.os_label = Gtk.Label(label=_("os_check"))
        vbox.pack_start(self.os_label, True, True, 0)
        
        self.os_spinner = Gtk.Spinner()
        vbox.pack_start(self.os_spinner, False, False, 0)
        self.os_spinner.start()
        
        self.stack.add_named(vbox, "os_check")
        self.stack.connect("notify::visible-child-name", self.on_os_page_visible)

    # ... (skipping some internal logic which stays same)

    def on_os_page_visible(self, stack, param):
        if stack.get_visible_child_name() == "os_check":
            GLib.timeout_add_seconds(1, self.perform_os_check)

    def perform_os_check(self):
        if utils.is_linux_mint():
            self.os_label.set_markup(f"<span color='#2ecc71' weight='bold'>{_('mint_ready')}</span>")
            self.os_spinner.stop()
            GLib.timeout_add_seconds(1, lambda: self.stack.set_visible_child_name("deps"))
        else:
            self.os_label.set_markup(f"<span color='#e74c3c'>{_('os_warn')}</span>")
            self.os_spinner.stop()
            btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            btn_yes = Gtk.Button(label=_("continue"))
            btn_yes.connect("clicked", lambda w: self.stack.set_visible_child_name("deps"))
            btn_no = Gtk.Button(label=_("cancel"))
            btn_no.connect("clicked", lambda w: self.destroy())
            btn_box.pack_start(btn_yes, True, True, 0)
            btn_box.pack_start(btn_no, True, True, 0)
            self.stack.get_child_by_name("os_check").pack_end(btn_box, False, False, 0)
            self.show_all()
        return False

    def create_deps_page(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.deps_label = Gtk.Label()
        self.deps_label.set_markup(f"<span weight='bold'>{_('configuring')}</span>")
        vbox.pack_start(self.deps_label, False, False, 5)
        
        self.deps_list = Gtk.ListBox()
        self.deps_list.set_selection_mode(Gtk.SelectionMode.NONE)
        vbox.pack_start(self.deps_list, True, True, 0)
        
        self.btn_install = Gtk.Button(label=_("start_config"))
        self.btn_install.get_style_context().add_class("suggested-action")
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
            "gir1.2-keybinder-3.0": _("shortcut_mgr"),
            "gir1.2-xapp-1.0": _("tray_support")
        }
        
        for name, status in deps.items():
            row = Gtk.ListBoxRow()
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            row.add(hbox)
            label = Gtk.Label(label=friendly_names.get(name, name), xalign=0)
            hbox.pack_start(label, True, True, 10)
            icon_name = "emblem-ok-symbolic" if status else "emblem-important-symbolic"
            icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.MENU)
            hbox.pack_end(icon, False, False, 10)
            self.deps_list.add(row)
            
        # Add permissions check row
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
        script = f"""pkexec sh -c "apt update && apt install -y brightnessctl python3-pynput gir1.2-keybinder-3.0 gir1.2-xapp-1.0 && {os.path.abspath('setup_permissions.sh')}" """
        
        def run_thread():
            res = subprocess.run(script, shell=True)
            GLib.idle_add(self.on_install_done, res.returncode)
            
        threading.Thread(target=run_thread).start()

    def on_install_done(self, code):
        if code == 0:
            self.stack.set_visible_child_name("final")
        else:
            dialog = Gtk.MessageDialog(transient_for=self, flags=0, message_type=Gtk.MessageType.ERROR,
                                       buttons=Gtk.ButtonsType.OK, text=_("config_fail"))
            dialog.run()
            dialog.destroy()
            self.btn_install.set_sensitive(True)

    def create_final_page(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        
        icon = Gtk.Image.new_from_icon_name("emblem-success-symbolic", Gtk.IconSize.DIALOG)
        vbox.pack_start(icon, False, False, 10)
        
        label = Gtk.Label()
        label.set_markup(f"<span size='xx-large' weight='bold'>{_('all_ready')}</span>")
        vbox.pack_start(label, False, False, 0)
        
        desc = Gtk.Label(label=_("final_desc"))
        desc.set_line_wrap(True)
        desc.set_justify(Gtk.Justification.CENTER)
        vbox.pack_start(desc, False, False, 0)
        
        btn = Gtk.Button(label=_("launch_app"))
        btn.get_style_context().add_class("suggested-action")
        btn.connect("clicked", self.on_finish)
        vbox.pack_end(btn, False, False, 0)
        
        self.stack.add_named(vbox, "final")

    def on_finish(self, btn):
        settings = config.load_settings()
        settings["is_installed"] = True
        config.save_settings(settings)
        
        # Try to find the binary first (if installed via deb)
        if os.path.exists("/usr/bin/kbdbacklight"):
            subprocess.Popen(["kbdbacklight"])
        else:
            # Fallback to local main.py
            subprocess.Popen(["python3", os.path.abspath("main.py")])
            
        self.destroy()
        Gtk.main_quit()

import threading
