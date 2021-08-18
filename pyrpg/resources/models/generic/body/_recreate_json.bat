REM Script for generation of Tiled JSON spritesheets
REM Run recreate scripts in all subfolders

ECHO Recreating JSON models in 'male' folder
cd male
call _recreate_json.bat
cd ..

ECHO Recreating JSON models in 'female' folder
cd female
call _recreate_json.bat
cd ..

ECHO Recreating JSON models in 'child' folder
cd child
call _recreate_json.bat
cd ..

pause
