#Liste les mdps des instructeurs

from demarches_simpy import Demarche, Profile
from dotenv import load_dotenv
import os
load_dotenv()

profile = Profile(os.getenv('DS_KEY'), verbose = False, warning = False)
demarche = Demarche(int(os.getenv('DEMARCHE_NUMBER')), profile)

print('-----------------------------------')
for instruct in demarche.get_instructeurs_info():
    print(f'Email : {instruct["email"]}')
    print(f'Password : {instruct["id"]}')
    print('-----------------------------------')