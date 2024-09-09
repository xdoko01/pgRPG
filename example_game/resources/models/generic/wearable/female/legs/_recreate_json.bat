REM Script for generation of Tiled JSON spritesheets
REM Run recreate scripts in all subfolders

ECHO Recreating JSON models in 'armor' folder
cd armor
call _recreate_json.bat
cd ..

ECHO Recreating JSON models in 'pants' folder
cd pants
call _recreate_json.bat
cd ..

ECHO Recreating JSON models in 'skirt' folder
cd skirt
call _recreate_json.bat
cd ..
