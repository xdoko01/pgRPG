# *ANIMATION SYSTEM*

## Input dependency
 - *MOVEMENT SYSTEM* - generating `NewFlagDoMove` component necessary for identification of move animation
 - *ARM WEAPON SYSTEM* - generating `NewWeaponInUse` component necessary for identification of action and action_idle animation

## Output dependency
 - *ATTACK SYSTEM* - processing of `NewFlagIsAnimationActionFrame` component in order to generate new projectile

## Description
Animation System is using `RenderableModel` and `Position` components to identify the entities that should be animated. It uses additional components `NewFlagDoMove`, `NewFlagDoAttack`, `NewWeaponInUse` to select the correct animation.

1. The first set of processors `NewMovementAnimationProcessor`, `NewActionAnimationProcessor`, `NewActionIdleAnimationProcessor` and `NewIdleAnimationProcessor` are seting the `RenderableComponent` to the correct animation.

2. The additional processor `NewPerformFrameUpdateProcessor` is then shifting the frame of the animation to the next one so that animation displays correctly later in *RENDER SYSTEM*. 

3. Once the `NewPerformFrameUpdateProcessor` comes accros so-called action frame, i.e. frame when projectile object is generated, new Component `NewFlagIsAnimationActionFrame` is added on the entity. This flag is later used in *ATTACK SYSTEM* to generate projectile in the right moment.

# Order of the processors
The animation processor that is setting idle status is specific. In the filter conditions it is specifiing components that given entity must not have - cannot be moving, cannot be attacking, cannot be dying ... this is because every change of action is causing reseting of the frame to 0. Hence, if we implement the processors in order idle, walk, attack there will be always only first frame from the attack displayed as the idle animation processor will always reset the frame to 0

Preferable order of procesors to ensure that in case both movement and action is happening, action has priority

`NewPerformMovementAnimationProcessor`
`NewPerformActionAnimationProcessor` - this ensures that action animation has priority over movement animation 
`NewPerformActionIdleAnimationProcessor`
`NewPerformIdleAnimationProcessor`
`NewPerformFrameUpdateProcessor`

