--[[ 
--Print all entities used in the game

local d2t = game.lua._dict_to_table
local ents = d2t(game.alias_to_entity)

for k,v in pairs(ents) do
	print('E: '.. k ..'  ID: '.. v)
end
--]]

-- Print all entities having AmmoPack component
local l2t = game.lua._list_to_table
local ents = l2t(game.world.get_components(game.components.AmmoPack))

function values(t)
	local i = 0
	return function() i = i + 1; return t[i] end
end

for i = 1,#ents,1 do
	for j = 1,#ents[i],1 do
		print(ents[i][j])
	end
end
--	for ent in values(ents) do
--	print(ent)
--end

--print(game.world.get_components(game.components.AmmoPack))
