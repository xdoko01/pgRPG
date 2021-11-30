# *RENDER SYSTEM*

## Input dependency
 - *ANIMATION SYSTEM* - animation system is updating the animation on the `RenderModel` in order to display the correct frame using the *RENDER SYSTEM*
 - *ARM WEAPON SYSTEM* - generating `NewWeaponInUse` component necessary for identification of active weapon that should be animated. The component `HasWeapon` in order to assin the `GenerateRenderDataFromParentProcessor` to the weapon entity and generator entity.

## Output dependency

## Description
The aim of the render system is to draw the game on the game screen. In order to do that it contain set of processors that render objects to all active cameras layer by layer. The Render System is also coupled with the Animation System in order to display the correct animation frames depending on object's in-game action.

The Render System is using `Camera` components as a panes to which entities are drawn. Also it uses `RenderableModel` component where the animation frames are stored.

The set of Render System processors is drawing layer by layer to the cameras. First, map background is drawn by `PerformRenderMapProcessor`. Next, entites with position on the map are being drawn by `PerformRenderModelProcessor`. As some entites can wear clothes and/or wear a weapon/ammo there are processors `NewPerformRenderWearablesProcessor`, `PerformRenderArmedWeaponProcessor` and `PerformRenderArmedAmmoProcessor`.

In order for the last 3 mentioned processor to be rendered, there is `GenerateRenderDataFromParentProcessor` to supply information about position and correct frame for correct animation of wearables/ammo/weapons.

At the end, there is `PerformBlitCameraProcessor` that ensures that content of the cameras is displayed onto the main game window. 

# Order of the processors
Preferable order of procesors to ensure that all the layers are properly rendered is following:

`PerformClearWindowProcessor` - clear game window pane
`PerformClearCameraProcessor` - clear pane of all cameras
`PerformScrollCameraProcessor` - move the camera offset to enable smooth scrolling
`PerformRenderMapProcessor` - draw map
`PerformRenderModelProcessor` - draw entities with position
`GenerateRenderDataFromParentProcessor` - prepare data for entites without position that need to be displayed
`NewPerformRenderWearablesProcessor` - first draw clothes weared
`PerformRenderArmedWeaponProcessor` - next, draw weapon used by the character
`PerformRenderArmedAmmoProcessor` - next, draw ammo animation
`PerformRenderDebugInfoProcessor` - once everything is rendered, optionally draw debug information
`PerformBlitCameraProcessor` - blit everything on the game window
