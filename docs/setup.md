# Setup

## Installation

***TODO***

## Configuration

### Step 1: Install Havok

1. **Install Havok** from the **Resources** link.
2. Run the executable file to start the installation process. During the installation, **save the installation path** somewhere for future reference.
3. After the installation, navigate to the folder `havok_contectool\New DLL` in the **Resources** folder and copy the two `.dll` files.
4. Go to the previously saved Havok installation path and locate the directory:
   `Havok\HavokContentTools\filters`
5. Paste the copied `.dll` files into this folder and **replace** the existing files when prompted.

### Step 2: Configure the Tool

Once Havok is installed, you can proceed to configure the tool and its core features.

After installing the addon, you will see a new tab in the right-hand sidebar (press `N` if it doesn’t show up) called **UV Tools**. Once you open it, you will see the following two fields:

![sidebar addon](assets/images/configuration.png)

### Standalone Filter Manager Path

The path you saved earlier during the Havok installation is required here.
In the **Standalone Filter Manager Path** field, **select** the file `hctStandAloneFilterManager.exe` located inside the folder:
`Havok\HavokContentTools`

### Export Path

This is an optional directory where all your project files will be stored.
If you don’t specify an export path, the addon will automatically create an `export_data` folder next to your current Blender project file. Throughout this guide, this folder will be referred to as `<export>`.

???+ warning

    Your Blender project must be saved somewhere on disk in order for the addon to save setup files and addon functionality.
