REM Script for generation of Tiled JSON spritesheets
REM Run recreate scripts in all subfolders

ECHO Recreating JSON models in 'armor' folder
cd armor
call _recreate_json.bat
cd ..

ECHO Recreating JSON models in 'boots' folder
cd boots
call _recreate_json.bat
cd ..

ECHO Recreating JSON models in 'shoes' folder
cd shoes
call _recreate_json.bat
cd ..

ECHO Recreating JSON models in 'slippers' folder
cd slippers
call _recreate_json.bat
cd ..