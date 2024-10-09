REM Script for generation of Tiled JSON spritesheets
REM Run recreate scripts in all subfolders

python ../../../../../utils/generate_model_json_from_template.py ../../_template.json *.png spellcast spellcast_idle thrust idle_thrust slash idle_slash shoot idle_shoot expire idle_expire

