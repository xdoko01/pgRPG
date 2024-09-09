REM Script for generation of Tiled JSON spritesheets
REM Run recreate scripts in all subfolders

ECHO Recreating JSON models in 'bracelets' folder
cd bracelets
call _recreate_json.bat
cd ..

ECHO Recreating JSON models in 'bracers' folder
cd bracers
call _recreate_json.bat
cd ..

ECHO Recreating JSON models in 'gloves' folder
cd gloves
call _recreate_json.bat
cd ..
