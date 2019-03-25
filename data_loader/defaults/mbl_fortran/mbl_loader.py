import numpy as _np

from dataIO import hdf5saver as hds

from ..loading.loader import Loader
from ..utils.helper_fun import get_key_from_val
from . import mbl_job_defs as job_defs
from . import mbl_misc_defs as misc_defs


class Mbl_Loader(Loader):
    def __init__(self, storage, data_path):
        super(Mbl_Loader, self).__init__(
            misc_defs, storage, data_path)
        self.inv_val_cases = misc_defs.inv_val_cases
    #  methods

    def system_dict_to_str(self, system_dict):
        """
                Converts a dict of system parameters
                into a string

        Parameters:

        system_dict: dict
                A dict describing system
                parameters

        """
        if system_dict['base'] is False:
            system_dict['base'] = 'F'
        elif system_dict['base'] is True:
            system_dict['base'] = 'T'

        if system_dict['size'] < system_dict['ne']:
            raise ValueError(
                ('Number of charge carriers cannot be greater'
                 'than the system size.'))
        elif system_dict['size'] < system_dict['nu']:
            raise ValueError(
                'Number of up-spins cannot be greater than the system size.')
        elif system_dict['size'] < (system_dict['ne'] + system_dict['nu']):
            raise ValueError(
                ('The number of up-spins and charge carriers must'
                    'not be greater than the system size.'))
        return 'D{}SS{:0>4}_Ne{:0>3}{}_NU{:0>3}'.format(system_dict['dim'],
                                                        system_dict['size'],
                                                        system_dict['ne'],
                                                        system_dict['base'],
                                                        system_dict['nu'])

    def system_str_to_dict(self, system_str):
        """
        Converts a string describing system
        parameters to a dict.
        Parameters:
        system_str: str
                A string describing system
                parameters.

        """

        syspar_file = system_str.strip('.dat').strip('.txt')

        syspar = {}

        low = syspar_file.find('D') + 1
        up = syspar_file.find('SS')
        syspar['dim'] = int(syspar_file[low:up])

        low = up + 2
        up = syspar_file.find('_Ne')
        syspar['size'] = int(syspar_file[low:up])

        low = up + 3
        base = 'F'
        if 'T' in syspar_file:
            base = 'T'
        syspar['base'] = base
        up = syspar_file.find(base)

        syspar['ne'] = int(syspar_file[low:up])
        syspar['nu'] = int(syspar_file[-3:])

        return syspar

    @staticmethod
    def _split_modname(filename):
        """
        A function that splits a filename
        in such a way that it returns
        substrings describing particular
        contributions to the Hamiltonian.

        Example:
        filename:

        *_Mod_-1.00000d0_ih_2_+1.10000d0_dg_2_Mod_-1.00000d0_ih_2_+1.10000d0_dg_1_tof_0000.npy

        The function would split the string according to the '_Mod_'
        delimiter and return a list without the preceeding part
        denoted by *.

        Return would thus be:
        [-1.00000d0_ih_2_+1.10000d0_dg_2_,
        -1.00000d0_ih_2_+1.10000d0_dg_1_]
        """

        file, other = filename.split('_tof_')
        mods = file.split('_Mod_')[1:]

        return mods

    @staticmethod
    def _extract_iters(mod):
        """
        A function that returns iteration
        signifiers from a modname substring.

        Example:
        mod: -1.00000d0_ih_2_+1.10000d0_dg_1_
        The function should return:

        ['_ih_2_', '_dg_1_']

        """

        mod = mod.replace('-', '/').replace('+', '/')
        iters = mod.split('/')[1:]

        return set([iter_[9:] for iter_ in iters])

    def get_modpar_values(self, file):
        """"
        Extract module parameter values from a filename

        INPUT:

        file - filename
        mode - hcb or tJ_heis studies
        """

        vals = {}

        mods = self._split_modname(file)
        # invert val_cases

        for mod in mods:

            iters = self._extract_iters(mod)
            case = get_key_from_val(iters, self.inv_val_cases)
            # SPIN FLIPS
            # if (('_ff_' in mod) and ('_dg_' in mod)):
            #     case = 'flip'  # spin flips module - also contains
            # # the random spin disorder

            # # HOPPING
            # elif (('_ih_' in mod) and ('_dg_' in mod)):
            #     if '_dg_0' in mod:
            #         case = 'hops'  # hopping module
            #     elif '_dg_1' in mod:
            #         case = 'hcb_nn'
            #     elif '_dg_2' in mod:
            #         case = 'hcb_snn'

            # # DIAGONAL MODULES:
            # elif (('_dg_' in mod) and not (('_ih_' or '_ff_') in mod)):

            #     # STAGGERED FIELD
            #     if ('_dg_0' in mod):
            #         case = 'h_stagg'
            #     # HOLE DISORDER
            #     if ('_dg_1' in mod):
            #         case = 'hole'  # random hole disorder module
            #     # HOLE SYMMETRY BREAKING DISORDER
            #     elif ('_dg_2' in mod):
            #         case = 'hole_sym'
            #     # SPIN SYMMETRY BREAKING TERM
            #     elif ('_dg_3' in mod):
            #         case = 'spin_sym'
            #     elif ('_dg_4' in mod):
            #         case = 'hcb_dis'

            # finds the number in the modpar part of the filename string
            ind0 = 0
            for val_case in self.val_cases[case]:
                ind = str.index(mod, self.pars[val_case])
                numstr = mod[ind0: ind]
                vals[val_case] = _np.float(numstr.replace('d', 'e'))

                ind0 = ind + 5

        # formatting where needed so that the proper
        # parameter values are obtained
        # reformat_dict={'W':2, 'J':4, 'JOF':2, 'WSYM':2, 'H_STAGG':2}

        # reformats (rescales) the extracted parameter value
        for key in self.reformat_dict:
            try:
                vals[key] = float(self.reformat_dict[key]) * vals[key]
            except KeyError:
                print(
                    ('get_modpar_values info: Key'
                     '{} in vals not yet initialized').format(key))

        return vals

    @staticmethod
    def _check_pathstring(pathstring, cases, all_cases=True):
        """
        Checks if a given folder or file is to be selected from
        the list of subfolders in a given directory or
        from a list of files in a directory.

        INPUT:

        pathstring - a string, foldername or filename
        cases - a dictionary of module cases
        """
        def check_true(modstring):
            """
            We need to treat the quantity substring separately.
            """
            check_quantity = ((modstring.strip() in pathstring)) and (
                pathstring.startswith(modstring.strip()))
            check_modstr = ('Mod_' + modstring.strip() +
                            '_Mod' in pathstring) or \
                ('Mod_' + modstring.strip() + '_tof' in pathstring)
            # print(check_modstr)
            return check_modstr or check_quantity

        cases_fun = {True: all, False: any}

        include = cases_fun[all_cases](check_true(case)
                                       for case in cases.values())

        return include

    # def load(filetype, modpar, syspar):
