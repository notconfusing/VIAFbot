wikilinks = open("wikilinks.out")
wikilinksforbot = open("wikilinksforbot.out", 'w')  

for line in wikilinks:
    line = line.split('\t',1)  # I like to be explicit here
    name = line[0]
    viafurl = line[1]
    viafnum = viafurl[21:]
    wikilinksforbot.write(name + '\t' + viafnum + '\n')
    
wikilinks.close()
wikilinksforbot.close()
