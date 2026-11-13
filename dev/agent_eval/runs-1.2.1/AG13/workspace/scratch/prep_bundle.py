import sys, shutil, subprocess, os
src = sys.argv[1]
b = open(src, 'rb').read()
while b.endswith(b'\n') or b.endswith(b'\r'):
    b = b[:-1]
open(src, 'wb').write(b)
print('bytes', len(b), 'single quotes', b.count(b"'"), 'CR', b.count(b'\r'))
if len(sys.argv) > 2:
    tmp = os.path.join('scratch', 'mem', 'CERBERO-' + os.path.basename(src))
    shutil.copy(src, tmp)
    out = subprocess.run(['python', 'scratch/validate.py', 'scratch/mem/CERBERO-B-*.md'], capture_output=True, text=True).stdout
    os.remove(tmp)
    print(out)
