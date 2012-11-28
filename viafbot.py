#!/usr/bin/python
# -*- coding: utf-8 -*-
# CC-BY-SA Max Klein and OCLC Research
# importing modules
# requires that pywikipediabot modules be in your PYTHONPATH
#WARNING this uses a modified version of textlib that replaces once not for all occurences in writeEntireTemplate3
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import wikipedia
import pywikibot.exceptions as exceptions
import pywikibot.textlib_customised as textlib
from time import gmtime, strftime #for timestamping
import json #for saving and recovering the stats dict
import logging
import re
logging.basicConfig(filename='logofviafbot.log',level=logging.DEBUG)
#load settings

#wikipedia site  variables
enwp = wikipedia.getSite('en','wikipedia')
dewp = wikipedia.getSite('de','wikipedia')

#get positions or create them if none
try:
    positionsJSON = open('positions.JSON')
    positions = json.load(positionsJSON)
    positionsJSON.close()
except IOError:
    positions = {'touched' : 0, 'totalRedirects' : 0, 'nopage' : 0, 'nopageDE' : 0 , 'DAB': 0 , 'begriff' : 0 , 'hasInterwiki' : 0 , 'probablyAPerson' : 0 ,
                 'case1' : 0, 'case2' : 0,  'case3' : 0, 'case4' : 0, 'case5' : 0, 'case6' : 0, 'case7' : 0, 'case8' : 0, 'case9' : 0, 'case10' : 0, 'case11' : 0, 'case12' : 0, 'case13' : 0,
                 'superfluous' : 0, 'lockedError' : 0 , 'editConflictError' : 0, 'pageNotSavedError' : 0, 'spamfilterError' : 0, 'longPageError' : 0, 
                 'noACtemplateCount' : 0, 'noNormdatenTemplatecount' : 0, 'ACtemplateNoVIAFcount' : 0, 'normdatenTemplateNoVIAFcount' : 0, 'ACVIAFcount' : 0, 'normdatenVIAFcount' : 0}
#get the wikilinks file
wikilinksfile = open("wikilinksforbotstubtest.out")#should be wikilinksforbot.out when real
wikilinks = wikilinksfile.readlines()
wikilinksfile.close()


def saveSettings():
    positionsJSON = open('positions.JSON', 'w')
    json.dump(positions, positionsJSON, indent=4)
    positionsJSON.close()
    
def pageValidate(nameOfPage, language):
    """accepts string of page name in *language* Wikipedia. 
    returns a Page Object of either the page or it's redirect (upto 10 redirects).
    returns None if the page does not exist"""
    possiblePage = wikipedia.Page(language,nameOfPage)
    for i in range(1,10):
        try:
            possiblePage.get()
            return possiblePage
        except exceptions.IsRedirectPage, redirPageName:
            positions['totalRedirects'] += 1
            possiblePage = wikipedia.Page(language,str(redirPageName))
        except exceptions.NoPage:
            logging.warning('Does not exists or has more than 10 redirects %s', nameOfPage)
            if language == enwp:
                positions['nopage'] += 1
            else:
                positions['nopageDE'] += 1
            return None
        except exceptions.SectionError:
            logging.warning('Section Error on %s', nameOfPage)
            if language == enwp:
                positions['nopage'] += 1
            else:
                positions['nopageDE'] += 1
            return None

def isDab(pageObject, language):
    """determines if the pageObject is a DAB in *language*"""
    templates = pageObject.templatesWithParams()
    for template in templates:
        templateUpper = str(template[0]).upper()
        if language == enwp:
            if templateUpper in ('DAB', 'DBIG', 'DISAM', 'DISAMB', 'DISAMBIG', 'DISAMBIGUATION', 'DISAMBIGUATION PAGE'):
                logging.warning('DAB redirect found at %s', pageObject.title())
                positions['DAB'] +=1
                return True
        elif language == dewp:
            if templateUpper == 'BEGRIFFSKL\xc3\xa4RUNG':
                logging.warning('begriff redirect found at %s', pageObject.title())
                positions['begriff'] +=1
                return True
        else: logging.warning("you passed something to isDab that wasn't enwp or dewp")
    return False

def persondataCheck(pageObject):
    """Does pageobject have persondata? bool"""
    templates = pageObject.templatesWithParams()
    for template in templates:
        if template[0] == 'Persondata':
            return True
    return False

    
def categoryLivingPeopleCheck(pageObject):
    """does pageobject have category:living people? or categories to indicate birth or death dates? bool"""
    categoryList = pageObject.categories()
    for category in categoryList:
        if str(category)[:-2][-6:] in ('births', 'deaths', 'people'): #looking for xxxx births xxxx deaths or living people
            return True
    return False #we didn't find it in all of the categories

def probablyAPerson(pageObject):
    if persondataCheck(pageObject):
        positions['probablyAPerson'] +=1
        return True
    elif categoryLivingPeopleCheck(pageObject):
        positions['probablyAPerson'] +=1
        return True
    else:
        return False

def getGermanName(pageObject):
    """returns a Page object which is the equivalent German Wikipedia page to argument
    raises NoPage if there is no German equivalent."""
    pageText = pageObject.get()
    interWikis = textlib.getLanguageLinks(pageText)
    try:
        return interWikis[dewp]
    except KeyError:
        return None
    
def determineAuthorityControlTemplate(pageObject, language):
    """returns 'notemplate' if no Authority Control Template or Normdaten template, 'templateNoVIAF' if AC or ND template but no VIAF number, 
    and returns the viaf number if it exists as type int. Returns -1 if VIAFnumber was for some reason non-numerical"""
    templates = pageObject.templatesWithParams()
    if language == enwp:
        templateName,  templateVIAFcount, templateNoVIAFcount, templateNone = 'Authority control', 'ACVIAFcount', 'ACtemplateNoVIAFcount', 'noACtemplateCount'
    else: #it's German
        templateName, templateVIAFcount, templateNoVIAFcount, templateNone = 'Normdaten', 'normdatenVIAFcount', 'normdatenTemplateNoVIAFcount', 'noNormdatenTemplatecount'
    for template in templates:
        if template[0] == templateName:
            for param in template[1]:
                if param[:4] in ['VIAF', ' VIA']:
                    positions[templateVIAFcount] += 1
                    try:
                        templateVIAFnum = int(param[5:])
                    except ValueError:
                        logging.warning('Non-numerical VIAFnum for %s', pageObject.title())
                        templateVIAFnum = -1 #this will cause viafbot to report a conflict and it is an invalid viafnumber
                    return templateVIAFnum
            positions[templateNoVIAFcount] += 1 
            return 'templateNoVIAF'
    positions[templateNone] += 1
    return 'noTemplate'

def writeToWiki(validatedPage, acStatus, normdatenStatus, viafnum, writeAttempts):
    """13 case switch that Writes viafnum or reports viafnum conflicts to or about validatedPage.
    Key 
    nd - normdaten; ac - authority control; vl - viaf->wikipedia link number
    (xx) - template does not exist; |xx| - has template but no viaf parameter; |(xx)| -> (xx) or |xx|
    
    1 - |(nd)|, (ac)
        AC template added VIAF parameter written.
    2 - |(nd)|, |ac| 
        VIAF parameter written.
    3 - |(nd)|, ac == vl 
        No writing necessary.
    4 - |(nd)|, ac != vl 
        requires human attention. Nothing written.
    5 - nd , (ac), nd == vl.
        AC template added VIAF parameter written.
    6 - nd, (ac), nd != vl.
        requires human attention. Nothing Written.
    7 - nd, |ac|, nd == vl.
        VIAF parameter written.
    8 - nd, |ac|, nd != vl.
        requires human attention.
    9 - nd, ac , nd == ac == vl.
        No writing necessary.
    10- nd, ac, nd == ac != vl.
        requires human attention. Nothing written.
    11- nd, ac, nd != ac, nd == vl.
        requires human attention. Nothing written.
    12- nd, ac, nd != ac, ac == vl.
        requires human attention. Nothing written.
    13- nd, ac, nd != ac != vl.
        requires human attention. Nothing written."""   
    case = ''  
    try:
        if (normdatenStatus == 'noTemplate') or (normdatenStatus == 'templateNoVIAF'): #there's no normdaten to check
            if acStatus == 'noTemplate':
                case = 'case1'
            elif acStatus == 'templateNoVIAF':
                case = 'case2'
            elif type(acStatus)==int:
                if acStatus == viafnum:
                    case = 'case3'
                else:
                    case = 'case4'
        elif type(normdatenStatus)==int: #there's normdaten
            if acStatus == 'noTemplate':
                if normdatenStatus == viafnum:
                    case = 'case5'
                else:
                    case = 'case6'
            elif acStatus == 'templateNoVIAF':
                if normdatenStatus == viafnum: #so there is a english template and viafnum agrees with dewp
                    case = 'case7'
                else:
                    case = 'case8'
            elif type(acStatus)==int:
                if acStatus == normdatenStatus:
                    if acStatus == viafnum:
                        case = 'case9'
                    else:
                        case = 'case10'
                else:
                    if normdatenStatus == viafnum:
                        case = 'case11'
                    elif acStatus == viafnum:
                        case = 'case12'
                    else:
                        case = 'case13'
        else:
            raise exceptions.Error
        
        #increment positions
        positions[case] += 1
        #log a bit
        logging.info('%s found on article %s', case, validatedPage.title())
        #write to wiki in the right cases
        if case in ['case1', 'case5']:
            writeEntireTemplate(validatedPage, viafnum)
        elif case in ['case2', 'case7']:
            writeVIAFparamOnly(validatedPage, viafnum)            
            
    #exceptions raised while trying to write 
    except exceptions.LockedPage:
        writeAttempts += 1
        if writeAttempts <= 6:
            writeToWiki(validatedPage, acStatus, normdatenStatus, viafnum, writeAttempts)
        else:
            positions['lockedError'] += 1
            logging.info('locked page found: %s', validatedPage.title() )

    except exceptions.PageNotSaved:
        writeAttempts += 1
        if writeAttempts <= 6:
            writeToWiki(validatedPage, acStatus, normdatenStatus, viafnum, writeAttempts)
        else:
            positions['pageNotSavedError'] += 1
            logging.info('PageNotSaved error found: %s', validatedPage.title() )  
    
    except exceptions.EditConflict:
        writeAttempts += 1
        if writeAttempts <= 6:
            writeToWiki(validatedPage, acStatus, normdatenStatus, viafnum, writeAttempts)
        else:
            positions['editConflictError'] += 1
            logging.info('EditConflict error found: %s', validatedPage.title() )  
            
    except exceptions.SpamfilterError:
        writeAttempts += 1
        if writeAttempts <= 6:
            writeToWiki(validatedPage, acStatus, normdatenStatus, viafnum, writeAttempts)
        else:
            positions['spamfilterError'] += 1
            logging.info('spamfilter error found: %s', validatedPage.title() )  
            
    except exceptions.LongPageError:
        writeAttempts += 1
        if writeAttempts <= 6:
            writeToWiki(validatedPage, acStatus, normdatenStatus, viafnum, writeAttempts)
        else:
            positions['longPageError'] += 1
            logging.info('longPage error found: %s', validatedPage.title() )
    

def writeEntireTemplate(validatedPage, viafnum):
    """Find the lowest index of the list of matches"""
    #dictionary is of matches and their lowest index position in the pageWikiText
    dictOfMatches = {'<!-- Metadata: see [[Wikipedia:Persondata':'',
                    '{{Persondata': '',
                    '{{DEFAULTSORT':'',
                    '[[Category:': ''}
    
    pageWikiText = validatedPage.get()
    
    #iterater over the keys put their lowest position
    lowestOccuringMatch = ''
    lowestOccuringMatchIndex = ''
    for match in dictOfMatches:
        try: 
            dictOfMatches[match] = pageWikiText.index(match)
            if dictOfMatches[match] < lowestOccuringMatchIndex:
                lowestOccuringMatch = match
                lowestOccuringMatchIndex = dictOfMatches[match]
        except ValueError:
            pass 
    #if there was nothing to put the template above just log otherwise call replaceExcept
    if lowestOccuringMatch == '<!-- Metadata: see [[Wikipedia:Persondata':
        replacementText = textlib.replaceExcept(pageWikiText, '<!-- Metadata: see \[\[Wikipedia:Persondata\]\] -->' , '{{Authority control|VIAF=' + str(viafnum) + '}}' + '\n' + '<!-- Metadata: see [[Wikipedia:Persondata]] -->', exceptions=[], caseInsensitive=True,
                  allowoverlap=False, marker = '', site = enwp)
    elif lowestOccuringMatch == '{{Persondata':
        replacementText = textlib.replaceExcept(pageWikiText, '{{Persondata' , '{{Authority control|VIAF=' + str(viafnum) + '}}' + '\n' + '{{Persondata', exceptions=[], caseInsensitive=True,
                  allowoverlap=False, marker = '', site = enwp)
    elif lowestOccuringMatch == '{{DEFAULTSORT':
        replacementText = textlib.replaceExcept(pageWikiText, '{{DEFAULTSORT' , '{{Authority control|VIAF=' + str(viafnum) + '}}' + '\n' + '{{DEFAULTSORT', exceptions=[], caseInsensitive=True,
                  allowoverlap=False, marker = '', site = enwp)
    elif lowestOccuringMatch == '[[Category:':
        replacementText = textlib.replaceExcept(pageWikiText, '\[\[Category:' , '{{Authority control|VIAF=' + str(viafnum) + '}}' +'\n' + '[[Category:', exceptions=[], caseInsensitive=True,
                  allowoverlap=False, marker = '', site = enwp)
    elif lowestOccuringMatch == '':
        logging.warning("writeEntireTemplate on page had no persondata, category, default sort for page: %s", validatedPage.title())   
        replacementText = pageWikiText
    
    try:
        validatedPage.put(newtext = replacementText, comment = 'Added the {{[[Template:Authority control|Authority control]]}} template with' + ' VIAF number ' + str(viafnum)+ ': ' + 'http://viaf.org/viaf/' + str(viafnum)+' . Please [[WP:VIAF/errors|report any errors]].', 
                          watchArticle = False , minorEdit=True, force=False, sysop=False, botflag=True, maxTries = 5)
    except exceptions.LockedPage:
        raise exceptions.LockedPage
    except exceptions.EditConflict:
        raise exceptions.EditConflict
    except exceptions.ServerError:
        logging.warning("writeEntireTemplate gave a generic server error for %s",  validatedPage.title())
    except exceptions.SpamfilterError:
        raise exceptions.SpamfilterError
    except exceptions.PageNotSaved:
        raise exceptions.PageNotSaved       



def writeVIAFparamOnly(validatedPage,viafnum):
    """Uses the textlib method replaceExcept"""

    pageWikiText = validatedPage.get()

    replacementText = textlib.replaceExcept(pageWikiText, '{{Authority control' , '{{Authority control|VIAF=' + str(viafnum), exceptions=[], caseInsensitive=False,
                  allowoverlap=False, marker = '', site = enwp)

    try:
        validatedPage.put(newtext = replacementText, comment = 'Added VIAF number ' + str(viafnum) + ' to {{[[Template:Authority control|Authority control]]}} template. http://viaf.org/viaf/' + str(viafnum) +' .Please [[WP:VIAF/errors|report any errors]].',
                           watchArticle = False , minorEdit=True, force=False, sysop=False, botflag=True, maxTries = 5)
    except exceptions.LockedPage:
        raise exceptions.LockedPage
    except exceptions.EditConflict:
        raise exceptions.EditConflict
    except exceptions.ServerError:
        logging.warning("writeVIAFparam on page gave a generic server error for page %s",  validatedPage.title())
    except exceptions.SpamfilterError:
        raise exceptions.SpamfilterError
    except exceptions.PageNotSaved:
        raise exceptions.PageNotSaved   

              
#main loop
#slice the wikilinks file to pick up from the last time it ran
totaltodo = len(wikilinks)
wikilinks = wikilinks[positions['touched']:]
for wikilink in wikilinks:
    '''Load the article and number from file'''
    wikilink = wikilink.split() #wikilink should be now be list of lenght two as [name, viafnum]
    
    #validate by following redirects
    unvalidatedPageName = wikilink[0]
    viafnum = int(wikilink[1])
    
    positions['touched'] = positions['touched'] + 1 #how many wikilinks we've seen
    
    #Find english redirects, deletions and dabs, after all this file could be 6 months out of date
    validatedPage = pageValidate(unvalidatedPageName, enwp) #It's possible that the page doesn't exist
    if not validatedPage: #validatedPage is in fact not a not an existing page onwiki 
        saveSettings() 
        continue  #If the page doesn't exist, then we don't need to write anything to the Wiki.
    if isDab(validatedPage, enwp):
        saveSettings()
        continue
    if not probablyAPerson(validatedPage):
        saveSettings()
        continue
    else: #if it exists and it's not a dab then lets get the bloody acStatus
        acStatus = determineAuthorityControlTemplate(validatedPage,enwp)
    
    #see if a German page exists
    germanName = getGermanName(validatedPage)
    if not germanName: #because germanName is none if there is no interwiki
        normdatenStatus = 'noTemplate'
    else: # a german page name existed
        positions['hasInterwiki'] += 1
        #validated it against redirects etc
        validatedGermanPage = pageValidate(germanName.title(), dewp)
        if not validatedGermanPage:
            normdatenStatus = 'noTemplate'
        elif isDab(validatedGermanPage, dewp):
            normdatenStatus = 'noTemplate'
        else:
            normdatenStatus = determineAuthorityControlTemplate(validatedGermanPage,dewp)
    
    #now that we have acStatus and normdatenStatus it's time to write to the Wiki if necc.
    writeToWiki(validatedPage, acStatus, normdatenStatus, viafnum, writeAttempts=0)

    saveSettings()
    print str(positions['touched']), 'of ', str(totaltodo)
