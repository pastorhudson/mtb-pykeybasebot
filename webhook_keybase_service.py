import subprocess
import os

subprocess.call(args=['./keybase', '--home', './webhookbot', 'service', '--oneshot-username', 'marvn', '<', os.environ.get('KEYBASE_PAPERKEY')])