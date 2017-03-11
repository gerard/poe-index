#!/usr/bin/env python3
import os
import os.path
import sys
import re
import json
import requests
from stashlib.logger import Logger
from stashlib.item import Item

POE_STASH_API_STAMP_START = "27868105-29938218-27836989-32264752-30226786"
POE_STASH_API_STAMP_START = "48550941-51528233-48134864-56016831-52124034"
def jdump(*objs):
    for o in objs:
        sys.stdout.write(json.dumps(o, indent=4))
        sys.stdout.write('\t')
    sys.stdout.write('\n')

def mod_parse_step(s, sl, vl):
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
    return mod_parse_step(m.group(3), sl, vl)

def mod_parse(s):
    sl = []
    vl = []

    pr = mod_parse_step(s, sl, vl)
    return ('@'.join(pr[0]), pr[1])

# XXX: Storing json stream takes way to much space, figure out a method of
#      rotation based on age and/or size.  Maybe a filtering so user can
#      choose to cache only certain league or items (we need to check jsonpath
#      to query anyway).
# XXX: typeLine should be a unique id for the implicit properties. Except when
#      there are balance updates...
# XXX: Figure out what the stuff with Set:MS Set:S, etc means.
class StashAPI:
    POE_STASH_API_ENDP = "http://www.pathofexile.com/api/public-stash-tabs"

    def __init__(self, start, logger):
        self.__next = start
        # XXX: This should be configurable
        self.__cpath = os.path.join(os.getenv("HOME"), ".stache")
        self.__logger = logger
        self.__failed = False

    def __cached_fname(self, n):
        return os.path.join(self.__cpath, n)

    def set_caching_path(self, path):
        self.__cpath = path

    def next(self):
        if self.__failed:
            return None

        fname = self.__cached_fname(self.__next)
        try:
            with open(fname) as f:
                ret = json.load(f)
            self.__logger.debug("Using cached change-id[{}]", self.__next)
        except:
            # XXX: No pokemon exception handling!
            self.__logger.debug("Fetching change-id[{}]", self.__next)
            try:
                r = requests.get("{}/?id={}.gz".format(StashAPI.POE_STASH_API_ENDP,
                                                       self.__next))
            except: # XXX: Some sort of retry at the end of stream.
                self.__logger.error("Failed to get change-id[{}]", self.__next)
                self.__failed = True
                return None
            ret = r.json()
            with open(fname, "w") as f:
                f.write(json.dumps(ret))

        self.__next = ret["next_change_id"]
        return ret

logger = Logger(sys.stderr)
sapi = StashAPI(POE_STASH_API_STAMP_START, logger)

while True:
    j = sapi.next()

    if j is None:
        sys.exit(1)

    for sdata in j["stashes"]:
        for idata in sdata["items"]:
            #i = Item(idata,
            #         sdata["accountName"],
            #         sdata["lastCharacterName"])
            if idata["typeLine"] == 'Ancient Reliquary Key' and "note" in idata:
                logger.debug("{}\t{}\t{}\t{}".format(idata["note"], sdata["accountName"], sdata["lastCharacterName"], idata["league"]))
            #print(i)
            #jdump([i.implicits(), i.explicits()])
