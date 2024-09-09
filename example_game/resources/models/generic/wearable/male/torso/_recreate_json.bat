REM Script for generation of Tiled JSON spritesheets
REM Run recreate scripts in all subfolders

ECHO Recreating JSON models in 'back' folder
cd back
call _recreate_json.bat
cd ..

ECHO Recreating JSON models in 'chain' folder
cd chain
call _recreate_json.bat
cd ..

ECHO Recreating JSON models in 'leather' folder
cd leather
call _recreate_json.bat
cd ..

ECHO Recreating JSON models in 'plate' folder
cd plate
call _recreate_json.bat
cd ..

ECHO Recreating JSON models in 'shirts' folder
cd shirts
call _recreate_json.bat
cd ..
