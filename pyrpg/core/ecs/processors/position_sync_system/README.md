PositionSyncSystem
------------------

NewGeneratePositionSyncProcessor
 - CanWear + Position + FlagDoMove-> for each wearable entity ID assign FlagSyncPosition(x,y,map, dir, dir_name)
 - WeaponInUse + Position + HasWeapon + FlagDoMove -> on active weapon add FlagSyncPosition(x,y,map, dir, dir_name)
 - AmmoInUse + Position + HasWeapon + FlagDoMove -> on active ammo add FlagSyncPosition(x,y,map, dir, dir_name)

NewPerformPositionSyncProcessor
 - FlagSyncPosition(x,y,map, dir, dir_name) + Position -> adjust position

NewRemoveFlagSyncPositionProcessor
 - FlagSyncPosition