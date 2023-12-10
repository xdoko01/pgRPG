'''
  Experimenting with composition of commands from functions based on json definition.

'''

def GetActorLocation(target: int) -> dict:
    print(f'Returning location for {target=}')
    return {"return_value": [5,5]}

def GetRandomPointInNavigableRadius(origin, radius)-> dict:
    print(f'Returning random location for {origin=} and {radius=}')
    return {"random_location": [6,6], "return_value": "SUCCESS"}

def SetBlackboardValue(key, value) -> dict:
    print(f'Setting blackboard value {key=}, {value=}')
    return dict()

def main():
    
    task = {
      "name": "TaskGetRandomLocation",
      "params": ["target", "radius", "blackboard key"],
  
      "functions": [
        {
          "name": "GetActorLocation",
          "params": {
            "target": "$target",
          },
          "returns": ["return_value"]
        },
        {
          "name": "GetRandomPointInNavigableRadius",
          "params": {
            "origin": "GetActorLocation.return_value",
            "radius": "$radius"
          },
          "returns": ["random_location", "return_value"]
        },
        {
          "name": "SetBlackboardValue",
          "params": {
            "key": "$blackboard_key",
            "value": "GetRandomPointInNavigableRadius.random_location"
          },
          "returns": []
        }
      ],
      "returns": ["GetRandomPointInNavigableRadius.return_value"]
    }

    eval("GetActorLocation")
    #for t in task["functions"]:
    #    t["name"]