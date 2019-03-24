import numpy as _np

from dataIO import hdf5saver as hds

from ..loading.loader import Loader
from . import mbl_job_defs as job_defs
from . import mbl_misc_defs as misc_defs


class Mbl_Loader(Loader):
    def __init__(self, storage, data_path):
        super(Mbl_Loader, self).__init__(
            misc_defs, job_defs, storage, data_path)

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

    def get_modpar_values(self, file):
        """"
        Extract module parameter values from a filename

        INPUT:

        file - filename
        mode - hcb or tJ_heis studies
        """

        vals = {}
        file, misc_vals = file.split('_tof_')
        names = file.split('_Mod_')

        # quantity - what is stored in the file
        # mods - modules that are stored in the file
        mods = names[1:]

        for mod in mods:

            # SPIN FLIPS
            if (('_ff_' in mod) and ('_dg_' in mod)):
                case = 'flip'  # spin flips module - also contains
            # the random spin disorder

            # HOPPING
            elif (('_ih_' in mod) and ('_dg_' in mod)):
                if '_dg_0' in mod:
                    case = 'hops'  # hopping module
                elif '_dg_1' in mod:
                    case = 'hcb_nn'
                elif '_dg_2' in mod:
                    case = 'hcb_snn'

            # DIAGONAL MODULES:
            elif (('_dg_' in mod) and not (('_ih_' or '_ff_') in mod)):

                # STAGGERED FIELD
                if ('_dg_0' in mod):
                    case = 'h_stagg'
                # HOLE DISORDER
                if ('_dg_1' in mod):
                    case = 'hole'  # random hole disorder module
                # HOLE SYMMETRY BREAKING DISORDER
                elif ('_dg_2' in mod):
                    case = 'hole_sym'
                # SPIN SYMMETRY BREAKING TERM
                elif ('_dg_3' in mod):
                    case = 'spin_sym'
                elif ('_dg_4' in mod):
                    case = 'hcb_dis'

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
        def _check_true(modstring):
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


    def load(filetype, modpar, syspar):

