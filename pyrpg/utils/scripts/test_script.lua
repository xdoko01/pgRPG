-- Print all entities used in the game

local d2t = game.lua._dict_to_table
local ents = d2t(game.alias_to_entity)

for k,v in pairs(ents) do
	print('E: '.. k ..'  ID: '.. v)
end
