import subprocess, sys
with open('smoke.log','w') as log:
 p=subprocess.Popen(['java','-XX:ActiveProcessorCount=2','-Xms256M','-Xmx1G','-Djline.terminal=jline.UnsupportedTerminal','-jar','paper.jar','--nogui'],stdin=subprocess.PIPE,stdout=log,stderr=subprocess.STDOUT)
 try: p.wait(timeout=180)
 except subprocess.TimeoutExpired: p.kill();p.wait()
text=open('smoke.log').read()
ok=p.returncode==0 and 'HYLOR_INTEGRATION_CHECK=PASS' in text
if not ok: print(text[-20000:])
print('SERVER INTEGRATION:', 'PASS' if ok else 'FAIL')
sys.exit(0 if ok else 1)
