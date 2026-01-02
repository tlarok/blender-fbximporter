# HowTo: Mesh & Armature Setup

First, you need an **armature/skeleton** that the mesh is already rigged to, along with a **FLVER** file that uses the same armature.

For FromSoft player characters, it's recommended to extract the skeleton from `fc_m_0000.partsbnd.dcx`. Since FLVER files cannot be imported directly without external tools or addons, user suggested using the [Aqua Toolset](https://github.com/Shadowth117/Aqua-Toolset) to export the model as an FBX, which can then be imported into Blender.

???+ warning

    FromSoftware armatures are typically named `Master`. Make sure the armature in your Blender scene is renamed to `Master`, or the created physics will not work correctly.

Next, prepare the mesh you are creating physics or clothing for. It must be rigged to the same armature. Also mesh must be triangular, otherwise mesh will have missmatch with model you will later import in flver.

* Enable **Auto Normalize** in Blender in weight painting mode in settings in the right

![auto normilize setting](../assets/images/auto_normilize.png)

* **Or** after finishing weight painting, go to **Weight Paint Mode → Weights → Normalize All**

![normilize manually](../assets/images/normilize_all.png)

There is also an option to use a **proxy/simulation mesh** (a simplified version of your model) for physics simulation and transfer its motion to the main mesh. This is useful if:

* Your model is very high-poly
* The mesh does not deform well during simulation

???+ note

    The deformed mesh will inherit the proxy/simulation mesh’s weight painting.
