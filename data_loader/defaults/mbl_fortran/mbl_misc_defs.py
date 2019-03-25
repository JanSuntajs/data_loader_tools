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

from future.utils import iteritems

from . import mbl_job_defs as mjd


def _get_key_from_val(val, dictionary):
    for key, value in iteritems(dictionary):
        if value == val:
            return key


def _extract_pars_keys(param_string):
    """
    A function for extracting parameters
    and their signature symbols from the
    mbl_job_defs.mod_dict.

    Parameters:
    ----------
    param_string: string
                A value corresponding
                to a key from the
                mbl_job_defs.mod_dict.
    Returns:
    modname: string
                Name of the module
    par_keys: dict
                Dictionary containing
                parameters and their
                corresponding
                signature symbols.
    Example
    -------
    Let's take mbl_job_defs.mod_dict['hopping']
    as param_string. It has the following form:

    mbl_hop_ex           kin      S_z
    Parameters

    T= set_t ih 2
    J1= set_j1 dg 0

    Applying the function on this string returns:
    ('mbl_hop_ex', {'T': '_ih_2_', 'J1': '_dg_0_'})
    """
    lines = param_string.split('\n')
    modname = lines[0].split(' ')[0]
    key_template = '_{}_'
    par_keys = {}
    key_pars = {}
    for line in lines:
        if '=' in line:

            par, key = line.split('=')

            key = key.strip(' ').split(' ')
            key = '_'.join(key[1:])
            key = key_template.format(key)

            par_keys[par.strip(' ')] = key
            key_pars[key] = par.strip(' ')
    return modname, par_keys, key_pars


def _get_pars_val_cases():
    """
    A function that creates
    the pars and val_cases
    dicts. See comment strings
    below in this file for an
    explanation of those.

    """
    val_cases = {}
    inv_val_cases = {}
    par_dict = {}
    for key in mjd.mod_dict:
        name, dict_, inv_dict_ = _extract_pars_keys(mjd.mod_dict[key])

        name = name.strip('?!')

        if 'staggered' in key:
            if any('WSYM' in elt for elt in dict_.keys()):
                dict_['H_STAGG'] = dict_.pop('WSYM')

        if 'hcb' in name:
            if any('W' in elt for elt in dict_.keys()):
                dict_['W_hcb'] = dict_.pop('W')
            if any('J' in elt for elt in dict_.keys()):
                for key in dict_.keys():
                    new_key = key.replace('J', 'V')
                    print(new_key)
                    dict_[new_key] = dict_.pop(key)
        par_dict.update(dict_)
        val_cases[name] = set(dict_.keys())
        inv_val_cases[name] = set(inv_dict_.keys())

    return par_dict, val_cases, inv_val_cases

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

# Example:
# pars = {'JOF': '_ff_0',
#         'W': '_dg_0',
#         'T': '_ih_2',
#         'T2': '_ih_2',
#         'J': '_dg_0',
#         'H': '_dg_1',
#         'HSYM': '_dg_2',
#         'WSYM': '_dg_3',
#         'H_STAGG': '_dg_0',
#         'V1': '_dg_1',
#         'V2': '_dg_2',
#         'W_hcb': '_dg_4'}

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
# Example:
# val_cases = {
#     'hops': ['T', 'J1'],
#     'flip': ['J2', 'W'],
#     'hole': ['H'],
#     'hole_sym': ['HSYM'],
#     'spin_sym': ['WSYM'],
#     'h_stagg': ['H_STAGG'],
#     'hcb_nn': ['T', 'V1'],
#     'hcb_snn': ['T2', 'V2'],
#     'hcb_dis': ['W_hcb']


pars, val_cases, inv_val_cases = _get_pars_val_cases()

# how to reformat parameter values - what values to multiply them with
reformat_dict = {'W': 2., 'J2': 4., 'J1': 2., 'WSYM': 2., 'H_STAGG': 2.,
                 'T': 1., 'HSYM': 1., 'H': 1., 'T2': 1., 'V1': 1., 'V2': 1.,
                 'W_hcb': 1.}


# how the modpar parameter values
# are formatted in the files we
# are extracting from
value_format_template = '{:+.5f}d0{}'
value_separator_template = ['Mod_', '_tof']
