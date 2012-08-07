#!/usr/bin/python
# -*- coding: utf-8 -*-

# importing modules
# requires that pywikipediabot modules be in your PYTHONPATH
import sys
from wikipedia import *

 
# global variables
enwp = getSite('en','wikipedia')
dewp = getSite('de','wikipedia')
wikilinks = open("wikilinksforbot.out")
wikilinks = wikilinks.readlines()
viafbotrun = ("viafbotrun.log", 'w+')
same = 0
total = 0
nopage = 0


def pageValidate(nameOfPage,maximumDepth):
    """returns a string of either the page or it's redirect (upto maxmimDepth).  
    Or returns None if the page does not exist"""
    lastPossible = nameOfPage
    for i in range(1,maximumDepth):
        newPossible = pageValidator(lastPossible)
        if (str(newPossible) == str(lastPossible)):
            return newPossible
        elif newPossible == None:
                return None
        lastPossible = str(newPossible)
    print("For article " + nameOfPage + "there are more than " + str(maximumDepth) +"redirects")
 
def pageValidator(nameOfPage): #TODO handle mutliple redirects
    """returns a string of either the page or it's redirect (does not check double redirects).  
    Or returns None if the page does not exist"""
    namepage = Page(enwp, nameOfPage)
    try:
        namepage.get()
    except IsRedirectPage, redirPageName:
        return redirPageName
    except NoPage, errorlist:
        return None
    else:
        return nameOfPage
        
def determineAuthorityControlTemplate(nameOfPage):
    """returns 'noACtemplate' if no Authority Control Template, 'templateNoVIAF' if AC template but no VIAF number, 
    and returns the viaf number if it exists"""
    namepage = Page(enwp,nameOfPage)
    templates = namepage.templatesWithParams()
    for template in templates:
        if template[0] == 'Authority control':
            for param in template[1]:
                if param[:4] == 'VIAF':
                    return param[5:]
            return 'templateNoVIAF'
    return 'noACtemplate'

print pageValidate('User:VIAFbot/redir2',5) #TODO check double redirects
#the main loop

for wikilink in wikilinks:
    wikilink = wikilink.split() #to get the line into a list of (name, viafnum)
    unvalidatedPageName = wikilink[0]
    validatedPage = pageValidate(unvalidatedPageName,20) #TODO handle None return 
    ACstatus = determineAuthorityControlTemplate(validatedPage)
    Germanstatus = determineAuthorityControlTemplateGerman(validatedPage)
    writeToWiki(ACstatus, Germanstatus)
    writeToLog()
    
    origNameOfPage = wikilink[0]
    afternameOfPage = pageValidator(origNameOfPage)
    print origNameOfPage, afternameOfPage
    total = total +1
    if afternameOfPage == None:
        nopage= nopage +1
        viafbotrun.write("No such article as " + origNameOfPage)
    else:
        pass
    if origNameOfPage == afternameOfPage:
        same = same +1
    else:
        pass
    linkvalidity.write( str(total) + " " + str(same) + str(nopage) + '\n')

#close resources
wikilinks.close()