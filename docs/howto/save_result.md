# Adding the simulation results to your game

At the top of the window, you will see a **monitor icon**. Click on it to preview your cloth simulation and check if everything was set up correctly. If changes are needed, you can go back and adjust the settings.

---

## Exporting Clothing

Now you can press **Ctrl + S** to save your setup and close the window to move on to the Filter Manager.

Next, you need to import your mesh into **FLVER** with the correct buffer exposed to Havok in order to ensure that the cloth will apply correctly in the game. For this, you can use the **12thAvenger's tool**, [FbxImporter](https://github.com/The12thAvenger/FbxImporter).

**Important**: Always import meshes in the correct order to avoid issues. If you reimport meshes into an already created FLVER, there could be problems due to incorrect ordering.

## Import Meshes in the Correct Order:

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

## Exporting the Clothing File

1. Go to **Execute Cloth Setup** in the Filter Manager.
2. If the field is empty, type anything in it to enable the **...** button, allowing you to select the FLVER file you imported the model into.
3. After selecting the FLVER file, go to **Write to Platform**.

## Write to Platform

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

## Continue with the Process for All Games

Once you have the hkx file ready, you need to obtain the **DCX model file** containing the clothing. You can then copy the **CLM2 file** and the file IDs into the `_witchy-bnd4.xml` for your DCX file. This could be an armor or any other item that contains the hkx and CLM2 file, as the CLM2 is essential for the physics to work in the game.

## Packing the DCX

Once you've packed everything into the DCX, go ahead and test the physics in the game to make sure everything works correctly.
