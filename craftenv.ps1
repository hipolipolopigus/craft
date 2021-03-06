
#    this file sets some environment variables that are needed
#    for finding programs and libraries etc.
#    by Hannah von Reth <vonreth@kde.org>
#    you should copy CraftSettings.ini.template to ..\etc\CraftSettings.ini
#    and adapt it to your needs (see that file for more info)

cls

$env:CraftRoot=[System.IO.Path]::GetDirectoryName($myInvocation.MyCommand.Definition)

$CRAFT_ARGUMENTS = $args

&{
[version]$minPythonVersion = 3.6

function findPython([string] $name)
{
    $py = (Get-Command $name -ErrorAction SilentlyContinue)
    if ($py -and ($py | Get-Member Version) -and $py.Version -ge $minPythonVersion) {
        $env:CRAFT_PYTHON=$py.Source
    }
}

findPython("python3")
findPython("python")

function readINI([string] $fileName)
{
   $ini = @{}

  switch -regex -file $fileName {
    "^\[(.+)\]$" {
      $section = $matches[1].Trim()
      $ini[$section] = @{}
    }
    "^\s*([^#].+?)\s*=\s*(.*)" {
      $name,$value = $matches[1..2]
      $ini[$section][$name] = $value.Trim()
    }
  }
  $ini
}


if(test-path -path $env:CraftRoot\..\etc\kdesettings.ini)
{
    mv $env:CraftRoot\..\etc\kdesettings.ini $env:CraftRoot\..\etc\CraftSettings.ini
}


if(test-path -path $env:CraftRoot\..\etc\CraftSettings.ini)
{
    $settings = readINI $env:CraftRoot\..\etc\CraftSettings.ini
}
else
{
    Write-Error("$env:CraftRoot\..\etc\CraftSettings.ini Does not exist")
    break
}
if( $CRAFT_ARGUMENTS[0] -eq "--get")
{
    Write-Host($settings[$CRAFT_ARGUMENTS[1]][$CRAFT_ARGUMENTS[2]])
    break
}


function prependPATH([string] $path)
{
    $env:PATH="$path{0}$env:PATH" -f [IO.Path]::PathSeparator
}


if( -Not $env:CRAFT_PYTHON)
{
    prependPATH $settings["Paths"]["Python"]
    $env:CRAFT_PYTHON=[IO.PATH]::COMBINE($settings["Paths"]["Python"], "python")
}

(& $env:CRAFT_PYTHON ([IO.PATH]::COMBINE("$env:CraftRoot", "bin", "CraftSetupHelper.py")) "--setup") |
foreach {
  if ($_ -match "=") {
    $v = $_.split("=")
    set-item -force -path "ENV:\$($v[0])"  -value "$($v[1])"
    #Write-Host("$v[0]=$v[1]")
  }
}

cd "$env:KDEROOT"
}


function Global:craft()
{
    return & $env:CRAFT_PYTHON ([IO.PATH]::COMBINE("$env:CraftRoot", "bin", "craft.py")) $args
}

function Global:cb([string] $package)
{
    $dir = craft -q --get "buildDir()" $package | Out-String
    if($LASTEXITCODE) {
        Write-Host $dir
    } else {
        cd "$dir".Trim()
    }
}

function Global:cs([string] $package)
{
    $dir = craft -q --get "sourceDir()" $package | Out-String
    if($LASTEXITCODE) {
        Write-Host $dir
    } else {
        cd "$dir".Trim()
    }
}

function Global:cr()
{
    cd $env:KDEROOT
}


if($args.Length -ne 0)
{
    & $args
}

