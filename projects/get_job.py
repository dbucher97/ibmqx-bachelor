from IBMQuantumExperience import IBMQuantumExperience
from pprint import pprint
import sys
import Qconfig

api = IBMQuantumExperience(Qconfig.APItoken, config=Qconfig.config)

pprint(api.get_job(sys.argv[1]))
