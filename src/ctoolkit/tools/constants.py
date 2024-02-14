from toolkit.global_vars.ext_libs import *

# Some constants
class constants:
    def __init__(self):
        self.kcalmol_to_eV = 0.0433634
        self.atm_to_GPa = 0.000101325
        self.mass = {"H":1.008,"Li":6.94,"Na":39.098,"Rb":85.468,"Cs":132.91,"Fr":223,
                "Be":9.0122,"Mg":24.305,"Ca":40.078,"Sr":87.62,"Ba":137.33,"Ra":226,
                "Sc":44.956,"Y":88.906,
                "Ti":47.867,"Zr":91.224,"Hf":178.49,"Rf":267,
                "V":50.942,"Nb":92.906,"Ta":180.95,"Db":268,
                "Cr":51.996,"Mo":95.95,"W":183.84,"Sg":269,
                "Mn":54.938,"Tc":98,"Re":186.21,"Bh":270,
                "Fe":55.845,"Ru":101.07,"Os":190.23,"Hs":277,
                "Co":58.933,"Rh":102.91,"Ir":192.22,"Mt":278,
                "Ni":58.963,"Pd":106.42,"Pt":195.08,"Ds":281,
                "Cu":63.546,"Ag":107.87,"Au":196.97,"Rg":282,
                "Zn":65.38,"Cd":112.41,"Hg":200.59,"Cn":285,
                "B":10.81,"Al":26.982,"Ga":69.723,"In":114.82,"Ta":204.38,"Nh":286,
                "C":12.011,"Si":28.085,"Ge":72.63,"Sn":118.71,"Pb":207.2,"Fl":289,
                "N":14.007,"P":30.974,"As":74.922,"Sb":121.76,"Bi":208.98,"Mc":290,
                "O":15.999,"S":32.06,"Se":78.971,"Te":127.60,"Po":209,"Lv":293,
                "F":18.998,"Cl":35.45,"Br":79.904,"I":126.90,"At":210,"Ts":294,
                "He":4.0026,"Ne":20.180,"Ar":39.948,"Kr":83.798,"Xe":131.29,"Rn":222,"Og":294,
                "La":138.91,"Ce":140.12,"Pr":140.91,"Nd":144.24,"Pm":145,"Sm":150,"Eu":151.96,"Gd":157.25,"Tb":158.93,"Dy":162.50,"Ho":164.93,"Er":167.26,"Tm":168.93,"Yb":173.02,"Lu":174.97,
                "Ac":227,"Th":232.04,"Pa":231.04,"U":238.03,"Np":237,"Pu":244,"Am":243,"Cm":247,"Bk":247,"Cf":251,"Es":252,"Fm":257,"Md":258,"No":259,"Lr":266}
