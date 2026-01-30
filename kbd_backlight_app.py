#!/usr/bin/env python3
import os
import gi
import config
import utils
from backlight_mgr import BacklightManager
from i18n import _

gi.require_version('Gtk', '3.0')
try:
    gi.require_version('XApp', '1.0')
    from gi.repository import XApp
except ImportError:
    XApp = None

try:
    gi.require_version('Keybinder', '3.0')
    from gi.repository import Keybinder
except ImportError:
    Keybinder = None

from gi.repository import Gtk, GLib, Gio, Gdk

class KbdBacklightApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.github.kbdbacklight",
                         flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE)
        
        self.settings = config.load_settings()
        self.mgr = BacklightManager(self.settings, self.on_brightness_changed)
        
        self.window = None
        self.status_icon = None
        
        # Shortcuts feature removed in v2.7.0 for stability

    def do_command_line(self, command_line):
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--up", action="store_true")
        parser.add_argument("--down", action="store_true")
        parser.add_argument("--toggle", action="store_true")
        args = parser.parse_args(command_line.get_arguments()[1:])
        
        if args.up: self.mgr.activate_temp_light() if self.settings["temp_light_enabled"] else self.mgr.adjust_brightness(1)
        elif args.down: self.mgr.activate_temp_light() if self.settings["temp_light_enabled"] else self.mgr.adjust_brightness(-1)
        elif args.toggle: self.mgr.set_brightness(0 if self.mgr.get_brightness() > 0 else self.settings.get("last_brightness", 3))
        else: self.activate()
        return 0

    def on_brightness_changed(self, value):
        if value > 0: self.settings["last_brightness"] = value
        config.save_settings(self.settings)
        GLib.idle_add(self.update_ui_state)

    def do_activate(self):
        if not self.window:
            self.create_window()
        self.window.show_all()
        self.window.present()

    def do_startup(self):
        Gtk.Application.do_startup(self)
        self.create_status_icon()
        GLib.timeout_add_seconds(2, self.periodic_check)

    def periodic_check(self):
        self.update_ui_state()
        return True

    def create_status_icon(self):
        if XApp:
            self.status_icon = XApp.StatusIcon()
            self.status_icon.connect("activate", lambda i,b,t: self.on_tray_activate())
        else:
            self.status_icon = Gtk.StatusIcon()
            self.status_icon.connect("activate", lambda i: self.on_tray_activate())
        self.update_tray_icon()

    def update_tray_icon(self):
        b = self.mgr.get_brightness()
        ic = "display-brightness-symbolic" if b > 0 else "input-keyboard-symbolic"
        if XApp and isinstance(self.status_icon, XApp.StatusIcon):
            self.status_icon.set_icon_name(ic)
            self.status_icon.set_tooltip_text(f"Klavye Işığı: {b}")
        else:
            self.status_icon.set_from_icon_name(ic)
            self.status_icon.set_tooltip(f"Klavye Işığı: {b}")

    def on_tray_activate(self):
        if self.window and self.window.get_visible(): self.window.hide()
        else: self.activate()

    def create_window(self):
        self.window = Gtk.ApplicationWindow(application=self, title="Klavye Işığı")
        self.window.set_border_width(10)
        self.window.connect("delete-event", lambda w,e: self.window.hide() or True)

        nb = Gtk.Notebook()
        self.window.add(nb)

        # Tab 1
        v1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        v1.set_border_width(15)
        nb.append_page(v1, Gtk.Label(label="Kontrol"))
        
        self.large_icon = Gtk.Image.new_from_icon_name("display-brightness-symbolic", Gtk.IconSize.DIALOG)
        v1.pack_start(self.large_icon, False, False, 10)
        
        self.status_label = Gtk.Label(label="...")
        v1.pack_start(self.status_label, False, False, 0)

        hbox_switch = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        v1.pack_start(hbox_switch, False, False, 5)
        hbox_switch.pack_start(Gtk.Label(label=_("current_brightness") + ":"), False, False, 5)
        
        self.switch = Gtk.Switch()
        self.switch.connect("notify::active", self.on_switch_toggled)
        hbox_switch.pack_start(self.switch, False, False, 5)

        v1.pack_start(Gtk.Label(label=_("brightness_level"), xalign=0), False, False, 0)
        adj = Gtk.Adjustment(value=self.mgr.get_brightness(), lower=0, upper=self.mgr.max_brightness, step_increment=1)
        self.slider = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adj)
        self.slider.set_digits(0)
        self.slider.connect("value-changed", self.on_slider_moved)
        v1.pack_start(self.slider, False, False, 0)

        cb_auto = Gtk.CheckButton(label=_("autostart"))
        cb_auto.set_active(self.settings.get("autostart"))
        cb_auto.connect("toggled", self.on_autostart_toggled)
        v1.pack_start(cb_auto, False, False, 0)

        cb_temp = Gtk.CheckButton(label=_("temp_light"))
        cb_temp.set_active(self.settings.get("temp_light_enabled"))
        cb_temp.connect("toggled", self.on_temp_toggle)
        v1.pack_start(cb_temp, False, False, 0)

        v1.pack_start(Gtk.Label(label=_("burn_duration_label"), xalign=0), False, False, 0)
        d_adj = Gtk.Adjustment(value=self.settings.get("temp_light_duration"), lower=1, upper=60, step_increment=1)
        self.d_slider = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=d_adj)
        self.d_slider.set_digits(0)
        self.d_slider.connect("value-changed", self.on_dur_moved)
        v1.pack_start(self.d_slider, False, False, 0)

        # Language Selection
        hbox_lang = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        v1.pack_start(hbox_lang, False, False, 10)
        hbox_lang.pack_start(Gtk.Label(label=_("language") + ":"), False, False, 0)
        
        self.combo_lang = Gtk.ComboBoxText()
        self.combo_lang.append("tr", "Türkçe")
        self.combo_lang.append("en", "English")
        self.combo_lang.set_active_id(self.settings.get("language", "tr"))
        self.combo_lang.connect("changed", self.on_language_changed)
        hbox_lang.pack_start(self.combo_lang, True, True, 0)

        btn_reset = Gtk.Button(label=_("reset_app"))
        btn_reset.get_style_context().add_class("destructive-action")
        btn_reset.connect("clicked", self.on_reset_clicked)
        v1.pack_end(btn_reset, False, False, 10)

        # Tab 2: Efektler (Ritim/Sequencer)
        v_eff = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        v_eff.set_border_width(15)
        nb.append_page(v_eff, Gtk.Label(label=_("tab_effects")))

        info_eff = Gtk.Label(label=_("eff_desc"))
        info_eff.set_line_wrap(True)
        v_eff.pack_start(info_eff, False, False, 0)

        # Step Sequencer (16 steps)
        self.steps = [0] * 16 # Values 0-max
        self.step_btns = []
        
        grid_seq = Gtk.Grid(column_spacing=2, row_spacing=2)
        grid_seq.set_halign(Gtk.Align.CENTER)
        v_eff.pack_start(grid_seq, False, False, 10)
        
        for i in range(16):
            btn = Gtk.Button(label="0")
            btn.set_size_request(40, 40)
            btn.connect("clicked", self.on_step_clicked, i)
            grid_seq.attach(btn, i % 8, i // 8, 1, 1)
            self.step_btns.append(btn)

        # ... (rest of Efektler controls)
        hbox_eff_ctrl = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox_eff_ctrl.set_halign(Gtk.Align.CENTER)
        v_eff.pack_start(hbox_eff_ctrl, False, False, 10)

        self.btn_play = Gtk.Button(label=_("start_rhythm"))
        self.btn_play.get_style_context().add_class("suggested-action")
        self.btn_play.connect("clicked", self.on_play_rhythm)
        hbox_eff_ctrl.pack_start(self.btn_play, False, False, 0)

        self.btn_stop = Gtk.Button(label=_("stop"))
        self.btn_stop.connect("clicked", lambda b: self.mgr.stop_pattern() or self.update_ui_state())
        hbox_eff_ctrl.pack_start(self.btn_stop, False, False, 0)

        btn_sos = Gtk.Button(label=_("sos_mode"))
        btn_sos.connect("clicked", self.on_sos_clicked)
        v_eff.pack_start(btn_sos, False, False, 0)

        # Tab 4: Hakkında
        v3 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        v3.set_border_width(20)
        nb.append_page(v3, Gtk.Label(label=_("tab_about")))
        
        label_title = Gtk.Label()
        label_title.set_markup(f"<span size='large' weight='bold'>{_('app_title')}</span>")
        v3.pack_start(label_title, False, False, 0)
        
        label_info = Gtk.Label()
        label_info.set_markup(f"{_('about_text')}\n\n"
                            f"<b>{_('version')}:</b> 2.8.1\n"
                            f"<b>{_('developer')}:</b> nyx47rd &amp; Deepmind Team")
        label_info.set_justify(Gtk.Justification.CENTER)
        label_info.set_line_wrap(True)
        v3.pack_start(label_info, False, False, 0)
        
        # Proje sayfası henüz hazır değil, kaldırıldı

        self.update_ui_state()

    def on_language_changed(self, combo):
        new_lang = combo.get_active_id()
        if self.settings.get("language") != new_lang:
            self.settings["language"] = new_lang
            config.save_settings(self.settings)
            
            d = Gtk.MessageDialog(transient_for=self.window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text=_("restart_msg"))
            d.run()
            d.destroy()
            
            # Super-robust restart
            import sys, subprocess
            script_path = os.path.abspath(sys.argv[0])
            python_exe = sys.executable or "/usr/bin/python3"
            
            # Strategy 1: Replace current process
            try:
                os.execl(python_exe, python_exe, script_path, *sys.argv[1:])
            except Exception:
                # Strategy 2: Spawn new and exit (fallback)
                subprocess.Popen([python_exe, script_path] + sys.argv[1:])
                sys.exit(0)

    def on_reset_clicked(self, btn):
        dialog = Gtk.MessageDialog(transient_for=self.window, flags=0, message_type=Gtk.MessageType.QUESTION,
                                   buttons=Gtk.ButtonsType.YES_NO, text=_("reset_q"))
        dialog.format_secondary_text(_("reset_desc"))
        res = dialog.run()
        dialog.destroy()
        
        if res == Gtk.ResponseType.YES:
            if utils.reset_system():
                import subprocess
                # Launch installer anew
                subprocess.Popen(["python3", os.path.abspath("main.py")])
                self.quit()

    def update_ui_state(self):
        b = self.mgr.get_brightness()
        cur_text = f"{_('current_brightness')}: {b}"
        if hasattr(self, 'status_label'): self.status_label.set_text(cur_text)
        if hasattr(self, 'switch'):
            self.switch.handler_block_by_func(self.on_switch_toggled)
            self.switch.set_active(b > 0)
            self.switch.handler_unblock_by_func(self.on_switch_toggled)
        if hasattr(self, 'slider'):
            self.slider.handler_block_by_func(self.on_slider_moved)
            self.slider.set_value(b)
            self.slider.handler_unblock_by_func(self.on_slider_moved)
        if hasattr(self, 'large_icon'):
            ic = "display-brightness-symbolic" if b > 0 else "input-keyboard-symbolic"
            self.large_icon.set_from_icon_name(ic, Gtk.IconSize.DIALOG)
        self.update_tray_icon()

    def on_switch_toggled(self, sw, p):
        self.mgr.set_brightness(self.settings.get("last_brightness", self.mgr.max_brightness) if sw.get_active() else 0)

    def on_slider_moved(self, s):
        self.mgr.set_brightness(int(s.get_value()))

    def on_autostart_toggled(self, cb):
        self.settings["autostart"] = cb.get_active()
        config.update_autostart(cb.get_active(), os.path.abspath(__file__.replace("kbd_backlight_app.py", "main.py")))
        config.save_settings(self.settings)

    def on_temp_toggle(self, cb):
        self.settings["temp_light_enabled"] = cb.get_active()
        if cb.get_active(): self.mgr.start_global_listener()
        else: self.mgr.stop_global_listener()
        config.save_settings(self.settings)

    def on_dur_moved(self, s):
        self.settings["temp_light_duration"] = int(s.get_value())
        config.save_settings(self.settings)

    def on_step_clicked(self, btn, idx):
        self.steps[idx] = (self.steps[idx] + 1) % (self.mgr.max_brightness + 1)
        btn.set_label(str(self.steps[idx]))

    def on_play_rhythm(self, btn):
        pattern = [(s, 1000) for s in self.steps]
        self.mgr.play_pattern(pattern)

    def on_sos_clicked(self, btn):
        # SOS levels dynamic
        high = max(1, self.mgr.max_brightness - 1) if self.mgr.max_brightness > 1 else self.mgr.max_brightness
        sos = [
            (high, 500), (0, 500), (high, 500), (0, 500), (high, 500), (0, 1000),
            (high, 1500), (0, 500), (high, 1500), (0, 500), (high, 1500), (0, 1000),
            (high, 500), (0, 500), (high, 500), (0, 500), (high, 500), (0, 3000)
        ]
        self.mgr.play_pattern(sos)

if __name__ == "__main__":
    from gi.repository import Gtk
    import sys
    app = KbdBacklightApp()
    app.run(sys.argv)
