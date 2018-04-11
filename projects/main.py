import Qconfig
import sys
import json
import os
import time
import datetime
from qiskit import QuantumProgram, QuantumCircuit
from qiskit.tools.visualization import plot_histogram, plot_circuit
from qiskit.tools.file_io import file_datestr, save_result_to_file, load_result_from_file
from file_io import file_datestr, save_result_to_file, load_result_from_file
from qbit_mapping import unscramble_counts

BASE_DIR = "/home/david/bachelor/ibmqx/projects/"
os.chdir(BASE_DIR)

meta_results = []


def is_simulation(backend):
    if backend in ["ibmqx2", "ibmqx4", "ibmqx5"]:
        return False
    else:
        return True


def get_name():
    return sys.argv[0][:-3]


def setup_circuit(qp, num_reg, additional_registers=None, name=None):
    # Adds circiut to existing program.
    # Automatic Naming
    if name == None:
        name = get_name()
    c = 0
    post = ''
    ppost = '%d' % len(qp.get_circuit_names()) if len(qp.get_circuit_names()) > 0 else ''
    while name+post in qp.get_circuit_names():
        c += 1
        post = '_%d' % c
    qr = qp.create_quantum_register('qr'+ppost, num_reg)
    cr = qp.create_classical_register('cr'+ppost, num_reg)
    qrs = []
    crs = []
    if additional_registers:
        if "qr" in additional_registers:
            for reg_name, reg_len in additional_registers["qr"].items():
                qrs += [qp.create_quantum_register(reg_name, reg_len)]
        if "cr" in additional_registers:
            for reg_name, reg_len in additional_registers["cr"].items():
                crs += [qp.create_classical_register(reg_name, reg_len)]
    qc = qp.create_circuit(name+post, [qr]+qrs, [cr]+crs)
    if qrs:
        qr = [qr] + qrs
    if crs:
        cr = [cr] + crs
    return qc, qr, cr


def setup(num_reg, additional_registers=None, name=None, login=False):
    # Returns Quantum Program, Quantum Circuit.
    qp = QuantumProgram()
    if login and not (len(sys.argv) > 1 and (sys.argv[1] == "load" or sys.argv[1] == "simulate")):
        qp.set_api(Qconfig.APItoken, Qconfig.config['url'])
    qc, qr, cr = setup_circuit(qp, num_reg, name=name, additional_registers=additional_registers)
    return qp, qc, qr, cr


def execute(qp, circuits=None, backend="local_qiskit_simulator", shots=1024, sav=1, meta=None,
            unscramble=True, max_credits=3, config=None):
    # Executes specified circuits. If none specified, executes all.
    if len(sys.argv) > 1 and sys.argv[1] == "load":
        h = 1
        try:
            h = int(sys.argv[2])
        except IndexError:
            pass
        except ValueError:
            pass
        result = load_result(meta=meta, h=h)
    else:
        if len(sys.argv) > 1 and sys.argv[1] == "simulate":
            backend = "local_qiskit_simulator"
        if circuits == None:
            circuits = list(qp.get_circuit_names())
        result = None
        while result == None or result.get_status() == "ERROR":
            if not result == None:
                jid = result.get_job_id()
                print(jid, "failed")
                add_failed_jobids([jid], name=result._qobj["circuits"][0]["name"])
            result = qp.execute(circuits, backend=backend,
                                shots=shots, timeout=1200, wait=10, max_credits=max_credits,
                                config=config)
        if sav == 2 or (sav == 1 and not is_simulation(backend)):
            save_result(result, meta=meta)
    if unscramble and backend == "ibmqx5":
        for d in result._result["result"]:
            d["data"]["counts"] = unscramble_counts(d["data"]["counts"])
    return result


def add_failed_jobids(jobids, name=None):
    if name == None:
        name = get_name()
    make_dirs(name, False)
    path = os.path.join(name, "failed")
    if not os.path.exists(path):
        os.mkdir(path)
    with open(os.path.join(path, "job_ids.txt"), "a") as f:
        for jid in jobids:
            f.write(jid+"\t"+'{:%Y_%m_%d_%H_%M}'.format(datetime.datetime.now())+"\n")


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
    return path


def save_result(result, name=None, meta=None):
    # saves the data as json
    if not name:
        name = get_name()
    backend = result._qobj.get("config").get("backend")
    path = make_dirs(name, is_simulation(backend))
    save_result_to_file(result, file_datestr(path, name), metadata=meta)


def load_result(name=None, filename=None, meta=None, h=1, simulations=False):
    if filename == None:
        if not name:
            name = get_name()
        if not os.path.isdir(name):
            print("project '%s' not started yet" % name)
            sys.exit(1)
        d = []
        if not simulations:
            d = sorted(os.listdir(name), reverse=True)
            d = list(map(lambda s: os.path.join(name, s), d))
            d = [e for e in d if os.path.isfile(e)]
        if not d:
            if not simulations:
                print("no saved experiments for '%s', looking for simulations" % name)
            name = os.path.join(name, "simulations")
            d = sorted(os.listdir(name), reverse=True)
            d = list(map(lambda s: os.path.join(name, s), d))
            d = [e for e in d if os.path.isfile(e)]
        if not d:
            print("no files found for '%s'" % name)
            sys.exit(1)
        cur = ""
        c = 0
        for e in d:
            c += 1
            cur = e
            if meta:
                x = load_result_from_file(e)
                if x[1] != meta:
                    c -= 1
            if c == h:
                break
        filename = cur
    print("loaded " + meta)
    result, meta = load_result_from_file(filename)
    add_meta_for_result(result, meta)
    return result


def add_meta_for_result(result, meta):
    global meta_results
    if meta:
        meta_results += [(meta, result)]


def get_meta_from_result(result):
    global meta_results
    for m, r in meta_results:
        if result == r:
            return m


def visualize(result, circuits=None, ntk=False):
    # Visualizes specified curcuit results as histogram.
    if circuits == None:
        circuits = result.get_names()
    for name in circuits:
        plot_histogram(result.get_counts(name), ntk)
