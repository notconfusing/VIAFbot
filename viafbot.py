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
        try: 
            newPossible = pageValidator(lastPossible)
            if (str(newPossible) == str(lastPossible)):
                return newPossible
        except NoPage:
            raise NoPage
        lastPossible = str(newPossible)
    raise NoPage
 
def pageValidator(nameOfPage): #TODO handle mutliple redirects
    """returns a string of either the page or it's redirect (does not check double redirects).  
    Raises NoPage exception if page does not exist"""
    namepage = Page(enwp, nameOfPage)
    try:
        namepage.get()
    except IsRedirectPage, redirPageName:
        return redirPageName
    except NoPage:
        raise NoPage
    else:
        return nameOfPage
        
def determineAuthorityControlTemplate(nameOfPage, site):
    """returns 'noACtemplate' if no Authority Control Template, 'templateNoVIAF' if AC template but no VIAF number, 
    and returns the viaf number if it exists"""
    namepage = Page(site,nameOfPage)
    templates = namepage.templatesWithParams()
    if site == enwp:
        targetTem = 'AuthorityControl'
    else:
        targetTem = 'Normdaten'
    for template in templates:
        if template[0] == targetTem:
            for param in template[1]:
                if param[:4] == 'VIAF':
                    return param[5:]
            return 'templateNoVIAF'
    return 'noACtemplate'


#the main loop

for wikilink in wikilinks:
    wikilink = wikilink.split() #to get the line into a list of (name, viafnum)
    unvalidatedPageName = wikilink[0]
    try:
        validatedPage = pageValidate(unvalidatedPageName,20) #It's possible that the page doesn't exist
    except NoPage:
        viafbotrun.write(unvalidatedPageName + "did not exist, or redirected more than 20 times")
        continue #If the page doesn't exist, then we don't need to write anything to the Wiki.
    ACstatus = determineAuthorityControlTemplate(validatedPage, enwp)
    Germanstatus = determineAuthorityControlTemplate(validatedPage, dewp)
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