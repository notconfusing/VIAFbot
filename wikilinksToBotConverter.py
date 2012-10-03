# -*- coding: utf-8 -*-
wikilinks = open("wikilinks.out", 'r')
wikilinksforbot = open("wikilinksforbot.out", 'w+')

for line in wikilinks:
    line = line.split()
    name = line[0]
    viafurl = line[1]
    viafnum = viafurl[21:]
    wikilinksforbot.write(name + '\t' + viafnum + '\n')
    
wikilinks.close()
wikilinksforbot.close() 
