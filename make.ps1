# THIS SCRIPT IS FOR THE PEOPLE WHO WANT TO BUILD THE L# COMPILER FROM SOURCE.
# THERE ARE MULTIPLE WAYS TO DO THIS. THERE IS USING GIT MANUALLY BY
# CLONING THE REPOSITORY WITH git clone https://github.com/Donkasem55/L-sharp.git
# AND THEN CD-ING INTO THE REPOSITORY, cd L-sharp
# FINALLY, YOU RUN THIS SCRIPT, .\make.ps1, TO BUILD IT. MAKE SURE YOU HAVE PYTHON INSTALLED.

# YOU CAN ALSO USE A PACKAGE MANAGER IF ONE SUPPORTS THIS.

Write-Output "Checking for Python..."

$commands = @('python','python3','py')
$found = $null

foreach ($cmd in $commands) {
    try {
        $info = & $cmd --version 2>&1
        if ($LASTEXITCODE -eq 0 -or $info) {
            $found = [PSCustomObject]@{
                Command = $cmd
                Version = ($info -join "`n").Trim()
                Path    = (Get-Command $cmd -ErrorAction SilentlyContinue).Source
            }
            break
        }
    } catch {
    }
}

function Test-PyInstaller {
    param($pyExec)

    $exe = Get-Command pyinstaller -ErrorAction SilentlyContinue
    if ($exe) {
        return [PSCustomObject]@{ Found = $true; Method = 'exe'; Path = $exe.Source }
    }

    try {
        $out = & $pyExec -c "import importlib, sys
try:
    m = importlib.import_module('PyInstaller')
    v = getattr(m, '__version__', None) or getattr(getattr(m, 'version', None), 'VERSION', None)
    print('ok:'+str(v))
except Exception:
    try:
        import pkgutil
        loader = pkgutil.find_loader('PyInstaller')
        if loader:
            print('ok:unknown')
        else:
            raise SystemExit(2)
    except Exception:
        raise SystemExit(2)
" 2>&1
        if ($LASTEXITCODE -eq 0 -or ($out -match '^ok:')) {
            $ver = if ($out -match '^ok:(.*)') { $matches[1].Trim() } else { 'unknown' }
            return [PSCustomObject]@{ Found = $true; Method = 'module'; Version = $ver; Path = $null }
        }
    } catch {}

    try {
        $pipOut = & $pyExec -m pip show pyinstaller 2>$null
        if ($pipOut) {
            $verLine = ($pipOut | Where-Object { $_ -like 'Version:*' }) -join ''
            $ver = $verLine -replace 'Version:\s*',''
            return [PSCustomObject]@{ Found = $true; Method = 'pip'; Version = ($ver.Trim() -ne '' ? $ver.Trim() : 'unknown'); Path = $null }
        }
    } catch {}

    return [PSCustomObject]@{ Found = $false }
}

if ($found) {
    Write-Output "Python found: $($found.Command)"
    Write-Output "Version: $($found.Version)"
    if ($found.Path) { Write-Output "Location: $($found.Path)" }
    Write-Output "Checking for PyInstaller..."

    $pi = Test-PyInstaller -pyExec $python.Exec

    if ($pi.Found) {
        Write-Output "PyInstaller found (method: $($pi.Method))"
        if ($pi.Version) { Write-Output "Version: $($pi.Version)" }
        if ($pi.Path) { Write-Output "Path: $($pi.Path)" }
        exit 0
    } else {
        Write-Output "Dependency: PyInstaller not found. Installing PyInstaller automatically..."
        & $found.Path -m pip install PyInstaller
    }

    Write-Output "Packaging L#..."
    & $found.Path -m PyInstaller main.py --add-data "stdlib;stdlib" --onefile --name lshrp.exe
    try {
        cp dist\lshrp.exe C:\Users\$($env:USERNAME)\bin
    } catch {
        mkdir C:\Users\$($env:USERNAME)\bin
        cp dist\lshrp.exe C:\Users\$($env:USERNAME)\bin
    }
    Copy-Item -Path stdlib\* -Recurse -Destination "C:\Users\$($env:USERNAME)\bin" -Verbose
    Write-Output "Finished!"
    exit 0
} else {
    Write-Output "Error: Python not found. You may run winget install Python.Python.3.14 to install Python 3.14."
    exit 1
}