import json
import re

class Item:
    def __init__(self, i, acc, lchar):
        self.__impl = None
        self.__expl = None
        self.__data = i

    def __repr__(self):
        return json.dumps(self.__data, indent=4)

    @classmethod
    def __mod_parse_step(self, s, sl, vl):
        # s: Unparsed string
        # sl: List of parsed string chunks
        # vl: List of values
        # Chunks get split at the values.
        m = re.search("([^0-9\.]*)([0-9\.]*)(.*)", s)
        if m is None:
            return Exception("Parse Error")

        sl.append(m.group(1))
        if m.group(2) == "":
            return (sl, vl)

        vl.append(m.group(2))
        return self.__mod_parse_step(m.group(3), sl, vl)

    @classmethod
    def __mod_parse(self, s):
        sl = []
        vl = []

        pr = self.__mod_parse_step(s, sl, vl)
        return ('@'.join(pr[0]), pr[1])

    # Memoization decorator?
    def implicits(self):
        if self.__impl is None:
            self.__impl = []
            for m in self.__data.get("implicitMods", []):
                self.__impl.append(Item.__mod_parse(m))
        return self.__impl

    # XXX: This is same as above...
    def explicits(self):
        if self.__expl is None:
            self.__expl = []
            for m in self.__data.get("explicitMods", []):
                self.__expl.append(Item.__mod_parse(m))
        return self.__expl

    # XXX: Use same mod parsing than implicits/explicits
    def utility(self):
        return NotImplementedn

    # XXX: We need a default AttributeNotFound handler to avoid writing
    #      accessors.
    def icon(self):
        if self.__icon is None:
            self.__icon = None
