import Qconfig
import sys
import json
import os
import time
from datetime import datetime
from qiskit import QuantumProgram, QuantumCircuit
from qiskit.tools.visualization import plot_histogram, plot_circuit


def is_simulation(backend):
    if backend in ["ibmqx2", "ibmqx4", "ibmqx5"]:
        return False
    else:
        return True


def setup_circuit(qp, num_reg, name=None):
    # Adds circiut to existing program.
    # Automatic Naming
    if name == None:
        name = sys.argv[0][:-3]
    c = 0
    post = ''
    ppost = '%d' % len(qp.get_circuit_names()) if len(qp.get_circuit_names()) > 0 else ''
    while name+post in qp.get_circuit_names():
        c += 1
        post = '_%d' % c
    qr = qp.create_quantum_register('qr'+ppost, num_reg)
    cr = qp.create_classical_register('cr'+ppost, num_reg)
    qc = qp.create_circuit(name+post, [qr, cr])
    return qc, qr, cr


def setup(num_reg, name=None, login=True):
    # Returns Quantum Program, Quantum Circuit.
    qp = QuantumProgram()
    if login:
        qp.set_api(Qconfig.APItoken, Qconfig.config['url'])
    qc, qr, cr = setup_circuit(qp, num_reg, name)
    return qp, qc, qr, cr


def execute(qp, circuits=None, backend="local_qiskit_simulator", shots=1024, sav=1, info=""):
    # Executes specified circuits. If none specified, executes all.
    if circuits == None:
        circuits = list(qp.get_circuit_names())
    result = qp.execute(circuits, backend=backend,
                        shots=shots, timeout=1200, wait=10)
    time.sleep(1)
    print(result)
    if sav == 1 and not is_simulation(backend):
        save(result, backend, info=info)
    elif sav == 2:
        save(result, backend, info=info)
    return result


def make_dirs(name, simulation):
    path = name+"/"
    try:
        os.mkdir(name)
    except FileExistsError:
        pass
    if simulation:
        path += "simulations/"
        try:
            os.mkdir(name+"/simulations")
        except FileExistsError:
            pass
    return path+name+"_<+>.json"


def save(result, backend, circuits=None, info=""):
    # saves the data as json
    if circuits == None:
        circuits = result.get_names()
    try:
        jid = result.get_job_id()
    except KeyError:
        jid = "local"
    for name in circuits:
        data = result.get_data(name)
        qasm = result.get_ran_qasm(name)
        path = make_dirs(name, is_simulation(backend))
        path = path.replace(
            "<+>", datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))
        with open(path, "w") as f:
            json.dump({"job_id": jid, "info": info, "data": data, "qasm": qasm}, f, indent=4)


def load_file(filename):
    with open(filename, "r") as f:
        d = json.load(f)
    return d


def load(name, filename=None, info=None, h=1):
    if filename==None:
        d = sorted(os.listdir(name), reverse=True)
        d = list(map(lambda s: name+"/"+s, d))
        cur = ""
        c = 0
        for e in d:
            c+=1
            cur = e
            x = load_file(e)
            if info:
                if x["info"] != info:
                    c-=1
            if c == h:
                break
        filename = cur
    return load_file(filename)


def visualize(result, circuits=None, ntk=False):
    # Visualizes specified curcuit results as histogram.
    if circuits == None:
        circuits = result.get_names()
    for name in circuits:
        plot_histogram(result.get_counts(name), ntk)
