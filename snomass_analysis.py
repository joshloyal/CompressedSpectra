#!/bin/bash

"exec" "python" "-Wignore" "$0" "$@"

from InputReader import MCfile, InputReader
from ROOT import *
from AtlasStyle import *
import rootutils as ru
from numpy import array
from myutilities import create_directory

# global flags
make_signal_grid = True

def create_trees(trees):
    # get the input mc files and their metadata
    data_dir = '/Volumes/BlackArmor Drive/Data/CompressedSpectra/' + \
        'monte_carlo/signal_grids/GO_decoupledSQ_13TeV/'
    mcfile_list = data_dir+'scan_summary.dat'
    reader = InputReader(mcfile_list)
    reader.process_file()

    # create the signal grid
    if make_signal_grid:
        signal_grid = ([],[])
        for mcfile in reader.mcfiles:
            signal_grid[0].append(mcfile.mGO) # gluino mass
            signal_grid[1].append(mcfile.mN1) # neutralino mass 
        
        # fill TGraph (x=mGO, y=mN1)
        sgrid = ru.create_tgraph(signal_grid[0], signal_grid[1])        
        sgrid.GetXaxis().SetTitle('m_{g}')
        sgrid.GetYaxis().SetTitle('m_{#chi}')
        
        # draw signal grid
        canvas = TCanvas()
        sgrid.Draw('AP')
        canvas.SaveAs('./output/signal_grid.pdf')
        

    # create a single chain with all of the mc events
    for mcfile in reader.mcfiles:
        chain = TChain('Delphes')
        data_file = data_dir+'Decayed/Events/'+mcfile.file_prefix+'.Delphes3.root'
        chain.Add(data_file)
        trees.append( (mcfile,chain) )

        # create the output directory structure as well
        outdir = './output/mGO_%s_mN1_%s' %(mcfile.mGO, mcfile.mN1)
        create_directory(outdir)

def book_histograms(mcfile, result, plots):
    prefix = './output/mGO_%s_mN1_%s/' %(mcfile.mGO,mcfile.mN1)
    plots['JetPT'] = result.AddHist1D(
        prefix+'jet_pt', 'jet P_{T}', 
        'jet P_{T}, GeV/c', 'number of jets', 
        500, 0.0, 5000.0)

    plots['MissingET'] = result.AddHist1D(
        prefix+'missing_et', 'Missing E_{T}',
        'Missing E_{T}, GeV', 'number of events',
        250, 0.0, 2500.0)

def analyse_events(treeReader, plots):
    # get pointers to branches used in this analysis
    branchJet      = treeReader.UseBranch('Jet')
    branchElectron = treeReader.UseBranch('Electron')
    branchMuon     = treeReader.UseBranch('Muon')
    branchMET      = treeReader.UseBranch('MissingET')

    # event loop here
    nEntries = treeReader.GetEntries()
    print 'nEntries to process = ', nEntries
    for entry in range(nEntries):
        if entry%10000 == 0:
            print 'Processed = ', entry

        # load selected branches with data from specified event
        treeReader.ReadEntry(entry)

        # ---------------------------------------------- OBJECT RECONSTRUCTION
        Jets = []
        if branchJet.GetEntries() > 0:
            for jet_number in range(0,Jet_size):
            jet = branchJet.At(jet_number)
            if jet.PT <= 30.:
                continue
            if abs(jet.Eta) >= 4.5:
                continue
            Jets.append(jet)
        # sort the list of jets by pt
        Jets = sorted(Jets, key=lambda jet: -jet.PT)
        for jet in Jets:
            if abs(jet.Eta) < 2.0:
                break

        
        Electrons = []
        if branchElectron.GetEntries() > 0:
            for electron_number in range(0,Electron_size):
                electron = branchElectron.At(electron_number)
                if electron.PT <= 20:
                    continue
                if abs(electron.Eta) >= 2.47:
                    continue
                Electrons.append(electron)

        Muons =[]
        if branchMuon.GetEntries() > 0:
            for muon_number in range(0,Muon_size):
                muon = branchMuon.At(muon_number)
                if muon.PT <= 7:
                    continue
                if abs(muon.Eta) >= 2.5:
                    continue
                Muons.append(muon)
        
        MET = []
        if branchMET.GetEntries() > 0:
            met = branchMET.At(0)
            plots['MissingET'].Fill(met.MET)



        if len(Jets) > 1:
            rejection_count = 0
            for jet in Jets:
                if jet.PT > 30 and abs(jet.Eta) < 4.5:
                    rejection_count = rejection_count + 1
        if rejection_count > 2:
            continue
            plots['JetPT'].Fill(jet.PT)

def print_histograms(result, plots):
    result.Print('pdf')

def main():
    ROOT.gROOT.SetBatch(1)
    ROOT.gSystem.Load('libDelphes')

    # create the approriate tree
    meta_data = []
    create_trees(meta_data)

    # loop over all of the signal grid
    for mcfile,tree in meta_data: 
        print '\n#--------- Processing (mGO=%s, mN1=%s) ---------#\n' \
            %(mcfile.mGO, mcfile.mN1)
        
        # create a treereader and result class
        treeReader = ExRootTreeReader(tree)
        result     = ExRootResult()
        plots = {'JetPT' : TH1D(), 'MissingET' : TH1D()}

        book_histograms(mcfile, result, plots)

        analyse_events(treeReader, plots)

        print_histograms(result, plots)

        result.Write('./output/mGO_%s_mN1_%s/results.root'%(mcfile.mGO,mcfile.mN1))

if __name__ == '__main__':
    main()
