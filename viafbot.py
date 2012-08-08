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


def pageValidate(nameOfPage):
    """accepts string of page name in EnglishWikipedia. 
    returns a Page Object of either the page or it's redirect (upto 10 redirects).
    raises NoPage exception if the page does not exist"""
    possiblePage = Page(enwp,nameOfPage)
    for i in range(1,10):
        try:
            possiblePage.get()
            return possiblePage
        except IsRedirectPage, redirPageName:
            possiblePage = Page(enwp,str(redirPageName))
        except NoPage:
            raise NoPage
        
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

def getGermanName(nameOfPage):
    """returns a strng which is the equivalent German Wikipedia page to argument
    raises NoPage if there is no German equivalent."""
    namepage = Page(enwp,nameOfPage)
    interWikis = namepage.get().getLanguageLinks # is this second call to namepage.get() too much io?



print pageValidate('Mayakovsky')
print pageValidate('User:VIAFbot/redir2')

#the main loop
for wikilink in wikilinks:
    wikilink = wikilink.split() #to get the line into a list of (name, viafnum)
    unvalidatedPageName = wikilink[0]
    try:
        validatedPage = pageValidate(unvalidatedPageName) #It's possible that the page doesn't exist
    except NoPage:
        viafbotrun.write(unvalidatedPageName.title() + "did not exist, or redirected more than 20 times")
        continue  #If the page doesn't exist, then we don't need to write anything to the Wiki.
    
    #get statuses of Authority Control and Normdaten templates
    ACstatus = determineAuthorityControlTemplate(validatedPage, enwp)
    germanName = getGermanName(validatedPage)
    germanACstatus = determineAuthorityControlTemplate(validatedPage, dewp)
    
    
    writeToWiki(ACstatus, germanACstatus)
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