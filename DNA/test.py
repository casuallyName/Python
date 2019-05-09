DNA_path = './5_UTR.txt'
f=open(DNA_path)
ls=[]
for line in f:
        if not line.startswith('>'):
                ls.append(line.replace('\n',''))#去掉行尾的换行符真的很重要
f.close()
A=C=T=G=0
DNA_str=''
for i in range(0,len(ls)):
        DNA_str += ls[i]
#print(DNA_str)
for i in range(0,len(DNA_str)):
        print(DNA_str[i],end="")
        if i%50==0 and i > 1:
                print("")
print("\n")
A+=DNA_str.count('A')
C+=DNA_str.count('C')
T+=DNA_str.count('T')
G+=DNA_str.count('G')

print("A: %d\nC: %d\nT: %d\nG: %d\n"%(A,C,T,G))
GC = (G + C)/( A + T + C + G)*100
print("G+C:%.2f%%"%GC)
