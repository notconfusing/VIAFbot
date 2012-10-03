ntem = open('ntem.out')

templates = ntem.readline().split()

def isinlist():
    for template in templates:
        if template[0][0] == 'Authority control': 
            return 'True'
        else: 
            return 'False' 
    
#print isinlist('authority control')

isinlist()
print templates[0]