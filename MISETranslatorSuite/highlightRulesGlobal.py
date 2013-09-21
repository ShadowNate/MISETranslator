#-------------------------------------------------------------------------------
# Name:        keeps highlight rules centrally
#               keeps and notifies a list of "watcher" highlighters (calls their re-highlight)
# TODO: maybe make it a singleton ?
#-------------------------------------------------------------------------------
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *

_hlmodul_highlightingRules = []
_hlmodul_searchhighlightingRule = []  # just one rule, but with Column Index to match too! (or -1 to match everywhere)
_hlmodul_highlighteRulesWatchers = []


def setSearchHighlightRule(ruleExprStr, ruleClassFormat, caseSensitivity = True, columnToMatch = -1):
    qtCaseSens = Qt.CaseSensitive
    if not caseSensitivity:
        qtCaseSens = Qt.CaseInsensitive
    if len(_hlmodul_searchhighlightingRule) == 0:
        _hlmodul_searchhighlightingRule.append((QtCore.QRegExp(ruleExprStr, qtCaseSens), ruleClassFormat, columnToMatch))
    else:
        _hlmodul_searchhighlightingRule[0] = (QtCore.QRegExp(ruleExprStr, qtCaseSens), ruleClassFormat, columnToMatch)
    updateWatchers()

def addHighlightRule(ruleExprStr, ruleClassFormat, caseSensitivity = True, columnToMatch = -1):
    qtCaseSens = Qt.CaseSensitive
    if not caseSensitivity:
        qtCaseSens = Qt.CaseInsensitive
    _hlmodul_highlightingRules.append((QtCore.QRegExp(ruleExprStr, qtCaseSens), ruleClassFormat, columnToMatch))
    updateWatchers()

def updateWatchers():
    for hlWatcher in _hlmodul_highlighteRulesWatchers:
        if(hlWatcher is not None):
            try:
                hlWatcher.rehighlight()
            except:
                _hlmodul_highlighteRulesWatchers.remove(hlWatcher) # will this create problems? (removal while traversing with for.. in ) ?
        else:
            _hlmodul_highlighteRulesWatchers.remove(hlWatcher) # will this create problems? (removal while traversing with for.. in ) ?

def getAllHighlightRules():
    retList = []
    retList.extend(_hlmodul_highlightingRules)
    retList.extend(_hlmodul_searchhighlightingRule)
    return retList

def addHighlighterWatcher(highlighterObj):
    _hlmodul_highlighteRulesWatchers.append(highlighterObj)

def clearAll():
    del _hlmodul_highlighteRulesWatchers[:]
    del _hlmodul_highlightingRules[:]
    del _hlmodul_searchhighlightingRule[:]
    updateWatchers()

def clearWatchers():
    del _hlmodul_highlighteRulesWatchers[:]

def clearConstantRules():
    del _hlmodul_highlightingRules[:]
    updateWatchers()

def clearSearchRule():
    del _hlmodul_searchhighlightingRule[:]
    updateWatchers()


def main():
    pass

if __name__ == '__main__':
    main()
