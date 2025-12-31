# Setting up your mesh for cloth simulation

Havok uses **vertex-based cloth simulation**, which is what this workflow supports.
The simulation is physically accurate, but for performance reasons **self-collision is not supported**.

---

## Selection Sets / UV Indices

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

## Vertex Selection Groups

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

## Collidables

Because cloth meshes move dynamically, precise control over their position is difficult.
Collidable shapes are used to restrict or guide movement. The following collidable shapes are available:

* Capsule
* Sphere
* Plane
* Convex Geometry
* Convex Heightfield

<img width="641" height="348" alt="image" src="https://github.com/user-attachments/assets/b371e5eb-c0d0-446b-bf74-4045e0e354ea" />

### Notes on Collidables

* Collidable objects use the prefix `collision_<type>` so the addon can identify and skip them during processing.
* They often include a **bone name prefix** to assign the collidable to a specific bone.
* Collidables do **not** need to be parented to the armature and should remain disconnected.


### Creating and Assigning Collidables

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

## Capsule Resizing

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

???+ note

    Tapered Capsules are not supported by the addon. For proper functionality, it is recommended to convert the collidable to **Convex Geometry**.
