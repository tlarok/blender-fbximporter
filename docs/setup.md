# Setup

## Installation

***TODO***

## Configuration

Start by configuring the tool and its core features.

After installing the addon, you will see a new tab in the right tools sidebar (press `N` if you don’t see it) called **UV Tools**. Once opened, you will see the following two fields:

<img width="737" height="122" alt="Без имени-2" src="https://github.com/user-attachments/assets/f39ae368-9b80-46d7-ad69-10e46e1b86ba" />

### Standalone Filter Manager Path

This allows the addon to open the Filter Manager automatically every time you export a scene. Otherwise you will only get a scene (`.hkt`) file.

Go to your Havok installation directory and select
`hctStandAloneFilterManager.exe`.

### Export Path

This is an optional directory where all project files will be stored.
If no path is chosen, the addon will create an `export_data` folder next to the Blender file you are working on. Throughout this guide this directory will be labeled as `<export>`.

???+ warning

    Your Blender project must be saved somewhere on disk in order for the addon to function correctly.
