# Animation System

Animation system consists of processors that change the animation properties on the `RenderableModel` components.

For every animation type there is separate processor that catches flags and change the animation accordingly.

The order of the animation processors is important - ex. if entity has moved and also has attacked then the animation that is implemented by later processor is applied.

The animation processor that is setting idle status is specific. In the filter conditions it is specifiing components that given entity must not have - cannot be moving, cannot be attacking, cannot be dying ...
