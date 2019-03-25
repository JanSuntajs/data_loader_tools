"""


"""

import os
import glob
from future.utils import iteritems


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

    modules = []

    def __init__(self, misc_defs_mod, storage, data_path, modules):
        super(Loader, self).__init__()

        if self.__class__.__name__ == "Loader":
            raise ValueError("This class is not intended"
                             " to be instantiated directly.")

        self._misc_defs = misc_defs_mod

        self.storage = storage
        self.data_path = data_path

        for module in modules:
            if module in self._misc_defs.val_cases.keys():
                self.modules.append(module)
            else:
                raise ValueError(('Module {} not in the'
                                  'list of allowed modules!'.format(
                                      module)))

    @property
    def val_cases(self):

        val_cases = self._misc_defs.val_cases.copy()

        return {key: value for (key, value)
                in iteritems(val_cases) if key in self.modules}

    @property
    def pars(self):

        pars_def = self._misc_defs.pars.copy()
        pars = {}
        for key in self.val_cases:
            for param in self.val_cases[key]:
                pars[param] = pars_def[param]
        return pars

    @property
    def default_modpars(self):

        modpar = {}
        for key in self.pars.keys():
            modpar[key] = 0.0
        return modpar

    @property
    def reformat_dict(self):

        return self._misc_defs.reformat_dict

    @property
    def value_format_template(self):

        return self._misc_defs.value_format_template

    @property
    def value_separator_template(self):

        return self._misc_defs.value_separator_template

    @property
    def mod_str(self):
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
            sorted(set([module.strip("!?") for module in self.modules])))
        return mod_names

    def _format_module_string(self, case, modpar):
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
        mod_template = self.value_format_template

        names = []
        if set(self.val_cases[case]) <= set(modpar.keys()):
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
                                 mod_template.format(
                                     param_value, iter_type))

                except KeyError:
                    print(
                        ('format_module_string info:'
                         ' Key {} in modpar not present.')
                        .format(param))
                # rescale param_value

        print('_'.join(names))
        names = '_'.join(names)
    return names

    def _rescale_modpar_params(self, modpar):
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

    def _get_folder(self, *args):
        """
        Returns the path to the actual folder
        with results for a particular combination
        of system and module parameters.

        """
        folder = self.results_root_folder

        for arg in args:

            folder += arg + '/'

        folder_exists = os.path.isdir(folder)
        return folder, folder_exists

    def _system_dict_to_str(self, system_dict={}):
        """
        Converts a dictionary of system parameters
        into a string.

        Parameters:

        system_dict: dict
                A dict describing system
                parameters
        """

        pass

    def _system_str_to_dict(self, system_str=""):
        """
        Converts a string describing system
        parameters to a dict.
        Parameters:
        system_str: str
                A string describing system
                parameters.

        """
        pass

    def get_modpar_values(self, filename=""):
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

    def _cases(self, modpar):
        """
        Returns a dict where
        keys are from the
        self.val_cases dict
        and values are
        formatted module
        strings.

        """
        cases = {}
        for key in self.val_cases:
            cases[key] = self._format_module_string(key, modpar)
        return cases

    def _check_pathstring(self, pathstring, cases, all_cases=True):
        """
        Checks if a given folder or file is to be selected from
        the list of subfolders in a given directory or
        from a list of files in a directory.
        Intented usage: first call self_cases(modpar),
        then plug the argument into _check_pathstring
        as the cases argument.
        INPUT:

        pathstring - a string, foldername or filename
        cases - a dictionary of module cases
        """
        seps = self.value_separator_template
        cases = self._cases(modpar)

        def check_true(modstring):
            """
            We need to treat the quantity substring separately.
            """

            check_quantity = ((modstring.strip() in pathstring)) and (
                pathstring.startswith(modstring.strip()))
            check_modstr = (seps[0] + modstring.strip() +
                            seps[0] in pathstring) or \
                (seps[0] + modstring.strip() + seps[1] in pathstring)
            # print(check_modstr)
            return check_modstr or check_quantity

        cases_fun = {True: all, False: any}

        include = cases_fun[all_cases](check_true(case)
                                       for case in cases.values())

        return include

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
