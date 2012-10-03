lsfile = open('linkvalidity.html')
redirectfile = open('redirects.out', 'w+')
dnefile = open('dne.out', 'w+')

ls = lsfile.readlines()

redirect = 0
dne = 0

for l in ls:
    m = l.split()  
    if m[-1] == 'redirect':
        redirect = redirect + 1
        redirectfile.write(l)
    elif m[-1] == 'exists':
        dne = dne + 1
        dnefile.write(l[4:])
    
    
redirectfile.write('total redirects ' + str(redirect))
dnefile.write('total does not exists ' + str(dne))

redirectfile.close()
dnefile.close()
