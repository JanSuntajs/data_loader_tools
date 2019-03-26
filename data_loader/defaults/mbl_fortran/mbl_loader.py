import numpy as _np

import os
from future.utils import iteritems

from ...loading.loader import Loader
from ...utils.helper_fun import get_key_from_val
from . import mbl_misc_defs as misc_defs


class Mbl_Loader(Loader):
    """
    A class for loading mbl datasets
    that inherits from the loader
    class.

    Some attributes explained (more
    has to be done in the future):

    load_method:
    """

    def __init__(self, storage, data_path, modules):
        super(Mbl_Loader, self).__init__(
            misc_defs, storage, data_path, modules)

    #  methods

    @property
    def inv_val_cases(self):
        inv_val_cases = self._misc_defs.inv_val_cases.copy()

        return {key: value for (key, value)
                in iteritems(inv_val_cases) if key in self.modules}

    def _system_dict_to_str(self, system_dict):
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

    def _system_str_to_dict(self, system_str):
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

    def _split_modname(self, filename):
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

        seps = self.value_separator_template
        file, other = filename.split(seps[1])
        mods = file.split(seps[0])[1:]

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
        ['_ih_2_': '-1.00000d0', '_dg_1_': '+1.10000d0'  ]
        """

        mod = mod.replace('-', '/').replace('+', '/')
        iters = mod.split('/')[1:]

        iter_vals = dict([iter_.split('d0')[::-1] for iter_ in iters])

        iters = set(iter_vals.keys())

        return iters, iter_vals

    def get_modpar_values(self, file):
        """"
        Extract module parameter values from a filename
        string.

        Parameters
        ----------
        file - str

            Filename of the form:
            *_Mod_-1.00000d0_ih_2_+1.10000d0_dg_2_Mod_+5.00000d0
            _dg_4_Mod_-1.00000d0_ih_2_+1.10000d0_dg_1_tof_0000*

            The routine extracts the numerical values and
            associates them to their parameters based on the values
            of symbols such as _ih_2_, _dg_2_ and the like.

        Returns
        -------
        vals: dict
            A dict of key-value pairs where key is a parameter
            (for instance T, T1, V, V1 - the usual Hamiltonian
            model parameters) and values are the (rescaled)
            numerical values.


        """

        vals = {}

        mods = self._split_modname(file)
        # invert val_cases

        for mod in mods:

            iters, iter_vals = self._extract_iters(mod)
            case = get_key_from_val(iters, self.inv_val_cases)

            # finds the number in the modpar part of the filename string
            for param in self.val_cases[case]:

                param_symbol = self.pars[param]
                vals[param] = _np.float(iter_vals[param_symbol])

        # formatting where needed so that the proper
        # parameter values are obtained
        # reformats (rescales) the extracted parameter value

        for key in vals:
            vals[key] *= float(self.reformat_dict[key])

        return vals

    def load(self, datatype, filetype, syspar, modpar, *args, **kwargs):
        """


        """

        sys_str = self._system_dict_to_str(syspar)

        args = [self.mod_str, sys_str]
        # navigate towards sys_str folder
        data_path, check_exist = self._get_folder(
            datatype, *args)

        cases = self._cases(modpar)

        folders = os.listdir(data_path)

        folder = next((folder for folder in folders if self._check_pathstring(
            folder, cases)), None)

        results_folder = data_path + '/' + folder

        results = self._get_results_file(
            filetype, results_folder, *args, **kwargs)

        return results
