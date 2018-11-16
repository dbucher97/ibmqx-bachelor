import os

os.chdir("confs")
l = [x for x in os.listdir() if x.endswith("Z.tex")]
for e in l:
    os.system("latexmk -pdf %s"%e[:-4])
os.system("latexmk -c")
os.chdir("..")
