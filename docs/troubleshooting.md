# Troubleshooting

Below are some common issues you may encounter during the process and how to resolve them.

---

## 1. **Export Doesn’t Execute**

* **Transformations not applied**:
  If the export does not execute correctly, this is often caused by unapplied transformations. The addon automatically applies transformations, but **12thAvenger’s tool** does not.
  To avoid mismatches, in Blender select **all display meshes** that will be included in the FLVER **along with the armature**, then go to:
  **Object → Apply → All Transformations**.
  After that, re-import the model into FLVER and repeat the export process.

---

## 2. **Cloth Is Weirdly Deformed**

* **Non-normalized weight painting**:
  If the cloth mesh appears distorted or deformed in-game, the weight paint is likely not normalized. To fix this, check all display meshes and proxy models. Enter **Weight Paint Mode**, then use:
  **Weight → Normalize All**.
  Afterward, re-export the scene, re-import everything into FLVER, and re-export the cloth.

---

## 3. **Vertices Are Flying Into Space**

* **Non-normalized weight painting**:
  If the mesh stretches or explodes in-game, the weight paint may not be normalized. This issue is usually easy to fix. Verify all display meshes and proxy models, enter **Weight Paint Mode**, and select:
  **Weight → Normalize All**.
  Then re-export the scene, re-import the display model into FLVER, and re-export the cloth.

* **Missing weight painting**:
  If parts of the mesh have **no weight paint at all**, normalization will not fix the issue. Vertices without any bone influence can fly off or behave unpredictably in-game.
  In this case, you must manually assign proper weights to the affected vertices. If you are not familiar with weight painting or rigging, it is strongly recommended to watch some basic **3D modeling and rigging tutorials** before continuing.

* **Incorrect mesh order in FLVER**:
  If the mesh was imported in an unusual or incorrect order, this can also cause the issue. Go back to the [save result](howto/save_result.md) step and repeat the process from there.

---

If you encounter any other issues not covered in this guide, feel free to contact me on the [Discord server](https://discord.gg/zcvPMmBF). My username is **Tlarok**.