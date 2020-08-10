from mycroft.skills.core import MycroftSkill, intent_file_handler
from mycroft.messagebus.message import Message
from jiggle import MouseJiggler
from time import sleep


class MouseJigglerSkill(MycroftSkill):
    def __init__(self):
        super(MouseJigglerSkill, self).__init__("MouseJigglerSkill")
        self.jiggler = None
        if "auto_start" not in self.settings:
            self.settings["auto_start"] = True
        if "intensity" not in self.settings:
            self.settings["intensity"] = 1
        if "always_on" not in self.settings:
            self.settings["always_on"] = False
        if "idle_time" not in self.settings:
            self.settings["idle_time"] = 15
        if "mouse_events" not in self.settings:
            self.settings["mouse_events"] = True

    def start_mouse(self):
        self.jiggler = MouseJiggler(daemonic=True,
                                    idle_time=self.settings["idle_time"],
                                    jiggle=self.settings["intensity"],
                                    ignore_idle=self.settings["always_on"])

        def on_mouse_move(mouse_position):
            self.bus.emit(Message("mouse.position",
                                  {"x": mouse_position.x,
                                   "y": mouse_position.y}))

        def on_jiggle():
            self.bus.emit(Message("mouse.jiggle"))

        def on_idle():
            self.bus.emit(Message("mouse.idle"))

        def on_active():
            self.bus.emit(Message("mouse.active"))

        def on_stop():
            self.bus.emit(Message("mouse.events.stopped"))

        if self.settings["mouse_events"]:
            self.jiggler.on_mouse_move = on_mouse_move
            self.jiggler.on_jiggle = on_jiggle
            self.jiggler.on_idle = on_idle
            self.jiggler.on_active = on_active
            self.jiggler.on_stop = on_stop

        self.jiggler.start()

    def stop_mouse(self):
        self.jiggler.stop()
        self.jiggler = None

    def initialize(self):
        if self.settings["auto_start"]:
            self.start_mouse()
        self.add_event('skill-mouse-jiggler.jarbasskills.home',
                       self.handle_homescreen)

    def get_intro_message(self):
        self.speak_dialog("intro")

    # homescreen
    def handle_homescreen(self, message):
        j = MouseJiggler(daemonic=True,
                         jiggle=10,
                         ignore_idle=True)
        j.start()
        sleep(30)
        j.stop()

    # Intents
    @intent_file_handler("mouse_start.intent")
    def handle_start(self, message):
        self.start_mouse()
        self.speak_dialog("jiggle_start")

    @intent_file_handler("mouse_stop.intent")
    def handle_stop(self, message):
        self.stop_mouse()
        self.speak_dialog("jiggle_stop")

    @intent_file_handler("mouse_status.intent")
    def handle_status(self, message):
        status = True
        if self.jiggler is None:
            status = False
        if status:
            self.speak_dialog("jiggle_status_on")
        else:
            self.speak_dialog("jiggle_status_off")


def create_skill():
    return MouseJigglerSkill()
