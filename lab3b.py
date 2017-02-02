#!/usr/bin/env python
import csv

class Block:
    def __init__(self, number):
        self.number = number
        self.ref_inode_list=[]
        self.ref_indirect_list=[]
    def add_inode_ref(self,ref):
        self.ref_inode_list.append(ref)
    def add_indirect_ref(self,ref):
        self.ref_indirect_list.append(ref)

def present(list_alloc, blocknum,inodenum):
    for alloc_block in list_alloc:
        if blocknum == list_alloc[alloc_block].number:
            if inodenum not in list_alloc[alloc_block].ref_inode_list:
                list_alloc[alloc_block].add_inode_ref(inodenum)
            return 1
    return 0
def presentIndir(list_alloc, blocknum,indirnum):
    for alloc_block in list_alloc:
        if blocknum == list_alloc[alloc_block].number:
             if indirnum not in list_alloc[alloc_block].ref_indirect_list:
                 list_alloc[alloc_block].add_indirect_ref(indirnum)
             return 1
    return 0
class Inode:
    def __init__(self, number,numlinks):
        self.number = number
        self.numlinks=numlinks
        self.ref_list=[]
        self.ptrs=[]
    def add_ref(self,ref):
        self.ref_list.append(ref)
    def add_ptr(self,ptr):
        self.ptrs.append(ptr)

free_inodes=[]
free_blocks=[]
alloc_inodes={}
alloc_blocks={}

totalblocks=0
totalInodes=0

textfile = open("lab3b_check.txt", "w")

f = open('super.csv')
csv_f = csv.reader(f)
for row in csv_f:
    totalInodes=int(row[1])
    totalblocks=int(row[2])

freeInodes=0
freeBlocks=0
blockBitmap=[]
inodeBitmap=[]
inodeBitmapNum=[]

f = open('group.csv')
csv_f = csv.reader(f)
for row in csv_f:
    freeInodes = freeInodes + int(row[2])
    freeBlocks = freeBlocks + int(row[1])
    inodeBitmap.append(row[4])
    inodeBitmapNum.append(int(row[2]))
    blockBitmap.append(row[5])

f = open('bitmap.csv')
csv_f = csv.reader(f)
for row in csv_f:
    if (row[0]) in blockBitmap:
         free_blocks.append(int(row[1]))
    if (row[0]) in inodeBitmap:
        free_inodes.append(int(row[1]))
       

f = open('inode.csv')
csv_f = csv.reader(f)
for row in csv_f:
    a=Inode(int(row[0]),int(row[5]))
    for num in range(11,26):
        a.add_ptr(int(row[num],16))
        alloc_inodes[int(row[0])]=a
    for block in a.ptrs:
        if block!=0:
             if not (present(alloc_blocks,block,a.number)):
                  b = Block(block)
                  b.add_inode_ref(int(row[0]))
                  alloc_blocks[block]=b

directoryTable={}
directoryTable_check=[]
dirCheck=[]
f = open('directory.csv')
csv_f = csv.reader(f)
for row in csv_f:
    if int(row[0]) in directoryTable:
        directoryTable[int(row[0])].append(int(row[4]))
        directoryTable_check.append(int(row[4]))
        if int(row[4]) not in dirCheck:
            dirCheck.append(int(row[4]))
    else:
        directoryTable[int(row[0])]=[int(row[4])]
        directoryTable_check.append(int(row[4]))
        if int(row[4]) not in dirCheck:
            dirCheck.append(int(row[4]))

    if row[5] == '.':
        if row[0] != row[4]:
            print >> textfile, 'INCORRECT ENTRY IN <', row[0], '> NAME < . > LINK TO <', row[4], '> SHOULD BE <', row[0], '>'

f = open('directory.csv')
csv_f = csv.reader(f)
for row in csv_f:
    if row[5] == '..':
        if int(row[4]) not in directoryTable[int(row[4])]:
            correct=0
            for num in directoryTable:
                if int(row[4]) in directoryTable[num]:
                    correct=num
                    break
            print >> textfile, 'INCORRECT ENTRY IN <', row[4], '> NAME < .. > LINK TO <', row[0], '> SHOULD BE <', correct, '>'
            
for num in dirCheck:
    counter=0;
    for index in range(0,len(directoryTable_check)):
        if num == directoryTable_check[index]:
            counter=counter +1
    if num in alloc_inodes:
        if counter != alloc_inodes[num].numlinks:
            print >> textfile, 'LINKCOUNT <', num, '> IS <', alloc_inodes[num].numlinks, '> SHOULD BE <', counter, '>'
            
for entry in directoryTable:
    for entry_child in directoryTable[entry]:
        if entry_child not in alloc_inodes:
            print >> textfile, 'UNALLOCATED INODE <', entry_child, '> REFERENCED BY DIRECTORY <', entry, '> ENTRY <', directoryTable[entry].index(entry_child), '>'

for inode in alloc_inodes:
    if inode > 10 and alloc_inodes[inode].numlinks == 0:
        pre=0
        for num in range(0,len(inodeBitmap)):
            pre = pre + inodeBitmapNum[num]
            if inode <= pre:
                print >> textfile, 'MISSING INODE <', inode, '> SHOULD BE IN FREE LIST <' , inodeBitmap[num], '>'
                break
indirectTable={}
f = open('indirect.csv')
csv_f = csv.reader(f)
for row in csv_f:
    if int(row[0],16) in indirectTable:
        indirectTable[int(row[0],16)].append(int(row[2],16))
        if not present(alloc_blocks,int(row[2],16),int(row[0],16)):
            b=Block(int(row[2],16))
            b.add_indirect_ref(int(row[0],16))
            alloc_blocks[int(row[2],16)]=b
    else:
        indirectTable[int(row[0],16)]=[int(row[2],16)]
        if not present(alloc_blocks,int(row[2],16),int(row[0],16)):
            b=Block(int(row[2],16))
            b.add_indirect_ref(int(row[0],16))
            alloc_blocks[int(row[2],16)]=b


for block in alloc_blocks:
    counter=0
    if alloc_blocks[block].number in free_blocks:
        string = 'UNALLOCATED BLOCK < '
        string += str(alloc_blocks[block].number)
        string += ' > REFERENCED BY '
        #counter = 0
        for inode in alloc_inodes:
            counter=0
            if alloc_blocks[block].number in alloc_inodes[inode].ptrs:
                entrynum= alloc_inodes[inode].ptrs.index(alloc_blocks[block].number)
                string2 = ''
                if counter == 0:
                    counter = 1
                    string2 += string
                string2 += 'INODE < '
                string2 += str(alloc_inodes[inode].number)
                string2 += ' > ENTRY < '
                string2 += str(entrynum)
                string2 += ' >'

            for ptr in alloc_inodes[inode].ptrs:
                if ptr != 0:
                    counter=counter+1
                if ptr in indirectTable:
                    for val in indirectTable[ptr]:
                        counter=counter+1
                        if val in indirectTable:
                            for val1 in indirectTable[val]:
                                counter=counter+1
                                if val1 in indirectTable:
                                    for val2 in indirectTable[val1]:
                                        counter=counter+1
                                        if val2 == alloc_inodes[inode].number:
                                            location= indirectTable[val1].index(val2)
                                            string2 += 'INODE < '
                                            string2 += str(alloc_inodes[inode].number)
                                            string2 += ' > INDIRECT BLOCK < '
                                            string2 += str(val1)
                                            string2 += ' > ENTRY < '
                                            string2 += str(location)
                                            string2 += ' >'
                                            #print("Unallocated block num",val2, "Inode num", alloc_inodes[node].number,
                                            #"block num ", val1,"entry num ", location)
                                #else:
                                    #counter=counter+1
                                if val1 == alloc_inodes[inode].number:
                                    location= indirectTable[val].index(val1)
                                    string2 += 'INODE < '
                                    string2 += str(alloc_inodes[inode].number)
                                    string2 += ' > INDIRECT BLOCK < '
                                    string2 += str(val)                                        
                                    string2 += ' > ENTRY < '
                                    string2 += str(location)
                                    string2 += ' >'
                       # else:
                            #counter=counter+1
                        if val == alloc_inodes[inode].number:
                            location= indirectTable[ptr].index(check)
                            string2 += 'INODE < '
                            string2 += str(alloc_inodes[inode].number)
                            string2 += ' > INDIRECT BLOCK < '
                            string2 += str(ptr)
                            string2 += ' > ENTRY < '
                            string2 += str(location)
                            string2 += ' >'
                #else:
                    #counter=counter+1
            print counter
            counter=0
        print >> textfile, string2
        #print counter
for block in alloc_blocks:
    if (len(alloc_blocks[block].ref_inode_list) + len(alloc_blocks[block].ref_indirect_list) > 1):
        string = 'MULTIPLY REFERENCED BLOCK < '
        string += str(block)
        string += ' > BY'
        for inode in alloc_blocks[block].ref_inode_list:
            entry= alloc_inodes[inode].ptrs.index(block)
            string += ' INODE < '
            string += str(inode)
            string += ' > ENTRY < '
            string += str(entry)
            string += ' >'
        for indir in alloc_blocks[block].ref_indirect_list:
            entry= indirectTable[indir].index(block)
            string += 'INDIRECT BLOCK < '
            string += str(indir)
            string += ' > ENTRY < '
            string += str(entry)
            string += ' >'
        
        print >> textfile, string

f = open('inode.csv')
csv_f = csv.reader(f)
for row in csv_f:
    counter=0
    inodenum = int(row[0])
    iblocks= int(row[10])
    if iblocks >= 12:
        num = 23
    if iblocks >= (255 + 12):
        #print iblocks
        num = 24
    if iblocks > (255*255 + 12):
        
        num = 25
    endrange = 11+iblocks
    for i in range(11,endrange):
        if i > 22 and i <=num:
            counter=counter+1
            if int(row[i],16) == 0 or int(row[i],16) > totalblocks:
                
                print >> textfile, 'INVALID BLOCK <', int(row[i]), '> IN INODE <', int(row[0]), '> INDIRECT BLOCK <', row[i], '> ENTRY <', num, '>'
            else:
                if int(row[i],16) in indirectTable:
                    for val in indirectTable[int(row[i],16)]:
                        counter=counter+1
                        if val in indirectTable:
                            for	val1 in	indirectTable[val]:
                                counter=counter+1
                                if val1	in indirectTable:
                                    for	val2 in	indirectTable[val1]:
                                        counter=counter+1
                                        #print counter
                                        if val2 == 0 or	val2 > totalblocks:
                                            print >> textfile, 'INVALID BLOCK <', val2, '> IN INODE <', row[0], '> INDIRECT BLOCK <', row[i], '> ENTRY <', num, '>'
                                else:
                                    #counter=counter+1
                                    #print counter
                                    if val1 == 0 or val1 > totalblocks:
                                        print >> textfile, 'INVALID BLOCK <', val1, '> IN INODE <', row[0], '> INDIRECT BLOCK <', row[i], '> ENTRY <', num, '>'
                        else:
                            #counter=counter+1
                            #print counter
                            if val == 0 or val > totalblocks:
                                print >> textfile, 'INVALID BLOCK <', val, '> IN INODE <', row[0], '> INDIRECT BLOCK <', row[i], '> ENTRY <', num, '>'
        if i <= 22:
            #print i
            counter= counter + 1
            if int(row[i],16) == 0 or int(row[i],16) > totalblocks:
                print >> textfile, 'INVALID BLOCK <', row[i], '> IN INODE <', row[0], '> ENTRY <', num, '>'
    #print counter
        
