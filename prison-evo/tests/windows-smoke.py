import os, subprocess, sys
os.chdir(sys.argv[1])
command=['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File','launch.ps1']
try:
    result=subprocess.run(command,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=300)
except subprocess.TimeoutExpired as exc:
    print('Windows launcher timed out')
    if exc.stdout: print(exc.stdout.decode('utf-8',errors='replace')[-20000:])
    sys.exit(1)
text=result.stdout.decode('utf-8',errors='replace')
print(text[-12000:])
checks={'PowerShell exited cleanly': result.returncode==0,
        'Java was started': 'Starting server. Connect' in text,
        'Server integration checks passed': 'HYLOR_INTEGRATION_CHECK=PASS' in text,
        'Previous Java error absent': 'could not find java.dll' not in text}
for name,passed in checks.items(): print(name+': '+('PASS' if passed else 'FAIL'))
sys.exit(0 if all(checks.values()) else 1)
