REM Script for generation of Tiled JSON spritesheets

python ../../../../../utils/generate_model_json_from_template.py ../../_template.json *.png
python ../../../../../utils/generate_model_json_from_template.py ../../_template.json body_male_magic.png shoot shoot_idle thrust thrust_idle slash slash_idle
python ../../../../../utils/generate_model_json_from_template.py ../../_template.json body_male_minotaur.png spellcast spellcast_idle shoot shoot_idle thrust thrust_idle shoot shoot_idle
python ../../../../../utils/generate_model_json_from_template.py ../../_template.json body_male_bauldric.png thrust thrust_idle shoot shoot_idle

