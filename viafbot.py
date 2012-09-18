#!/usr/bin/python
# -*- coding: utf-8 -*-
# CC-BY-SA Max Klein and OCLC Research
# importing modules
# requires that pywikipediabot modules be in your PYTHONPATH
import wikipedia
import pywikibot.exceptions as exceptions
import pywikibot.textlib as textlib
import add_text_customised#for method writeEntireTemplate
#if using writeVIAFparamOnly not writeVIAFparamOnly2: 
from time import gmtime, strftime #for timestamping

 
#wikipedia site  variables
enwp = wikipedia.getSite('en','wikipedia')
dewp = wikipedia.getSite('de','wikipedia')
#files
wikilinksfile = open("35linksfortrial.out")#should be wikilinksforbot.out when real
wikilinks = wikilinksfile.readlines()
viafbotrun = open("viafbotrun.log", 'w+')
NoDEWPlog = open("NoDEWP.log", 'w+')
YesDEWPlog = open("YesDEWP.log", 'w+')
conflict4log = open("conflict4.log", 'w+')
conflict6log = open("conflict6.log", 'w+')
conflict8log = open("conflict8.log", 'w+')
conflict10log = open("conflict10.log", 'w+')
conflict11log = open("conflict11.log", 'w+')
conflict12log = open("conflict12.log", 'w+')
conflict13log = open("conflict13.log", 'w+')
superfluouslog = open("superfluous.log", 'w+')
lockedErrorlog = open("lockedError.log", 'w+') 
editConflictErrorlog = open("editConflictError.log", 'w+')
pageNotSavedErrorlog = open("pageNotSavedError.log", 'w+')
spamfilterErrorlog = open("spamfilterError.log", 'w+')
longPageErrorlog = open("longPageError.log", 'w+')
#global stats
touched = 0
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
noACtemplateCount = 0
noNormdatenTemplatecount = 0
ACtemplateNoVIAFcount = 0
normdatenTemplateNoVIAFcount = 0
ACVIAFcount = 0
normdatenVIAFcount = 0
                           
    #close resources
wikilinksfile.close()





def pageValidate(nameOfPage):
    """accepts string of page name in EnglishWikipedia. 
    returns a Page Object of either the page or it's redirect (upto 10 redirects).
    raises NoPage exception if the page does not exist"""
    possiblePage = wikipedia.Page(enwp,nameOfPage)
    for i in range(1,10):
        try:
            possiblePage.get()
            return possiblePage
        except exceptions.IsRedirectPage, redirPageName:
            possiblePage = wikipedia.Page(enwp,str(redirPageName))
        except exceptions.NoPage:
            raise exceptions.NoPage
        
def determineAuthorityControlTemplate(pageObject):
    """returns 'noACtemplate' if no Authority Control Template, 'templateNoVIAF' if AC template but no VIAF number, 
    and returns the viaf number if it exists as type int"""
    global noACtemplateCount
    global ACtemplateNoVIAFcount
    global ACVIAFcount
    templates = pageObject.templatesWithParams()
    for template in templates:
        if template[0] == 'Authority control':
            for param in template[1]:
                if param[:4] == 'VIAF':
                    ACVIAFcount = ACVIAFcount + 1
                    try:
                        templateVIAFnum = int(param[5:])
                    except ValueError:
                        viafbotrun.write(pageObject.title() + 'had an non-numerical VIAFnumber \n')
                        templateVIAFnum = -1 #this will cause viafbot to report a conflict and it is an invalid viafnumber
                    return templateVIAFnum
            ACtemplateNoVIAFcount = ACtemplateNoVIAFcount + 1 
            return 'templateNoVIAF'
    noACtemplateCount = noACtemplateCount + 1
    return 'noACtemplate'

def determineNormdatenTemplate(pageObject):
    """returns 'noNormdatenTemplate' if no Normdaten Template, 'templateNoVIAF'sss if Normdaten template but no VIAF number, 
    and returns the viaf number if it exists as type int"""
    global noNormdatenTemplatecount
    global normdatenTemplateNoVIAFcount
    global normdatenVIAFcount 
    templates = pageObject.templatesWithParams()
    for template in templates:
        if template[0] == 'Normdaten':
            for param in template[1]:
                if param[:4] == 'VIAF':
                    normdatenVIAFcount = normdatenVIAFcount + 1
                    try:
                        templateVIAFnum = int(param[5:])
                    except ValueError:
                        viafbotrun.write(pageObject.title() + 'had an non-numerical VIAFnumber\n')
                        templateVIAFnum = 'templateNoVIAF'
                    return templateVIAFnum
            normdatenTemplateNoVIAFcount = normdatenTemplateNoVIAFcount + 1
            return 'templateNoVIAF'
    noNormdatenTemplatecount = noNormdatenTemplatecount + 1
    return 'noNormdatenTemplate'

def getGermanName(pageObject):
    """returns a Page object which is the equivalent German Wikipedia page to argument
    raises NoPage if there is no German equivalent."""
    pageText = pageObject.get()
    interWikis = textlib.getLanguageLinks(pageText)
    try:
        return interWikis[dewp]
    except KeyError:
        raise exceptions.NoPage
    
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
    timestamp = strftime("%H:%M, %d %B %Y", gmtime())
    global lockedError
    global editConflictError
    global pageNotSavedError
    global spamfilterError
    global longPageError
  
    try:
        if (normdatenStatus == 'noNormdatenTemplate') or (normdatenStatus == 'templateNoVIAF'):
            if acStatus == 'noACtemplate':
                writeEntireTemplate(validatedPage, viafnum)
                logOnWiki(1,validatedPage, viafnum)
            elif acStatus == 'templateNoVIAF':
                writeVIAFparamOnly2(validatedPage,viafnum)
                logOnWiki(2, validatedPage, viafnum)
            elif type(acStatus)==int:
                if acStatus == viafnum:
                    logOnWiki(3, validatedPage, viafnum)
                else:
                    logOnWiki(4, validatedPage, viafnum)
        elif type(normdatenStatus)==int:
            if acStatus == 'noACtemplate':
                if normdatenStatus == viafnum:
                    writeEntireTemplate(validatedPage, viafnum)
                    logOnWiki(5, validatedPage, viafnum)
                else:
                    logOnWiki(6, validatedPage, viafnum)
            elif acStatus == 'templateNoVIAF':
                if normdatenStatus == viafnum: #so there is a english template and viafnum agrees with dewp
                    writeVIAFparamOnly2(validatedPage,viafnum)
                    logOnWiki(7, validatedPage, viafnum)
                else:
                    logOnWiki(8, validatedPage, viafnum)
            elif type(acStatus)==int:
                if acStatus == normdatenStatus:
                    if acStatus == viafnum:
                        logOnWiki(9, validatedPage, viafnum)
                    else:
                        logOnWiki(10, validatedPage, viafnum)
                else:
                    if normdatenStatus == viafnum:
                        logOnWiki(11, validatedPage, viafnum)
                    elif acStatus == viafnum:
                        logOnWiki(12, validatedPage, viafnum)
                    else:
                        logOnWiki(13, validatedPage, viafnum)
        else:
            raise exceptions.Error
        #exceptions raised while trying to write 
    except exceptions.LockedPage:
        if writeAttempts == 0:
            lockedError = lockedError + 1
        else: pass
        writeAttempts = writeAttempts + 1
        if writeAttempts <= 6:
            writeToWiki(validatedPage, acStatus, normdatenStatus, writeAttempts)
        else:
            lockedErrorlog.write('* ' + timestamp + ' . ' + validatedPage.title(asLink=True) + ' was locked.\n' )
            if lockedError % 100 == 99:
                wikipedia.Page(enwp,'User:VIAFbot/Errors/Locked').append(last100LogLinesAsString(lockedErrorlog), comment='Logging', minorEdit=True, section=0)
            else: pass

    except exceptions.PageNotSaved:
        if writeAttempts == 0:
            pageNotSavedError = pageNotSavedError + 1
        else: pass
        writeAttempts = writeAttempts + 1
        if writeAttempts <= 6:
            writeToWiki(validatedPage, acStatus, normdatenStatus, writeAttempts)
        else:
            pageNotSavedErrorlog.write('* ' + timestamp + ' . ' + validatedPage.title(asLink=True) + ' generic page not saved.\n' )
            if pageNotSavedError % 100 == 99:
                wikipedia.Page(enwp,'User:VIAFbot/Errors/PageNotSaved').append(last100LogLinesAsString(pageNotSavedErrorlog), comment='Logging', minorEdit=True, section=0)
            else: pass            
 
    except exceptions.EditConflict:
        if writeAttempts == 0:
            editConflictError = editConflictError + 1
        else: pass
        writeAttempts = writeAttempts + 1
        if writeAttempts <= 6:
            writeToWiki(validatedPage, acStatus, normdatenStatus, writeAttempts)
        else:
            editConflictErrorlog.write('* ' + timestamp + ' . ' + validatedPage.title(asLink=True) + ' editconflict.\n')
            if editConflictError % 100 == 99:
                wikipedia.Page(enwp,'User:VIAFbot/Errors/EditConflict').append(last100LogLinesAsString(editConflictErrorlog), comment='Logging', minorEdit=True, section=0)
            else: pass
            
    except exceptions.SpamfilterError:
        if writeAttempts == 0:
            spamfilterError = spamfilterError + 1
        else: pass
        writeAttempts = writeAttempts + 1
        if writeAttempts <= 6:
            writeToWiki(validatedPage, acStatus, normdatenStatus, writeAttempts)
        else:
            spamfilterErrorlog.write('* ' + timestamp + ' . ' + validatedPage.title(asLink=True) + ' did not pass spamfilter.\n')
            if spamfilterError % 100 == 99:
                wikipedia.Page(enwp,'User:VIAFbot/Errors/Spamfilter').append(last100LogLinesAsString(spamfilterErrorlog), comment='Logging', minorEdit=True, section=0)
            else: pass

    except exceptions.LongPageError:
        if writeAttempts == 0:
            longPageError = longPageError + 1
        else: pass
        writeAttempts = writeAttempts + 1
        if writeAttempts <= 6:
            writeToWiki(validatedPage, acStatus, normdatenStatus, writeAttempts)
        else:
            longPageErrorlog.write('* ' + timestamp + ' . ' + validatedPage.title(asLink=True) + ' page too long error.\n')
            if longPageError % 100 == 99:
                wikipedia.Page(enwp,'User:VIAFbot/Errors/LongPage').append(last100LogLinesAsString(longPageErrorlog), comment='Logging', minorEdit=True, section=0)
            else: pass            
 
    
def logOnWiki(casenum, validatedPage, viafnum):
    """
    Key 
    nd - normdaten; ac - authority control; vl - viaf->link number
    (xx) - template does not exist; |xx| - has template but no viaf parameter; |(xx)| -> (xx) or |xx|"""
    timestamp = strftime("%H:%M, %d %B %Y", gmtime())
    global NoDEWP
    global YesDEWP
    global conflict4
    global conflict6
    global conflict8
    global conflict10
    global conflict11
    global conflict12
    global conflict13
    global superfluous
    try:
        """1 - |(nd)|, (ac)
            VIAF parameter written."""
        if casenum == 1:
            NoDEWP += 1
            NoDEWPlog.write('* ' + timestamp + " . " + validatedPage.title(asLink=True) + ' added VIAF number ' + str(viafnum)+ '\n')
            if NoDEWP % 100 == 99:
                archiveNum = NoDEWP / 100
                wikipedia.Page(enwp,'User:VIAFbot/NoDEWP/' + str(archiveNum)).append( last100LogLinesAsString(NoDEWPlog) , comment='Logging', minorEdit=True, section=0) 
            else: pass
        """2 - |(nd)|, |ac| 
            VIAF parameter written."""
        if casenum == 2:
            NoDEWP += 1
            NoDEWPlog.write('* ' + timestamp + " . " + validatedPage.title(asLink=True) + ' added VIAF number ' + str(viafnum)+ '\n')
            if NoDEWP % 100 == 99:
                archiveNum = NoDEWP / 100
                wikipedia.Page(enwp,'User:VIAFbot/NoDEWP/' + str(archiveNum)).append( last100LogLinesAsString(NoDEWPlog) , comment='Logging', minorEdit=True, section=0) 
            else: pass
        """3 - |(nd)|, ac == vl 
            No writing necessary."""
        if casenum == 3:
            superfluous += 1
            superfluouslog.write('* ' + timestamp + ' . ' + validatedPage.title(asLink=True) + ' ' + str(viafnum) + ' was already added to both enwp and dewp.\n')
            if superfluous % 100 == 99:
                archiveNum = superfluous / 100
                wikipedia.Page(enwp,'User:VIAFbot/Superfluous/' + str(archiveNum)).append( last100LogLinesAsString(superfluouslog), comment='Logging', minorEdit=True, section=0) 
            else: pass
        """4 - |(nd)|, ac != vl 
            requires human attention. Nothing written."""
        if casenum == 4:
            conflict4 += 1
            conflict4log.write('* ' + timestamp + ' . ' + validatedPage.title(asLink=True) + ' requires human attention: ac != vl . VIAF number: \n' + str(viafnum))
            if conflict4 % 100 == 99:
                archiveNum =  conflict4 / 100
                wikipedia.Page(enwp,'User:VIAFbot/Conflict/4/' + str(archiveNum)).append(last100LogLinesAsString(conflict4log), comment='Logging', minorEdit=True, section=0) 
            else: pass
        """5 - nd , (ac), nd == vl.
            VIAF parameter written."""
        if casenum == 5:
            YesDEWP += 1
            YesDEWPlog.write('* ' + timestamp + " . " + validatedPage.title(asLink=True) + ' added VIAF number ' + str(viafnum)+ '\n')
            if YesDEWP % 100 == 99:
                archiveNum = YesDEWP / 100
                wikipedia.Page(enwp,'User:VIAFbot/YesDEWP/' + str(archiveNum)).append( last100LogLinesAsString(YesDEWPlog) , comment='Logging', minorEdit=True, section=0) 
            else: pass        
        """6 - nd, (ac), nd != vl.
            requires human attention. Nothing Written."""
        if casenum == 6:
            conflict6 += 1
            conflict6log.write('* ' + timestamp + ' . ' + validatedPage.title(asLink=True) + ' requires human attention: nd != vl . VIAF number: \n' + str(viafnum))
            if conflict6 % 100 == 99:
                archiveNum =  conflict6 / 100
                wikipedia.Page(enwp,'User:VIAFbot/Conflict/6/' + str(archiveNum)).append(last100LogLinesAsString(conflict6log), comment='Logging', minorEdit=True, section=0) 
            else: pass
        """7 - nd, |ac|, nd == vl.
            VIAF parameter written."""
        if casenum == 7:
            YesDEWP += 1
            YesDEWPlog.write('* ' + timestamp + " . " + validatedPage.title(asLink=True) + ' added VIAF number ' + str(viafnum)+ '\n')
            if YesDEWP % 100 == 99:
                archiveNum = YesDEWP / 100
                wikipedia.Page(enwp,'User:VIAFbot/YesDEWP/' + str(archiveNum)).append( last100LogLinesAsString(YesDEWPlog) , comment='Logging', minorEdit=True, section=0) 
            else: pass
        """8 - nd, |ac|, nd != vl.
            requires human attention."""
        if casenum == 8:
            conflict8 += 1
            conflict8log.write('* ' + timestamp + ' . ' + validatedPage.title(asLink=True) + ' requires human attention: nd != vl . VIAF number: \n' + str(viafnum))
            if conflict8 % 100 == 99:
                archiveNum =  conflict8 / 100
                wikipedia.Page(enwp,'User:VIAFbot/Conflict/8/' + str(archiveNum)).append(last100LogLinesAsString(conflict8log), comment='Logging', minorEdit=True, section=0) 
            else: pass
        """9 - nd, ac , nd == ac == vl.
            No writing necessary."""
        if casenum == 9:
            superfluous += 1
            superfluouslog.write('* ' + timestamp + ' . ' + validatedPage.title(asLink=True) + ' ' + str(viafnum) + ' was already added to both enwp and dewp.\n')
            if superfluous % 100 == 99:
                archiveNum = superfluous / 100
                wikipedia.Page(enwp,'User:VIAFbot/Superfluous/' + str(archiveNum)).append( last100LogLinesAsString(superfluouslog), comment='Logging', minorEdit=True, section=0) 
            else: pass
        """10- nd, ac, nd == ac != vl.
            requires human attention. Nothing written."""
        if casenum == 10:
            conflict10 += 1
            conflict10log.write('* ' + timestamp + ' . ' + validatedPage.title(asLink=True) + ' requires human attention: nd == ac != vl . VIAF number: \n' + str(viafnum))
            if conflict10 % 100 == 99:
                archiveNum =  conflict10 / 100
                wikipedia.Page(enwp,'User:VIAFbot/Conflict/10/' + str(archiveNum)).append(last100LogLinesAsString(conflict10log), comment='Logging', minorEdit=True, section=0) 
            else: pass
        """11- nd, ac, nd != ac, nd == vl.
            requires human attention. Nothing written."""
        if casenum == 11:
            conflict11 += 1
            conflict11log.write('* ' + timestamp + ' . ' + validatedPage.title(asLink=True) + ' requires human attention: nd != ac, nd == vl . VIAF number: \n' + str(viafnum))
            if conflict11 % 100 == 99:
                archiveNum =  conflict11 / 100
                wikipedia.Page(enwp,'User:VIAFbot/Conflict/11/' + str(archiveNum)).append(last100LogLinesAsString(conflict11log), comment='Logging', minorEdit=True, section=0) 
            else: pass
        """12- nd, ac, nd != ac, ac == vl.
            requires human attention. Nothing written."""
        if casenum == 12:
            conflict12 += 1
            conflict12log.write('* ' + timestamp + ' . ' + validatedPage.title(asLink=True) + ' requires human attention: nd != ac, ac == vl . VIAF number: \n' + str(viafnum))
            if conflict12 % 100 == 99:
                archiveNum =  conflict12 / 100
                wikipedia.Page(enwp,'User:VIAFbot/Conflict/12/' + str(archiveNum)).append(last100LogLinesAsString(conflict12log), comment='Logging', minorEdit=True, section=0) 
            else: pass
        """13- nd, ac, nd != ac != vl.
            requires human attention. Nothing written."""
        if casenum == 13:
            conflict13 += 1
            conflict13log.write('* ' + timestamp + ' . ' + validatedPage.title(asLink=True) + ' requires human attention: nd != ac != vl . VIAF number: \n' + str(viafnum))
            if conflict13 % 100 == 99:
                archiveNum =  conflict13 / 100
                wikipedia.Page(enwp,'User:VIAFbot/Conflict/13/' + str(archiveNum)).append(last100LogLinesAsString(conflict13log), comment='Logging', minorEdit=True, section=0) 
            else: pass
    except exceptions.LockedPage:
        viafbotrun.write(timestamp + ' http://en.wikipedia.org/wiki/' +  validatedPage.title() + ' log page gave locked page error \n')
    except exceptions.PageNotSaved:
        viafbotrun.write(timestamp + ' http://en.wikipedia.org/wiki/' +  validatedPage.title() + ' log page gave page not saved error \n')
    except exceptions.EditConflict:
        viafbotrun.write(timestamp + ' http://en.wikipedia.org/wiki/' +  validatedPage.title() + ' log page gave gave edit conflict error \n')
    except exceptions.SpamfilterError:
        viafbotrun.write(timestamp + ' http://en.wikipedia.org/wiki/' +  validatedPage.title() + ' log page gave spam filter error \n')
    except exceptions.LongPageError:
        viafbotrun.write(timestamp + ' http://en.wikipedia.org/wiki/' +  validatedPage.title() + ' log page gave long page error \n')
    
def last100LogLinesAsString(logfile):
    """Retruns the last 100 (or remainder if log has less than 100 lines) of a log as string"""
    wikitext = ''
    loglist = logfile.readlines()
    if len(loglist) < 100:
        pass
    else:
        loglist = loglist [-100:]
        print
    for i in range(0,len(loglist)):
        wikitext += loglist[i]
    return wikitext

    
        
def writeEntireTemplate(validatedPage, viafnum):
    """Uses add_text.py to add the wikitext of
     {{Authority control}} template with the VIAF parameter"""
    ACtemplateWithVIAF = '\n{{Authority control|VIAF=' + str(viafnum) + '}}\n'
    editSummary = 'Added the {{[[Template:Authority control|Authority control]]}} template with VIAF number ' + str(viafnum) + '.'
    try:
        add_text_customised.add_text(page = validatedPage, 
             addText = ACtemplateWithVIAF, 
             always = True, #so add_text won't ask for confirmation
             summary = editSummary)
    except exceptions.LockedPage:
        raise exceptions.LockedPage
    except exceptions.EditConflict:
        raise exceptions.EditConflict
    except exceptions.ServerError:
        viafbotrun.write("writeEntireTemplate on page " + 'http://en.wikipedia.org/wiki/' +  validatedPage.title() + ' gave generic server error.\n')
    except exceptions.SpamfilterError:
        raise exceptions.SpamfilterError
    except exceptions.PageNotSaved:
        raise exceptions.PageNotSaved       



def writeVIAFparamOnly2(validatedPage,viafnum):
    """Uses the textlib method replaceExcept"""

    pageWikiText = validatedPage.get()

    replacementText = textlib.replaceExcept(pageWikiText, '{{Authority control' , '{{Authority control|VIAF=' + str(viafnum), exceptions=[], caseInsensitive=False,
                  allowoverlap=False, marker = '', site = enwp)

    try:
        validatedPage.put(newtext = replacementText, comment = 'Added VIAF number ' + str(viafnum) + ' to {{[[Template:Authority control|Authority control]]}} template.', watchArticle = False , minorEdit=True, force=False, sysop=False, botflag=True, maxTries = 5)
    except exceptions.LockedPage:
        raise exceptions.LockedPage
    except exceptions.EditConflict:
        raise exceptions.EditConflict
    except exceptions.ServerError:
        viafbotrun.write("writeEntireTemplate on page " + 'http://en.wikipedia.org/wiki/' +  validatedPage.title() + ' gave generic server error.\n')
    except exceptions.SpamfilterError:
        raise exceptions.SpamfilterError
    except exceptions.PageNotSaved:
        raise exceptions.PageNotSaved     
def writeStats():
    wikipedia.Page(enwp,'User:VIAFbot/Stats').put(
        '{| class="wikitable"\n\
        |-\n\
        | Pages VIAF bot has touched || '+str(touched)+'\n\
        |-\n\
        | Page redirects detected|| '+str(totalRedirects)+'\n\
        |-\n\
        | Page deletions detected|| '+str(nopage)+'\n\
        |-\n\
        | Pages for which German Wikipedia has no VIAF data|| '+str(NoDEWP)+'\n\
        |-\n\
        | Pages for which German Wikipedia had VIAF data that agreed with viaf.org || '+str(YesDEWP)+'\n\
        |-\n\
        | [[User:VIAFbot/Conflicts|Conflict type 4]] || '+str(conflict4)+'\n\
        |-\n\
        | [[User:VIAFbot/Conflicts|Conflict type 6]] || '+str(conflict6)+'\n\
        |-\n\
        | [[User:VIAFbot/Conflicts|Conflict type 8]] || '+str(conflict8)+'\n\
        |-\n\
        | [[User:VIAFbot/Conflicts|Conflict type 10]] || '+str(conflict10)+'\n\
        |-\n\
        | [[User:VIAFbot/Conflicts|Conflict type 11]] || '+str(conflict11)+'\n\
        |-\n\
        | [[User:VIAFbot/Conflicts|Conflict type 12]] || '+str(conflict12)+'\n\
        |-\n\
        | [[User:VIAFbot/Conflicts|Conflict type 13]] || '+str(conflict13)+'\n\
        |-\n\
        | Pages for which humans had already put in all correct VIAF data|| '+str(superfluous)+'\n\
        |-\n\
        | [[User:VIAFbot/Errors/Locked|Pages that VIAFbot tried to edit but were locked]] || '+str(lockedError)+'\n\
        |-\n\
        | [[User:VIAFbot/Errors/EditConflict|Pages that VIAFbot tried to edit but resulted in edit conflicts]] || '+str(editConflictError)+'\n\
        |-\n\
        | [[User:VIAFbot/Errors/PageNotSaved|Pages that could not be saved for other reasons]] || '+str(pageNotSavedError)+'\n\
        |-\n\
        | [[User:VIAFbot/Errors/Spamfilter|Pages that VIAFbot tried to edit but were detected as spam]] || '+str(spamfilterError)+'\n\
        |-\n\
        | [[User:VIAFbot/Errors/LongPage|Pages that VIAFbot tried to edit but were over the maximum page length]] || '+str(longPageError)+'\n\
        |-\n\
        | Pages which VIAFbot touched but had no {{tl|Authority control}} || '+str(noACtemplateCount)+'\n\
        |-\n\
        | Pages which VIAFbot touched but had no Normdaten template || '+str(noNormdatenTemplatecount)+'\n\
        |-\n\
        | Pages which VIAFbot touched had {{tl|Authority control}}, but no VIAF parameter || '+str(ACtemplateNoVIAFcount)+'\n\
        |-\n\
        | Pages which VIAFbot touched had Normdaten template but no VIAF parameter || '+str(normdatenTemplateNoVIAFcount)+'\n\
        |-\n\
        | Pages which VIAFbot touched that already had {{tl|Authority control}} with VIAF parameter || '+str(ACVIAFcount)+'\n\
        |-\n\
        | Pages which VIAFbot touched that already had Normdaten template with VIAF parameter|| '+str(normdatenVIAFcount)+'\n\
        |}', 
        comment='Updating Stats', minorEdit=True)    
        
#the main loop
for wikilink in wikilinks:
    '''Load the article and number from file'''
    wikilink = wikilink.split() #to get the line into a list of (name, viafnum)
    unvalidatedPageName = wikilink[0]
    viafnum = int(wikilink[1])
    touched = touched + 1
    '''Find redirects or deletions, after all this file could be 6 months oout of date'''
    try:
        validatedPage = pageValidate(unvalidatedPageName) #It's possible that the page doesn't exist
    except exceptions.NoPage:
        viafbotrun.write(unvalidatedPageName.title() + "did not exist, or redirected more than 10 times")
        continue  #If the page doesn't exist, then we don't need to write anything to the Wiki.
    '''get statuses of Authority Control and Normdaten templates'''
    acStatus = determineAuthorityControlTemplate(validatedPage)
    try:
        germanPageName = getGermanName(validatedPage)
    except exceptions.NoPage: #There was no German equivalent page
        germanPageName = None
    if germanPageName: #Only need to get NormdatenStaus if a German equivalent page exists.
        normdatenStatus = determineNormdatenTemplate(germanPageName)
    else:
        normdatenStatus = 'noNormdatenTemplate' #if there's no page there's also noACtemplate either 
    '''Write the viafnumber according to what we found from DEWP''' 
    try:
        writeToWiki(validatedPage, acStatus, normdatenStatus, viafnum, writeAttempts=0)
    except exceptions.Error:
        viafbotrun.write('http://en.wikipedia.org/wiki/' +  validatedPage.title() + " was not written to wiki because of ac and nd status were not valid")#write to log
    '''Write statistics onwiki every so often'''
    if (touched % 1000) == 0:
        writeStats()
    else: pass

#close files
wikilinksfile.close()
viafbotrun.close()
NoDEWPlog.close()
YesDEWPlog.close()
conflict4log.close()
conflict6log.close()
conflict8log.close()
conflict10log.close()
conflict11log.close()
conflict12log.close()
conflict13log.close()
superfluouslog.close()
lockedErrorlog.close()
editConflictErrorlog.close()
pageNotSavedErrorlog.close()
spamfilterErrorlog.close()
longPageErrorlog.close()
