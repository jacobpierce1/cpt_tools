import sys

from .cpt_config import *
from .nuclear_data import nuclear_data 

# sys.path.append( './' ) 

# import .cpt_config
# import nuclear_data
# import nuclear_data
# cesium_133_mass = 132905451.961
# cesium_133_omega =  657844.45


# mass is the mass of the ion, not mass of atom
def mass_to_omega( ion_mass, q, atomic_mass = 0 ) :

    if atomic_mass :
        ion_mass -= q * nuclear_data.electron_mass 

    omega = ( q * calibrant_omega
              * ( calibrant_mass - nuclear_data.electron_mass )
              / ion_mass )
    return omega




# once again, return mass of the ion, not of the atom
def omega_to_mass( omega, q, atomic_mass = 0 ) :
    mass = ( q * calibrant_omega
             * ( calibrant_mass - nuclear_data.electron_mass )
             / omega )

    if atomic_mass :
        mass += q * nuclear_data.electron_mass

    return mass



def find_wc( wc_guess, diff_phi_rad_abs, diff_phi_rad_unc, tacc ):
    Ni = int(wc_guess * tacc)
    wc_abs = (diff_phi_rad_abs + 2 * pi * Ni) / (2 * pi * tacc)
    wc_unc = diff_phi_rad_unc / (2 * pi * tacc)

    Nf = Ni

    if (wc_abs - wc_guess) > 1:
        Nf = Ni - 1
        wc_abs = (diff_phi_rad_abs + 2 * pi * Nf) / (2 * pi * tacc)

    if (wc_abs - wc_guess) < -1:
        Nf = Ni + 1
        wc_abs = (diff_phi_rad_abs + 2 * pi * Nf) / (2 * pi * tacc)

    return wc_abs, wc_unc, Ni, Nf
