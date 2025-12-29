# blender-fbximporter
blender addon for creating havok/hkt scene file with all needed settings for creating physics

Requirements

Blender: Latest version from Steam (tested and recommended).
You may try using older versions down to 2.93.0, but anything under 4.0.0 unsupported and may cause unknown issues.

Visual Studio 2012 Redistributable (Update 4):
Download from the official Microsoft page:
[Visual Studio 2012 VC++ Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170#visual-studio-2012-vc-110)

Video Guides

currently there only quick workflow showing how to get scene opened in filter manager, for further setup i reccomend watching 3ds max guide.
For the 3ds Max users, just skip the setup part and follow the steps from the second video instead.

[addon guide](https://www.youtube.com/watch?v=f0zeviw5CWE)

[3ds max guide](https://www.youtube.com/watch?v=BjVqN-UMw7w)

---

## Setup

Start by configuring the tool and its core features.

### Standalone Filter Manager Path

Go to your Havok installation directory and select
`hctStandAloneFilterManager.exe`.

This allows the addon to open the Filter Manager automatically every time you export a scene, instead of only creating a scene (`.hkt`) file.

### (Optional) Export Path

This is an optional directory where all project files will be stored.
If no path is chosen, the addon will create an `export_data` folder next to the Blender file you are working on.

> **Important:** Your Blender project must be saved somewhere on disk in order for the addon to function correctly.

---

## Usage

Games currently known to support custom physics creation:

* Bloodborne
* Dark Souls III
* Elden Ring
* Elden Ring Nightreign

There is also a possibility of supporting **Dark Souls II (SOTFS)** and **Sekiro**, but there are no confirmed working examples yet.

---

## Preparation

First, you need an **armature/skeleton** that the mesh is already rigged to, along with a **FLVER** file that uses the same armature.

For player characters, it is recommended to extract the skeleton from
`fc_m_0000.partsbnd.dcx`.

> FromSoftware armatures are typically named `Master`.
> Make sure the armature in your Blender scene is renamed to `Master`, or the created physics will not work correctly.

Next, prepare the mesh you are creating physics or clothing for. It must be rigged to the same armature.

* Enable **Auto Normalize** in Blender’s weight painting settings, **or**
* After finishing weight painting, go to **Weight Paint Mode → Weights → Normalize All**

There is also an option to use a **proxy/simulation mesh** (a simplified version of your model) for physics simulation and transfer its motion to the main mesh. This is useful if:

* Your model is very high-poly
* The mesh does not deform well during simulation

> The deformed mesh will inherit the proxy/simulation mesh’s weight painting.

---

## Setting Up the Mesh for Simulation

Havok uses **vertex-based cloth simulation**, which is what this workflow supports.
The simulation is physically accurate, but for performance reasons **self-collision is not supported**.

---

### Selection Sets / UV Indices

These are vertex selections used to define different behavior zones. Common usage includes:

* Simulated vertices
* Fixed vertices
* Display-only vertices
* Collision or other constraint groups

To create them:

1. Select the mesh
2. Enter **Edit Mode**
3. Select the desired vertices
4. Fill in the **Section Name**
5. Press **Save UV Indices**

This will create an entry in:

* `export_data/selectionsets/uv_indices.json`, or
* `optional_export_path/selectionsets/uv_indices.json`

---

### Vertex Groups

Vertex groups are float-based selections used when non-uniform values are required.

To export a vertex group:

* Create a vertex group on the mesh
* Enable **Export Normalize**
* Set **Min Export Value** and **Max Export Value**
* Select the **Weight Group** to export
* Choose a **Weight Type**

Available weight types:

* **Distance**
  Used for distance constraints or collision radii.
* **Float**
  Used for modifiers.
* **Angle**
  Used for angle-based modifiers.

The data will be saved to:

* `export_data/floatchannels/weight_groups.json`, or
* `optional_export_path/floatchannels/weight_groups.json`

---

### Collidables

Because cloth meshes move dynamically, precise control over their position is difficult.
Collidable shapes are used to restrict or guide movement.

#### Available Collidable Shapes

* Capsule
* Sphere
* Plane
* Convex Geometry
* Convex Heightfield

#### Notes on Collidables

* Collidable objects use the prefix `collision_<type>` so the addon can identify and skip them during processing.
* They often include a **bone name prefix** to assign the collidable to a specific bone.
* Collidables do **not** need to be parented to the armature and should remain disconnected.


#### Creating and Assigning Collidables

* Select a mesh or collidable object shape type you want to change
* Choose a **Collision Type**
* Assign a bone using the **Bone Selector** (if needed)
* Press **Set Collision** to convert the mesh into the selected collision shape

If the object is already a collidable, it will be updated unless a Bone Selector is set.

When selecting an **armature**, a **Place Collidable** button appears:

* Select **one bone** in Edit/Pose mode → create a **sphere**
* Select **two bones** in Edit/Pose mode → create a **capsule**

### Capsule Resizing

When a **capsule collidable mesh** is selected, additional resize options will appear.

Capsules can be resized using the following controls:

* **Bottom**
* **Middle**
* **Top**

To resize the capsule:

1. Toggle the desired controls (`Bottom`, `Middle`, and/or `Top`)
2. Press **Resize Capsule** to apply the changes

If the capsule's size choses is **uneven**, the collidable effectively becomes a **Tapered Capsule**.

> **Note:** Tapered Capsules are not supported by the addon.
> For proper functionality, it is recommended to convert the collidable to **Convex Geometry**.

---

## Workflow

Once everything is set up, export the scene by pressing:

**`Export FBX And Run Importer`**

This will export the scene and automatically launch the Havok Filter Manager with your data loaded.

you need specific setup there which you can get here - [file](https://github.com/tlarok/blender-fbximporter/blob/main/defaults.hko)

---
