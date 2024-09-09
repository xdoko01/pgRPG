REM Script for generation of Tiled JSON spritesheets

python ../../../../../utils/generate_model_json_from_template.py ../../_template.json *.png
python ../../../../../utils/generate_model_json_from_template.py ../../_template.json body_male_magic.png shoot shoot_idle thrust thrust_idle slash slash_idle
python ../../../../../utils/generate_model_json_from_template.py ../../_template.json body_male_minotaur.png spellcast spellcast_idle shoot shoot_idle thrust thrust_idle shoot shoot_idle
python ../../../../../utils/generate_model_json_from_template.py ../../_template.json body_male_bauldric.png thrust thrust_idle shoot shoot_idle

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
