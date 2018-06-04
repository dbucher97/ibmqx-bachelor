from main import get_calibration
import sys, os

def tex_calibration(jid):
    calibration = get_calibration(jid)
    dat = calibration["lastUpdateDate"]
    d = {}
    for qubit in calibration["qubits"]:
        name = qubit.get("name")
        if name:
            dd = {}
            dd["T1"] = qubit.get("T1").get("value")
            dd["T2"] = qubit.get("T2").get("value")
            dd["gate_error"] = qubit.get("gateError").get("value")
            dd["readout_error"] = qubit.get("readoutError").get("value")
            d[name] = dd
    e = {}
    for cx in calibration["multiQubitGates"]:
        n = "-".join(list(map(str, cx.get("qubits"))))
        e[n] = cx.get("gateError").get("value")

    with open("confs/conf.tex", "r") as f:
        s = f.read()
    s = s.replace("<<jid>>", jid)
    for k, v in d.items():
        q = k[1:]
        s = s.replace("<<r%s>>"%q,"%.2f"%round(v["readout_error"]*10, 2))
        s = s.replace("<<g%s>>"%q, "%.2f"%round(v["gate_error"]*1e3, 2))
    for k, v in e.items():
        s = s.replace("<<cx%s>>"%k, "%.2f"%round(v*1e2, 2))

    with open("confs/%s.tex"%jid, "w") as f:
        f.write(s)
    os.chdir("confs")
    os.system("latexmk -pdf %s"%jid)
    os.chdir("..")

if __name__ == "__main__":
    tex_calibration(sys.argv[1])
