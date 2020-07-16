# ------------------------------------------------------------------------------
#  Copyright (C) 2020 Michael Daniels
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
# ------------------------------------------------------------------------------

import pywikibot
import json
from datetime import datetime, timezone

site = pywikibot.Site('en', 'wikipedia')
metawiki = pywikibot.Site('meta', 'meta')


def globalallusers(site, group):
    """

    :param site: The site to get our data from.
    :type site: pywikibot.site.APISite
    :param group: The group to get.
    :type group: str
    :return: A pywikibot generator of all global users in the given global group.
    :rtype: pywikibot.data.api.ListGenerator
    """
    agugen = pywikibot.data.api.ListGenerator('globalallusers',
                                              aguprop='groups', site=site)
    if group:
        agugen.request['agugroup'] = group
    return agugen


def sortkeys(key: str) -> str:
    """
    Sorts the user groups before saving them to the wiki.

    @param key: User right
    @type key: str
    @return: Corresponding abbreviation
    @rtype: str
    """
    sortkeyDict = {
        "sysop": "A",
        "arbcom": "ARB",
        "bureaucrat": "B",
        "checkuser": "CU",
        "oversight": "CV",
        "interface-admin": "IA",
        "abusefilter": "EFM",
        "abusefilter-helper": "EFH",
        "accountcreator": "ACC",
        "autoreviewer": "AP",
        "extendedmover": "PM",
        "filemover": "FM",
        "massmessage-sender": "MMS",
        "patroller": "NPR",
        "reviewer": "PCR",
        "rollbacker": "RB",
        "global-renamer": "GRe",
        "global-rollbacker": "GRb",
        "templateeditor": "TE",
        "otrs-member": "OTRS",
        "steward": "S"
    }
    return sortkeyDict[key]


combinedJsDataPage = pywikibot.Page(site, "User:MDanielsBot/markAdmins-Data.js")
combinedJsonDataPage = pywikibot.Page(site, "User:MDanielsBot/markAdmins-Data.json")


localGroups = ["abusefilter", "abusefilter-helper", "accountcreator",
               "bureaucrat", "checkuser", "extendedmover", "filemover",
               "interface-admin", "massmessage-sender", "oversight",
               "sysop", "templateeditor"]
extraLocalGroups = ["autoreviewer", "patroller", "reviewer", "rollbacker"]
globalGroups = ["otrs-member", "steward", "global-rollbacker"]
metaGroups = ["global-renamer"]
arbcomJson = pywikibot.Page(site, "User:AmoryBot/crathighlighter.js/arbcom.json").get()
arbcom_members = json.loads(arbcomJson)

outputDict = {}

print(datetime.now(timezone.utc).strftime("%b %d %Y %H:%M:%S.%f") +
      " -- Starting!", flush=True)

for group in localGroups:
    for user in site.allusers(group=group):
        if user['name'] in outputDict.keys():
            outputDict[user['name']].append(group)
        else:
            outputDict[user['name']] = [group]

for group in globalGroups:
    for user in globalallusers(site, group):
        if user['name'] in outputDict.keys():
            outputDict[user['name']].append(group)
        else:
            outputDict[user['name']] = [group]

for user in arbcom_members:
    if user in outputDict.keys():
        outputDict[user].append("arbcom")
    else:
        outputDict[user] = ["arbcom"]

for group in extraLocalGroups:
    for user in site.allusers(group=group):
        if user['name'] in outputDict.keys():
            outputDict[user['name']].append(group)
        else:
            outputDict[user['name']] = [group]

for group in metaGroups:
    for user in metawiki.allusers(group=group):
        if user['name'] in outputDict.keys():
            outputDict[user['name']].append(group)
        else:
            outputDict[user['name']] = [group]

print(datetime.now(timezone.utc).strftime("%b %d %Y %H:%M:%S.%f") +
      " -- Computing output...", flush=True)

# Sort our flags
for item in outputDict:
    outputDict[item].sort(key=sortkeys)

# Construct combined JSON page
pageTop = "mw.hook('userjs.script-loaded.markadmins').fire("
outputJson = json.dumps(outputDict, sort_keys=True,
                        indent=4, separators=(',', ': '), ensure_ascii=False)
pageBottom = ");"

newText = pageTop + outputJson + pageBottom
oldJspage = combinedJsDataPage.get()
oldJsonpage = combinedJsonDataPage.get()

if newText != oldJspage or outputJson != oldJsonpage:
    print(datetime.now(timezone.utc).strftime("%b %d %Y %H:%M:%S.%f")
          + " -- Updated!", flush=True)
    combinedJsDataPage.put(newText, "Update markadmins data")
    combinedJsonDataPage.put(outputJson, "Update markadmins data")
else:
    print(datetime.now(timezone.utc).strftime("%b %d %Y %H:%M:%S.%f")
          + " -- No changes", flush=True)
