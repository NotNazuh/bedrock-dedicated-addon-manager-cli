## BDS Addon Manager

##### KNOWN ISSUES:
1. If the addon has mutltiple manifest.json files and the application doesn't pick the correct one then it will throw an error.

##### HOW TO USE:
** _Assuming that you've already cloned the repo_ **
For this example we will be using a behavior pack called FamousMonuments.mcpack. (This addon doesn't actually exist, its just an example)

**PREREQUISITES:**
A working Bedrock dedicated server (Before doing anything, make sure to run your server first so everything gets initalized and ready) <br/>
Python3 (Python3.11 was used to create this)<br/>
a working bedrock addon<br/>

**Lets Get Started:**
If you havent already, add the addons to their respective pack folder in the bedrock server (resource pack -> server_path/resource_packs, behavior pack -> server_path/behavior_packs)  
First clone this repo, which can either be done by downloading this repo, or using git  
```git
git https://github.com/NotNazuh/bedrock-dedicated-addon-manager-cli.git .
```
Then cd into the src folder and run:
```powershell
python3 main.py
```
If this is your first time running the application, you will be put into a setup.
Fill in all the required information for the setup, then bds-addon-manager will be ready to use.
Now that we are ready, lets first see all our addons in the server (not including default server addons like vanilla_1.19.70).
To do this we'll use the list commmand, which as the name states lists all the active addons.
```powershell
python3 main.py list
```
output:
```
IDX       NAME                                                               TYPE               UUID                                            ENABLED          SIZE
1       | Absolute Guns 2 3D - V1.4                                    |     resource    |      0f9d2435-a9ac-48d1-a750-34a05fc1131d      |      false     |     1232 kb
2       | Agriculture's Fantasy                                        |     resource    |      b572d192-c6e8-4d3f-80f6-5d29bf7bfbd1      |      false     |      114 kb
3       | lAlchemy And Sorceryr                                        |     resource    |      c3497d23-d8c4-4c00-b892-1dadda11ffe7      |      false     |      124 kb
4       | Anime pets                                                   |     resource    |      101f1b9b-978f-6399-8a06-a0c4ef8cbb3b      |      false     |      651 kb
5       | Chainsawman Add-on                                           |     resource    |      7503ce94-45a1-4c65-a6f4-c1a2cd5bf9d5      |      false     |      354 kb
6       | Defense Turrets                                              |     resource    |      e3c85bb8-7c73-45ec-8693-f6583fe68cac      |      false     |       72 kb
```

Cool, now we can see all our addons, to see how to enable and disable addons run the help command, which will show all commands.  
```powershell
python3 main.py help
```
output:
```
COMMANDS

How to use: py main.py <command>

setup - run the setup function to update your config.json file

list - returns a list of all commands in the server, active or inactive

help - displays help

enable <uuid/all> - enables the addon with the given uuid or all addons

disable <uuid/all> - disables the addon with the given uuid or all addons
```
