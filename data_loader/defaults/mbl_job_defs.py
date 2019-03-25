"""
Module with job definitions used both
in running the main diagonalization
jobs or when running the analysis
code.

"""
from scipy.special import comb


def num_states(size, ne, nu):
    """
    A routine that returns the number
    of states for a given system.

    INPUT:

    size - system size
    ne - number of charge carriers
    nu - number of up spins

    """

    return comb(size, ne, True) * \
        comb(size - ne, nu, True)


#  pack jobs together
mod_dict = {
    "hopping":

    """mbl_hop_ex           kin      S_z
    Parameters

    T= set_t ih 2
    J1= set_j1 dg 0
    """,
    "rd_spins":

    """rd_field_ex?         S^+S^-  null
    Parameters

    J2= set_j2 ff 0
    W= set_w dg 0
    """,

    "rd_holes":

    """rd_holes_ex?         hole_dis         diag
    Parameters

    H= set_h dg 1
    """,
    "hole_sym_break":

    """sybr_h_ex         hole_sym_break
    Parameters

    HSYM= set_hsym dg 2
    """,

    "spin_sym_break":

    """sybr_s_ex         spin_sym_break
    Parameters

    WSYM= set_wsym dg 3
    """,

    "staggered_h":

    """e_field_ex!                  kin_phase       h_staggered
    Parameters


    WSYM= set_wsym dg 0

    """,

    "efield":

    """e_field_ex!                  kin_phase       h_staggered
    Parameters

    T= set_t ih 2

    H= set_wsym dg 0

    """,

    "hcb_nn":  # hard-core bosons, nearest-neighbour hopping

    """hcb_hop_nn_ex    hcb_nn_hop      hcb_nn_int
    Parameters

    T= set_t ih 2
    J1= set_j1 dg 1


    """,
    "hcb_snn":  # hard-core bosons, second-nearest neighbour hopping

    """hcb_hop_snn_ex    hcb_snn_hop      hcb_snn_int
    Parameters

    T2= set_t2 ih 2
    J2= set_j2 dg 2


    """,
    "hcb_rnd":  # hard-core bosons, random disorder

    """hcb_rd_field_ex? hcb_rdn_spin_field
    Parameters

    W= set_w dg 4

    """

}


# jobs packed together
job_dict = {

    # stagg. h, random holes
    'staggered_hole_spin_random':
    [mod_dict['hopping'], mod_dict['rd_spins'],
     mod_dict['rd_holes'], mod_dict['staggered_h']],
    # sym_break, random spin
    'hole_spin_sym_break_hole_spin_random':
    [mod_dict['hopping'], mod_dict['rd_spins'], mod_dict['rd_holes'],
     mod_dict['spin_sym_break'], mod_dict['hole_sym_break']],
    'hcb_snn': [mod_dict['hcb_nn'], mod_dict['hcb_snn'], mod_dict['hcb_rnd']]
}


redef_dict = {

    'heisenberg_odd_sites':
    # sets ne to zero and takes care of the nu number
    {
        'NU': lambda x, y: {'NU': '{}'.format(int((y['s_size'] - 1) / 2))},
        'ne': lambda x, y: {'ne': '{}'.format(0)},
    },

    'spin_zero':
    # sets total spin to zero
    {
        'NU': lambda x, y: {
            'NU': '{}'.format(int((y['s_size'] - y['ne']) / 2))},

    },

    'one_third_doping':
    # takes care of Sz=0 condition and for one third hole doping with respect
    # to system size
    {
        'ne': lambda x, y: {'ne': '{}'.format(int(y['s_size'] / 3))},
        'NU': lambda x, y: {'NU': '{}'.format(int(y['s_size'] / 3))},
    },

    'one_half_doping':
    # takes care of Sz=0 condition and for one half hole doping
    # with respect to system size

    {
        'ne': lambda x, y: {'ne': '{}'.format(int(y['s_size'] / 2))},
        'NU': lambda x, y: {'NU': '{}'.format(int(y['s_size'] / 4))},
    },

    'match_HSYM_with_WSYM':  # ensures that the symbreak parameters match
    {

        'HSYM': lambda x, y: {'HSYM': '{:+.5f}d0'.format(y['WSYM'])},
    },

    'match_JOF_with_J':
    # makes sure that J and JOF are the
    #  same if that is needed

    {

        'JOF': lambda x, y: {'J2': '{:+.5f}d0'.format(0.5 * y['J'])},

    },

    'hcb_interaction':
    {

        'J': lambda x, y: {'J1': '{:+.5f}d0'.format(x)},
        'JOF': lambda x, y: {'J2': '{:+.5f}d0'.format(x)},
        'W': lambda x, y: {'W': '{:+.5f}d0'.format(x)}

    },


    'hcb_half_filling':
    {

        'ne': lambda x, y: {'ne': '{}'.format(int(y['s_size'] / 2))},
        'NU': lambda x, y: {'NU': '{}'.format(0)},

    },

    'hcb_match_JOF_with_J':
    # makes sure that J and JOF are the
    #  same if that is needed

    {

        'JOF': lambda x, y: {'J2': '{:+.5f}d0'.format(y['J'])},

    },


    'lvl_var_set_percentage':

    {

        'min_ener': lambda x, y: {'min_ener':
                                  '{:+.2f}'.format(
                                      0.5 * (1 - 500 / \
                                             num_states(y['s_size'],
                                                        y['ne'], y['nu'])))}

    }

}



