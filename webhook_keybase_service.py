import subprocess
import os

subprocess.call(
    args=['keybase', '--home', './webhookbot', 'service', '--oneshot-username', 'morethanmarvin', os.environ.get('KEYBASE_PAPERKEY')])