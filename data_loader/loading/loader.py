"""


"""

import os
import glob


class Loader(object):

    """

    Parameters:
    -----------
    misc_defs_mod: module
                A module with miscellanea definitions
                of parameter names. Needs to have the
                following attributes:
                pars: dict
                val_cases: dict
                reformat_dict
                value_format_template
    job_defs_mod: module
                A module with job definitions. Need
                to have the following attributes:
                redef_dict: dict
                job_dict: dict
                mod_dict: dict
    """

    def __init__(self, misc_defs_mod, job_defs_mod, storage, data_path):
        super(Loader, self).__init__()

        self.pars = misc_defs_mod.pars
        self.val_cases = misc_defs_mod.val_cases
        self.reformat_dict = misc_defs_mod.reformat_dict
        self.value_format_template = misc_defs_mod.value_format_template

        self.redef_dict = job_defs_mod.redef_dict
        self.job_dict = job_defs_mod.job_dict
        self.mod_dict = job_defs_mod.mod_dict

        self.storage = storage
        self.data_path = data_path

    @staticmethod
    def mod_str(modules):
        """
        Creates a joined string of modules given
        the name of Hamiltonian's modules as an
        input.

        This routine is needed in finding the
        locations of the data files needed for
        analysis and plotting.

            Parameters
            ----------
            modules: list
                            A list of strings which should
                            correspond to Hamiltonian
                            module names
            Returns
            -------
            mod_names: string
                            A joined string of parameter names
        """

        mod_names = "".join(
            sorted(set([module.strip("!?") for module in modules])))
        return mod_names

    def format_module_string(self, case, modpar):
        """
        A function that casts the string
        describing the module names into
        a proper form.

        Parameters:
        -----------
        case: string
                    An entry from the self.pars
                    dict.
            modpar: dict
                    A dictionary of key,value
                    pairs describing module
                    parameters with their
                    names and their
                    corresponding values.

        """
        names = []
        mod_template = self.value_format_template

        if set(set.val_cases[case]) <= set(modpar.keys()):
            for param in self.val_cases[case]:
                i = 0
                try:
                    iter_type = self.pars[param]
                    param_value = modpar[param]
                    param_value *= 1. / float(self.reformat_dict[param])

                    # offdiagonal term written first, then the diagonal
                    if '_dg_' in iter_type:
                        i = len(names)

                    names.insert(i,
                                 mod_template.format(param_value, iter_type))

                except KeyError:
                    print(
                        ('format_module_string info:'
                         ' Key {} in modpar not present.')
                        .format(param))
                # rescale param_value

        print('_'.join(names))
        return '_'.join(names)

    def rescale_modpar_params(self, modpar):
        """
        A function that rescales the module
        parameters properly
        """
        modpar_ = modpar.copy()
        for param in modpar:
            try:
                modpar_[param] *= 1. / float(self.reformat_dict[param])
            except KeyError:
                print(
                    ('rescale_modpar_params info: Key {}'
                        'not present in reformat_dict.')
                    .format(param))

        return modpar_

    @property
    def results_root_folder(self):
        """
        Returns the path to the numerical results folder
        and checks whether the folder exists. """

        folder = self.storage + '/' + self.data_path

        return folder

    def get_results_folder(self, *args):
        """
        Returns the path to the actual folder
        with results for a particular combination
        of system and module parameters.

        """
        folder = self.results_root_folder()

        for arg in args:

            folder += arg + '/'

        folder_exists = os.path.isdir(folder)
        return folder, folder_exists

    def system_dict_to_str(self, system_dict):
        """
        Converts a dictionary of system parameters
        into a string.

        Parameters:

        system_dict: dict
                A dict describing system
                parameters
        """

        pass

    def system_str_to_dict(self, system_str):
        """
        Converts a string describing system
        parameters to a dict.
        Parameters:
        system_str: str
                A string describing system
                parameters.

        """

    def get_modpar_values(self, filename):
        """
        A routine for extracting module
        parameter values from a filename.

        Parameters
        ----------

        filename: string
                    A filename from which
                    the parameter values
                    are to be extracted.

        Returns
        -------

        vals: dict
                    A dictionary of parameter
                    values.
        """

        pass

    def _get_results_file(self, filestr, results_folder):
        """
        A routine that creates a list of appropriate
        filenames in the folder for loading.

        Parameters
        ----------

        filestr: str
                    A filename string or a substring of the
                    desired file to be loaded
        results_folder:
                    Path to the folder with results.

        Returns
        -------

        files: list
                    A list of files appropriate for loading.
                    It is up to the user to decide which
                    loading method should work the best.
        """
        cwd = os.getcwd()
        try:
            os.chdir(results_folder)
        except FileNotFoundError:
            print('Folder {} does not exist!'.format(results_folder))
            pass

        files = glob.glob('*' + filestr + '*')
        print(os.getcwd())
        os.chdir(cwd)

        return files



