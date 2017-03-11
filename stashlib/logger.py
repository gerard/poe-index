import datetime

class Logger:
    def __init__(self, fd):
        self.__fd = fd

    def __log(self, lead, s, args):
        self.__fd.write("[{}]".format(datetime.datetime.now()) + lead + ": " + s.format(*args) + "\n")
        self.__fd.flush()

    def debug(self, s, *args):
        self.__log("D", s, args)

    def error(self, s, *args):
        self.__log("E", s, args)
