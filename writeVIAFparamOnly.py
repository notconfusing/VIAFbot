from replace_customised import *
def writeVIAFparamOnly(validatedPage,viafnum):
    """Instantiates and runs replace.py's ReplaceRobot class"""
    global lockedError
    global editConflictError
    global spamfilterError
    global pageNotSavedError
    timestamp = strftime("%H:%M, %d %B %Y", gmtime())
    preloadingGen = [validatedPage]
    replacements = [('{{Authority control' , '{{Authority control|VIAF=' + str(viafnum))]
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
    try:
        replaceBot.run()
    except exceptions.LockedPage:
        lockedError += 1
        wikipedia.Page(enwp,'User:VIAFbot/Errors/Locked').append('\n\n' + timestamp + ' ' + validatedPage.title(asLink=True) + ' was locked when VIAFbot tried to edit it', comment='Logging', minorEdit=True, section=0)
    except exceptions.EditConflict:
        editConflictError += 1
        wikipedia.Page(enwp,'User:VIAFbot/Errors/EditConflict').append('\n\n' + timestamp + ' ' + validatedPage.title(asLink=True) + ' involved in an edit conflict when VIAFbot tried to edit it', comment='Logging', minorEdit=True, section=0)
    except exceptions.ServerError:
        pass
    except exceptions.SpamfilterError:
        spamfilterError += 1
        wikipedia.Page(enwp,'Creating User:VIAFbot/Errors/Spamfilter').append('\n\n' + timestamp + ' ' + validatedPage.title(asLink=True) + ' was detected as a spam edit', comment='Logging', minorEdit=True, section=0)
    except exceptions.PageNotSaved:
        pageNotSavedError +=1
        wikipedia.Page(enwp,'User:VIAFbot/Errors/PageNotSaved').append('\n\n' + timestamp + ' ' + validatedPage.title(asLink=True) + ' was not saved for some reason that is not editconflict, spam or locked', comment='Logging', minorEdit=True, section=0)