class MCfile:
    def __init__(self, mGO, mN1, production_mode, decay_mode, sigma, N_events, file_prefix):
        self.mGO = mGO
        self.mN1 = mN1
        self.production_mode = production_mode
        self.decay_mode = decay_mode
        self.sigma = sigma
        self.N_events = N_events
        self.file_prefix = file_prefix

class InputReader:
    def __init__(self, infile):
        self.infile = infile
    def process_file(self):
        self.mcfiles = []
        for line in open(self.infile, 'r'):
            if line[0] == '#':
                continue
            line = line.replace('\n', '')
            mc_info = line.split(' ')
            self.mcfiles.append(
                MCfile(int(mc_info[0]), int(mc_info[1]), mc_info[2], mc_info[3],
                float(mc_info[4]), int(mc_info[5]), mc_info[6]) )
        
#### Example use
# reader = InputReader('scan_summary.dat')
# reader.process_file()
# for mcfile in reader.mcfiles:
#     print mcfile.N_events, mcfile.file_prefix


