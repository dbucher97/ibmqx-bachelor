from main import *
from phase_estimation import *

p_depol = 0.01
coherent_dephase_prob = 0.0
pauli_dephase_prob = 0.0
factor = np.exp(1j*coherent_dephase_prob)
matrix_dephase = [
    [[1, 0], [0, 0]],
    [[0, 0], [factor.real, factor.imag]]
]
pauli_dephase = [1-pauli_dephase_prob, 0, 0, pauli_dephase_prob]

noise_params =  {
    # "reset_error": p_reset,
    # "readout_error": [p_m0, p_m1],
    # "relaxation_rate": r,
    # "thermal_populations": [p0, p1],
    # "measure": {
    #     "p_depol": p_depol, #p_meas,
    #     # "p_pauli": [pI_meas, pX_meas, pY_meas, pZ_meas],
    #     "gate_time": 1,#t_meas,
    #     # "U_error": matrix_meas
    # },
    # "reset": {
    #     "p_depol": p_depol, #p_res,
    #     "p_pauli": [pI_res, pX_res, pY_res, pZ_res],
    #     "gate_time": 1, #t_res,
    #     "U_error": matrix_res
    # },
    "id": {
        "p_depol": p_depol,  # p_id,
        "p_pauli": pauli_dephase, #[pI_id, pX_id, pY_id, pZ_id],
        "gate_time": 1,  # , t_id,
        "U_error": matrix_dephase, #matrix_id
    },
    "U": {
        "p_depol": p_depol,  # p_u,
        "p_pauli": pauli_dephase, #[pI_u, pX_u, pY_u, pZ_u],
        "gate_time": 1,  # t_u,
        "U_error": matrix_dephase, #matrix_u
    },
    "X90": {
        "p_depol": p_depol,  # p_x90,
        "p_pauli": pauli_dephase, #[pI_x90, pX_x90, pY_x90, pZ_x90],
        "gate_time": 1,  # t_X90,
        "U_error": matrix_dephase, #matrix_x90,
        # "amp_error": alpha,
        # "phase_error": omega
    },
    # "CX": {
    #     "p_depol": p_depol, #p_cx,
    #     "p_pauli": [pII_cx, pIX_cx, pIY_cx, pIZ_cx,
    #                 pXI_cx, pXX_cx, pXY_cx, pXZ_cx,
    #                 pYI_cx, pYX_cx, pYY_cx, pYZ_cx,
    #                 pZI_cx, pZX_cx, pZY_cx, pZZ_cx],
    #     "gate_time": 1, #t_cx,
    #     "U_error": matrix_cx,
    #     "amp_error": alpha,
    #     "zz_error": gamma
}


def gen_noise_params(p_depol):
    return {
        # "reset_error": p_reset,
        # "readout_error": [p_m0, p_m1],
        # "relaxation_rate": r,
        # "thermal_populations": [p0, p1],
        # "measure": {
        #     "p_depol": p_depol, #p_meas,
        #     # "p_pauli": [pI_meas, pX_meas, pY_meas, pZ_meas],
        #     "gate_time": 1,#t_meas,
        #     # "U_error": matrix_meas
        # },
        # "reset": {
        #     "p_depol": p_depol, #p_res,
        #     "p_pauli": [pI_res, pX_res, pY_res, pZ_res],
        #     "gate_time": 1, #t_res,
        #     "U_error": matrix_res
        # },
        "id": {
            "p_depol": p_depol,  # p_id,
            "p_pauli": pauli_dephase, #[pI_id, pX_id, pY_id, pZ_id],
            "gate_time": 1,  # , t_id,
            "U_error": matrix_dephase, #matrix_id
        },
        "U": {
            "p_depol": p_depol,  # p_u,
            "p_pauli": pauli_dephase, #[pI_u, pX_u, pY_u, pZ_u],
            "gate_time": 1,  # t_u,
            "U_error": matrix_dephase, #matrix_u
        },
        "X90": {
            "p_depol": p_depol,  # p_x90,
            "p_pauli": pauli_dephase, #[pI_x90, pX_x90, pY_x90, pZ_x90],
            "gate_time": 1,  # t_X90,
            "U_error": matrix_dephase, #matrix_x90,
            # "amp_error": alpha,
            # "phase_error": omega
        },
        # "CX": {
        #     "p_depol": p_depol, #p_cx,
        #     "p_pauli": [pII_cx, pIX_cx, pIY_cx, pIZ_cx,
        #                 pXI_cx, pXX_cx, pXY_cx, pXZ_cx,
        #                 pYI_cx, pYX_cx, pYY_cx, pYZ_cx,
        #                 pZI_cx, pZX_cx, pZY_cx, pZZ_cx],
        #     "gate_time": 1, #t_cx,
        #     "U_error": matrix_cx,
        #     "amp_error": alpha,
        #     "zz_error": gamma
    }


def fill_counts(counts, n):
    for i in range(2**n):
        s = "{:b}".format(i)
        s = "0"*(n-len(s))+s
        if s not in counts:
            counts[s] = 0
    return counts


n=3

depols = np.linspace(0.001, 1, 20)
errors = []

from pprint import pprint
for i in depols:
    #pprint(noise_params)
    noise_params = gen_noise_params(i)
    #pprint(noise_params)
    qp, qc, qrs, cr = setup(n, name="depol%f"%i, additional_registers={"qr": {"ur": 1}})
    qr, ur = qrs

    qc.x(ur[0])

    def cu(qc, ctl, ur, n): return qc.cu1(n*2*np.pi*0.125, ctl, ur[0])

    phase_estimation(qc, qr, ur, cu)
    # qc.x(qr[2])

    #qc.barrier(qr)
    qc.measure(qr, cr)

    res = execute(qp, config={"noise_params": noise_params})
    # print(res.get_counts(get_name()))
    res = handle_counts(res.get_counts("depol%f"%i), n)
    try:
        err = 1-res.get("001").get("percentage")/100
    except AttributeError:
        err = 1
    errors += [err]
    #print_handled_counts(res)

import matplotlib.pyplot as plt

plt.plot(depols, errors)
plt.show()

