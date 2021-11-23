# *RENDER SYSTEM*

## Input dependency
 - *ANIMATION SYSTEM* - animation system is updating the animation on the `RenderModel` in order to display the correct frame using the *RENDER SYSTEM*
 - *ARM WEAPON SYSTEM* - generating `NewWeaponInUse` component necessary for identification of active weapon that should be animated. The component `NewHasWeapon` in order to assin the `NewGenerateRenderDataFromParentProcessor` to the weapon entity and generator entity.

## Output dependency

## Description
The aim of the render system is to draw the game on the game screen. In order to do that it contain set of processors that render objects to all active cameras layer by layer. The Render System is also coupled with the Animation System in order to display the correct animation frames depending on object's in-game action.

The Render System is using `Camera` components as a panes to which entities are drawn. Also it uses `RenderableModel` component where the animation frames are stored.

The set of Render System processors is drawing layer by layer to the cameras. First, map background is drawn by `NewPerformRenderMapProcessor`. Next, entites with position on the map are being drawn by `NewPerformRenderModelProcessor`. As some entites can wear clothes and/or wear a weapon/ammo there are processors `NewPerformRenderWearablesProcessor`, `NewPerformRenderArmedWeaponProcessor` and `NewPerformRenderArmedAmmoProcessor`.

In order for the last 3 mentioned processor to be rendered, there is `NewGenerateRenderDataFromParentProcessor` to supply information about position and correct frame for correct animation of wearables/ammo/weapons.

At the end, there is `NewPerformBlitCameraProcessor` that ensures that content of the cameras is displayed onto the main game window. 

# Order of the processors
Preferable order of procesors to ensure that all the layers are properly rendered is following:

`NewPerformClearWindowProcessor` - clear game window pane
`NewPerformClearCameraProcessor` - clear pane of all cameras
`NewPerformScrollCameraProcessor` - move the camera offset to enable smooth scrolling
`NewPerformRenderMapProcessor` - draw map
`NewPerformRenderModelProcessor` - draw entities with position
`NewGenerateRenderDataFromParentProcessor` - prepare data for entites without position that need to be displayed
`NewPerformRenderWearablesProcessor` - first draw clothes weared
`NewPerformRenderArmedWeaponProcessor` - next, draw weapon used by the character
`NewPerformRenderArmedAmmoProcessor` - next, draw ammo animation
`NewPerformRenderDebugInfoProcessor` - once everything is rendered, optionally draw debug information
`NewPerformBlitCameraProcessor` - blit everything on the game window
