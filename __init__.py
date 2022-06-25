from mycroft import MycroftSkill, intent_file_handler


class CrearEventoCampus(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('campus.evento.crear.intent')
    def handle_campus_evento_crear(self, message):
        self.speak_dialog('campus.evento.crear')


def create_skill():
    return CrearEventoCampus()

