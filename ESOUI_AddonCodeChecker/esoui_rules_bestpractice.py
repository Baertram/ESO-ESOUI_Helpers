# Offizielle ESOUI Vorgaben & Best Practices (nach Dateitypen getrennt) - Original Foren Post: https://www.esoui.com/forums/showpost.php?p=49229&postcount=1
CUSTOM_RULES = """
[zip file contents]
- There must not be any hidden or system or development IDE files/folders in the zip file, like .github, .vs, .idea, etc. These must be removed before uploading the zip file.
- The zip file must not contain any executable files or other zip/rar/tar/'archive' files. It may contain pdf documents for explanation, and other .txt files (non-manifest files where the name does not match the addon folder), .md files, but it should not contain any Microsoft Word or RTF files, or images, nor any videos. Only filetypes usualyl allowed are .txt .addon .dds .lua .xml .md and subfolders. Any other filetype should be reported and checked.

[MANIFEST / MANIFEST-LIKE FILES (.addon / .txt / .toc)]
CRITICAL RULES (Must be followed):
- The ZIP's main level must contain 1 folder with the addon name, where the foldername is case sensitive and must match the manifest file name in that folder exactly.
- The manifest file (.addon, or .txt) name must match the main directory folder name inside the ZIP exactly.
- APIVersion: Must only contain a maximum of TWO API versions (e.g., '## APIVersion: 101050 101051'). If three or more are listed, it is invalid. Best practice: Use the current live version and a following 'future' + 1 version.
- Dependencies: For non-optional dependencies (## DependsOn, ## PCDependsOn, ## ConsoleDependsOn), you MUST enforce the '>=' version check format (e.g., '## DependsOn: LibAddonMenu-2.0>=43'). 
- Optional Dependencies: OptionalDependsOn does not support any >= version checks as these are optional and will never suppress your addon loading like mandatory DependsOn does.
- Dependencies Syntax: There must be a colon ':' right after the tag name, and multiple dependencies must ONLY be separated by a space. Do NOT use commas ',' or semicolons ';'.
- SavedVariables: The ## SavedVariables: table names defined in that row behind the : will create global tables in _G! You can define multiple SavedVariable tables in the same row just split by a space. You must assure that th SV table names are unique and long enough, and clearly attached to the addon name to prevent global namespace pollution e.g. MyAddonName_SV instead of MA_SV.
- The rows in the manifest files must not be longer than 301 bytes each. If e.g. your DependsOn or OptionalDependsOn rows are longer, split them up into multiple rows starting with the same tag e.g. ## OptionalDependsOn: .

BEST PRACTICES (Highly recommended):
- Version Check: Verify that version numbers used in '>=' dependency checks match valid recent addon version integers.

[LUA FILES (.lua)]
CRITICAL RULES (Must be followed):
- Global Namespace Pollution: Do NOT create new global variables, global tables, or non-local functions. Everything that leaks into the global table (_G) without explicit intent is a violation, unless it's aleady globally accessible as part of the esoui vanilla source code/API Documentation.
- Global Table Strict Exception: You are ONLY allowed to create exactly ONE unique global table (e.g., 'MyAddon = MyAddon or {}') IF the addon actually consists of multiple .lua files that need to share data, or if there is an Keybinding.xml or other XML files referencing it. If the addon consists of ONLY ONE single .lua file and does NOT provide an external API to other addons or keybindings, creating a global table is UNNECESSARY and counts as Global Pollution! Everything must be kept strictly 'local' in single-file addons.
- Naming conventions for global variables: If global variables are defined for your addon make sure they use a unique long name that is clearly connected to your addon name, no abbreviated names like e.g. BS or BS_UI or similar, but use the long name BattlegroundStatus e.g..
- Local Functions & Variables: Local variables and local functions (e.g., 'local function Initialize()') are PERFECTLY FINE and highly encouraged. Do NOT force truly local functions or local helper variables to become methods of the global addon table. Only attach functions to the global addon table if they genuinely need cross-file or XML accessibility!
- Function Hooking Exception (CRITICAL): Overwriting or hooking existing global game functions (typically starting with 'ZO_' like 'ZO_GetPlatformTraitInformationIcon' or 'ZO_GetItemSellInformationIcon'; but can be any exisiting vanilla esoui or other addons' global funciton) is fully ALLOWED and required for addon functionality. Do NOT flag the rewriting of existing game functions or engines as global pollution! Do NOT ask the developer to move these hooked vanilla functions into their own addon table, as that would break the game hook.
- Ingame Messages: Do NOT print chat messages like "My addon has loaded" to the general chat window on startup (causes chat spam). Use LibDebugLogger or an explicit opt-in setting instead.
- SavedVariables Usage: SavedVariables are nil before EVENT_ADD_ON_LOADED. Ensure they are only accessed during or after this event. Do not use outdated 'CharacterName' saved ZO_SavedVars wrapper calls; use 'NewCharacterIDSettings' ('ZO_SavedVars:NewCharacterIdSettings'). 
- Deprecated LibStub Usage: Do NOT use LibStub. It is completely obsolete since the 'Summerset' update and must not be used anymore. If you see 'LibStub' being called or used in the active source code, report it as a CRITICAL VIOLATION. (Note: It is allowed inside pure code comments, but forbidden in functional code). Tell the developer to check the official guidelines for replacement here: https://wiki.esoui.com/Libraries#LibStub_-_Library_version_control_.28obsolete.21.29

BEST PRACTICES (Highly recommended):
- Event Filters: ONLY suggest Event Filters (via 'AddFilterForEvent') if the code actively registers high-frequency events that actually support filters (Currently supported Event Filters' Events are: EVENT_ABILITY_COOLDOWN_UPDATED, EVENT_COMBAT_EVENT, EVENT_EFFECT_CHANGED, EVENT_INVENTORY_SINGLE_SLOT_UPDATE, EVENT_POWER_UPDATE, EVENT_INTERFACE_SETTING_CHANGED, Any event with a unitTag argument, any event with a shownInGamepadPreferredMode argument.). Do NOT suggest event filters for other events (e.g. generic setup events like 'EVENT_ADD_ON_LOADED', as they do not support filters).
- Performance: Define a local speed-up reference to your global addon table at the top of the file (e.g., 'local ma = MyAddon') so the Lua interpreter doesn't repeatedly scan the _G table when accessing global properties. Re-use that local reference in your total file, instead of the global variable then.

[XML FILES (.xml)]
CRITICAL RULES (Must be followed):
- Absolute Paths: Do NOT use hardcoded absolute file paths.
- UI Naming Conflicts: Ensure all UI control elements and frames have unique names to avoid conflicts with other addons or the base game UI. Same rules apply like for global lua variables: Must be unique and clearly connected to your addon name, no abbreviated names like e.g. BS_UI_TLC.
- Structure: Check for properly closed tags and syntactically correct layout positioning properties.
"""
