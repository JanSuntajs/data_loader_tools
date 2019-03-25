from future.utils import iteritems


def get_key_from_val(value, dict):
    """
    A routine that extracts a key
    corresponding to a dictionary
    value, given that the mapping
    is unique.

    Parameters
    ----------
    value - dictionary value

    dict: a dictionary of key, value
              pairs.

    """

    for key, val in iteritems(dict):

        if val == value:

            return key


def merge_dicts(keys, template_dict={}):

    default = {}

    for key in keys:
        try:
            default.update(template_dict[key])
        except KeyError:
            print('Key {} not found in template dict!'.format(key))

    return default
