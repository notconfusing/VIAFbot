#!/usr/bin/python
# -*- coding: utf-8 -*-

# importing modules
# requires that pywikipediabot modules be in your PYTHONPATH
import sys
from wikipedia import *
from add_text import * #for method writeEntireTemplate
from replace import * #for method writeVIAFaramOnly
from time import gmtime, strftime #for timestamping
 
# global variables
enwp = getSite('en','wikipedia')
dewp = getSite('de','wikipedia')
wikilinksfile = open("wikilinksforbot.out")
wikilinks = wikilinksfile.readlines()
viafbotrun = ("viafbotrun.log", 'w+')

def run():
    touched = 0
    same = 0
    totalRedirects = 0
    nopage = 0
    NoDEWP = 0 #counting how many times viafbot made edits were dewp could benefit
    YesDEWP = 0 #counting how mant times viafbot agreed with dewp.
    conflict4 = 0
    conflict6 = 0
    conflict8 = 0
    conflict10 = 0
    conflict11 = 0
    conflict12 = 0
    conflict13 = 0
    superfluous = 0 #counting how many times viaf bot's job had nothing to do.
    lockedError = 0 
    editConflictError = 0#edit conflict
    pageNotSavedError = 0
    spamfilterError = 0
    longPageError = 0
    #the main loop
    for wikilink in wikilinks:
        wikilink = wikilink.split() #to get the line into a list of (name, viafnum)
        unvalidatedPageName = wikilink[0]
        viafnum = wikilink[1]
        touched = touched + 1
        try:
            validatedPage = pageValidate(unvalidatedPageName) #It's possible that the page doesn't exist
        except NoPage:
            viafbotrun.write(unvalidatedPageName.title() + "did not exist, or redirected more than 10 times")
            continue  #If the page doesn't exist, then we don't need to write anything to the Wiki.
        
        #get statuses of Authority Control and Normdaten templates
        acStatus = determineAuthorityControlTemplate(validatedPage)
        try:
            germanPageName = getGermanName(validatedPage)
        except NoPage: #There was no German equivalent page
            germanPageName = None
            viafbotrun.write('No German equivalent')
        if germanPageName: #Only need to get NormdatenStaus if a German equivalent page exists.
            normdatenStatus = determineNormdatenTemplate(germanPageName)
        else:
            normdatenStatus = 'noNormdatenTemplate' #if there's no page there's also noACtemplate either
            
    
        try:
            writeToWiki(validatedPage, acStatus, normdatenStatus, writeAttempts=0)
        except Error:
            #write to log

    

        origNameOfPage = wikilink[0]
        afternameOfPage = pageValidator(origNameOfPage)
        print origNameOfPage, afternameOfPage
        totalRedirects = totalRedirects +1
        if afternameOfPage == None:
            nopage= nopage +1
            viafbotrun.write("No such article as " + origNameOfPage)
        else:
            pass
        if origNameOfPage == afternameOfPage:
            same = same +1
        else:
            pass
        linkvalidity.write( str(totalRedirects) + " " + str(same) + str(nopage) + '\n')

    #close resources
    wikilinksfile.close()





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
        
def determineAuthorityControlTemplate(pageObject):
    """returns 'noACtemplate' if no Authority Control Template, 'templateNoVIAF' if AC template but no VIAF number, 
    and returns the viaf number if it exists"""
    templates = pageObject.templatesWithParams()
    for template in templates:
        if template[0] == 'Authority control':
            for param in template[1]:
                if param[:4] == 'VIAF':
                    return param[5:]
            return 'templateNoVIAF'
    return 'noACtemplate'

def determineNormdatenTemplate(pageObject):
    """returns 'noNormdatenTemplate' if no Normdaten Template, 'templateNoVIAF'sss if Normdaten template but no VIAF number, 
    and returns the viaf number if it exists"""
    templates = pageObject.templatesWithParams()
    for template in templates:
        if template[0] == 'Normdaten':
            for param in template[1]:
                if param[:4] == 'VIAF':
                    return param[5:]
            return 'templateNoVIAF'
    return 'noNormdatenTemplate'

def getGermanName(pageObject):
    """returns a Page object which is the equivalent German Wikipedia page to argument
    raises NoPage if there is no German equivalent."""
    pageText = pageObject.get()
    interWikis = getLanguageLinks(pageText)
    try:
        return interWikis[dewp]
    except KeyError:
        raise NoPage
    
def writeToWiki(validatedPage, acStatus, normdatenStatus, writeAttempts):
    """13 case switch that Writes viafnum or reports viafnum conflicts to or about validatedPage.
    Key 
    nd - normdaten; ac - authority control; vl - viaf->wikipedia link number
    (xx) - template does not exist; |xx| - has template but no viaf parameter; |(xx)| -> (xx) or |xx|
    
    1 - |(nd)|, (ac)
        VIAF parameter written.
    2 - |(nd)|, |ac| 
        VIAF parameter written.
    3 - |(nd)|, ac == vl 
        No writing necessary.
    4 - |(nd)|, ac != vl 
        Requires human attention. Nothing written.
    5 - nd , (ac), nd == vl.
        VIAF parameter written.
    6 - nd, (ac), nd != vl.
        Requires human attention. Nothing Written.
    7 - nd, |ac|, nd == vl.
        VIAF parameter written.
    8 - nd, |ac|, nd != vl.
        Requires human attention.
    9 - nd, ac , nd == ac == vl.
        No writing necessary.
    10- nd, ac, nd == ac != vl.
        Requires human attention. Nothing written.
    11- nd, ac, nd != ac, nd == vl.
        Requires human attention. Nothing written.
    12- nd, ac, nd != ac, ac == vl.
        Requires human attention. Nothing written.
    13- nd, ac, nd != ac != vl.
        Requires human attention. Nothing written."""
        
    try:
        if (normdatenStatus == 'noNormdatenTemplate') or (normdatenStatus == 'templateNoVIAF'):
            if acStatus == 'noACtempate':
                #no normdaten template, no ac template
                writeEntireTemplate(validatedPage, viafnum)
                logOnWiki(1,validatedPage)
            elif acStatus == 'templateNoVIAF':
                writeVIAFparamOnly(validatedPage,viafnum)
                logOnWiki(2, validatedPage)
            elif type(acStatus)==int:
                if viafnum == acStatus:
                    logOnWiki(3, validatedPage)
                else:
                    logOnWiki(4, validatedPage)
        elif type(normdatenStatus)==int:
            if acStatus == 'noACtempate':
                if acStatus == normdatenStatus:
                    writeEntireTemplate(validatedPage, viafnum)
                    logOnWiki(5, validatedPage)
                else:
                    logOnWiki(6, validatedPage)
            elif acStatus == 'templateNoVIAF':
                if viafnum == normdatenStatus: #so there is a english template and viafnum agrees with dewp
                    writeVIAFparamOnly(validatedPage,viafnum)
                    logOnWiki(7, validatedPage)
                else:
                    logOnWiki(8, validatedPage)
            elif type(acStatus)==int:
                if acStatus == normdatenStatus:
                    if acStatus == viafnum:
                        logOnWiki(9, validatedPage)
                    else:
                        logOnWiki(10, validatedPage)
                else:
                    if acStatus == viafnum:
                        logOnWiki(11, validatedPage)
                    elif viafnum == normdatenStatus:
                        logOnWiki(12, validatedPage)
                    else:
                        logOnWiki(13, validatedPage)
        else:
            raise Error
    except LockedPage:
        if writeAttempts == 0:
            lockedError = lockedError + 1
        else: pass
        writeAttempts = writeAttempts + 1
        if writeAttempts <= 6:
            writeToWiki(validatedPage, acStatus, normdatenStatus, writeAttempts)
        else:
            Page(enwp,'User:VIAFbot/Errors/Locked').append(timestamp + validatedPage.title(asLink=True) + ' was locked ' , comment='Logging', minorEdit=True, section=0)
    except PageNotSaved:
        if writeAttempts == 0:
            pageNotSavedError = pageNotSavedError + 1
        else: pass
        writeAttempts = writeAttempts + 1
        if writeAttempts <= 6:
            writeToWiki(validatedPage, acStatus, normdatenStatus, writeAttempts)
        else:
        Page(enwp,'User:VIAFbot/Errors/PageNotSaved').append(timestamp + validatedPage.title(asLink=True) + ' generic page not saved' , comment='Logging', minorEdit=True, section=0)
    except EditConflict:
        if writeAttempts == 0:
            editConflictError = editConflictError + 1
        else: pass
        writeAttempts = writeAttempts + 1
        if writeAttempts <= 6:
            writeToWiki(validatedPage, acStatus, normdatenStatus, writeAttempts)
        else:
        Page(enwp,'User:VIAFbot/Errors/EditConflict').append(timestamp + validatedPage.title(asLink=True) + ' edit conflict ' , comment='Logging', minorEdit=True, section=0)
    except SpamfilterError:
        if writeAttempts == 0:
            spamfilterError = spamfilterError + 1
        else: pass
        writeAttempts = writeAttempts + 1
        if writeAttempts <= 6:
            writeToWiki(validatedPage, acStatus, normdatenStatus, writeAttempts)
        else:
        Page(enwp,'User:VIAFbot/Errors/Spamfilter').append(timestamp + validatedPage.title(asLink=True) + ' did not pass spamfilter ' , comment='Logging', minorEdit=True, section=0)
    except LongPageError:
        if writeAttempts == 0:
            longPageError = longPageError + 1
        else: pass
        writeAttempts = writeAttempts + 1
        if writeAttempts <= 6:
            writeToWiki(validatedPage, acStatus, normdatenStatus, writeAttempts)
        else:
        Page(enwp,'User:VIAFbot/Errors/LongPage').append(timestamp + validatedPage.title(asLink=True) + ' page too long error ' , comment='Logging', minorEdit=True, section=0)
 
        
    
def logOnWiki(casenum, validatedPage):
    """
    Key 
    nd - normdaten; ac - authority control; vl - viaf->link number
    (xx) - template does not exist; |xx| - has template but no viaf parameter; |(xx)| -> (xx) or |xx|"""
    timestamp = strftime("%H:%M, %d %B %Y", gmtime())
    try:
        """1 - |(nd)|, (ac)
            VIAF parameter written."""
        if casenum == 1:
            archiveNum = NoDEWP / 100
            Page(enwp,'User:VIAFbot/NoDEWP/' + str(archiveNum)).append(timestamp + validatedPage.title(asLink=True) + ' added VIAF number ' + str(viafnum) , comment='Logging', minorEdit=True, section=0) 
            NoDEWP = NoDEWP + 1
        """2 - |(nd)|, |ac| 
            VIAF parameter written."""
        if casenum == 2:
            archiveNum = NoDEWP / 100
            Page(enwp,'User:VIAFbot/NoDEWP/' + str(archiveNum)).append(timestamp + validatedPage.title(asLink=True) + ' added VIAF number ' + str(viafnum) , comment='Logging', minorEdit=True, section=0) 
            NoDEWP = NoDEWP + 1
        """3 - |(nd)|, ac == vl 
            No writing necessary."""
        if casenum == 3:
            archiveNum = superfluous / 100
            Page(enwp,'User:VIAFbot/Superfluous/' + str(archiveNum)).append(timestamp + validatedPage.title(asLink=True) + str(viafnum) + ' was already added to both enwp and dewp.', comment='Logging', minorEdit=True, section=0) 
            superfluous = superfluous + 1
        """4 - |(nd)|, ac != vl 
            Requires human attention. Nothing written."""
        if casenum == 4:
            archiveNum = conflict4 / 100
            Page(enwp,'User:VIAFbot/Conflict/6/' + str(archiveNum)).append(timestamp + validatedPage.title(asLink=True) + 'Requires human attention: ac != vl . VIAF number: ' + str(viafnum) , comment='Logging', minorEdit=True, section=0) 
            conflict4 = conflict4 + 1
        """5 - nd , (ac), nd == vl.
            VIAF parameter written."""
        if casenum == 5:
            archiveNum = YesDEWP / 100
            Page(enwp,'User:VIAFbot/DEWP/' + str(archiveNum)).append(timestamp + validatedPage.title(asLink=True) + ' added VIAF number ' + str(viafnum) , comment='Logging', minorEdit=True, section=0) 
            YesDEWP = YesDEWP + 1
        """6 - nd, (ac), nd != vl.
            Requires human attention. Nothing Written."""
        if casenum == 6:
            archiveNum = conflict6 / 100
            Page(enwp,'User:VIAFbot/Conflict/6/' + str(archiveNum)).append(timestamp + validatedPage.title(asLink=True) + 'Requires human attention: nd != vl . VIAF number: ' + str(viafnum) , comment='Logging', minorEdit=True, section=0) 
            conflict6 = conflict6 + 1
        """7 - nd, |ac|, nd == vl.
            VIAF parameter written."""
        if casenum == 7:
            archiveNum = YesDEWP / 100
            Page(enwp,'User:VIAFbot/DEWP/' + str(archiveNum)).append(timestamp + validatedPage.title(asLink=True) + ' added VIAF number ' + str(viafnum) , comment='Logging', minorEdit=True, section=0) 
            YesDEWP = YesDEWP + 1
        """8 - nd, |ac|, nd != vl.
            Requires human attention."""
        if casenum == 8:
            archiveNum = conflict8 / 100
            Page(enwp,'User:VIAFbot/Conflict/8/' + str(archiveNum)).append(timestamp + validatedPage.title(asLink=True) + 'Requires human attention: nd != vl . VIAF number: ' + str(viafnum) , comment='Logging', minorEdit=True, section=0) 
            conflict8 = conflict8 + 1
        """9 - nd, ac , nd == ac == vl.
            No writing necessary."""
        if casenum == 9:
            archiveNum = superfluous / 100
            Page(enwp,'User:VIAFbot/Superfluous/' + str(archiveNum)).append(timestamp + validatedPage.title(asLink=True) + str(viafnum) + ' was already added to both enwp and dewp.', comment='Logging', minorEdit=True, section=0) 
            superfluous = superfluous + 1
        """10- nd, ac, nd == ac != vl.
            Requires human attention. Nothing written."""
        if casenum == 10:
            archiveNum = conflict10 / 100
            Page(enwp,'User:VIAFbot/Conflict/10/' + str(archiveNum)).append(timestamp + validatedPage.title(asLink=True) + 'Requires human attention: nd == ac != vl . VIAF number: ' + str(viafnum) , comment='Logging', minorEdit=True, section=0) 
            conflict10 = conflict10 + 1
        """11- nd, ac, nd != ac, nd == vl.
            Requires human attention. Nothing written."""
        if casenum == 11:
            archiveNum = conflict11 / 100
            Page(enwp,'User:VIAFbot/Conflict/11/' + str(archiveNum)).append(timestamp + validatedPage.title(asLink=True) + 'Requires human attention: nd != ac, nd== vl . VIAF number: ' + str(viafnum) , comment='Logging', minorEdit=True, section=0) 
            conflict11 = conflict11 + 1
        """12- nd, ac, nd != ac, ac == vl.
            Requires human attention. Nothing written."""
        if casenum == 12:
            archiveNum = conflict12 / 100
            Page(enwp,'User:VIAFbot/Conflict/12/' + str(archiveNum)).append(timestamp + validatedPage.title(asLink=True) + 'Requires human attention: nd != ac, ac == vl . VIAF number: ' + str(viafnum) , comment='Logging', minorEdit=True, section=0) 
            conflict12 = conflict12 + 1
        """13- nd, ac, nd != ac != vl.
            Requires human attention. Nothing written."""
        if casenum == 13:
            archiveNum = conflict13 / 100
            Page(enwp,'User:VIAFbot/Conflict/13/' + str(archiveNum)).append(timestamp + validatedPage.title(asLink=True) + 'Requires human attention: nd != ac != vl . VIAF number: ' + str(viafnum) , comment='Logging', minorEdit=True, section=0) 
            conflict13 = conflict13 + 1
    except LockedPage:
        raise LockedPage
    except PageNotSaved:
        raise LockedPage
    except EditConflict:
        raise EditConflict
    except SpamfilterError:
        raise SpamfilterError
    except LongPageError:
        raise LongPageError
        
def writeEntireTemplate(validatedPage, viafnum):
    """Uses add_text.py to add the wikitext of
     {{Authority control}} template with the VIAF parameter"""
    ACtemplateWithVIAF = '\n{{Authority control|VIAF=' + str(viafnum) + '}}\n'
    editSummary = 'Added the {{Authority control}} template with VIAF number ' + str(viafnum) + '.'
    add_text(page = validatedPage, 
             addText = ACtemplateWithVIAF, 
             always = True, #so add_text won't ask for confirmation
             summary = editSummary)

def writeVIAFparamOnly(validatedPage,viafnum):
    """Instantiates and runs replace.py's ReplaceRobot class"""
    preloadingGen = [validatedPage]
    replacements = [('{{Authority control' , '{{Authority control|VIAF=' + str(viafnum) + '|')]
    editSummary = 'Adding VIAF parameter to Authority control with VIAF number ' + str(viafnum)
    exceptions = []
    acceptall = True
    allowoverlap = False
    recursive = False
    add_cat = None
    sleep = None
    titlefile = None
    excoutfile = None
    replaceBot = ReplaceRobot(preloadingGen, replacements, exceptions, acceptall,
                       allowoverlap, recursive, add_cat, sleep, editSummary,
                       titlefile, excoutfile)
    replaceBot.run()

