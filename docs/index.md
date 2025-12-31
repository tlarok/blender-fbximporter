# blender-fbximporter

This addon is designed for creating *Havok clothing data* and simplifies the process of converting FBX scene files into Havok-compatible `.hkt` files. 

It makes it easier to set up clothing physics by providing an interface for exporting vertex sets, vertex groups (Float/Distance/Angle groups), collidable objects, and more. These can then be used in Havok's Filter Manager for further configuration and cloth simulation.

Games where this tool is known to work are:
- Elden Ring
- Elden Ring Nightreign
- Dark Souls 3
- Bloodborne

???+ note

    **Dark Souls II (SOTFS)** and **Sekiro** may also work, but there are no confirmed working examples yet.

---

## Overview

- [Start Here!](preface.md)
- [Setup](setup.md)
- HowTo
    1. [Prepare your Armature](howto/armature.md)
    2. [Setup your simulation mesh](howto/mesh_setup.md)
    3. [Import your scene into Havok](howto/mesh_export.md)
    4. Configure the cloth simulation 
        - [Simple](howto/sim_simple.md)
        - [Thick (one mesh)](howto/sim_thick_one_mesh.md)
        - [Thick (two mesh)](howto/sim_thick_two_mesh.md)
    5. [Export Simulation Results](howto/save_result.md)
- [Troubleshooting](troubleshooting.md)

---

## Video Guides

Currently there is only a quick workflow showing how to get a scene opened in filter manager. For further setup I reccomend watching the 3ds max guide.
For the 3ds Max users, just skip the setup part and follow the steps from the second video instead.

[addon guide](https://www.youtube.com/watch?v=f0zeviw5CWE)

[3ds max guide](https://www.youtube.com/watch?v=BjVqN-UMw7w)
