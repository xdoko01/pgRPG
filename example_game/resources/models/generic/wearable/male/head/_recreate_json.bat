REM Script for generation of Tiled JSON spritesheets
REM Run recreate scripts in all subfolders

ECHO Recreating JSON models in 'bandanas' folder
cd bandanas
call _recreate_json.bat
cd ..

ECHO Recreating JSON models in 'caps' folder
cd caps
call _recreate_json.bat
cd ..

ECHO Recreating JSON models in 'facial' folder
cd facial
call _recreate_json.bat
cd ..

ECHO Recreating JSON models in 'helms' folder
cd helms
call _recreate_json.bat
cd ..

ECHO Recreating JSON models in 'hoods' folder
cd hoods
call _recreate_json.bat
cd ..
