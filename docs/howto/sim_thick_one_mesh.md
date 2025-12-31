# Thick Simple Clothing Simulation (One Mesh)

<img width="802" height="442" alt="Без имени-2" src="https://github.com/user-attachments/assets/162c1372-e7ba-4d92-9ca6-135396ba3ab7" />

This clothing type uses a set mesh for simulation, where the vertices selected for deformation will be influenced by the simulated particles of the same mesh. When you select this option, a window will appear with the following options:

* **Mesh**: The mesh you want to simulate.
* **Skeleton**: The skeleton mesh that the clothing is rigged to.

## Simulation Options:

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

## Configuring the Cloth Simulation

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

## Finalizing the Simulation

1. **Simulation**
   Go back to **Operators**, open **Simulate**, and click **Simulate**. Under **Constraint Execution (Advanced)**, select **Smart Iterate** and adjust the complexity based on mesh complexity:

   * **1** for low-poly meshes
   * **3** for higher poly meshes
   * Use **Thick Clothing (2 meshes)** for very high-poly meshes.

2. **Create Skin Transition**
   For **Elden Ring** or **Elden Ring Nightreign** (or newer versions), go to the **Scripts** tab and select **Wizard Browser...**. Then choose **Create Skin Transition**. In the new pop-up, select the mesh, choose **Simulated State** (usually **`#01#`**), and press **Create Skin Transitions**.

3. **Disable Tangents and Bitangents**
   After the skin transition is created, go back to **Operators**, select **[skin]**, and in **SkinOp**, disable the **Tangents** and **Bitangents** checkboxes.

## Next step
   * [Export Results](save_result.md)
