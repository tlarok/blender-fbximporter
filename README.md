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

### Vertex Selection Groups

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

For the specific setup required, you can get it from [here](https://github.com/tlarok/blender-fbximporter/blob/main/defaults.hko).

Once the setup is loaded, the configuration will change, and you should see the following options:

* **Create Tangents**
* **Create Skeleton**
* **Create Cloth Collidables**
* **Setup Cloth**
* **Execute Cloth Setup (Ds3)**
* **Prune Types**
* **Write to Platform**

### Step-by-step Setup

1. **Choose `Setup Cloth`**
   In the new window on the right, click **`Launch Cloth Setup Tool`**. Ensure that `Cloth Setup Tool Mode` is set to **`Standalone`**. **`Modal`** technically works but is not recommended.

2. **Cloth Setup Tool**
   When the Cloth Setup Tool opens, you will see an empty cloth entity. You can delete this entity. Next, click on the **`Script`** tab at the top, and select **`Wizard Browser...`**. This will pop up a window with different cloth simulation types. While you can create most of them manually, this guide will cover only the following types:

   * **[Simple](#character-simple-clothing-simulation)**
   * **[Thick Single Mesh](#thick-simple-clothing-simulation-one-mesh)**
   * **[Two Mesh Simulation](#thick-simple-clothing-simulation-two-mesh)**

---

### Character Simple Clothing Simulation

This clothing type uses a set mesh for simulation and its own vertices for cloth simulation. When you select it, a window will appear with the following options:

* **Mesh**: The mesh you want to simulate.
* **Skeleton**: The skeleton mesh that the clothing is rigged to.

#### Simulation Options:

* **Simulation Verts**: You can select the vertices to simulate.

* **Fixed Particles**: These are parts that are restricted from movement to prevent the mesh from flying away. A warning will appear if you don’t include all necessary fixed particles, but it will still work. It is **not recommended** to skip this.

* **Both above include:**

  * `<ALL>`
  * `<NONE>`
  * Or custom selection groups you made beforehand.

* **Max Distance**: This constraint limits the distance the vertices can move. You can also use the vertex group export with the distance type.

* **Add Stretch Links**: If enabled, this will add additional Stretch Link constraints to counteract stretching caused by gravity.

After selecting the desired values, press **OK**. This will create a basic cloth setup that you can adjust.

---

### Configuring the Cloth Simulation

1. **Rename `Simulate` to `#01#`**
   If you're working with **Elden Ring** or **Elden Ring Nightreign**, right-click on **States**, and select **New** to create a new state. Rename it to **`#00#`**.

2. **Adjust Skin Settings**
   Go to **Operator** and select `mesh_name + ' SkinOp'`. In the right window, uncheck the **`Tangents`** and **`Bitangents`** checkboxes next to the **Skin** section.

3. **Rename the Transform Set**
   Under **Transform Sets**, click **Master TransformSet** and rename **`Master TransformSet`** to **Master**. If the skeleton name is not **Master TransformSet**, go to Blender and rename the armature to **Master**, then re-export the scene over again.

4. **Set Gravity and Damping**
   In the **Sim Cloths** section, under the mesh name **`SimCloth`**, go to **Simulation Properties**. Change **Gravity** to the desired value (usually negative Y/Middle), and increase **Damping** (default is 0.001). Damping affects the speed of the simulation, with values closer to 1 making it faster.

5. **Adjust Constraints**
   Under **Constraints Options** inside **SimCloth**, you’ll find the **Mass** setting, which controls the strength of constraints, the bigger it is the less constraints effect simulation. Set it to **0.33** (or higher depending on preference). You will also see the following constraints already included:

   * **Standard Links**: Links that connect adjacent particles and maintain their relative distance.
   * **Stretch Links**: Specialized links to counteract stretching.
   * **Local Range Constraints**: Limits the movement of particles to a defined area.

   You may want to add optional constraints such as:

   * **Bend Stiffness Constraints**: Prevents the cloth from folding.
   * **Volume Constraints**: Attempts to preserve the original shape of the cloth.
   * **Transition Constraints**: Smooths the transition between animated and simulated positions.

6. **Add Constraints**
   Add **Bend Stiffness** to prevent cloth from self-colliding. For Elden Ring or Elden Ring Nightreign, also add **Transition Constraints**.

7. **Adjust Bend Stiffness**
   Set the **Bend Stiffness** to a value between **1** and **0.0001**, depending on how stiff or flexible you want the cloth to be.

8. **Set Collision Options**
   Under **Simulation Cloth** > **Collision Options**, set the **Radius** (recommended values: **0.02** or **0.01**) and keep the **Friction** at default, or adjust as needed.

9. **Add Collidables**
   If the collidables are not showing up, click the right file icon, select the desired collidables, and indicate which vertices the mesh will collide with if needed.

10. **Set Particle-Force Interaction**
    In the **Advanced Option** section of **Simulation Cloth**, set the **Total Mass** to **10** (this controls how easily the mesh will be moved by world wind).

---

### Finalizing the Simulation

1. **Simulation**
   Go back to **Operators**, open **Simulate**, and click **Simulate**. Under **Constraint Execution (Advanced)**, select **Smart Iterate** and adjust the complexity based on mesh complexity:

   * **1** for low-poly meshes
   * **3** for higher poly meshes
   * Use **Thick Clothing (2 meshes)** for very high-poly meshes.

2. **Create Skin Transition**
   For **Elden Ring** or **Elden Ring Nightreign** (or newer versions), go to the **Scripts** tab and select **Wizard Browser...**. Then choose **Create Skin Transition**. In the new pop-up, select the mesh, choose **Simulated State** (usually **`#01#`**), and press **Create Skin Transitions**.

3. **Disable Tangents and Bitangents**
   After the skin transition is created, go back to **Operators**, select **[skin]**, and in **SkinOp**, disable the **Tangents** and **Bitangents** checkboxes.

---

### Thick Simple Clothing Simulation (One Mesh)

This clothing type uses a set mesh for simulation, where the vertices selected for deformation will be influenced by the simulated particles of the same mesh. When you select this option, a window will appear with the following options:

* **Mesh**: The mesh you want to simulate.
* **Skeleton**: The skeleton mesh that the clothing is rigged to.

#### Simulation Options:

* **Simulation Verts**: Select the vertices to simulate.

* **Deformed Verts**: Select the vertices to deform.

* **Fixed Particles**: These are parts that are restricted from movement to prevent the mesh from flying away. A warning will appear if you don’t include all necessary fixed particles, but it will still work. It is **not recommended** to skip this.

* **All of the above include**:

  * `<ALL>`
  * `<NONE>`
  * Or custom selection groups you made beforehand.

* **Max Distance**: This constraint limits the distance the simulated vertices can move. You can also use the vertex group export with the distance type.

* **Add Stretch Links**: If enabled, this will add additional Stretch Link constraints to counteract stretching caused by gravity.

After selecting the desired values, press **OK**. This will create a basic cloth setup that you can adjust.

---

### Configuring the Cloth Simulation

1. **Rename `Simulate` to `#01#`**
   If you're working with **Elden Ring** or **Elden Ring Nightreign**, right-click on **States**, and select **New** to create a new state. Rename it to **`#00#`**.

2. **Adjust Skin Settings**
   Go to **Operator** and select `Skin`. In the right window, uncheck the **`Tangents`** and **`Bitangents`** checkboxes next to the **Skin** section. Apply the same process to the **`Deform Display Mesh`**.

3. **Rename the Transform Set**
   Under **Transform Sets**, click **Master TransformSet** and rename **`Master TransformSet`** to **Master**. If the skeleton name is not **Master TransformSet**, go to Blender and rename the armature to **Master**, then re-export the scene.

4. **Set Gravity and Damping**
   In the **Sim Cloths** section, under the mesh name **`SimCloth`**, go to **Simulation Properties**. Change **Gravity** to the desired value (usually negative Y/Middle), and increase **Damping** (default is 0.001). Damping affects the speed of the simulation, with values closer to 1 making it faster.

5. **Adjust Constraints**
   Under **Constraints Options** inside **SimCloth**, you’ll find the **Mass** setting, which controls the strength of constraints. The higher the value, the less effect constraints have on the simulation. Set it to **0.33** (or higher depending on preference). The default constraints already included are:

   * **Standard Links**: Links that connect adjacent particles and maintain their relative distance.
   * **Stretch Links**: Specialized links to counteract stretching.
   * **Local Range Constraints**: Limits the movement of particles to a defined area.

   You may want to add optional constraints such as:

   * **Bend Stiffness Constraints**: Prevents the cloth from folding.
   * **Volume Constraints**: Attempts to preserve the original shape of the cloth.
   * **Transition Constraints**: Smooths the transition between animated and simulated positions.

6. **Add Constraints**
   Add **Bend Stiffness** to prevent cloth from self-colliding. For Elden Ring or Elden Ring Nightreign, also add **Transition Constraints**.

7. **Adjust Bend Stiffness**
   Set the **Bend Stiffness** to a value between **1** and **0.0001**, depending on how stiff or flexible you want the cloth to be.

8. **Set Collision Options**
   Under **Simulation Cloth** > **Collision Options**, set the **Radius** (recommended values: **0.02** or **0.01**) and keep the **Friction** at default, or adjust as needed.

9. **Add Collidables**
   If the collidables are not showing up, click the right file icon, select the desired collidables, and indicate which vertices the mesh will collide with if needed.

10. **Set Particle-Force Interaction**
    In the **Advanced Option** section of **Simulation Cloth**, set the **Total Mass** to **10** (this controls how easily the mesh will be moved by world wind).

---

### Finalizing the Simulation

1. **Simulation**
   Go back to **Operators**, open **Simulate**, and click **Simulate**. Under **Constraint Execution (Advanced)**, select **Smart Iterate** and adjust the complexity based on mesh complexity:

   * **1** for low-poly meshes
   * **3** for higher poly meshes
   * Use **Thick Clothing (2 meshes)** for very high-poly meshes.

2. **Create Skin Transition**
   For **Elden Ring** or **Elden Ring Nightreign** (or newer versions), go to the **Scripts** tab and select **Wizard Browser...**. Then choose **Create Skin Transition**. In the new pop-up, select the mesh, choose **Simulated State** (usually **`#01#`**), and press **Create Skin Transitions**.

3. **Disable Tangents and Bitangents**
   After the skin transition is created, go back to **Operators**, select **[skin]**, and in **SkinOp**, disable the **Tangents** and **Bitangents** checkboxes.

---

---

### Thick Simple Clothing Simulation (Two Mesh)

This clothing type uses a set of 2 meshes for simulation, where one is used for simulation and the second is used for deforming by the first. A window will appear with the following options:

* **Display Mesh**: The mesh you want to deform.
* **Deform Verts**: Select the vertices to deform.
* **Simulate Mesh**: The mesh you want to simulate.
* **Simulation Verts**: Select the vertices to simulate.
* **Skeleton**: The skeleton mesh that the clothing is rigged to.

#### Simulation Options:

* **Fixed Particles**: These are parts that are restricted from movement to prevent the mesh from flying away. A warning will appear if you don’t include all necessary fixed particles, but it will still work. It is **not recommended** to skip this.
* **All of the Verts above include**:
  * `<ALL>`
  * `<NONE>`
  * Or custom selection groups you made beforehand.
* **Max Distance**: This constraint limits the distance the simulated vertices can move. You can also use the vertex group export with the distance type.
* **Add Stretch Links**: If enabled, this will add additional Stretch Link constraints to counteract stretching caused by gravity.

After selecting the desired values, press **OK**. This will create a basic cloth setup that you can adjust.

---

### Configuring the Cloth Simulation

1. **Rename `Simulate` to `#01#`**
   If you're working with **Elden Ring** or **Elden Ring Nightreign**, right-click on **States**, and select **New** to create a new state. Rename it to **`#00#`**.

2. **Adjust Skin Settings**
   Go to **Operator** and select `Skin`. In the right window, uncheck the **`Tangents`** and **`Bitangents`** checkboxes next to the **Skin** section. Apply the same process to the **`Deform Display Mesh`**.

3. **Rename the Transform Set**
   Under **Transform Sets**, click **Master TransformSet** and rename **`Master TransformSet`** to **Master**. If the skeleton name is not **Master TransformSet**, go to Blender and rename the armature to **Master**, then re-export the scene.

4. **Set Gravity and Damping**
   In the **Sim Cloths** section, under the mesh name **`SimCloth`**, go to **Simulation Properties**. Change **Gravity** to the desired value (usually negative Y/Middle), and increase **Damping** (default is 0.001). Damping affects the speed of the simulation, with values closer to 1 making it faster.

5. **Adjust Constraints**
   Under **Constraints Options** inside **SimCloth**, you’ll find the **Mass** setting, which controls the strength of constraints. The higher the value, the less effect constraints have on the simulation. Set it to **0.33** (or higher depending on preference). The default constraints already included are:
   - **Standard Links**: Links that connect adjacent particles and maintain their relative distance.
   - **Stretch Links**: Specialized links to counteract stretching.
   - **Local Range Constraints**: Limits the movement of particles to a defined area.

   You may want to add optional constraints such as:
   - **Bend Stiffness Constraints**: Prevents the cloth from folding.
   - **Volume Constraints**: Attempts to preserve the original shape of the cloth.
   - **Transition Constraints**: Smooths the transition between animated and simulated positions.

6. **Add Constraints**
   Add **Bend Stiffness** to prevent cloth from self-colliding. For Elden Ring or Elden Ring Nightreign, also add **Transition Constraints**.

7. **Adjust Bend Stiffness**
   Set the **Bend Stiffness** to a value between **1** and **0.0001**, depending on how stiff or flexible you want the cloth to be.

8. **Set Collision Options**
   Under **Simulation Cloth** > **Collision Options**, set the **Radius** (recommended values: **0.02** or **0.01**) and keep the **Friction** at default, or adjust as needed.

9. **Add Collidables**
   If the collidables are not showing up, click the right file icon, select the desired collidables, and indicate which vertices the mesh will collide with if needed.

10. **Set Particle-Force Interaction**
    In the **Advanced Option** section of **Simulation Cloth**, set the **Total Mass** to **10** (this controls how easily the mesh will be moved by world wind).

---

### Finalizing the Simulation

1. **Simulation**
   Go back to **Operators**, open **Simulate**, and click **Simulate**. Under **Constraint Execution (Advanced)**, select **Smart Iterate** and adjust the complexity based on mesh complexity:
   - **1** for low-poly meshes
   - **3** for higher poly meshes
   - Use **Thick Clothing (2 meshes)** for very high-poly meshes.

2. **Create Skin Transition**
   For **Elden Ring** or **Elden Ring Nightreign** (or newer versions), go to the **Scripts** tab and select **Wizard Browser...**. Then choose **Create Skin Transition**. In the new pop-up, select the mesh, choose **Simulated State** (usually **`#01#`**), and press **Create Skin Transitions**.

---


### Preview the Cloth

At the top of the window, you will see a **monitor icon**. Click on it to preview your cloth simulation and check if everything was set up correctly. If changes are needed, you can go back and adjust the settings.


---
