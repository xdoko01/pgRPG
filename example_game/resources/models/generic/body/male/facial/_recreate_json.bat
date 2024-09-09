REM Script for generation of Tiled JSON spritesheets

ECHO Recreating JSON models in 'beard' folder
cd beard
call _recreate_json.bat
cd ..

ECHO Recreating JSON models in 'bigstache' folder
cd bigstache
call _recreate_json.bat
cd ..

ECHO Recreating JSON models in 'fiveoclock' folder
cd fiveoclock
call _recreate_json.bat
cd ..

ECHO Recreating JSON models in 'frenchstache' folder
cd frenchstache
call _recreate_json.bat
cd ..

ECHO Recreating JSON models in 'mustache' folder
cd mustache
call _recreate_json.bat
cd ..
