#!/usr/bin/env python

import os
import sys
from subprocess import call
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk


help_text = """
Usage:
\ttag-dialog [FILE...] [INITIAL COMMAND]

Simple GUI dialog for the tagging files. Intended to be used in
"Custom Actions" provided by most file management/preview applications.

Commands:
\t+[TAG]   adds a tag to the given files
\t-[TAG]   removes a tag from the given files

Options:
\t--help   prints this help text and exits

For issues and documentation: https://github.com/brendanwhitfield/tag-tool
"""



provider = Gtk.CssProvider()
provider.load_from_data(b"""

    GtkWindow
    {
        background:black;
        color:white;
    }

    GtkEntry
    {
        color:inherit;
        background: #333;
        border:none;
        font-family:monospace;
    }

""")
Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


class Window:

    def __init__(self, files, init_str=""):
        self.files = files
        self.window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
    
        self.window.connect("delete_event", lambda w,e: False)
        self.window.connect("destroy", Gtk.main_quit)
    
        self.window.set_border_width(10)
        self.window.set_title("Tag-Tool")
        self.window.set_default_size(400, -1)
        self.window.set_resizable(True)
        self.window.set_modal(True)
        self.window.set_position(Gtk.WindowPosition.CENTER)

        self.entry = Gtk.Entry()
        self.window.add(self.entry)

        self.entry.set_text(init_str)
        self.entry.connect("key-release-event", self.on_key_release)

        self.entry.show()
        self.window.show()

        # put the cursor at the end of the text
        # needs to happen AFTER the window is shown
        l = len(self.entry.get_text())
        self.entry.grab_focus()
        self.entry.select_region(l,l)


    def on_key_release(self, widget, data=None):
        if data.keyval == Gdk.KEY_Return:
            self.tag()
        elif data.keyval == Gdk.KEY_Escape:
            Gtk.main_quit()
        # TODO: tab-complete


    def tag(self):
        # run the tag command
        command = ["tag"] + self.files + self.entry.get_text().split()
        Gtk.main_quit()
        call(command)



if __name__ == "__main__":

    files = []
    init_str = ""

    for arg in sys.argv[1:]:
        if arg == "--help":
            print(help_text)
            exit(0)
        elif os.path.isfile(arg):
            files.append(arg)
        else:
            init_str = arg

    if len(files) == 0:
        print("Please enter one or more files to be tagged")
        exit(1)

    window = Window(files, init_str)
    Gtk.main()
