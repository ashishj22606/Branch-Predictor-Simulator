import codecs
import math

predictor = input("Enter Predictor name: ")
if predictor == 'smith':
    b = int(input("Enter No of counter bits for prediction: "))
    traceFilename = input("Enter TracefileName: ")
    m2 = None
    m1 = None
    n = None
elif predictor == 'bimodal':
    m2 = int(input("Enter  number of PC bits used to index the bimodal table: "))
    traceFilename = input("Enter TracefileName: ")
elif predictor == 'gshare':
    m1 = int(input("Enter m1: "))
    n = int(input("Enter n: "))
    traceFilename = input("Enter TracefileName: ")
else:
    k = int(input("Enter k:"))
    m1 = int(input("Enter m1: "))
    n = int(input("Enter n: "))
    m2 = int(input("Enter M2"))
    traceFilename = input("Enter TracefileName: ")
    
file = codecs.open(traceFilename,'r','utf8')
contents = file.readlines()
addresses = []
branches = []
taken, notTaken = 0 , 0

for i in range(len(contents)):
    if contents[i].split(" ")[1][:1]=='t' or contents[i].split(" ")[1][:1]=='n':
        addresses.append(contents[i].split(" ")[0])
        branches.append(contents[i].split(" ")[1][:1])
        if contents[i].split(" ")[1][:1]=='t': taken+=1
        else: notTaken+=1
for i in range(len(addresses)):
    if len(addresses[i])<8:
        while len(addresses[i])!=8:
            addresses[i]='0'+ addresses[i]

#convert hex to decimal
for i in range(len(addresses)):
    temp = addresses[i]
    temp1 = int(temp,16)
    addresses[i]=temp1

class SmithNBit:
    def __init__(self, b):
        self.lower = 0
        self.threshold = int(math.pow(2,b-1))
        self.counter = int(math.pow(2,b-1))
        self.higher = int(math.pow(2,b))-1
        self.predictions = 0
        self.mispredictions = 0
        
    def predict(self,branch):
        self.predictions+=1
        if self.counter >= self.threshold:
            pred = 't' 
        else: 
            pred = 'n'
        return pred
    
    def updatecounter(self,pred,branch):
        if branch=='t':
            if self.counter < self.higher:
                self.counter+=1
        else:
            if self.counter > self.lower and self.counter>0:
                self.counter-=1
        if branch!=pred:
            self.mispredictions+=1

               
               
    def printCounterContents(self):
        print(f"Final Counter Content: {self.counter}")
        
           
    def getCounterValue(self):
        return self.counter
    
    def printResults(self):
        print("OUTPUT")
        print(f"number of predictions: {len(branches)}")
        print(f"number of mispredictions: {self.mispredictions}")
        print(f"misprediction rate: {self.mispredictions*100/len(branches)}")
        self.printCounterContents()


class Bimodal:
    def __init__(self,m):
        self.predictionTableSize = int(math.pow(2,m))
        self.mask = (self.predictionTableSize - 1) << 2
        self.predictionss = 0
        self.mispredictionss = 0
        self.max=7
        self.taken=4
        self.counters = [4 for i in range(self.predictionTableSize)]
        self.index=0
        
    
        
    def predict(self,branch,address):
        self.predictionss+=1
        self.index = int((address/4)%self.predictionTableSize)
        predic='n'
        if self.counters[self.index]>=self.taken:
            predic = 't'
        return predic
    
    def updatecounter(self,predic,branch):
        if branch=='t' and self.counters[self.index]<self.max:
            self.counters[self.index]+=1
        elif branch=='n' and self.counters[self.index]>0:
            self.counters[self.index]-=1
        if predic!=branch:
            self.mispredictionss+=1
        

        
               
    def printCounterContents(self):
        print("FINAL BIMODAL CONTENTS: ")
        for i in range(self.predictionTableSize):
            print(f"{i}       {self.counters[i]}")
            
    def printResults(self):
        print("OUTPUT")
        print(f"number of predictions: {self.predictionss}")
        print(f"number of mispredictions: {self.mispredictionss}")
        print(f"misprediction rate: {self.mispredictionss*100/self.predictionss}")

class Gshare:
    def __init__(self,m,n):
        self.m = m
        self.n = n
        self.predictionTableSize = int(math.pow(2,self.m))
        self.globalHistoryRegister = 0
        self.predictionss = 0
        self.mispredictionss = 0
        self.max=7
        self.taken=4
        self.counters = [4 for i in range(self.predictionTableSize)]
        self.index =0
        
    def predict(self, branch, address):
        self.predictionss+=1
        m_bits = int((address/4)%self.predictionTableSize)
        m_n_bits = int(m_bits/math.pow(2,n))
        n_bits = int((address/4)%math.pow(2,n))
        xor = n_bits^self.globalHistoryRegister
        self.index = m_n_bits<<n
        self.index=self.index+xor
        prec='n'
        if self.counters[self.index]>=self.taken:
            prec='t'
        return prec
            
    def updatecounter(self,branch):
        if branch=='t' and self.counters[self.index]<self.max:
            self.counters[self.index]+=1
        elif branch=='n' and self.counters[self.index]>0:
            self.counters[self.index]-=1
        
            
    def updategshareBHR(self,prec,branch):
        if prec!=branch:
            self.mispredictionss+=1
        self.globalHistoryRegister=self.globalHistoryRegister>>1
        if branch=='t':
            self.globalHistoryRegister=self.globalHistoryRegister+int(math.pow(2,n-1))
        
        
    def printCounterContents(self):
        print("FINAL GSHARE CONTENT:")
        for i in range(self.predictionTableSize):
            print(f"{i}       {self.counters[i]}")
            
    def printResults(self):
        print("OUTPUT")
        print(f"number of predictions: {self.predictionss}")
        print(f"number of mispredictions: {self.mispredictionss}")
        print(f"misprediction rate: {self.mispredictionss*100/self.predictionss}")


class hybrid:
    def __init__(self):
        self.predictionsh=0
        self.mispredictionsh=0
        self.index1=0
        self.g = Gshare(m1,n)
        self.b = Bimodal(m2)
        self.size = int(math.pow(2,k))
        self.maskh = (self.size-1)<<2
        self.chooser_history = [SmithNBit(2) for i in range(self.size)]
        self.bimodal_c_pred=0
        self.gshare_c_pred=0
        
    def update_table(self, address, branch):
        self.predictionsh+=1
        self.index1 = (address & self.maskh)>>2
        bimodal_predict = self.b.predict(branch,address)
        gshare_predict = self.g.predict(branch, address)
        chooser_pred = self.chooser_history[self.index1].predict(branch)
        
        if chooser_pred=='t':
            final_pred = gshare_predict
            self.g.updatecounter(branch)
        else:
            final_pred = bimodal_predict
            self.b.updatecounter(branch,branch)
        self.g.updategshareBHR(final_pred,branch)
        
        if bimodal_predict==branch and gshare_predict!=branch:
            self.chooser_history[self.index1].updatecounter('n',branch)
        elif bimodal_predict!=branch and gshare_predict==branch:
            self.chooser_history[self.index1].updatecounter('t',branch)
            
        if final_pred!=branch:
            self.mispredictionsh+=1
            
            
                
    def printCounterContents(self):
        self.b.printCounterContents()
        print("FINAL CHOOSER CONTENT:")
        for i in range(self.size):
            print(f"{i}       {self.chooser_history[i].getCounterValue()}")
        self.g.printCounterContents()
            
    def printResults(self):
        print("OUTPUT")
        print(f"number of predictions: {self.predictionsh}")
        print(f"number of mispredictions: {self.mispredictionsh}")
        print(f"misprediction rate: {(self.mispredictionsh)*100/self.predictionsh}")



if predictor == 'smith':
    t = SmithNBit(b)
    for i in range(len(branches)):
        pred = t.predict(branches[i])
        t.updatecounter(pred,branches[i])
    t.printResults()


elif predictor == 'bimodal':
    b = Bimodal(m2)
    for i in range(len(branches)):
        predic = b.predict(branches[i],addresses[i])
        b.updatecounter(predic,branches[i])
    b.printResults()
    b.printCounterContents()


elif predictor == 'gshare':
    g = Gshare(m1,n)
    for i in range(len(branches)):
        prec = g.predict(branches[i],addresses[i])
        g.updatecounter(branches[i])
        g.updategshareBHR(prec,branches[i])
    g.printResults()
    g.printCounterContents()

    
else:
    h = hybrid()
    for i in range(len(branches)):
        h.update_table(addresses[i],branches[i])
    h.printResults()
    h.printCounterContents()
        