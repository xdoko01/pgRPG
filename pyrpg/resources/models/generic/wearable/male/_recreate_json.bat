REM Script for generation of Tiled JSON spritesheets
REM Run recreate scripts in all subfolders

ECHO Recreating JSON models in 'belt' folder
cd belt
call _recreate_json.bat
cd ..

ECHO Recreating JSON models in 'feet' folder
cd feet
call _recreate_json.bat
cd ..

ECHO Recreating JSON models in 'hands' folder
cd hands
call _recreate_json.bat
cd ..

ECHO Recreating JSON models in 'head' folder
cd head
call _recreate_json.bat
cd ..

ECHO Recreating JSON models in 'legs' folder
cd legs
call _recreate_json.bat
cd ..

ECHO Recreating JSON models in 'torso' folder
cd torso
call _recreate_json.bat
cd ..
