"""
A module containing job type
definitions for the mbl type
job studies which come handy
during the data extraction
and subsequent analysis. By
putting these inside an
installable package, the
parameters can be defined
system-wide.

Module's attributes:

pars: dict
        A parameter dictionary which
        provides information on which
        hamiltonian parts to look for
        in parameter name strings.
val_cases: dict
        A dict specifying which parts
        of the actual physical hamiltonians
        correspond to which parameter names.
reformat_dict: dict
        A dict specifying how to reformat
        the data entries (reformat -> rescale)

"""


#  Dict describing the Hamiltonian module. Contents are
#  as follows:

# JOF: offdiagonal J heisenberg coupling
# J: diagonal J Heisenberg coupling
# W: spin disorder field parameter
# H: potential(hole) disorder field parameter
# T, T2: nearest and next-nearest neighbour kinetic hopping
# HSYM, WSYM: potential and spin symmetry breaking terms
# H_STAGG: staggered magnetic field
# V1, V2: nearest and next-nearest interaction contribuitons
# W_hcb: hard-core bosonic contribution towards disorder

pars = {'JOF': '_ff_0',
        'W': '_dg_0',
        'T': '_ih_2',
        'T2': '_ih_2',
        'J': '_dg_0',
        'H': '_dg_1',
        'HSYM': '_dg_2',
        'WSYM': '_dg_3',
        'H_STAGG': '_dg_0',
        'V1': '_dg_1',
        'V2': '_dg_2',
        'W_hcb': '_dg_4'}

# Which cases comprise the Hamiltonian

# 'hops': hopping module with T and diagonal Heisenberg
# coupling
# 'flip': spin flips module with the offdiagonal Heisenberg
# coupling and spin disorder
# 'hole': hole disorder diagonal terms
# 'hole_sym', 'spin_sym': hole and spin disorder symmetry
# breaking diagonal terms
# 'h_stagg': staggered magnetic field
# 'hcb_nn': nearest neighbour contributions to hcb interaction
# and hopping
# 'hcb_snn': next-nearest neighbour contributions to hcb
# interaction and hopping
# 'hcb_dis':disorder in the hard-core boson case

val_cases = {
    'hops': ['T', 'J'],
    'flip': ['JOF', 'W'],
    'hole': ['H'],
    'hole_sym': ['HSYM'],
    'spin_sym': ['WSYM'],
    'h_stagg': ['H_STAGG'],
    'hcb_nn': ['T', 'V1'],
    'hcb_snn': ['T2', 'V2'],
    'hcb_dis': ['W_hcb']

}

# how to reformat parameter values - what values to multiply them with
reformat_dict = {'W': 2., 'J': 4., 'JOF': 2., 'WSYM': 2., 'H_STAGG': 2.,
                 'T': 1., 'HSYM': 1., 'H': 1., 'T2': 1., 'V1': 1., 'V2': 1.,
                 'W_hcb': 1.}


# how the modpar parameter values
# are formatted in the files we
# are extracting from
value_format_template = '{:+.5f}d0{}'
value_separator_template = ['Mod_', '_tof']
