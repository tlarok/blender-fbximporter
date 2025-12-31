# Troubleshooting

Here are some possible issues you might encounter during the process:

1. **Export Doesn’t Execute**:

   * **Transformation not applied**: If the export doesn’t execute properly, it may be due to transformations. The addon automatically applies all transformations, but the **12thAvenger's tool** does not. To avoid mismatches, in Blender, select all display meshes that will be in the FLVER, then go to the top menu: **Object → Apply → All Transformations**.

2. **Cloth Weirdly deformed**:

   * **Non-normalized weight paint**: If the mesh looks weird or deformed in the game, it’s likely because the weight paint wasn’t normalized. To fix this, go through all your display meshes and proxy models, then go into **Weight Paint Mode**, and click on the top menu: **Weight → Normalize All**. Re-export the scene and re-export the cloth after that.

If you encounter any other unknown issues that aren't covered in this guide, feel free to reach out to me in the Discord server. My username is **Tlarok**.
