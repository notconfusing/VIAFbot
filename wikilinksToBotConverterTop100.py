# -*- coding: utf-8 -*-
wikilinks = open("wikilinks.out", 'r')
wikilinksforbot = open("wikilinksforbot.out", 'w+')

lines = wikilinks.readlines()

for line in lines:
    line = line.split()
    name = line[0].encode('utf-8')
    viafurl = line[1].encode('utf-8')
    viafnum = viafurl[21:]
        
 #   nameandviafnum = [name, viafnum]
 #   print nameandviafnum.encode('utf-8')
    wikilinksforbot.write(str(name) + '\t' + str(viafnum) + '\n')