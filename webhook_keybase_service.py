import subprocess
import os

subprocess.call(
    args=['keybase', '--home', './webhookbot', 'service', '--oneshot-username', os.environ.get('KEYBASE_BOTNAME'), '<', os.environ.get('KEYBASE_PAPERKEY')])