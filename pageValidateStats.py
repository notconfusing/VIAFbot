from wikipedia import *

enwp = getSite('en','wikipedia')
same = 0
total = 0
nopage = 0
wikilinks = open("wikilinksforbot.out")
wikilinks = wikilinks.readlines()
linkvalidity = open('linkvalidity.html', 'w+')
linkvalidity.write('<html>')



def pageValidator(nameOfPage): #TODO handle mutliple redirects
    """returns a string of either the page or it's redirect (does not check double redirects).  
    Or returns None if the page does not exist"""
    namepage = Page(enwp, nameOfPage)
    try:
        namepage.get()
    except IsRedirectPage, redirPageName:
        return redirPageName
    except NoPage:
        return None
    else:
        return nameOfPage
    

for wikilink in wikilinks:
    wikilink = wikilink.split() #to get the line into a list of (name, viafnum)
    origNameOfPage = wikilink[0]
    afternameOfPage = pageValidator(origNameOfPage)
    total = total +1
    if afternameOfPage == None:
        nopage= nopage +1
        linkvalidity.write( str(origNameOfPage) + " viafnum of " + str(wikilink[1]) + " does not exists \n" + '<br>')
    elif origNameOfPage == afternameOfPage:
        same = same +1
    else:
        linkvalidity.write('<a href="http://en.wikipedia.org/wiki/' + origNameOfPage + '">' 
                           + " viafnum of " + str(wikilink[1])+
                           origNameOfPage + '</a>' + "is a redirect \n" + '<br>')
    if (total % 100) == 0:
        linkvalidity.write('Checked ' + str(total) + " records total so far " +
                          str((total - same - nopage)) + " were redirects, " +
                          str(nopage) + " were links that no longer exist. \n" + '<br>')
    else:
        pass


linkvalidity.write('</html>')
linkvalidity.close()
wikilinks.close()
