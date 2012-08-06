#!/usr/bin/python
# -*- coding: utf-8 -*-

# importing modules
# requires that pywikipediabot modules be in your PYTHONPATH
import sys
from wikipedia import *
from add_text import *
 
# global variables
enwp = getSite('en','wikipedia')
dewp = getSite('de','wikipedia')
 



def pageValidator(nameOfPage):
    """returns a string of either a page if it's valid"""
    namepage = Page(enwp, nameOfPage)
    try:
        namepage.get()
    except IsRedirectPage, redirPageName:
        return redirPageName
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

