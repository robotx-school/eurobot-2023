# Documentation about high-level
MICRO-SERVICED arch is new and not documented yet. `DESIGN.md` is legacy.
See file `DESIGN.md`
# Route format documentation

### General info
RoboScript example code:
```
[
  { "action": -1, "start_point": [0, 100], "direction": "E" }, // Init robot position
  { "action": "set_var", "name": "flag", "value": 1}, // Set var `flag` with value `1`
  { "action": "if", "current_value": "flag", "compare_with": 1 }, // Check if var `falg` equals to `1`
    { "action": "log", "content": "Flag is true" }, // Write in terminal `True` 
  { "action": "endif" } // If body closed
]
```
File format: `JSON` </br>
File structure: `list of dicts` </br>
<b>Example:</b></br>
```
[
    {
        "action": -1,
        "start_point": [
            0,
            356
        ],
        "direction": "E"
    },
    {
        "action": 1,
        "point": [
            270,
            356
        ]
    },
    {
        "action": 4,
        "back_point": [
            0,
            356
        ],
        "extra_force": 40
    },
    {
        "action": 1,
        "point": [
            270,
            356
        ]
    },
    {
        "action": 1,
        "point": [
            270,
            500
        ]
    }
]
```
### Info
<p>
One dict is one action. All actions execute step by step. Every step has `action` key. This key describes what type of action high-level preprocessor have to do.
</br><b>Available actions:</b> </br>
1. -1: header(change robot config) </br>
2. 0: high-level python code(used for debugging now)</br>
3. 1: drive(move robot to some point)</br>
4. 2: servo(move servo)</br>
5. 3: delay(on high-level)</br>
6. 4: backward driving</br>
7. 5: set variable value</br>
8. 6: if condition</br>
9. 7: endif
</p>
<p>
In new interpreter release we will add abillity to work with variables, simple if construction
</p>

