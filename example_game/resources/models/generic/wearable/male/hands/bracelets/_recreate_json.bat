REM Script for generation of Tiled JSON spritesheets

python ../../../../../../../utils/generate_model_json_from_template.py ../../../../_template.json *.png

python ../../../../../../../utils/generate_model_json_from_template.py ../../../../_template.json bracelet.png spellcast idle_spellcast thrust idle_thrust slash idle_slash expire idle_expire shoot idle_shoot
