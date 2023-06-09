from dotenv import load_dotenv, dotenv_values
import os
import sys

try:
    # fix directory issue
    sys.path.insert(0, os.getcwd())
    # print(sys.path)
except Exception as e:
    print("hello")

ENV_VALUES = {}

# load env
load_dotenv()
# create and expose ENV_VALUES
ENV_VALUES = dotenv_values('.env')
ENV_VALUES["datapath"] = "data"
ENV_VALUES["newDatas"] = "datas"

if len(list(ENV_VALUES.keys())) == 0:
    print(
        '.env file is missing from within your local project. '
        'This usually happens when you\'re in the wrong directory. '
        'And then go into that project, and run the same command.',
        force_print=True
    )
    os._exit(1)