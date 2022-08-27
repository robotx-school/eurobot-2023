# Communicate between main loop and process
from multiprocessing import Process, Value

class MainLoop:
    def __init__(self, pr):
        self.variable = Value("d", 1)
        p = Process(target=lambda: pr.loop(self.variable))
        p.start()
    def loop(self):
        while True:
            print(self.variable.value)
class Pr:
    def __init__(self):
        pass
    def loop(self, var):
        var.value = 2

process = Pr()
main = MainLoop(process)
main.loop()

        