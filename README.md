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

## Quick Search Steps

* [Setup](#setup)
* [Usage](#usage)
* [Preparation](#preparation)
* [Setting Up the Mesh for Simulation](#setting-up-the-mesh-for-simulation)
* [Workflow](#workflow)
* [Preview Cloth](#preview-the-cloth)
* [Exporting](#exporting-the-clothing-file)
* [Troubleshooting](#troubleshooting)

## Essention Tools
* [resources](https://drive.google.com/file/d/190iheSf0UHfU0XdSG0hd7ueUEtLxtpyP/view)
* [WitchyBND](https://github.com/ividyon/WitchyBND), keep in mind that latest version still doesn't work with bloodborne tpf files so use that one in the meanwhile [WitchyBND](https://github.com/ividyon/WitchyBND/releases/tag/v2.16.0.2)
* [FbxImporter](https://github.com/The12thAvenger/FbxImporter)
* [FLVER_Editor](https://github.com/Pear0533/FLVER_Editor)
* [DS3HavokConverter](https://github.com/The12thAvenger/DS3HavokConverter)
* [Discord Soulsmodding Serv With Some Tools ?ServerName?](https://discord.gg/emk4E6ny)
* [hkxpackbb](https://discord.com/channels/529802828278005773/529900741998149643/699509305929629849)
* [hkxpack](https://discord.com/channels/529802828278005773/529900741998149643/1187076379116839033)
* [Aqua Toolset](https://github.com/Shadowth117/Aqua-Toolset)


## Setup

Start by configuring the tool and its core features.

After installing the addon, you will see a new tab in the right tools sidebar (press **N** if you don’t see it) called **UV Tools**. Once opened, you will see the following two fields:

<img width="737" height="122" alt="Без имени-2" src="https://github.com/user-attachments/assets/f39ae368-9b80-46d7-ad69-10e46e1b86ba" />

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

For player characters, it's recommended to extract the skeleton from `fc_m_0000.partsbnd.dcx`. Since FLVER files cannot be imported directly without external tools or addons, user suggested using the [Aqua Toolset](https://github.com/Shadowth117/Aqua-Toolset) to export the model as an FBX, which can then be imported into Blender.

> FromSoftware armatures are typically named `Master`.
> Make sure the armature in your Blender scene is renamed to `Master`, or the created physics will not work correctly.

Next, prepare the mesh you are creating physics or clothing for. It must be rigged to the same armature. Also mesh must be triangular, otherwise mesh will have missmatch with model you will later import in flver.

* Enable **Auto Normalize** in Blender in weight painting mode in settings in the right

<img width="392" height="503" alt="image" src="https://github.com/user-attachments/assets/af97c2aa-41e0-4428-a9a0-27bfdcd75cbc" />

* **Or** after finishing weight painting, go to **Weight Paint Mode → Weights → Normalize All**

<img width="866" height="435" alt="image" src="https://github.com/user-attachments/assets/35262424-060e-4b06-bad2-9032a069699a" />

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

<img width="927" height="637" alt="image" src="https://github.com/user-attachments/assets/35c8c081-eece-426f-b85e-20de68185158" />

This will create an entry in:

* `blend_path/export_data/selectionsets/uv_indices.json`, or
* `optional_export_path/selectionsets/uv_indices.json`

---

### Vertex Selection Groups

Vertex groups are float-based selections used when non-uniform values are required.

To export a vertex group:

* Create a vertex group on the mesh
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

* Press a **Export Vertex Group(UV Oder)**

<img width="1323" height="780" alt="image" src="https://github.com/user-attachments/assets/296a2af9-0eaa-46f6-9ec3-2359438d6ff2" />

The data will be saved to:

* `blend_path/export_data/floatchannels/weight_groups.json`, or
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

<img width="641" height="348" alt="image" src="https://github.com/user-attachments/assets/b371e5eb-c0d0-446b-bf74-4045e0e354ea" />

#### Notes on Collidables

* Collidable objects use the prefix `collision_<type>` so the addon can identify and skip them during processing.
* They often include a **bone name prefix** to assign the collidable to a specific bone.
* Collidables do **not** need to be parented to the armature and should remain disconnected.


#### Creating and Assigning Collidables

* Select a mesh or collidable object shape type you want to change
* Choose a **Collision Type**
* Assign a bone using the **Bone Selector** (if needed)
* Press **Set Collision** to convert the mesh into the selected collision shape

<img width="403" height="197" alt="Без имени-2" src="https://github.com/user-attachments/assets/d4baba8c-cd30-4bda-be92-35d43aea7548" />

If the object is already a collidable, it will be updated except a Bone Selector if already set.

When selecting an **armature**, a **Place Collidable** button appears:

* Select **one bone** in Edit/Pose mode → create a **sphere**
* Select **two bones** in Edit/Pose mode → create a **capsule**

<img width="1068" height="434" alt="Без имени-2" src="https://github.com/user-attachments/assets/86e2cdd4-29a7-4d32-80a9-3f9e4423bd93" />

<img width="993" height="413" alt="Без имени-2" src="https://github.com/user-attachments/assets/08b03816-e216-4881-a823-4fb0e6dea8dc" />

### Capsule Resizing

When a **capsule collidable mesh** is selected, additional resize options will appear.

Capsules can be resized using the following control points:

* **Bottom**
* **Middle**
* **Top**

To resize the capsule:

1. Toggle the desired controls (`Bottom`, `Middle`, and/or `Top`)
2. Press **Resize Capsule** to apply the changes

<img width="1716" height="546" alt="Без имени-2" src="https://github.com/user-attachments/assets/17b108b0-8f6f-4254-99aa-396f44da6166" />

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

<img width="1003" height="727" alt="Без имени-2" src="https://github.com/user-attachments/assets/cd46f059-4068-4455-8c78-2a5847edfbb5" />

### Step-by-step Setup

1. **Choose `Setup Cloth`**
   In the new window on the right, click **`Launch Cloth Setup Tool`**. Ensure that `Cloth Setup Tool Mode` is set to **`Standalone`**. **`Modal`** technically works but is not recommended.

2. **Cloth Setup Tool**
   When the Cloth Setup Tool opens, you will see an empty cloth entity. You can delete this entity. Next, click on the **`Script`** tab at the top, and select **`Wizard Browser...`**. This will pop up a window with different cloth simulation types. While you can create most of them manually, this guide will cover only the following types:

   * **[Simple](#character-simple-clothing-simulation)**
   * **[Thick Single Mesh](#thick-simple-clothing-simulation-one-mesh)**
   * **[Two Mesh Simulation](#thick-simple-clothing-simulation-two-mesh)**

<img width="398" height="692" alt="image" src="https://github.com/user-attachments/assets/caca05a3-e7cf-4a51-bade-06ef16c6eb99" />

<img width="758" height="602" alt="Без имени-2" src="https://github.com/user-attachments/assets/e728bdc3-8468-492a-a291-a62b9ebc4b68" />

---

### Character Simple Clothing Simulation

<img width="621" height="360" alt="Без имени-2" src="https://github.com/user-attachments/assets/8a18bb89-981a-4d53-919a-fd3056b3ce8f" />

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

### Next step
   * [Preview Cloth](#preview-the-cloth)

---

### Thick Simple Clothing Simulation (One Mesh)

<img width="802" height="442" alt="Без имени-2" src="https://github.com/user-attachments/assets/162c1372-e7ba-4d92-9ca6-135396ba3ab7" />

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

### Next step
   * [Preview Cloth](#preview-the-cloth)

---

### Thick Simple Clothing Simulation (Two Mesh)

<img width="807" height="458" alt="Без имени-2" src="https://github.com/user-attachments/assets/291c7c6b-238e-4543-a81b-19db4ec3e326" />

This clothing type uses a set of 2 meshes for simulation, where one is used for simulation and the another is used for deforming by the first. A window will appear with the following options:

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

### Next step
   * [Preview Cloth](#preview-the-cloth)


---


### Preview the Cloth

At the top of the window, you will see a **monitor icon**. Click on it to preview your cloth simulation and check if everything was set up correctly. If changes are needed, you can go back and adjust the settings.

---

### Exporting Clothing

Now you can press **Ctrl + S** to save your setup and close the window to move on to the Filter Manager.

Next, you need to import your mesh into **FLVER** with the correct buffer exposed to Havok in order to ensure that the cloth will apply correctly in the game. For this, you can use the **12thAvenger's tool**, [FbxImporter](https://github.com/The12thAvenger/FbxImporter).

**Important**: Always import meshes in the correct order to avoid issues. If you reimport meshes into an already created FLVER, there could be problems due to incorrect ordering.

### Import Meshes in the Correct Order:

1. **First All Clothing Meshes Materials**:

   * **Bloodborne**: `p[arsn]_cloth.mtd`
   * **Dark Souls 3**: `c[arsn]_cloth.mtd`
   * **Elden Ring and Elden Ring Nightreign**: `c[amsn]_cloth.matxml`

2. **Non Clothing Meshes Materials**:
   * **Bloodborne**: `p[arsn].mtd`
   * **Dark Souls 3**: `c[arsn].mtd`
   * **Elden Ring and Elden Ring Nightreign**: `c[amsn].matxml`

**Note**: The FLVER file must come from the specific game you're working with. Using a FLVER from a different game type will not work.

Once your model is properly imported, you can move on to exporting the clothing file.

### Exporting the Clothing File

1. Go to **Execute Cloth Setup** in the Filter Manager.
2. If the field is empty, type anything in it to enable the **...** button, allowing you to select the FLVER file you imported the model into.
3. After selecting the FLVER file, go to **Write to Platform**.

### Write to Platform

Here, the process differs between games:

* **For Elden Ring and Elden Ring Nightreign**:

  * Set the **Format** to **MSVC x64, XBoxOne, Switch64_win**.
  * After that, press **Run Configuration**.
  * Keep in mind to export the file into the same folder as the scene (i.e., the `export_data` folder) as Havok can have issues if placed elsewhere.

* **For Bloodborne and Dark Souls 3**:

  * In **Filter Manager**, under **Execute Cloth Setup**, type anything in the field to enable the **...** button to select the FLVER file.
  * Set **Format** to **XML** and export it to the same folder as the scene (the `export_data` folder).
  * Use the **12thAvenger's tool** [DS3HavokConverter](https://github.com/The12thAvenger/DS3HavokConverter) to convert the XML into Havok 2014 XML format (since Bloodborne and Dark Souls 3 use Havok 2014, and newer versions won’t work).

  After that, you’ll need to convert the XML into **binary/hkx** format using **hkxpack**, which can be found on the Discord server ([?ServerName?](https://discord.gg/emk4E6ny)).

  There are two versions of hkxpack:

  * For **Dark Souls 3**: [hkxpack](https://discord.com/channels/529802828278005773/529900741998149643/1187076379116839033)
  * For **Bloodborne**: [hkxpackbb](https://discord.com/channels/529802828278005773/529900741998149643/699509305929629849)

  After running the XML through the tool, you'll get the required hkx clothing file.

### Continue with the Process for All Games

Once you have the hkx file ready, you need to obtain the **DCX model file** containing the clothing. You can then copy the **CLM2 file** and the file IDs into the `_witchy-bnd4.xml` for your DCX file. This could be an armor or any other item that contains the hkx and CLM2 file, as the CLM2 is essential for the physics to work in the game.

### Packing the DCX

Once you've packed everything into the DCX, go ahead and test the physics in the game to make sure everything works correctly.

---

### Troubleshooting

Here are some possible issues you might encounter during the process:

1. **Export Doesn’t Execute**:

   * **Transformation not applied**: If the export doesn’t execute properly, it may be due to transformations. The addon automatically applies all transformations, but the **12thAvenger's tool** does not. To avoid mismatches, in Blender, select all display meshes that will be in the FLVER, then go to the top menu: **Object → Apply → All Transformations**.

2. **Cloth Weirdly deformed**:

   * **Non-normalized weight paint**: If the mesh looks weird or deformed in the game, it’s likely because the weight paint wasn’t normalized. To fix this, go through all your display meshes and proxy models, then go into **Weight Paint Mode**, and click on the top menu: **Weight → Normalize All**. Re-export the scene and re-export the cloth after that.

If you encounter any other unknown issues that aren't covered in this guide, feel free to reach out to me in the Discord server. My username is **Tlarok**.
