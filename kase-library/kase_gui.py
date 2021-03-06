import Tkinter

__author__ = 'Jeremy'


"""
Special thanks to
ZetCode Tkinter tutorial
Author: Jan Bodnar
Website: www.zetcode.com
"""


from Tkinter import *
import tkFileDialog
from importTestArray import importSubstrateDefinitionsFile
from importTestArray import importSignificantSubstrates
import copy
import scipy.stats
import numpy
import randomSelectReplacement as rsr
from mytimer import mytimer

class TopLevel(Frame):

    OPTIONAL = "(optional)"

    def __init__(self, parent):
        Frame.__init__(self, parent, background="white")

        self.parent = parent
        self.donuts = 0
        self.file1 = StringVar()
        self.file1.set("")
        self.file2 = StringVar()
        self.file2.set("")
        self.numSimulations = StringVar()
        self.numSimulations.set("100,000")
        self.currSim = StringVar()
        self.currSim.set("0")
        self.outFilename = StringVar()
        self.outFilename.set(self.OPTIONAL)
        self.load1 = False
        self.load2 = False
        self.lineCount = 0

        self.initUI()


    def exeSim(self):

        x = 2 + 6
        if not self.load1:
            self.openSubKinDef()
        if self.load1 and not self.load2:
            self.openSubSigList()

        #if self.file1.get() == "" or self.file2.get() == "":
        if not (self.load1 and self.load2):
            # dialog = Tk()
            # dialog.grid()
            # label1 = Label(dialog, text="You must PICK and LOAD source files first").grid(row=0)
            # ok = Button(dialog, text=' OK ', command=dialog.quit).grid(row=1)
            print "Simulations not started due to input file error"
            self.textBox.insert(Tkinter.END, "Simulations not started due to input file error\n")
            self.lineCount += 1
        else:
            #print "numSimulations = "+self.numSimulations.get()
            numSubstrates = len(self.sigSubstrates)
            mt = mytimer()
            mt.start()
            kinaseSimulationsCounts = dict()

            #empty array with one member for each simulation
            s=self.numSimulations.get().replace(',','')
            emptyCounts = [0 for x in range(0, int(s))]

            simulations = dict()
            for kinase in self.allKinases.keys():
                simulations[kinase] = copy.deepcopy(emptyCounts)
            #now simulations[kin][s] points to kinase by name kin, sth simulation

            for s in range(0, int(self.numSimulations.get().replace(',',''))):
                (substratesChosen, kinaseCounts) = rsr.randoPermutationSimulation(self.substrate2kinases, numSubstrates)
                for substrate in substratesChosen:
                    kinases = self.substrate2kinases[substrate]
                    for kinase in kinases:
                        #k = allKinases.keys().index(kinase)
                        simulations[kinase][s] += 1
                if (s % 100 == 99):
                    print "Simulation "+str(s+1)+" complete\t"+mt.elapsed()
                    self.textBox.insert(
                        Tkinter.END,
                        "Simulation "+str(s+1)
                        +" complete\t"+mt.elapsed()+"\n")
                    self.textBox.see(Tkinter.END)
                    self.lineCount += 1
                    if self.lineCount % 10 == 0:    self.parent.update()
                self.currSim.set(str(s))

            meanSimulations = [0 for x in self.allKinases.keys()]
            stdSimulations = [0 for x in self.allKinases.keys()]
            self.zscoreKinases = [0 for x in self.allKinases.keys()]
            self.pvalueKinases = [0 for x in self.allKinases.keys()]
            self.results = []

            for k in range(0, len(self.allKinases.keys())):
                #meanSimulations[k] = math.mean(simulations[k])
                meanSimulations[k] = numpy.mean(simulations[self.allKinases.keys()[k]])
                #stdSimulations[k] = math.stdev(simulations[k])
                stdSimulations[k] = numpy.std(simulations[self.allKinases.keys()[k]])
                # if stdSimulations[k] == 0:
                #     print "nan detected"
                # if numpy.isnan(stdSimulations[k]):
                #     print "nan detected"
                kinase = self.allKinases.keys()[k]

                if stdSimulations[k] == 0:
                    self.zscoreKinases[k] = 0.0
                    self.pvalueKinases[k] = 0.0
                else:
                    if kinase in self.sigKinaseCount:
                        self.zscoreKinases[k] = (self.sigKinaseCount[kinase] - meanSimulations[k]) / stdSimulations[k]
                    else:
                        self.zscoreKinases[k] = (0 - meanSimulations[k]) / stdSimulations[k]
                    self.pvalueKinases[k] = scipy.stats.norm.sf(abs(self.zscoreKinases[k]))*2

                self.results.append( (self.pvalueKinases[k], self.allKinases.keys()[k], self.zscoreKinases[k]) )

            print "sorting results\t"+mt.elapsed()
            #self.textBox.insert(Tkinter.END, "sorting results\t"+mt.elapsed())
            self.results.sort()
            print "sorting complete\t"+mt.elapsed()
            self.textBox.insert(Tkinter.END, "sorting complete\t"+mt.elapsed()+"\n")
            self.textBox.see(Tkinter.END)
            self.lineCount += 1


            outFile = None
            if self.outFilename != self.OPTIONAL:
                outFile = open(self.outFilename.get(),'w')
            print "(kinase)\t(z-score)\t(p-value 2 tail)"
            self.textBox.insert(Tkinter.END, "(kinase)\t(z-score)\t(p-value 2 tail)"+"\n")
            if outFile:
                outFile.write("(kinase)\t(z-score)\t(p-value 2 tail)"+"\n")
            self.textBox.see(Tkinter.END)
            self.lineCount += 1

            for result in self.results:
                (p, kinase, z) = result
                print kinase+"\t%.03f\t%.03f"%(z,p)
                self.textBox.insert(Tkinter.END, kinase+"\t%.03f\t%.03f\n"%(z,p))
                self.textBox.see(Tkinter.END)
                self.lineCount += 1
                if self.lineCount % 10 == 0:    self.parent.update()
                if outFile:
                    outFile.write(kinase+"\t%.03f\t%.03f\n"%(z,p))


    def et(self):
        print "ET"

    def openSubKinDef(self):
        if self.file1.get() != "":
            (self.substrate2kinases, self.allKinases) = importSubstrateDefinitionsFile(self.file1.get())
            # substrate2kinases     text to (list of text) dictionary
            # allKinases            text to (integer count) dictionary
            self.load1 = True
            self.textBox.insert(Tkinter.END, "%d substrates and %d kinases are defined in the source file\n"
                                % ( len(self.substrate2kinases.keys()), len(self.allKinases.keys()) )   )
            self.lineCount += 1
        else:
            dialog = Tk()
            dialog.grid()
            label1 = Label(dialog, text="Pick a file first").grid(row=0)
            ok = Button(dialog, text=' OK ', command=dialog.destroy).grid(row=1)


    def browseSubKinDef(self):
        file1 = tkFileDialog.askopenfilename()
        self.file1.set(file1)

    def browseOutFilename(self):
        file = tkFileDialog.askopenfilename()
        self.outFilename.set(file)


    def openSubSigList(self):
        if self.file2.get() != "":
            if self.load1:
                (self.sigSubstrates, self.sigKinaseCount) = importSignificantSubstrates(self.file2.get(), self.substrate2kinases)
                self.load2 = True
                self.textBox.insert(Tkinter.END, "%d substrates and %d kinases are observed in experiment\n"
                                % ( len(self.sigSubstrates), len(self.sigKinaseCount.keys()) )   )
                self.lineCount += 1
            else:
                dialog = Tk()
                dialog.grid()
                label1 = Label(dialog, text="You must import Substrate Kinase Definitions first").grid(row=0)
                ok = Button(dialog, text=' OK ', command=dialog.destroy).grid(row=1)

        else:
            dialog = Tk()
            dialog.grid()
            label1 = Label(dialog, text="Pick a file first").grid(row=0)
            ok = Button(dialog, text=' OK ', command=dialog.destroy).grid(row=1)

    def browseSubSigList(self):
        file2 = tkFileDialog.askopenfilename()
        self.file2.set(file2)

    def initUI(self):

        self.parent.title("KASE: Kinome Array Significance Evaluator")
        self.grid()


        label1 = Label(self.parent, text="Substrate to Kinase definitions")
        label2 = Label(self.parent, text="Substrates significant list")
        label3 = Label(self.parent, text="simulation cycle complete")
        label5 = Label(self.parent, text="Output File Name")
        label7 = Label(self.parent, text="You can copy the output ==>")

        label1.grid(row=0, column=0)
        label2.grid(row=1, column=0)
        label3.grid(row=4, column=0)
        label5.grid(row=5, column=0)
        label7.grid(row=7, column=0)

        self.e1 = Entry(self.parent, textvariable=self.file1, width=100)
        self.e2 = Entry(self.parent, textvariable=self.file2, width=100)
        self.e3 = Entry(self.parent, textvariable=self.numSimulations)
        self.e4 = Entry(self.parent, textvariable=self.currSim)
        self.e5 = Entry(self.parent, textvariable=self.outFilename, width=100)

        self.b1 = Button(self.parent, text=' Browse  ', command=self.browseSubKinDef).grid(row=0, column=2)
        self.b2 = Button(self.parent, text=' Browse  ', command=self.browseSubSigList).grid(row=1, column=2)
        self.b5 = Button(self.parent, text=' Browse  ', command=self.browseOutFilename).grid(row=5, column=2)

        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        self.e3.grid(row=2, column=1)
        self.e4.grid(row=4, column=1)
        self.e5.grid(row=5, column=1)

        # checkbutton = Checkbutton(self.parent, text="I like donuts", variable=self.donuts)
        # checkbutton.grid(columnspan=2, sticky=W)
        button1 = Button(self.parent, text="Execute Simulation", command=self.exeSim)
        # button2 = Button(self.parent, text="ET", command=self.et())
        button1.grid(row=6, column=1)
        # button2.grid(row=3, column=2)
        self.parent.columnconfigure(0, weight=3)
        self.parent.columnconfigure(1, weight=6)
        self.parent.columnconfigure(2, weight=1)

        self.textBox = Text(self.parent)
        self.textBox.grid(row=7, column=1)



def main():
    root = Tk()
    root.geometry("900x600+50+50")
    app = TopLevel(root)
    root.mainloop()


if __name__ == '__main__':
    main()
