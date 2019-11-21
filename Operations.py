# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 16:21:08 2019

@author: Daan
"""

#import matplotlib.pyplot as plt
import numpy as np
from OOFunc import generateRunFiles,Flight,Airline,Gate,Terminal,todo
import xml.etree.ElementTree as ET

#Terminal(name,openEvening,distance)
t1 = Terminal("A",True,250)
t2 = Terminal("B",True,610)
t3 = Terminal("C",False,460)
t4 = Terminal("D",False,100)

#Gate(terminal,domesticFlight,distanceToTerminal)
g1 = Gate(t1,True,100)
g2 = Gate(t1,True,100)
g3 = Gate(t1,False,300)
g4 = Gate(t1,False,300)

g5 = Gate(t2,False,100)
g6 = Gate(t2,False,400)
g7 = Gate(t2,False,700)

g8 = Gate(t3,False,100)
g9 = Gate(t3,False,400)
g10 = Gate(t3,False,700)

g11 = Gate(t4,False,80)
g12 = Gate(t4,False,380)

#Airliner(name,gatePref)
AirFrance   = Airline("AirFrance",g5)
KLM = Airline("KLM",g8)
Delta = Airline("Delta",g11)
BritishAirways=Airline("British Airways",0)
Transavia=Airline("Transavia",0)
EasyJet = Airline("EasyJet",0)

#Flight(identifier,passengers,arrivalTime,departureTime,formFactor,airliner)
fl1 = Flight("JFK23", 250, "5:15pm","7pm","A",KLM)
fl2 = Flight("JFK24", 255, "5:25pm","6:35pm","B",EasyJet)
fl3 = Flight("JFK26", 255, "5:55pm", "7:05pm","C",Delta)
fl4 = Flight("JFK27", 300, "6:05pm", "7:10pm","D",BritishAirways)
fl5 = Flight("JFK28", 255, "6:15pm", "7:15pm","A",Transavia)
fl6 = Flight("JFK29", 20, "6:25pm", "7:20pm","D",Transavia)
fl7 = Flight("JFK30", 255, "6:30pm", "7:30pm","C",AirFrance)
fl8 = Flight("JFK31", 255, "6:35pm", "7:45pm","A",Transavia)
fl9 = Flight("JFK32", 255, "6:50pm", "8:10pm","B",KLM)
fl10 = Flight("JFK33", 255, "6:50pm", "8:25pm","D",KLM)
fl11 = Flight("JFK34", 255, "7:05pm", "8:45pm","B",KLM)
fl12 = Flight("JFK35", 255, "7:15pm", "8:55pm","C",KLM)
fl13 = Flight("JFK36", 255, "7:30pm", "9:05pm","A",Transavia)
fl14 = Flight("JFK37", 255, "7:45pm", "9:20pm","C",BritishAirways)
fl15 = Flight("JFK38", 255, "8:15pm", "10:05pm","B",EasyJet)


timemat = np.zeros((len(Flight._registry),len(Flight._registry))) #Generating time overlap matrix
i = 0
for fl in Flight._registry:
    j = 0
    for fl2 in Flight._registry:
        overlap = int(fl.timeSlotEndBuffer) - int(fl2.timeSlotBeginBuffer)
        if overlap >= 0 and int(fl2.timeSlotEndBuffer) > int(fl.timeSlotBeginBuffer):
            timemat[i][j] = 1
        j += 1
    i += 1

#list for binary generation
binlist=[]

#Take input flights and generate LP file
f = open("LPFiles\FirstIteration.lp","w+")    

#generate Objective
f.write("Minimize multi-objectives\n") #Z1 = sum_i sum_k Pi*Xi,k*Dterm_k
#f.write("Minimize objective:\n")
f.write("OBJ1: Priority=0 Weight=1.0 Abstol=0.0 Reltol=0.0\n")

todo("Implement objective function weights") 

amountFlights=len(Flight._registry)
amountGates=len(Gate._registry)

for fl in Flight._registry:
    for ga in Gate._registry:
       f.write(str(fl.passengers*ga.distance)) 
       f.write(" X_I"+str(fl.number)+"_L"+str(ga.number))
       if int(fl.number)!=int(amountFlights) or int(ga.number)!=int(amountGates):
          f.write(" + ") 
       else:
          f.write("")
          
f.write("\n")
f.write("\n")
f.write("OBJ2: Priority=0 Weight=1.0 Abstol=0.0 Reltol=0.0\n")

#ff uitgecomment om te testen
for fl in Flight._registry: #Z2 = sum_i sum_k Xi,k * Dterm_k
    for ga in Gate._registry:
       if int(fl.gatePref)!=0:
           f.write("-"+str(fl.gatePref))
           f.write(" X_I"+str(fl.number)+"_L"+str(ga.number)+" ")
       
f.write("\n")
f.write("\n")
todo("Implement objectives") #Tommy

#generate constraints
f.write("Subject to:\n")

#Make all X_I_L binary, and have all flights require a gate
for fl in Flight._registry:
    for ga in Gate._registry:
        curVar=str("X_I"+str(fl.number)+"_L"+str(ga.number))
        f.write(curVar)
        if int(ga.number)!=int(amountGates):
            f.write(" + ") 
        else:
            f.write(" = 1 \n")            
        binlist.append(curVar) #Make binary

#Time overlap constraint:        
#For all overlapping flights, gates can only have one flight assigned:
for i in range(len(timemat)):
    for j in range(i):
        if timemat[i,j]==1:
            flight1=Flight._registry[i]
            flight2=Flight._registry[j]
            for ga in Gate._registry:
                flight1var=str("X_I"+str(flight1.number)+"_L"+str(ga.number))
                flight2var=str("X_I"+str(flight2.number)+"_L"+str(ga.number))
                f.write(flight1var + " + " + flight2var + " <= 1 \n") 
            

#Gate constrain 2: # ensures flights after 6 pm are not in B or C 
todo("Implement GC2") 

#Form factor constraint: (Compliance of a/c formfactor to bay/gate) 
todo("Implement FFC") #Tommy

f.write("\n")
#Make parameters binary as needed
f.write("binary\n")
for i in binlist:
    f.write(i+" ")
#write end file
f.write("\n")
f.write("end")
f.close



#RUN CPlex
sol = generateRunFiles("FirstIteration.lp")   #Returns solution filepath

lines = [line.rstrip('\n') for line in open(sol)]
lines = [line.strip() for line in lines]

if lines[6].split('=')[0]=='objectiveValue':
    objectiveValue=float(lines[6].split('=')[1].strip('"'))
else:
    print("ERROR: objectiveValue not at expect location!")

#Import data
tree = ET.parse(sol)
root = tree.getroot()

solNameList=[]
solValueList=[]
for child in root[3]:
    locals().update(child.attrib) #name,value,index
    solNameList.append(name)
    solValueList.append(value)

offset = solNameList.index("X_I1_L1")
a = np.zeros((amountFlights,amountGates))
b = np.empty((amountFlights,amountGates), dtype=object)
for i in range(amountFlights):
    for j in range(amountGates):
        fgi=offset+i*amountGates+j #flightGateIndex
        a[i,j]=solValueList[fgi]
        b[i,j]=solNameList[fgi] #For verification

print("Objective Value is:"+str(objectiveValue))

#Show dataset
todo("Implement dataset mooie grafiekjes ") #Boris

#Show solution
todo("Implement solution mooie grafiekjes - using existing function")



#Bussen bij gate X, als bus er is, telt afstand minder zwaar
todo("Implement showoff")

todo("Implement bays?") #Daan
