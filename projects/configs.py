from main import get_calibration
import numpy as np
import sys, os

def tex_calibration(jid, runthrough=False):
    calibration = get_calibration(jid)
    dat = calibration["lastUpdateDate"]
    if os.path.isfile("confs/%s.pdf"%dat) and not runthrough:
        r = input("%s conf exists (%s). overwrite? y/[n]: " % (jid, dat))
        if not (r == "y" or r == "Y"):
            return
    dat_dat, dat_time=dat.split("T")
    dat_time = dat_time.split(".")[0]
    print(dat)
    d = {}
    gmax = 0
    rmax = 0
    for qubit in calibration["qubits"]:
        name = qubit.get("name")
        if name:
            dd = {}
            # print(qubit)
            dd["T1"] = qubit.get("T1").get("value")
            dd["T2"] = qubit.get("T2").get("value")
            dd["gate_error"] = qubit.get("gateError").get("value")
            dd["readout_error"] = qubit.get("readoutError").get("value")
            d[name] = dd
            if dd["gate_error"] > gmax:
                gmax = dd["gate_error"]
            if dd["readout_error"] > rmax:
                rmax = dd["readout_error"]

    mg = int(np.ceil(-np.log10(gmax)))
    mr = int(np.ceil(-np.log10(rmax)))
    e = {}
    cxmax = 0
    for cx in calibration["multiQubitGates"]:
        n = "-".join(list(map(str, cx.get("qubits"))))
        e[n] = cx.get("gateError").get("value")
        if e[n] > cxmax:
            cxmax = e[n]
    mcx = int(np.ceil(-np.log10(cxmax)))
    newlines = []
    with open("confs/conf.tex", "r") as f:
        for line in f:
            if line.strip().startswith("\\qubit"):
                i = int(line.split("{")[1][:-1])
                qubit = d["Q%d"%i]
                line = line.replace("T1", str(qubit.get("T1"))
                    ).replace("T2", str(qubit.get("T2"))
                    ).replace("eg", "%.2f"%(qubit.get("gate_error")*10**mg)
                    ).replace("er", "%.2f"%(qubit.get("readout_error")*10**mr))
            elif line.strip().startswith("\\draw[myarrow]"):
                a, b = line.split("--")
                a = a.strip().split("Q")[-1][:-1]
                b = b.strip().split(")")[0][2:]
                line = line.replace("{cx}", "{%.2f}"%(e[a+"-"+b]*10**mcx))
            else:
                line = line.replace("<mg>", str(mg)).replace("<mr>", str(mr)
                            ).replace("<mcx>", str(mcx)).replace("<date>", dat_dat[2:]
                            ).replace("<time>", dat_time)
            newlines += [line]
    # print("".join(newlines))

    with open("confs/%s.tex"%dat, "w") as f:
        for s in newlines:
            f.write(s)
    os.chdir("confs")
    os.system("latexmk -pdf %s"%dat)
    os.system("latexmk -c")
    os.chdir("..")

if __name__ == "__main__":
    runthrough = False
    if len(sys.argv) == 1 and os.path.isfile("confs/bin"):
        with open("confs/bin", "r") as f:
            arr = f.read().strip().split(" ")
    elif sys.argv[1] == "refresh":
        runthrough = True
        with open("confs/bbin", "r") as f:
            arr = f.read().strip().split(" ")
    else:
        arr = sys.argv[1:]
    for jid in arr:
        # print(jid)
        tex_calibration(jid, runthrough=runthrough)
