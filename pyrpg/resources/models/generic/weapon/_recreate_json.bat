REM Script for generation of Tiled JSON spritesheets
REM Run recreate scripts in all subfolders

ECHO Recreating JSON models in 'accessories' folder
cd accessories
call _recreate_json.bat
cd ..

ECHO Recreating JSON models in 'shoot' folder
cd shoot
call _recreate_json.bat
cd ..

ECHO Recreating JSON models in 'slash' folder
cd slash
call _recreate_json.bat
cd ..

ECHO Recreating JSON models in 'spellcast' folder
cd spellcast
call _recreate_json.bat
cd ..

ECHO Recreating JSON models in 'thrust' folder
cd thrust
call _recreate_json.bat
cd ..

pause
