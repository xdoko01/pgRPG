REM Script for generation of Tiled JSON spritesheets
REM Run recreate scripts in all subfolders

python ../../../../../utils/generate_model_json_from_template.py ../../_template.json *.png

ECHO Recreating JSON models in 'ears' folder
cd ears
call _recreate_json.bat
cd ..

ECHO Recreating JSON models in 'eyes' folder
cd eyes
call _recreate_json.bat
cd ..

ECHO Recreating JSON models in 'facial' folder
cd facial
call _recreate_json.bat
cd ..

ECHO Recreating JSON models in 'hair' folder
cd hair
call _recreate_json.bat
cd ..

ECHO Recreating JSON models in 'nose' folder
cd nose
call _recreate_json.bat
cd ..

ECHO Recreating JSON models in 'wound' folder
cd wound
call _recreate_json.bat
cd ..

pause
