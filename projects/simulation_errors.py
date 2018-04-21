from main import *
from phase_estimation import *
import matplotlib.pyplot as plt

coupling_map = [[1, 0], [1, 2], [2, 3], [3, 4], [3, 14], [5, 4], [6, 5], [6, 7], [6, 11], [7, 10],
                [8, 7], [9, 8], [9, 10], [11, 10], [12, 5], [12, 11], [12, 13], [13, 4], [13, 14],
                [15, 0], [15, 2], [15, 14]]
basis_gates = "u1,u2,u3,cx,id"


def gen_noise_params(relaxation, depol, pauli, unitary, gates=["U"], gate_time=1):
    factor = np.exp(1j*unitary)
    matrix_dephase = [
        [[1, 0], [0, 0]],
        [[0, 0], [factor.real, factor.imag]]
    ]
    pauli_dephase = [1-pauli, 0, 0, pauli]
    d = {}
    if pauli or unitary:
        if depol == 0:
            depol = 1e-5
    if relaxation:
        d["relaxation_rate"] = relaxation
        d["thermal_populations"] = [1,0]
    for g in gates:
        d[g] = {"gate_time": gate_time}
        if depol:
            d[g]["p_depol"] = depol
        if pauli:
            d[g]["p_pauli"] = pauli_dephase
        if unitary:
            d[g]["U_error"] = matrix_dephase
    return d

def fill_counts(counts, n):
    for i in range(2**n):
        s = "{:b}".format(i)
        s = "0"*(n-len(s))+s
        if s not in counts:
            counts[s] = 0
    return counts


def create_binary_phase_str(phase, n):
    if phase < 0: phase = 1+phase
    if phase > 1: phase = phase-1
    s = "{:b}".format(int(phase*2**n)).rjust(n, "0")
    s = "".join(reversed(s))
    return s

def get_error(phase, counts):
    key = create_binary_phase_str(phase, len(list(counts.keys())[0]))
    try:
        return counts[key]/sum(counts.values())
    except KeyError:
        return 0

def get_error_for_close(phase, counts):
    n = len(list(counts.keys())[0])
    key = create_binary_phase_str(phase, n)
    key1 = create_binary_phase_str(phase+2**-n, n)
    key2 = create_binary_phase_str(phase-2**-n, n)
    x = 0
    if key in counts: x += counts[key]
    if key != key1 and key1 in counts: x += counts[key1]
    if key != key2 and key2 in counts: x += counts[key2]
    print(x, key, key1, key2)
    return x/sum(counts.values())

def run_pe_circuit(phase, n, a=0, relaxation=0, depol=0, pauli=0, unitary=0):
    if a:
        qp, qc, qrs, cr = setup(n, additional_registers={"qr": {"ur": 1, "ar": a}})
        qr, ur, ar = qrs
        qreg = [qr[i] for i in range(len(qr))]
        qreg += [ar[i] for i in range(len(ar))]
    else:
        qp, qc, qrs, cr = setup(n, additional_registers={"qr": {"ur": 1}})
        qr, ur = qrs
        qreg = [qr[i] for i in range(len(qr))]

    def cu(qc, ctl, ur, n):
        p = (n*phase)%1
        if not (p < 1e-5 or 1-p < 1e-5):
            qc.cu1(p*2*np.pi, ctl, ur[0])

    qc.x(ur[0])

    phase_estimation(qc, qreg, ur, cu)

    qc.measure(qr, cr)

    noise_params = gen_noise_params(relaxation, depol, pauli, unitary)
    res = execute(qp, config={"noise_params": noise_params}, coupling_map=coupling_map,
                  basis_gates=basis_gates)
    counts = res.get_counts(get_name())
    return counts

def error_fun_run(fun, bounds, N, phase=None):
    x = np.linspace(*bounds, N)
    errors = []
    data = {"closest": []}
    b = phase==None
    for e in x:
        counts = fun(e)
        if b: phase = e
        errors+=[get_error(phase, counts)]
        print(errors[-1])
        data[str(e)] = counts
        print(counts)
        data["closest"] += [get_error_for_close(phase, counts)]
    return x, errors, data


def relaxation_run(phase, n, a=0, depol=0, pauli=0, unitary=0, bounds=[0, 0.1], N=5):
    fun = lambda e: run_pe_circuit(phase, n, a, e, depol, pauli, unitary)
    return error_fun_run(fun, bounds, N, phase)

def depol_run(phase, n, a=0, relaxation=0, pauli=0, unitary=0, bounds=[0, 1], N=5):
    fun = lambda e: run_pe_circuit(phase, n, a, relaxation, e, pauli, unitary)
    return error_fun_run(fun, bounds, N, phase)

def pauli_run(phase, n, a=0, relaxation=0, depol=0, unitary=0, bounds=[0, 1], N=5):
    fun = lambda e: run_pe_circuit(phase, n, a, relaxation, depol, e, unitary)
    return error_fun_run(fun, bounds, N, phase)

def unitary_run(phase, n, a=0, relaxation=0, depol=0, pauli=0, bounds=[0, np.pi], N=5):
    fun = lambda e: run_pe_circuit(phase, n, a, relaxation, depol, pauli, e)
    return error_fun_run(fun, bounds, N, phase)

def combined_noise_run(phase, n, a=0, relaxation=0, depol=0, pauli=0, unitary=0, N=5, bounds=[0, 1]):
    fun = lambda e: run_pe_circuit(phase, n, a, e*relaxation, e*depol, e*pauli, e*unitary)
    return error_fun_run(fun, bounds, N, phase)

def num_qubits_run(phase, n, a=0, relaxation=0, depol=0, pauli=0, unitary=0, N=5):
    fun = lambda e: run_pe_circuit(phase, int(n+e), a, relaxation, depol, pauli, unitary)
    return error_fun_run(fun, [0, N], N+1, phase)

def num_ancilla_qubits_run(phase, n, a=0, relaxation=0, depol=0, pauli=0, unitary=0, N=5):
    fun = lambda e: run_pe_circuit(phase, n, int(a+e), relaxation, depol, pauli, unitary)
    return error_fun_run(fun, [0, N], N+1, phase)

def phase_run(n, a=0, relaxation=0, depol=0, pauli=0, unitary=0, N=10):
    fun = lambda e: run_pe_circuit(e, n, a, relaxation, depol, pauli, unitary)
    return error_fun_run(fun, [0, 1-2**-N], N)

def plot_phase_counts(hc, phase, n, nn=None):
    bottom = 0.5
    ymin = bottom/(bottom+1)
    phi = list(map(lambda x: x["phase_angle"]*2*np.pi, hc.values()))
    prob = list(map(lambda x: x["percentage"]/100, hc.values()))

    # theta = np.linspace(0.0, 2 * np.pi, 2**n, endpoint=False)
    # radii = max_height*np.random.rand(N)
    if not nn:
        nn = n+1
    width = (2*np.pi) / 2**nn

    ax = plt.subplot(111, polar=True)
    ax.set_xticks([x/2**n*2*np.pi for x in range(2**n)])
    ax.set_xticklabels([round(x/2**n, 3) for x in range(2**n)])
    ax.set_yticks([])
    ax.set_ylim(0, bottom+1)
    ax.yaxis.grid(False)
    ax.xaxis.grid(False)
    ax.axvline(2*np.pi*phase, color="r", ymin=ymin)
    ax.plot(np.linspace(0, 2*np.pi, 1000, endpoint=False), bottom*np.ones(1000), color="black", linewidth=.5)
    for p in [x/2**n*2*np.pi for x in range(2**n)]:
        ax.axvline(p, color="gray", linestyle="dotted", ymin=ymin, linewidth=1, zorder=-1)
    bars = ax.bar(phi, prob, width=width, bottom=bottom)

    # Use custom colors and opacity
    # for r, bar in zip(radii, bars):
    #     bar.set_facecolor(plt.cm.jet(r / 10.))
    #     bar.set_alpha(0.8)

    plt.savefig("simulation_errors/phase_3_d0.01_%f.png"%phase)
    plt.cla()
    #plt.show()

if __name__ == "__main__":
    # x, e, data = phase_run(3, N=2, depol=0)
    n = 3
    for phase in np.linspace(0, 0.125, 30):
        counts = run_pe_circuit(phase, n, depol=0.01)
        hc = handle_counts(counts, n)
        plot_phase_counts(hc, phase, n, nn=5)
    # x, e, _ = num_qubits_run(0.5, 2, N=6, depol=0.001)
    # plt.axhline(y=1/2**4, color="r", linestyle="dashed")
    # plt.plot(x, e)
    # plt.plot(x, data["closest"])
    # plt.show()
