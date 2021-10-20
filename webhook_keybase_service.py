import subprocess

subprocess.call(
    args=['keybase', '--home', './webhookbot', 'service', '--oneshot-username', 'morethanmarvin', '<', 'paper-key'])