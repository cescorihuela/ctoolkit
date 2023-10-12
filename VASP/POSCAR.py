from toolkit.global_vars.ext_libs import *
from toolkit.global_vars.decorators import *
from toolkit.tools import tools

# Subclass POSCAR
class POSCAR():
    # Value initialization
    def __init__(self, mothership):
        self.tools = tools.tools()
        self.title = '\n'
        self.B = np.zeros([3,3], dtype=float)
        self.a_lat = 0
        self.names = []
        self.namelist = []
        self.atom_id = []
        self.lattype = '\n'
        self.multiplicity = [0]
        self.volume = 0.0
        self.at_frac = np.array(np.array([.0, .0, .0], dtype=float))
        self.at_cart = np.array(np.array([.0, .0, .0], dtype=float))
        self.type = "VASP"
    
        self.mothership = mothership
        self.is_filled = False

    # Generate a sample POSCAR from input python parameters
    def generate_poscar(self, B, alat, names, mult, atoms_frac, system_name='Generated by the Crystal Toolkit'):
        self.title = system_name + '\n'
        self.B = B
        self.a_lat = alat
        self.names = names
        self.lattype = 'Direct\n'
        self.multiplicity = mult
        self.volume = np.linalg.det(self.B)
        self.at_frac = atoms_frac
        self.at_cart = self.tools.frac_to_cart(self.B, self.at_frac) 

        self.is_filled = True

    # Read from POSCAR file
    @calculate_time
    def read_poscar(self, filename=None):
        if filename: self.poscar_filename = filename
        else: self.poscar_filename = sys.argv[1]
        fopen = open(self.poscar_filename,'r')
        lines = fopen.readlines()
        fopen.close()
        self.title = lines[0]
        self.a_lat = float(lines[1].split()[0])
        for i in range(3):
            self.B[i,:] = np.array(lines[2+i].split()[:],dtype=float)*self.a_lat
        self.names = lines[5].split()
        self.multiplicity = np.array(lines[6].split()[:], dtype=int)

        ct = 0
        # We need to initialize self.namelist into a list
        # in case read_poscar() is called multiple times
        self.namelist = []
        for i, name in enumerate(self.names):
            for atom in range(self.multiplicity[i]):
                self.namelist.append(self.names[i])
                self.atom_id.append(ct)
                ct += 1
        
        numatoms = ct
        self.lattype = lines[7] 
        at_frac_list = []
        at_cart_list = []
        for line in lines[8:8+numatoms]:
            vec_now = np.array(line.split()[:], dtype=float)
            at_frac_list.append(vec_now)

        self.at_frac = np.copy(np.array(at_frac_list, dtype=float))

        # Postprocessing
        self.frac_image_sniper()
        self.at_cart = np.array(self.tools.frac_to_cart(self.B, self.at_frac), dtype=float)
        self.volume = np.linalg.det(self.B)
        self.namelist = np.array(self.namelist)
        self.is_filled = True

    # A function to put back to the box atoms that slipped away
    @calculate_time
    def frac_image_sniper(self):
        tol = 0.05
        self.at_frac[np.abs(self.at_frac - 1.0) < tol] -= 1.0

    # Reprocess POSCAR if BASIS is changed
    @calculate_time
    def recalculate_poscar(self):
        self.at_frac = np.copy(self.tools.cart_to_frac(self.B, self.at_cart))
        self.frac_image_sniper()
        self.at_cart = np.copy(self.tools.frac_to_cart(self.B, self.at_frac))

    # Apply a rigid displacement. Can be moved to the toolbox.
    @calculate_time
    def rigid_displacement(self, vector):
        self.tools.rigid_displacement(vector, self)

    # Update basis of the POSCAR structure
    @calculate_time
    def update_B(self, B=None):
        if B is None: pass
        else: self.B = np.copy(np.array(B, dtype=float))
        self.volume = np.linalg.det(self.B)
        self.mothership.outcar.volume = np.linalg.det(self.B)

    # Atom selection tool. Returns atoms with "name" labels.
    @calculate_time
    def filter_atoms(self, name, mode='cart'):
        num_atoms = len(self.namelist[self.namelist == name])
        at_frac = np.zeros([num_atoms, 3], dtype=float)
        at_cart = np.zeros([num_atoms, 3], dtype=float)
        ct_name = 0
        for i in range(len(self.at_frac)):
            if self.namelist[i] == name:
                at_frac[ct_name] = self.at_frac[i]
                at_cart[ct_name] = self.at_cart[i]
                ct_name += 1

        if mode == 'frac':
            return at_frac
        if mode == 'cart':
            return at_cart

    # Atom selection tool 2. Return an iterable list of
    # the filtered atoms by "name".
    @calculate_time
    def filter_atoms_list(self, name):
        atom_list = []
        for i in range(len(self.namelist)):
            if self.namelist[i] == name:
                atom_list.append(i)
        return atom_list

    # Function that prints the POSCAR in frac format
    @calculate_time
    def write_frac(self, filename=None):
        s = ''
        s += (self.title)
        s += '%s\n' % (self.a_lat)
        s += '%12.8f %12.8f %12.8f\n' % (self.B[0,0], self.B[0,1], self.B[0,2])
        s += '%12.8f %12.8f %12.8f\n' % (self.B[1,0], self.B[1,1], self.B[1,2])
        s += '%12.8f %12.8f %12.8f\n' % (self.B[2,0], self.B[2,1], self.B[2,2])
        for name in self.names:
            s += '%5s' % (name)
        s += '\n'
        for mult in self.multiplicity:
            s += '%5d  ' % (mult)
        s += '\n'
        s += self.lattype
        for atom in range(len(self.at_frac)):
            for i in range(3):
                s += '%12.8f' % (self.at_frac[atom,i])
            if atom < len(self.at_frac)-1 : s += '\n'

        if filename:
            fopen = open(filename,'w')
            fopen.write(s)
            fopen.close()

        return s

    # Function that prints the POSCAR in cart format
    @calculate_time
    def write_cart(self, filename=None):
        s = ''
        s += (self.title)
        s += '%s\n' % (self.a_lat)
        s += '\t%.8f %.8f %.8f\n' % (self.B[0,0], self.B[0,1], self.B[0,2])
        s += '\t%.8f %.8f %.8f\n' % (self.B[1,0], self.B[1,1], self.B[1,2])
        s += '\t%.8f %.8f %.8f\n' % (self.B[2,0], self.B[2,1], self.B[2,2])
        for name in self.names:
            s += '\t%s\t' % (name)
        s += '\n'
        for mult in self.multiplicity:
            s += '\t%d\t' % (mult)

        s += '\n'
        s += 'Cartesian\n'
        for atom in range(len(self.at_cart)):
            s += '\t%.8f\t%.8f\t%.8f' % (self.at_cart[atom, 0], self.at_cart[atom, 1], self.at_cart[atom, 2])
            if atom < len(self.at_cart)-1 : s += '\n'

        if filename:
            fopen = open(filename,'w')
            fopen.write(s)
            fopen.close()

        return s

