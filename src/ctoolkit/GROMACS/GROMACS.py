from ctoolkit.global_vars.ext_libs import *
from ctoolkit.global_vars.decorators import *
from ctoolkit.tools import tools
class GROMACS():
    def __init__(self):
        pass
    
    def __init__(self):
        self.tools = tools()
        self.type = 'GROMACS'
    
    # This will read atomic positions of an MD run. Probably easy to tune it to read velocities.
    @calculate_time
    def read_gro_trajectory(self, filename, stype=None):
        with open(filename, 'r') as f:
            # Original GROMACS units are nm, ps, C, K, kJ/mol, bar, nm/ps
            nmtoA = 10
            nmpstoAfs = 0.01
            lines = f.readlines()
            import gc
            #for i, line in enumerate(f):
            #    if(i==1):
            #        numatoms = int(line.split()[0])
            #        break
            #numsteps = int(sum([1 for _ in f])/(numatoms+3))
            numatoms = int(lines[1].split()[0])
            numsteps = int(len(lines)/(numatoms+3))
            self.atposcart = np.zeros([numsteps,numatoms,3], dtype=float)
            self.atposfrac = np.zeros([numsteps,numatoms,3], dtype=float)
            self.atvelcart = np.zeros([numsteps,numatoms,3], dtype=float)
            self.atvelfrac = np.zeros([numsteps,numatoms,3], dtype=float)
            self.index = np.zeros([numsteps, numatoms], dtype=int)
            self.atom_names = np.zeros([numsteps, numatoms], dtype=str)
            self.boxes = np.zeros([numsteps, 3, 3], dtype=float)
            self.cellA = np.zeros([numsteps], dtype=float)
            self.cellB = np.zeros([numsteps], dtype=float)
            self.cellC = np.zeros([numsteps], dtype=float)
            self.vol = np.zeros([numsteps], dtype=float)
            pattern = r'[0-9]'
            print("Steps to be read:", numsteps)

            for i in range(numsteps-1, -1, -1):
                # First, read box
                bl = np.array([float(x) for x in lines[(numatoms+3)*(i+1) - 1].split()])
                self.boxes[i] = np.transpose(np.array([[bl[0], bl[3], bl[4]],
                                [bl[6], bl[1], bl[5]],
                                [bl[7], bl[8], bl[2]]], dtype=float))*nmtoA
                
                self.cellA[i] = np.sqrt(np.dot(self.boxes[i,:,0], self.boxes[i,:,0]))
                self.cellB[i] = np.sqrt(np.dot(self.boxes[i,:,1], self.boxes[i,:,1]))
                self.cellC[i] = np.sqrt(np.dot(self.boxes[i,:,2], self.boxes[i,:,2]))
                self.vol[i] = np.linalg.det(self.boxes[i]) 

                for at in range(numatoms-1, -1, -1):
                    l = lines[2+at + (numatoms+3)*i].split()
                    """ A slow selector
                    if(stype=='vel'):
                        self.atvelcart[i,at,:] = np.array([float(x) for x in l[6:9]], dtype=float)*nmpstoAfs
                    if(stype=='pos'):
                        self.atposcart[i,at,:] = np.array([float(x) for x in l[3:6]], dtype=float)*nmtoA
                    if(stype==None):
                        self.atposcart[i,at,:] = np.array([float(x) for x in l[3:6]], dtype=float)*nmtoA
                        self.atvelcart[i,at,:] = np.array([float(x) for x in l[6:9]], dtype=float)*nmpstoAfs
                    """
                    self.atposcart[i,at,:] = np.array([float(x) for x in l[3:6]], dtype=float)*nmtoA
                    self.atvelcart[i,at,:] = np.array([float(x) for x in l[6:9]], dtype=float)*nmpstoAfs
                    self.index[i, at] = int(l[2])
                    self.atom_names[i, at] = re.sub(pattern, '', l[1]) 
                    
                # Check if we're calling well cart_to_frac
                self.atposfrac[i] = self.tools.cart_to_frac(self.boxes[i], self.atposcart[i])
                self.atvelfrac[i] = self.tools.cart_to_frac(self.boxes[i], self.atvelcart[i])
                del lines[(2+numatoms+3)*i:]
                sys.stdout.write("%d/%d\r" % (numsteps-i, numsteps))
                sys.stdout.flush()
                #gc.collect()

    def read_step(self, step_id, numatoms, lines, lock):
        i = int(step_id+0)
        nmtoA = 10
        nmpstoAfs = 0.01
        bl = np.array([float(x) for x in lines[(numatoms+3)*(i+1) - 1].split()])

        boxes = np.transpose(np.array([[bl[0], bl[3], bl[4]],
                                [bl[6], bl[1], bl[5]],
                                [bl[7], bl[8], bl[2]]], dtype=float))*nmtoA

        cellA = np.sqrt(np.dot(boxes[:,0], boxes[:,0]))
        cellB = np.sqrt(np.dot(boxes[:,1], boxes[:,1]))
        cellC = np.sqrt(np.dot(boxes[:,2], boxes[:,2]))
        vol = np.linalg.det(boxes)

        atposcart = np.zeros([numatoms, 3], dtype=float)
        atvelcart = np.zeros([numatoms, 3], dtype=float)
        index = np.zeros([numatoms], dtype=float)
        atom_names = np.zeros([numatoms], dtype=str)
        pattern = r'[0-9]'
        for at in range(numatoms-1, -1, -1):
            l = lines[2+at + (numatoms+3)*i].split() 
            atposcart[at,:] = np.array([float(x) for x in l[3:6]], dtype=float)*nmtoA
            atvelcart[at,:] = np.array([float(x) for x in l[6:9]], dtype=float)*nmpstoAfs
            index[at] = int(l[2])
            atom_names[at] = re.sub(pattern, '', l[1])

        atposfrac = self.tools.cart_to_frac(boxes, atposcart)
        atvelfrac = self.tools.cart_to_frac(boxes, atvelcart)

        # Split writeout to memory so as to use a datalock
        with lock:
            self.boxes[i] = boxes
            self.cellA[i], self.cellB[i], self.cellC[i] = cellA, cellB, cellC
            self.vol[i] = vol
            self.atom_names[i] = atom_names
            self.index[i] = index
            self.atposfrac[i] = atposfrac
            self.atvelfrac[i] = atvelfrac

    def read_gro_trajectory_parallel(self, filename):
        with open(filename, 'r') as f:
            # Original GROMACS units are nm, ps, C, K, kJ/mol, bar, nm/ps
            nmtoA = 10
            nmpstoAfs = 0.01
            lines = f.readlines()
            numatoms = int(lines[1].split()[0])
            numsteps = int(len(lines)/(numatoms+3))
            self.atposcart = np.zeros([numsteps,numatoms,3], dtype=float)
            self.atposfrac = np.zeros([numsteps,numatoms,3], dtype=float)
            self.atvelcart = np.zeros([numsteps,numatoms,3], dtype=float)
            self.atvelfrac = np.zeros([numsteps,numatoms,3], dtype=float)
            self.index = np.zeros([numsteps, numatoms], dtype=int)
            self.atom_names = np.zeros([numsteps, numatoms], dtype=str)
            self.boxes = np.zeros([numsteps, 3, 3], dtype=float)
            self.cellA = np.zeros([numsteps], dtype=float)
            self.cellB = np.zeros([numsteps], dtype=float)
            self.cellC = np.zeros([numsteps], dtype=float)
            self.vol = np.zeros([numsteps], dtype=float)
            print("Steps to be read:", numsteps)

            import multiprocessing as mp
            m = mp.Manager()
            lock = mp.Lock()
            threads = [multiprocessing.Process(target=self.read_step, args=(step_id, numatoms, lines, lock))
                       for step_id in range(numsteps-1, -1, -1)]

            ncpu = 8
            for i in range(int(numsteps/ncpu)):
                for x in threads[i*ncpu:(i+1)*ncpu]:
                    x.start()

                for x in threads[i*ncpu:(i+1)*ncpu]:
                    x.join()
                sys.stdout.write("%d/%d...\r" % (i, int(numsteps/ncpu)))
                sys.stdout.flush()
            # Remaining steps
            
            for i in range(numsteps%ncpu):
                for x in threads[int(numsteps/ncpu+1)*ncpu:]:
                    x.start()
            for x in threads[int(numsteps/ncpu+1)*ncpu:]:
                    x.join()
            print(self.boxes)
