# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 16:21:08 2019

@author: Daan
"""


#import matplotlib.pyplot as plt
import numpy as np
from OOFunc import generateRunFiles,timeTo5Min,getTimetableMatrix,plotTimetable,Flight,Airline,Gate,Terminal,Bay,todo
import xml.etree.ElementTree as ET

todo("Make data set better") #e.g. add corresponding sizes to aircraft #Random dataset?
todo("Make bays size and distances correct")


#Terminal(name,openEvening,distance)
t1 = Terminal("A",True,250)
t2 = Terminal("B",True,610)
t3 = Terminal("C",False,460)
t4 = Terminal("D",False,100)

#Gate(terminal,domesticFlight,distanceToTerminal)
g1 = Gate(t1,True,100)
g2 = Gate(t1,False,100)
g3 = Gate(t1,True,300)
g4 = Gate(t1,False,300)

g5 = Gate(t2,False,100)
g6 = Gate(t2,False,400)
g7 = Gate(t2,False,700)

g8 = Gate(t3,False,100)
g9 = Gate(t3,False,400)
g10 = Gate(t3,False,700)

g11 = Gate(t4,False,80)
g12 = Gate(t4,False,380)

#Bay(linkedGates,distLinkedGates,formFactor)
b1 = Bay([g1,g3],[100,150],"B")
b2 = Bay([g1,g3],[150,100],"B")
b3 = Bay([g2,g4],[100,150],"B")
b4 = Bay([g2,g4],[150,100],"B")

b5 = Bay([g5,g6],[150,100],"A")
b6 = Bay([g5,g6],[100,150],"A")
b7 = Bay([g6,g7],[150,100],"A")
b8 = Bay([g6,g7],[100,150],"A")

b9  = Bay([g8,g9],[150,100],"A")
b10 = Bay([g8,g9],[100,150],"A")
b11 = Bay([g9,g10],[150,100],"A")
b12 = Bay([g9,g10],[100,150],"A")

b13 = Bay([g11],[100],"C")
b14 = Bay([g11,g12],[100,100],"C")
b15 = Bay([g11,g12],[100,100],"C")
b16 = Bay([g12],[100],"C")

#remote bays 
#b20 = Bay(Gate._registry,[])

#Airliner(name,gatePref)
AirFrance   = Airline("AirFrance",g5)
KLM = Airline("KLM",g8)
Delta = Airline("Delta",g11)
BritishAirways=Airline("British Airways")
Transavia=Airline("Transavia")
EasyJet = Airline("EasyJet")

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

#intialize useful Variables
amountFlights=len(Flight._registry)
amountGates=len(Gate._registry)
amountBays=len(Bay._registry)
    
#list for binary generation
binlist=[]

#I=flights
#K=bays
#L=gates

#RUN CPlex
    #Take input flights and generate LP file
    
todo("Currently the time matrix works for bays but not terminals")
todo("E.g. bay occupied for full time aircraft is at airport, terminal occupied for 15 minutes before and after arrival/departure")

todo("Implement objective function weights and priorities (currently they are pretty random)") 

with open("LPFiles\SecondIteration.lp","w+") as f:

    #generate Objective
    f.write("Minimize multi-objectives\n") #Z1 = sum_i sum_k Pi*Xi,k*Dterm_k
    f.write("OBJ1: Priority=4 Weight=1.0 Abstol=0.0 Reltol=0.0\n\n") #Choose gate closest to terminal exit, weighed by passengers in flight
    
    
    for fl in Flight._registry:
        for ga in Gate._registry:
           f.write(str(fl.passengers*ga.distanceToTerminal)) 
           f.write(" X_I"+str(fl.number)+"_L"+str(ga.number))
           if int(fl.number)!=int(amountFlights) or int(ga.number)!=int(amountGates):
              f.write(" + ") 
           else:
              f.write("")

    f.write("\n")
    f.write("\n")
    f.write("OBJ2: Priority=6 Weight=1.0 Abstol=0.0 Reltol=0.0\n\n") #Maximize gate preference
    
    for fl in Flight._registry: #Z2 = sum_i sum_k Xi,k * Dterm_k
        for ga in Gate._registry:
           if int(fl.gatePref)==ga.number:
               f.write("-"+str(1))
               f.write(" X_I"+str(fl.number)+"_L"+str(ga.number)+" ")
               binlist.append("X_I"+str(fl.number)+"_L"+str(ga.number))

    f.write("\n")
    f.write("\n")    
    f.write("OBJ3: Priority=2 Weight=1.0 Abstol=0.0 Reltol=0.0\n\n") #Minimize gate - bay distance , weighed by passengers in flight
    for fl in Flight._registry:
        for bay in Bay._registry:
           for i in range(len(bay.linkedGates)):
               ga=bay.linkedGates[i]
               gaDist=bay.linkedGatesDistances[i] 
               f.write(str(fl.passengers*gaDist))
               f.write(" X_I"+str(fl.number)+"_K"+str(bay.number)+"_L"+str(ga.number))
               binlist.append("X_I"+str(fl.number)+"_K"+str(bay.number)+"_L"+str(ga.number))
               if int(fl.number)!=int(amountFlights) or int(bay.number)!=int(amountBays) or i+1!=len(bay.linkedGates):
                  f.write(" + ") 
               else:
                  f.write("")
                   
    f.write("\n")
    f.write("\n")

    #generate constraints
    f.write("Subject to:\n")
    
    #Link X_I_K_L with X_I_K and X_I_L
    for fl in Flight._registry:
        for bay in Bay._registry:           
            for i in range(len(bay.linkedGates)):
                ga=bay.linkedGates[i]
                curXIKL=str("X_I"+str(fl.number)+"_K"+str(bay.number)+"_L"+str(ga.number))
                curXIK=str("X_I"+str(fl.number)+"_K"+str(bay.number))
                curXIL=str("X_I"+str(fl.number)+"_L"+str(ga.number))

#               Either or constraints, as is depicted in slides.    
#               This ensures 
#                
#               x1 must be 1 for x2 to be 1 
#               -x1+x2<=0
#               x1+x2-y1<=1                
                
#               This ensures that if X_I_K is 1, X_I_K_L is 1, and vice versa
                f.write("-"+curXIKL+" +"+curXIK+"<=0\n")
                f.write( curXIKL+" +"+curXIK+"-" + curXIKL+"_"+str(i)+ "<=1\n")
                
#               This does the same for X_I_L
                f.write("-"+curXIKL+" +"+curXIL+"<=0\n")
                f.write( curXIKL+" +"+curXIL+"-" + curXIKL+"_"+str(i)+"2 <=1\n")

    
    #Have all flights require a bay for full stay
    for fl in Flight._registry:
        for bay in Bay._registry:
            curVar=str("X_I"+str(fl.number)+"_K"+str(bay.number))
            binlist.append(curVar)
            f.write(curVar)
            if int(bay.number)!=int(amountBays):
                f.write(" + ") 
            else:
                f.write(" = 1 \n")     
                
#    #Have all flights require a gate for full stay
    for fl in Flight._registry:
        for ga in Gate._registry:
            curVar=str("X_I"+str(fl.number)+"_L"+str(ga.number))
            binlist.append(curVar)
            f.write(curVar)
            if int(ga.number)!=int(amountGates):
                f.write(" + ") 
            else:
                f.write(" = 1 \n")            
    
    #Time overlap constraint:        
    #For all overlapping flights, bays can only have one flight assigned:
    for i in range(len(timemat)):
        for j in range(i):
            if timemat[i,j]==1:
                flight1=Flight._registry[i]
                flight2=Flight._registry[j]
                for bay in Bay._registry:
                    flight1var=str("X_I"+str(flight1.number)+"_L"+str(bay.number))
                    flight2var=str("X_I"+str(flight2.number)+"_L"+str(bay.number))
                    f.write(flight1var + " + " + flight2var + " <= 1 \n") 
                
    
    #Gate constrain 1: # domestic flights to domestic gates
    todo("Implement GC1") 

    #Gate constrain 2: # ensures flights after 6 pm are not in gates closed after that hour
    todo("Implement GC2") 
    
    #Bay constraint 2: or Form factor constraint: (Compliance of a/c formfactor to bay/gate) 
    todo("Implement FFC") #Tommy
    todo("Figure out formfactors that are used for aircraft in airport")    
    todo("Maybe make it A = wide body, B = reg bod, C= narrow")
    todo("An A bay would be usable by 1 A, 1B or 2C") #Cool but hard to implement
    todo("A  B bay would be usable by 0 A, 1B or 1C")
    todo("A  C bay would be usable by 0 A, 0B or 1C")
    f.write("\n")
    #Make parameters binary as needed
    
    #Bay constraint 4: Refueling constraint 
    todo("Implement Refuel constraint")  #using bay.refuelBay (All bays currently able to refuel, change dataset to test)
    
    f.write("binary\n")
    for i in binlist:
        f.write(i+" ")
    #write end file
    f.write("\n")
    f.write("end")




#RUN CPlex:
sol = generateRunFiles("SecondIteration.lp")   #Returns solution filepath

lines = [line.rstrip('\n') for line in open(sol)]
lines = [line.strip() for line in lines]

if lines[6].split('=')[0]=='objectiveValue':
    objectiveValue=float(lines[6].split('=')[1].strip('"'))
    print("Objective value is",objectiveValue)
else:
    print("ERROR: objectiveValue not at expected location!")

#Import data:
tree = ET.parse(sol)
root = tree.getroot()

solNameList=[]
solValueList=[]
for child in root[3]:
    locals().update(child.attrib) #name,value,index
    solNameList.append(name)
    solValueList.append(value)


#retrieve X_I_L, X_I_K from solution, send to objects
a = np.zeros((amountFlights,amountGates))
b = np.empty((amountFlights,amountGates), dtype=object)        
c = np.zeros((amountFlights,amountBays))
d = np.empty((amountFlights,amountBays), dtype=object)        
for fl in Flight._registry:
    for ga in Gate._registry:
        i = fl.number-1
        j = ga.number-1
        curVar=str("X_I"+str(fl.number)+"_L"+str(ga.number))
        findVar=solNameList.index(curVar)
        a[i,j]=solValueList[findVar]
        b[i,j]=solNameList[findVar]
        if abs(int(solValueList[findVar]))!=0:
            fl.assignGate(ga)
            
    for bay in Bay._registry:
        i = fl.number-1
        j = ga.number-1
        curVar=str("X_I"+str(fl.number)+"_L"+str(bay.number))
        findVar=solNameList.index(curVar)
        c[i,j]=solValueList[findVar]
        d[i,j]=solNameList[findVar]
        if abs(int(solValueList[findVar]))!=0:
            fl.assignBay(bay)


#Show dataset
todo("Implement dataset mooie grafiekjes ") #Boris


#Grafiekje solution:
t=["5pm","6pm","7pm","8pm","9pm"]

#getTimetableMatrix(timeStart,timeEnd,amountGates)
timetableMatrix=getTimetableMatrix(t[0],t[-1],amountGates)
#plotTimeTable
plotTimetable(timetableMatrix,1,xTickLabels=t,xTickSpacing=11,yTickLabels=True)


#Bonus:

#Bussen bij gate X, als bus er is, telt afstand minder zwaar
todo("Implement busje")

        #e.g. 20 min on departure and 10 on arrival for gate, full time for bay.
todo("Eventueel towing implementen (Naar andere bay als dat goedkoper is)")