-- Checked on 11.11.2026 20:47:17 / ServerScope: live / APIVersion: 101051
-- Total Files Actually Scanned: 2424 (*.lua 1501 / *.xml 908 / *.txt 15)
-- Total Undocumented Global Variables Found: 1027

--0. Globals that were read manually from _G
ACTION_RESULT_EFFECT_FADED = nil
ACTION_RESULT_EFFECT_GAINED = nil
ACTION_RESULT_EFFECT_GAINED_DURATION = nil

-- 1. Global Constants (with ITERATION_ / _MIN_VALUE / _MAX_VALUE) --
ACCOUNT_LABEL_MAX_VALUE = nil --/esoui/Libraries/Utility/ZO_PlatformUtils.lua:31:41 | internalassert(UI_PLATFORM_MAX_VALUE == [[ ACCOUNT_LABEL_MAX_VALUE ]], "There should be a platform account label for every platform")
ADVENTURE_ZONE_BOSS_ITERATION_BEGIN = nil --/esoui/Ingame/AdventureZone/Gamepad/AdventureZoneBossTree_Gamepad.lua:24:16 | for boss = [[ ADVENTURE_ZONE_BOSS_ITERATION_BEGIN ]], ADVENTURE_ZONE_BOSS_ITERATION_END do
ADVENTURE_ZONE_BOSS_ITERATION_END = nil --/esoui/Ingame/AdventureZone/Gamepad/AdventureZoneBossTree_Gamepad.lua:24:53 | for boss = ADVENTURE_ZONE_BOSS_ITERATION_BEGIN, [[ ADVENTURE_ZONE_BOSS_ITERATION_END ]] do
ADVENTURE_ZONE_FACTION_ITERATION_BEGIN = nil --/esoui/Ingame/AdventureZone/Gamepad/AdventureZoneOverview_Gamepad.lua:63:27 | for faction = [[ ADVENTURE_ZONE_FACTION_ITERATION_BEGIN ]], ADVENTURE_ZONE_FACTION_ITERATION_END do
ADVENTURE_ZONE_FACTION_ITERATION_END = nil --/esoui/Ingame/AdventureZone/Gamepad/AdventureZoneOverview_Gamepad.lua:63:67 | for faction = ADVENTURE_ZONE_FACTION_ITERATION_BEGIN, [[ ADVENTURE_ZONE_FACTION_ITERATION_END ]] do
ALLIANCE_ITERATION_BEGIN = nil --/esoui/Ingame/Tooltip/MapTooltips.lua:305:20 | for alliance = [[ ALLIANCE_ITERATION_BEGIN ]], ALLIANCE_ITERATION_END do
ALLIANCE_ITERATION_END = nil --/esoui/Ingame/Tooltip/MapTooltips.lua:305:46 | for alliance = ALLIANCE_ITERATION_BEGIN, [[ ALLIANCE_ITERATION_END ]] do
ALLIANCE_MAX_VALUE = nil --/esoui/Common/RzChroma/RzChroma_Effects.lua:23:40 | for alliance = ALLIANCE_MIN_VALUE, [[ ALLIANCE_MAX_VALUE ]] do
ALLIANCE_MIN_VALUE = nil --/esoui/Common/RzChroma/RzChroma_Effects.lua:23:20 | for alliance = [[ ALLIANCE_MIN_VALUE ]], ALLIANCE_MAX_VALUE do
ANTIQUITY_DIFFICULTY_MAX_VALUE = nil --/esoui/Ingame/Antiquities/AntiquityManager.lua:209:42 | for antiquityDifficulty = 1, [[ ANTIQUITY_DIFFICULTY_MAX_VALUE ]] do
ANTIQUITY_FILTER_ITERATION_BEGIN = nil --/esoui/Ingame/Antiquities/Keyboard/AntiquityJournal_Keyboard.lua:880:22 | for filterType = [[ ANTIQUITY_FILTER_ITERATION_BEGIN ]], ANTIQUITY_FILTER_ITERATION_END do
ANTIQUITY_FILTER_ITERATION_END = nil --/esoui/Ingame/Antiquities/Keyboard/AntiquityJournal_Keyboard.lua:880:56 | for filterType = ANTIQUITY_FILTER_ITERATION_BEGIN, [[ ANTIQUITY_FILTER_ITERATION_END ]] do
ANTIQUITY_FILTER_MAX_VALUE = nil --/esoui/Ingame/Antiquities/Gamepad/AntiquityJournal_Gamepad.lua:234:53 | for i = ANTIQUITY_FILTER_MIN_VALUE, [[ ANTIQUITY_FILTER_MAX_VALUE ]] do
ANTIQUITY_FILTER_MIN_VALUE = nil --/esoui/Ingame/Antiquities/Gamepad/AntiquityJournal_Gamepad.lua:234:25 | for i = [[ ANTIQUITY_FILTER_MIN_VALUE ]], ANTIQUITY_FILTER_MAX_VALUE do
BATTLEGROUND_TEAM_ITERATION_BEGIN = nil --/esoui/Ingame/Battleground/BattlegroundScoreHud.lua:259:18 | for bgTeam = [[ BATTLEGROUND_TEAM_ITERATION_BEGIN ]], BATTLEGROUND_TEAM_ITERATION_END do --TODO Unavailable pre battleground -- GetBattlegroundNumTeams(GetCurrentBattlegroundId()) do
BATTLEGROUND_TEAM_ITERATION_END = nil --/esoui/Ingame/Battleground/BattlegroundScoreHud.lua:259:53 | for bgTeam = BATTLEGROUND_TEAM_ITERATION_BEGIN, [[ BATTLEGROUND_TEAM_ITERATION_END ]] do --TODO Unavailable pre battleground -- GetBattlegroundNumTeams(GetCurrentBattlegroundId()) do
BATTLEGROUND_TEAM_MAX_VALUE = nil --/esoui/Ingame/AddonCompatibilityAliases/PC/AddonCompatibilityAliases_PC.lua:1364:35 | BATTLEGROUND_ALLIANCE_MAX_VALUE = [[ BATTLEGROUND_TEAM_MAX_VALUE ]]
BATTLEGROUND_TEAM_MIN_VALUE = nil --/esoui/Ingame/AddonCompatibilityAliases/PC/AddonCompatibilityAliases_PC.lua:1363:35 | BATTLEGROUND_ALLIANCE_MIN_VALUE = [[ BATTLEGROUND_TEAM_MIN_VALUE ]]
BOSS_RANK_ITERATION_BEGIN = nil --/esoui/Ingame/UnitFrames/BossBar.lua:24:13 | for i = [[ BOSS_RANK_ITERATION_BEGIN ]], BOSS_RANK_ITERATION_END do
BOSS_RANK_ITERATION_END = nil --/esoui/Ingame/UnitFrames/BossBar.lua:24:40 | for i = BOSS_RANK_ITERATION_BEGIN, [[ BOSS_RANK_ITERATION_END ]] do
BUFFS_SETTING_ITERATION_BEGIN = nil --/esoui/Ingame/BuffDebuff/BuffDebuff.lua:378:17 | for i = [[ BUFFS_SETTING_ITERATION_BEGIN ]], BUFFS_SETTING_ITERATION_END do
BUFFS_SETTING_ITERATION_END = nil --/esoui/Ingame/BuffDebuff/BuffDebuff.lua:378:48 | for i = BUFFS_SETTING_ITERATION_BEGIN, [[ BUFFS_SETTING_ITERATION_END ]] do
CHAPTER_ITERATION_BEGIN = nil --/esoui/PregameAndIngame/OptionsPanels/OptionsPanel_Audio_Shared.lua:324:20 | for settingValue = [[ CHAPTER_ITERATION_BEGIN ]], CHAPTER_ITERATION_END do
CHROMA_DEVICE_TYPE_ITERATION_BEGIN = nil --/esoui/Common/RzChroma/RzChroma_Manager.lua:99:22 | for deviceType = [[ CHROMA_DEVICE_TYPE_ITERATION_BEGIN ]], CHROMA_DEVICE_TYPE_ITERATION_END do
CHROMA_DEVICE_TYPE_ITERATION_END = nil --/esoui/Common/RzChroma/RzChroma_Manager.lua:99:58 | for deviceType = CHROMA_DEVICE_TYPE_ITERATION_BEGIN, [[ CHROMA_DEVICE_TYPE_ITERATION_END ]] do
COLLECTIBLE_CATEGORY_TYPE_ITERATION_BEGIN = nil --/esoui/Ingame/Dyeing/Dyeing_Shared.lua:54:58 | IterateDyeableSlotData(RESTYLE_MODE_COLLECTIBLE, [[ COLLECTIBLE_CATEGORY_TYPE_ITERATION_BEGIN ]], COLLECTIBLE_CATEGORY_TYPE_ITERATION_END)
COLLECTIBLE_CATEGORY_TYPE_ITERATION_END = nil --/esoui/Ingame/Dyeing/Dyeing_Shared.lua:54:101 | IterateDyeableSlotData(RESTYLE_MODE_COLLECTIBLE, COLLECTIBLE_CATEGORY_TYPE_ITERATION_BEGIN, [[ COLLECTIBLE_CATEGORY_TYPE_ITERATION_END ]])
COLLECTIBLE_RESTRICTION_TYPE_ITERATION_BEGIN = nil --/esoui/PublicAllIngames/Tooltip/CollectionsTooltips.lua:248:31 | for restrictionType = [[ COLLECTIBLE_RESTRICTION_TYPE_ITERATION_BEGIN ]], COLLECTIBLE_RESTRICTION_TYPE_ITERATION_END do
COLLECTIBLE_RESTRICTION_TYPE_ITERATION_END = nil --/esoui/PublicAllIngames/Tooltip/CollectionsTooltips.lua:248:77 | for restrictionType = COLLECTIBLE_RESTRICTION_TYPE_ITERATION_BEGIN, [[ COLLECTIBLE_RESTRICTION_TYPE_ITERATION_END ]] do
CONSOLE_ENHANCED_RENDER_QUALITY_ITERATION_BEGIN = nil --/esoui/PregameAndIngame/OptionsPanels/OptionsPanel_Video_Shared.lua:164:28 | for settingValue = [[ CONSOLE_ENHANCED_RENDER_QUALITY_ITERATION_BEGIN ]], CONSOLE_ENHANCED_RENDER_QUALITY_ITERATION_END do
CONSOLE_ENHANCED_RENDER_QUALITY_ITERATION_END = nil --/esoui/PregameAndIngame/OptionsPanels/OptionsPanel_Video_Shared.lua:164:77 | for settingValue = CONSOLE_ENHANCED_RENDER_QUALITY_ITERATION_BEGIN, [[ CONSOLE_ENHANCED_RENDER_QUALITY_ITERATION_END ]] do
CONSOLE_SERVER_ITERATION_BEGIN = nil --/esoui/Pregame/AccountLogin/Gamepad/GameStartup_Gamepad.lua:82:18 | for choice = [[ CONSOLE_SERVER_ITERATION_BEGIN ]], CONSOLE_SERVER_ITERATION_END do
CONSOLE_SERVER_ITERATION_END = nil --/esoui/Pregame/AccountLogin/Gamepad/GameStartup_Gamepad.lua:82:50 | for choice = CONSOLE_SERVER_ITERATION_BEGIN, [[ CONSOLE_SERVER_ITERATION_END ]] do
CURRENCY_LOCATION_MAX_VALUE = nil --/esoui/Ingame/Inventory/InventoryWallet.lua:3:31 | local CURRENCY_LOCATION_ALL = [[ CURRENCY_LOCATION_MAX_VALUE ]] + 1
CURT_ITERATION_BEGIN = nil --/esoui/Ingame/Inventory/Inventory.lua:2656:24 | for currencyType = [[ CURT_ITERATION_BEGIN ]], CURT_ITERATION_END do
CURT_ITERATION_END = nil --/esoui/Ingame/Inventory/Inventory.lua:2656:46 | for currencyType = CURT_ITERATION_BEGIN, [[ CURT_ITERATION_END ]] do
CUSTOMER_SERVICE_SUBMIT_FEEDBACK_CATEGORY_ITERATION_BEGIN = nil --/esoui/Ingame/Help/HelpSubmitTicketData.lua:26:26 | iterationBegin = [[ CUSTOMER_SERVICE_SUBMIT_FEEDBACK_CATEGORY_ITERATION_BEGIN ]] + 1,
CUSTOMER_SERVICE_SUBMIT_FEEDBACK_CATEGORY_ITERATION_END = nil --/esoui/Ingame/Help/HelpSubmitTicketData.lua:27:24 | iterationEnd = [[ CUSTOMER_SERVICE_SUBMIT_FEEDBACK_CATEGORY_ITERATION_END ]],
CUSTOMER_SERVICE_SUBMIT_FEEDBACK_IMPACT_ITERATION_BEGIN = nil --/esoui/Ingame/Help/HelpSubmitTicketData.lua:18:26 | iterationBegin = [[ CUSTOMER_SERVICE_SUBMIT_FEEDBACK_IMPACT_ITERATION_BEGIN ]],
CUSTOMER_SERVICE_SUBMIT_FEEDBACK_IMPACT_ITERATION_END = nil --/esoui/Ingame/Help/HelpSubmitTicketData.lua:19:24 | iterationEnd = [[ CUSTOMER_SERVICE_SUBMIT_FEEDBACK_IMPACT_ITERATION_END ]],
DIGGING_ACTIVE_SKILL_ITERATION_BEGIN = nil --/esoui/InternalIngame/AntiquityDigging/AntiquityDigging.lua:289:17 | for skill = [[ DIGGING_ACTIVE_SKILL_ITERATION_BEGIN ]], DIGGING_ACTIVE_SKILL_ITERATION_END do
DIGGING_ACTIVE_SKILL_ITERATION_END = nil --/esoui/InternalIngame/AntiquityDigging/AntiquityDigging.lua:289:55 | for skill = DIGGING_ACTIVE_SKILL_ITERATION_BEGIN, [[ DIGGING_ACTIVE_SKILL_ITERATION_END ]] do
DYE_HUE_CATEGORY_ITERATION_BEGIN = nil --/esoui/Ingame/Dyeing/Dyeing_Shared.lua:668:23 | for hueCategory = [[ DYE_HUE_CATEGORY_ITERATION_BEGIN ]], DYE_HUE_CATEGORY_ITERATION_END do
DYE_HUE_CATEGORY_ITERATION_END = nil --/esoui/Ingame/Dyeing/Dyeing_Shared.lua:668:57 | for hueCategory = DYE_HUE_CATEGORY_ITERATION_BEGIN, [[ DYE_HUE_CATEGORY_ITERATION_END ]] do
DYE_RARITY_ITERATION_BEGIN = nil --/esoui/Ingame/Dyeing/Dyeing_Shared.lua:672:18 | for rarity = [[ DYE_RARITY_ITERATION_BEGIN ]], DYE_RARITY_ITERATION_END do
DYE_RARITY_ITERATION_END = nil --/esoui/Ingame/Dyeing/Dyeing_Shared.lua:672:46 | for rarity = DYE_RARITY_ITERATION_BEGIN, [[ DYE_RARITY_ITERATION_END ]] do
ENDLESS_DUNGEON_BUFF_BUCKET_TYPE_ITERATION_BEGIN = nil --/esoui/Ingame/EndlessDungeon/EndlessDungeonBuffSelector_Shared.lua:116:22 | for bucketType = [[ ENDLESS_DUNGEON_BUFF_BUCKET_TYPE_ITERATION_BEGIN ]], ENDLESS_DUNGEON_BUFF_BUCKET_TYPE_ITERATION_END do
ENDLESS_DUNGEON_BUFF_BUCKET_TYPE_ITERATION_END = nil --/esoui/Ingame/EndlessDungeon/EndlessDungeonBuffSelector_Shared.lua:116:72 | for bucketType = ENDLESS_DUNGEON_BUFF_BUCKET_TYPE_ITERATION_BEGIN, [[ ENDLESS_DUNGEON_BUFF_BUCKET_TYPE_ITERATION_END ]] do
ENDLESS_DUNGEON_BUFF_BUCKET_TYPE_MAX_VALUE = nil --/esoui/Ingame/EndlessDungeon/EndlessDungeonBuffSelector_Shared.lua:35:16 | for i = 1, [[ ENDLESS_DUNGEON_BUFF_BUCKET_TYPE_MAX_VALUE ]] + 1 do
ENDLESS_DUNGEON_COUNTER_TYPE_ITERATION_BEGIN = nil --/esoui/Ingame/EndlessDungeon/EndlessDungeonManager.lua:437:23 | for counterType = [[ ENDLESS_DUNGEON_COUNTER_TYPE_ITERATION_BEGIN ]], ENDLESS_DUNGEON_COUNTER_TYPE_ITERATION_END do
ENDLESS_DUNGEON_COUNTER_TYPE_ITERATION_END = nil --/esoui/Ingame/EndlessDungeon/EndlessDungeonManager.lua:437:69 | for counterType = ENDLESS_DUNGEON_COUNTER_TYPE_ITERATION_BEGIN, [[ ENDLESS_DUNGEON_COUNTER_TYPE_ITERATION_END ]] do
ENDLESS_DUNGEON_GROUP_TYPE_ITERATION_BEGIN = nil --/esoui/Ingame/Leaderboards/EndlessDungeonLeaderboards_Shared.lua:138:39 | for endlessDungeonGroupType = [[ ENDLESS_DUNGEON_GROUP_TYPE_ITERATION_BEGIN ]], ENDLESS_DUNGEON_GROUP_TYPE_ITERATION_END do
ENDLESS_DUNGEON_GROUP_TYPE_ITERATION_END = nil --/esoui/Ingame/Leaderboards/EndlessDungeonLeaderboards_Shared.lua:138:83 | for endlessDungeonGroupType = ENDLESS_DUNGEON_GROUP_TYPE_ITERATION_BEGIN, [[ ENDLESS_DUNGEON_GROUP_TYPE_ITERATION_END ]] do
EQUIP_SLOT_ITERATION_BEGIN = nil --/esoui/Ingame/Dyeing/Dyeing_Shared.lua:53:56 | IterateDyeableSlotData(RESTYLE_MODE_EQUIPMENT, [[ EQUIP_SLOT_ITERATION_BEGIN ]], EQUIP_SLOT_ITERATION_END)
EQUIP_SLOT_ITERATION_END = nil --/esoui/Ingame/Dyeing/Dyeing_Shared.lua:53:84 | IterateDyeableSlotData(RESTYLE_MODE_EQUIPMENT, EQUIP_SLOT_ITERATION_BEGIN, [[ EQUIP_SLOT_ITERATION_END ]])
FURNITURE_THEME_TYPE_ITERATION_BEGIN = nil --/esoui/Ingame/HousingEditor/Keyboard/FurnitureClasses_Keyboard.lua:706:26 | for furnitureTheme = [[ FURNITURE_THEME_TYPE_ITERATION_BEGIN ]], FURNITURE_THEME_TYPE_ITERATION_END do
FURNITURE_THEME_TYPE_ITERATION_END = nil --/esoui/Ingame/HousingEditor/Keyboard/FurnitureClasses_Keyboard.lua:706:64 | for furnitureTheme = FURNITURE_THEME_TYPE_ITERATION_BEGIN, [[ FURNITURE_THEME_TYPE_ITERATION_END ]] do
GAMEPLAY_ACTOR_CATEGORY_ITERATION_BEGIN = nil --/esoui/Ingame/Outfits/Outfit_Manager.lua:729:29 | for actorCategory = [[ GAMEPLAY_ACTOR_CATEGORY_ITERATION_BEGIN ]], GAMEPLAY_ACTOR_CATEGORY_ITERATION_END do
GAMEPLAY_ACTOR_CATEGORY_ITERATION_END = nil --/esoui/Ingame/Outfits/Outfit_Manager.lua:729:70 | for actorCategory = GAMEPLAY_ACTOR_CATEGORY_ITERATION_BEGIN, [[ GAMEPLAY_ACTOR_CATEGORY_ITERATION_END ]] do
GIFT_STATE_ITERATION_BEGIN = nil --/esoui/Ingame/GiftInventory/GiftInventory_Manager.lua:225:17 | for state = [[ GIFT_STATE_ITERATION_BEGIN ]], GIFT_STATE_ITERATION_END do
GIFT_STATE_ITERATION_END = nil --/esoui/Ingame/GiftInventory/GiftInventory_Manager.lua:225:45 | for state = GIFT_STATE_ITERATION_BEGIN, [[ GIFT_STATE_ITERATION_END ]] do
GROUP_FINDER_CATEGORY_ITERATION_BEGIN = nil --/esoui/Ingame/GroupFinder/GroupFinder_Shared.lua:208:17 | for index = [[ GROUP_FINDER_CATEGORY_ITERATION_BEGIN ]], GROUP_FINDER_CATEGORY_ITERATION_END do
GROUP_FINDER_CATEGORY_ITERATION_END = nil --/esoui/Ingame/GroupFinder/GroupFinder_Shared.lua:208:56 | for index = GROUP_FINDER_CATEGORY_ITERATION_BEGIN, [[ GROUP_FINDER_CATEGORY_ITERATION_END ]] do
GROUP_FINDER_PLAYSTYLE_ITERATION_BEGIN = nil --/esoui/Ingame/GroupFinder/GroupFinder_Shared.lua:382:28 | local startIndex = [[ GROUP_FINDER_PLAYSTYLE_ITERATION_BEGIN ]]
GROUP_FINDER_PLAYSTYLE_ITERATION_END = nil --/esoui/Ingame/GroupFinder/GroupFinder_Shared.lua:383:26 | local endIndex = [[ GROUP_FINDER_PLAYSTYLE_ITERATION_END ]]
GROUP_FINDER_SIZE_ITERATION_BEGIN = nil --/esoui/Ingame/GroupFinder/GroupFinder_Shared.lua:598:28 | local startIndex = [[ GROUP_FINDER_SIZE_ITERATION_BEGIN ]]
GROUP_FINDER_SIZE_MAX_VALUE = nil --/esoui/Ingame/GroupFinder/Gamepad/GroupFinder_AdditionalFilters_Gamepad.lua:374:32 | internalassert([[ GROUP_FINDER_SIZE_MAX_VALUE ]] <= math.pow(2, GROUP_FINDER_MAX_SEARCHABLE_SELECTIONS), "Number of possible options exceeds max, please set a max number of selectable items for this dropdown")
GUILD_ACTIVITY_ATTRIBUTE_VALUE_ITERATION_BEGIN = nil --/esoui/Ingame/GuildFinder/GuildBrowser_Manager.lua:196:170 | [GUILD_META_DATA_ATTRIBUTE_ACTIVITIES] = function(guildData) guildData.activitiesText = ZO_GuildFinder_Manager.GetAttributeCommaFormattedList(guildData.guildId, [[ GUILD_ACTIVITY_ATTRIBUTE_VALUE_ITERATION_BEGIN ]], GUILD_ACTIVITY_ATTRIBUTE_VALUE_ITERATION_END, DoesGuildHaveActivityAttribute, "SI_GUILDACTIVITYATTRIBUTEVALUE") end,
GUILD_ACTIVITY_ATTRIBUTE_VALUE_ITERATION_END = nil --/esoui/Ingame/GuildFinder/GuildBrowser_Manager.lua:196:218 | [GUILD_META_DATA_ATTRIBUTE_ACTIVITIES] = function(guildData) guildData.activitiesText = ZO_GuildFinder_Manager.GetAttributeCommaFormattedList(guildData.guildId, GUILD_ACTIVITY_ATTRIBUTE_VALUE_ITERATION_BEGIN, [[ GUILD_ACTIVITY_ATTRIBUTE_VALUE_ITERATION_END ]], DoesGuildHaveActivityAttribute, "SI_GUILDACTIVITYATTRIBUTEVALUE") end,
GUILD_FOCUS_ATTRIBUTE_VALUE_ITERATION_BEGIN = nil --/esoui/Ingame/GuildFinder/GuildRecruitment_GuildListing_Shared.lua:246:25 | iterBegin = [[ GUILD_FOCUS_ATTRIBUTE_VALUE_ITERATION_BEGIN ]],
GUILD_FOCUS_ATTRIBUTE_VALUE_ITERATION_END = nil --/esoui/Ingame/GuildFinder/GuildRecruitment_GuildListing_Shared.lua:231:23 | iterEnd = [[ GUILD_FOCUS_ATTRIBUTE_VALUE_ITERATION_END ]],
GUILD_HISTORY_EVENT_CATEGORY_ITERATION_BEGIN = nil --/esoui/Ingame/GuildHistory/GuildHistory_Data.lua:539:25 | for eventCategory = [[ GUILD_HISTORY_EVENT_CATEGORY_ITERATION_BEGIN ]], GUILD_HISTORY_EVENT_CATEGORY_ITERATION_END do
GUILD_HISTORY_EVENT_CATEGORY_ITERATION_END = nil --/esoui/Ingame/GuildHistory/GuildHistory_Data.lua:539:71 | for eventCategory = GUILD_HISTORY_EVENT_CATEGORY_ITERATION_BEGIN, [[ GUILD_HISTORY_EVENT_CATEGORY_ITERATION_END ]] do
GUILD_LANGUAGE_ATTRIBUTE_VALUE_ITERATION_BEGIN = nil --/esoui/Ingame/GuildFinder/GuildRecruitment_GuildListing_Shared.lua:274:25 | iterBegin = [[ GUILD_LANGUAGE_ATTRIBUTE_VALUE_ITERATION_BEGIN ]],
GUILD_LANGUAGE_ATTRIBUTE_VALUE_ITERATION_END = nil --/esoui/Ingame/GuildFinder/GuildRecruitment_GuildListing_Shared.lua:275:23 | iterEnd = [[ GUILD_LANGUAGE_ATTRIBUTE_VALUE_ITERATION_END ]],
GUILD_PERMISSION_ITERATION_BEGIN = nil --/esoui/Ingame/Guild/ZO_GuildRanks_Shared.lua:19:17 | for i = [[ GUILD_PERMISSION_ITERATION_BEGIN ]], GUILD_PERMISSION_ITERATION_END do
GUILD_PERMISSION_ITERATION_END = nil --/esoui/Ingame/Guild/ZO_GuildRanks_Shared.lua:19:51 | for i = GUILD_PERMISSION_ITERATION_BEGIN, [[ GUILD_PERMISSION_ITERATION_END ]] do
GUILD_PERMISSION_MAX_VALUE = nil --/esoui/Ingame/AddonCompatibilityAliases/PC/AddonCompatibilityAliases_PC.lua:302:12 | return [[ GUILD_PERMISSION_MAX_VALUE ]]
GUILD_PERSONALITY_ATTRIBUTE_VALUE_ITERATION_BEGIN = nil --/esoui/Ingame/GuildFinder/GuildRecruitment_GuildListing_Shared.lua:262:25 | iterBegin = [[ GUILD_PERSONALITY_ATTRIBUTE_VALUE_ITERATION_BEGIN ]],
GUILD_PERSONALITY_ATTRIBUTE_VALUE_ITERATION_END = nil --/esoui/Ingame/GuildFinder/GuildRecruitment_GuildListing_Shared.lua:263:23 | iterEnd = [[ GUILD_PERSONALITY_ATTRIBUTE_VALUE_ITERATION_END ]],
GUILD_RECRUITMENT_STATUS_ATTRIBUTE_VALUE_ITERATION_BEGIN = nil --/esoui/Ingame/GuildFinder/GuildRecruitment_GuildListing_Shared.lua:214:25 | iterBegin = [[ GUILD_RECRUITMENT_STATUS_ATTRIBUTE_VALUE_ITERATION_BEGIN ]],
GUILD_RECRUITMENT_STATUS_ATTRIBUTE_VALUE_ITERATION_END = nil --/esoui/Ingame/GuildFinder/GuildRecruitment_GuildListing_Shared.lua:215:23 | iterEnd = [[ GUILD_RECRUITMENT_STATUS_ATTRIBUTE_VALUE_ITERATION_END ]],
GUILD_SIZE_ATTRIBUTE_VALUE_ITERATION_BEGIN = nil --/esoui/Ingame/GuildFinder/Keyboard/GuildBrowser_GuildList_Keyboard.lua:483:13 | for i = [[ GUILD_SIZE_ATTRIBUTE_VALUE_ITERATION_BEGIN ]], GUILD_SIZE_ATTRIBUTE_VALUE_ITERATION_END do
GUILD_SIZE_ATTRIBUTE_VALUE_ITERATION_END = nil --/esoui/Ingame/GuildFinder/Keyboard/GuildBrowser_GuildList_Keyboard.lua:483:57 | for i = GUILD_SIZE_ATTRIBUTE_VALUE_ITERATION_BEGIN, [[ GUILD_SIZE_ATTRIBUTE_VALUE_ITERATION_END ]] do
HOUSE_CATEGORY_TYPE_ITERATION_BEGIN = nil --/esoui/Ingame/HouseTours/Keyboard/HouseTours_SearchResults_Keyboard.lua:673:13 | for i = [[ HOUSE_CATEGORY_TYPE_ITERATION_BEGIN ]], HOUSE_CATEGORY_TYPE_ITERATION_END do
HOUSE_CATEGORY_TYPE_ITERATION_END = nil --/esoui/Ingame/HouseTours/Keyboard/HouseTours_SearchResults_Keyboard.lua:673:50 | for i = HOUSE_CATEGORY_TYPE_ITERATION_BEGIN, [[ HOUSE_CATEGORY_TYPE_ITERATION_END ]] do
HOUSE_PERMISSION_DEFAULT_ACCESS_SETTING_ITERATION_BEGIN = nil --/esoui/Ingame/HouseTours/HouseToursData.lua:238:41 | for accessSetting = [[ HOUSE_PERMISSION_DEFAULT_ACCESS_SETTING_ITERATION_BEGIN ]], HOUSE_PERMISSION_DEFAULT_ACCESS_SETTING_ITERATION_END do
HOUSE_PERMISSION_DEFAULT_ACCESS_SETTING_ITERATION_END = nil --/esoui/Ingame/HouseTours/HouseToursData.lua:238:98 | for accessSetting = HOUSE_PERMISSION_DEFAULT_ACCESS_SETTING_ITERATION_BEGIN, [[ HOUSE_PERMISSION_DEFAULT_ACCESS_SETTING_ITERATION_END ]] do
HOUSE_PERMISSION_PRESET_SETTING_ITERATION_BEGIN = nil --/esoui/Ingame/HousingEditor/HouseSettings_Manager.lua:119:13 | for i = [[ HOUSE_PERMISSION_PRESET_SETTING_ITERATION_BEGIN ]], HOUSE_PERMISSION_PRESET_SETTING_ITERATION_END do
HOUSE_PERMISSION_PRESET_SETTING_ITERATION_END = nil --/esoui/Ingame/HousingEditor/HouseSettings_Manager.lua:119:62 | for i = HOUSE_PERMISSION_PRESET_SETTING_ITERATION_BEGIN, [[ HOUSE_PERMISSION_PRESET_SETTING_ITERATION_END ]] do
HOUSE_TOURS_LISTING_TAG_ITERATION_BEGIN = nil --/esoui/Ingame/HouseTours/Keyboard/HouseTours_SearchResults_Keyboard.lua:112:13 | for i = [[ HOUSE_TOURS_LISTING_TAG_ITERATION_BEGIN ]], HOUSE_TOURS_LISTING_TAG_ITERATION_END do
HOUSE_TOURS_LISTING_TAG_ITERATION_END = nil --/esoui/Ingame/HouseTours/Keyboard/HouseTours_SearchResults_Keyboard.lua:112:54 | for i = HOUSE_TOURS_LISTING_TAG_ITERATION_BEGIN, [[ HOUSE_TOURS_LISTING_TAG_ITERATION_END ]] do
HOUSING_FURNISHING_LIMIT_TYPE_ITERATION_BEGIN = nil --/esoui/Ingame/HousingEditor/FurnitureClasses_Shared.lua:24:21 | for limitType = [[ HOUSING_FURNISHING_LIMIT_TYPE_ITERATION_BEGIN ]], HOUSING_FURNISHING_LIMIT_TYPE_ITERATION_END do
HOUSING_FURNISHING_LIMIT_TYPE_ITERATION_END = nil --/esoui/Ingame/HousingEditor/FurnitureClasses_Shared.lua:24:68 | for limitType = HOUSING_FURNISHING_LIMIT_TYPE_ITERATION_BEGIN, [[ HOUSING_FURNISHING_LIMIT_TYPE_ITERATION_END ]] do
HOUSING_FURNITURE_BOUND_FILTER_ITERATION_BEGIN = nil --/esoui/Ingame/HousingEditor/Gamepad/FurnitureClasses_Gamepad.lua:280:27 | for filterValue = [[ HOUSING_FURNITURE_BOUND_FILTER_ITERATION_BEGIN ]], HOUSING_FURNITURE_BOUND_FILTER_ITERATION_END do
HOUSING_FURNITURE_BOUND_FILTER_ITERATION_END = nil --/esoui/Ingame/HousingEditor/Keyboard/FurnitureClasses_Keyboard.lua:674:63 | for filterValue = HOUSING_FURNITURE_BOUND_FILTER_ALL + 1, [[ HOUSING_FURNITURE_BOUND_FILTER_ITERATION_END ]] do
HOUSING_FURNITURE_LOCATION_FILTER_ITERATION_BEGIN = nil --/esoui/Ingame/HousingEditor/Gamepad/FurnitureClasses_Gamepad.lua:301:56 | for filterValue in ZO_FlagHelpers.FlagIterator([[ HOUSING_FURNITURE_LOCATION_FILTER_ITERATION_BEGIN ]] * 2, HOUSING_FURNITURE_LOCATION_FILTER_ITERATION_END) do
HOUSING_FURNITURE_LOCATION_FILTER_ITERATION_END = nil --/esoui/Ingame/HousingEditor/FurnitureClasses_Shared.lua:296:100 | for locationFlag in ZO_FlagHelpers.FlagIterator(HOUSING_FURNITURE_LOCATION_FILTER_ALL * 2, [[ HOUSING_FURNITURE_LOCATION_FILTER_ITERATION_END ]]) do
INTRO_GAMEPLAY_EXPERIENCE_JUMP_RESULT_ITERATION_BEGIN = nil --/esoui/Ingame/AddonCompatibilityAliases/AddonCompatibilityAliases_Shared.lua:79:57 | RETURNING_PLAYER_INSTANCE_JUMP_RESULT_ITERATION_BEGIN = [[ INTRO_GAMEPLAY_EXPERIENCE_JUMP_RESULT_ITERATION_BEGIN ]]
INTRO_GAMEPLAY_EXPERIENCE_JUMP_RESULT_ITERATION_END = nil --/esoui/Ingame/AddonCompatibilityAliases/AddonCompatibilityAliases_Shared.lua:80:55 | RETURNING_PLAYER_INSTANCE_JUMP_RESULT_ITERATION_END = [[ INTRO_GAMEPLAY_EXPERIENCE_JUMP_RESULT_ITERATION_END ]]
INTRO_GAMEPLAY_EXPERIENCE_JUMP_RESULT_MAX_VALUE = nil --/esoui/Ingame/AddonCompatibilityAliases/AddonCompatibilityAliases_Shared.lua:78:51 | RETURNING_PLAYER_INSTANCE_JUMP_RESULT_MAX_VALUE = [[ INTRO_GAMEPLAY_EXPERIENCE_JUMP_RESULT_MAX_VALUE ]]
INTRO_GAMEPLAY_EXPERIENCE_JUMP_RESULT_MIN_VALUE = nil --/esoui/Ingame/AddonCompatibilityAliases/AddonCompatibilityAliases_Shared.lua:77:51 | RETURNING_PLAYER_INSTANCE_JUMP_RESULT_MIN_VALUE = [[ INTRO_GAMEPLAY_EXPERIENCE_JUMP_RESULT_MIN_VALUE ]]
ITEM_FUNCTIONAL_QUALITY_ITERATION_BEGIN = nil --/esoui/Ingame/AddonCompatibilityAliases/PC/AddonCompatibilityAliases_PC.lua:912:32 | ITEM_QUALITY_ITERATION_BEGIN = [[ ITEM_FUNCTIONAL_QUALITY_ITERATION_BEGIN ]]
ITEM_FUNCTIONAL_QUALITY_ITERATION_END = nil --/esoui/Ingame/AddonCompatibilityAliases/PC/AddonCompatibilityAliases_PC.lua:913:30 | ITEM_QUALITY_ITERATION_END = [[ ITEM_FUNCTIONAL_QUALITY_ITERATION_END ]]
ITEM_FUNCTIONAL_QUALITY_MAX_VALUE = nil --/esoui/Ingame/AddonCompatibilityAliases/PC/AddonCompatibilityAliases_PC.lua:911:26 | ITEM_QUALITY_MAX_VALUE = [[ ITEM_FUNCTIONAL_QUALITY_MAX_VALUE ]]
ITEM_FUNCTIONAL_QUALITY_MIN_VALUE = nil --/esoui/Ingame/AddonCompatibilityAliases/PC/AddonCompatibilityAliases_PC.lua:910:26 | ITEM_QUALITY_MIN_VALUE = [[ ITEM_FUNCTIONAL_QUALITY_MIN_VALUE ]]
ITEM_LIST_SORT_TYPE_ITERATION_BEGIN = nil --/esoui/Ingame/Banking/Gamepad/BankingCommon_Gamepad.lua:116:66 | dialog.selectedSortType = dialog.selectedSortType or [[ ITEM_LIST_SORT_TYPE_ITERATION_BEGIN ]]
ITEM_LIST_SORT_TYPE_ITERATION_END = nil --/esoui/Ingame/Banking/Gamepad/BankingCommon_Gamepad.lua:145:70 | for i = ITEM_LIST_SORT_TYPE_ITERATION_BEGIN, [[ ITEM_LIST_SORT_TYPE_ITERATION_END ]] do
ITEM_TRAIT_TYPE_ITERATION_BEGIN = nil --/esoui/Ingame/Crafting/CraftingUtils.lua:603:21 | for traitType = [[ ITEM_TRAIT_TYPE_ITERATION_BEGIN ]], ITEM_TRAIT_TYPE_ITERATION_END do
ITEM_TRAIT_TYPE_ITERATION_END = nil --/esoui/Ingame/Crafting/CraftingUtils.lua:603:54 | for traitType = ITEM_TRAIT_TYPE_ITERATION_BEGIN, [[ ITEM_TRAIT_TYPE_ITERATION_END ]] do
LFG_ACTIVITY_ITERATION_BEGIN = nil --/esoui/Ingame/LFG/ZO_ActivityFinderRoot_Manager.lua:263:24 | for activityType = [[ LFG_ACTIVITY_ITERATION_BEGIN ]], LFG_ACTIVITY_ITERATION_END do
LFG_ACTIVITY_ITERATION_END = nil --/esoui/Ingame/LFG/ZO_ActivityFinderRoot_Manager.lua:263:54 | for activityType = LFG_ACTIVITY_ITERATION_BEGIN, [[ LFG_ACTIVITY_ITERATION_END ]] do
MAIL_CATEGORY_ITERATION_BEGIN = nil --/esoui/Ingame/Mail/Keyboard/MailInbox_Keyboard.lua:527:24 | for category = [[ MAIL_CATEGORY_ITERATION_BEGIN ]], MAIL_CATEGORY_ITERATION_END do
MAIL_CATEGORY_ITERATION_END = nil --/esoui/Ingame/Mail/Keyboard/MailInbox_Keyboard.lua:527:55 | for category = MAIL_CATEGORY_ITERATION_BEGIN, [[ MAIL_CATEGORY_ITERATION_END ]] do
MOD_BROWSER_CATEGORY_TYPE_ITERATION_BEGIN = nil --/esoui/PregameAndIngame/AddOns/Gamepad/ModBrowser_Gamepad.lua:848:13 | for i = [[ MOD_BROWSER_CATEGORY_TYPE_ITERATION_BEGIN ]], MOD_BROWSER_CATEGORY_TYPE_ITERATION_END do
MOD_BROWSER_CATEGORY_TYPE_ITERATION_END = nil --/esoui/PregameAndIngame/AddOns/Gamepad/ModBrowser_Gamepad.lua:848:56 | for i = MOD_BROWSER_CATEGORY_TYPE_ITERATION_BEGIN, [[ MOD_BROWSER_CATEGORY_TYPE_ITERATION_END ]] do
MOD_BROWSER_LISTING_REPORT_REASON_ITERATION_BEGIN = nil --/esoui/PregameAndIngame/AddOns/Gamepad/ModBrowser_Gamepad.lua:502:33 | for i = [[ MOD_BROWSER_LISTING_REPORT_REASON_ITERATION_BEGIN ]], MOD_BROWSER_LISTING_REPORT_REASON_ITERATION_END do
MOD_BROWSER_LISTING_REPORT_REASON_ITERATION_END = nil --/esoui/PregameAndIngame/AddOns/Gamepad/ModBrowser_Gamepad.lua:502:84 | for i = MOD_BROWSER_LISTING_REPORT_REASON_ITERATION_BEGIN, [[ MOD_BROWSER_LISTING_REPORT_REASON_ITERATION_END ]] do
MOD_BROWSER_LISTING_REPORT_SOURCE_ITERATION_BEGIN = nil --/esoui/PregameAndIngame/AddOns/Gamepad/ModBrowser_Gamepad.lua:454:33 | for i = [[ MOD_BROWSER_LISTING_REPORT_SOURCE_ITERATION_BEGIN ]], MOD_BROWSER_LISTING_REPORT_SOURCE_ITERATION_END do
MOD_BROWSER_LISTING_REPORT_SOURCE_ITERATION_END = nil --/esoui/PregameAndIngame/AddOns/Gamepad/ModBrowser_Gamepad.lua:454:84 | for i = MOD_BROWSER_LISTING_REPORT_SOURCE_ITERATION_BEGIN, [[ MOD_BROWSER_LISTING_REPORT_SOURCE_ITERATION_END ]] do
MORPH_SLOT_ITERATION_BEGIN = nil --/esoui/Ingame/Skills/PlayerSkillsData.lua:589:21 | for morphSlot = [[ MORPH_SLOT_ITERATION_BEGIN ]], MORPH_SLOT_ITERATION_END do
MORPH_SLOT_ITERATION_END = nil --/esoui/Ingame/Skills/PlayerSkillsData.lua:589:49 | for morphSlot = MORPH_SLOT_ITERATION_BEGIN, [[ MORPH_SLOT_ITERATION_END ]] do
NARRATION_TYPE_ITERATION_BEGIN = nil --/esoui/Libraries/ScreenNarration/ScreenNarrationManager.lua:422:29 | for narrationType = [[ NARRATION_TYPE_ITERATION_BEGIN ]], NARRATION_TYPE_ITERATION_END do
NARRATION_TYPE_ITERATION_END = nil --/esoui/Libraries/ScreenNarration/ScreenNarrationManager.lua:422:61 | for narrationType = NARRATION_TYPE_ITERATION_BEGIN, [[ NARRATION_TYPE_ITERATION_END ]] do
OFFICIAL_LANGUAGE_ITERATION_BEGIN = nil --/esoui/Ingame/ChatSystem/ChatData.lua:119:16 | for language = [[ OFFICIAL_LANGUAGE_ITERATION_BEGIN ]], OFFICIAL_LANGUAGE_ITERATION_END do
OFFICIAL_LANGUAGE_ITERATION_END = nil --/esoui/Ingame/ChatSystem/ChatData.lua:119:51 | for language = OFFICIAL_LANGUAGE_ITERATION_BEGIN, [[ OFFICIAL_LANGUAGE_ITERATION_END ]] do
OUTFIT_SLOT_ITERATION_BEGIN = nil --/esoui/Ingame/Outfits/Outfit_Manager.lua:359:27 | for outfitSlotIndex = [[ OUTFIT_SLOT_ITERATION_BEGIN ]], OUTFIT_SLOT_ITERATION_END do
OUTFIT_SLOT_ITERATION_END = nil --/esoui/Ingame/Outfits/Outfit_Manager.lua:359:56 | for outfitSlotIndex = OUTFIT_SLOT_ITERATION_BEGIN, [[ OUTFIT_SLOT_ITERATION_END ]] do
OVERLAND_DIFFICULTY_TYPE_ITERATION_BEGIN = nil --/esoui/Ingame/Stats/Gamepad/ZO_Stats_Gamepad.lua:2305:22 | for difficulty = [[ OVERLAND_DIFFICULTY_TYPE_ITERATION_BEGIN ]], OVERLAND_DIFFICULTY_TYPE_ITERATION_END do
OVERLAND_DIFFICULTY_TYPE_ITERATION_END = nil --/esoui/Ingame/Stats/Gamepad/ZO_Stats_Gamepad.lua:2305:64 | for difficulty = OVERLAND_DIFFICULTY_TYPE_ITERATION_BEGIN, [[ OVERLAND_DIFFICULTY_TYPE_ITERATION_END ]] do
PATH_FOLLOW_TYPE_ITERATION_BEGIN = nil --/esoui/Ingame/HousingEditor/Keyboard/HousingPathSettings_Keyboard.lua:268:13 | for i = [[ PATH_FOLLOW_TYPE_ITERATION_BEGIN ]], PATH_FOLLOW_TYPE_ITERATION_END do
PATH_FOLLOW_TYPE_ITERATION_END = nil --/esoui/Ingame/HousingEditor/Keyboard/HousingPathSettings_Keyboard.lua:268:47 | for i = PATH_FOLLOW_TYPE_ITERATION_BEGIN, [[ PATH_FOLLOW_TYPE_ITERATION_END ]] do
PLATFORM_SERVICE_TYPE_MAX_VALUE = nil --/esoui/Libraries/Utility/ZO_PlatformUtils.lua:59:50 | internalassert(PLATFORM_STORE_LABEL_MAX_VALUE == [[ PLATFORM_SERVICE_TYPE_MAX_VALUE ]], "There should be a platform store label for every platform service")
REWARD_TRACK_COMPONENT_ITERATION_BEGIN = nil --/esoui/Ingame/TamrielTomes/TamrielTomesScreen_Shared.lua:1845:31 | for rewardComponent = [[ REWARD_TRACK_COMPONENT_ITERATION_BEGIN ]], REWARD_TRACK_COMPONENT_ITERATION_END do
REWARD_TRACK_COMPONENT_ITERATION_END = nil --/esoui/Ingame/TamrielTomes/TamrielTomesScreen_Shared.lua:1845:71 | for rewardComponent = REWARD_TRACK_COMPONENT_ITERATION_BEGIN, [[ REWARD_TRACK_COMPONENT_ITERATION_END ]] do
RUMOR_TYPE_ITERATION_BEGIN = nil --/esoui/Ingame/ZO_Quest/Keyboard/QuestJournal_Rumors_Keyboard.lua:256:21 | for rumorType = [[ RUMOR_TYPE_ITERATION_BEGIN ]], RUMOR_TYPE_ITERATION_END do
RUMOR_TYPE_ITERATION_END = nil --/esoui/Ingame/ZO_Quest/Keyboard/QuestJournal_Rumors_Keyboard.lua:256:49 | for rumorType = RUMOR_TYPE_ITERATION_BEGIN, [[ RUMOR_TYPE_ITERATION_END ]] do
SCRIBING_SLOT_ITERATION_BEGIN = nil --/esoui/Ingame/Tooltip/ScribingTooltips.lua:69:16 | for slot = [[ SCRIBING_SLOT_ITERATION_BEGIN ]], SCRIBING_SLOT_ITERATION_END do
SCRIBING_SLOT_ITERATION_END = nil --/esoui/Ingame/Tooltip/ScribingTooltips.lua:69:47 | for slot = SCRIBING_SLOT_ITERATION_BEGIN, [[ SCRIBING_SLOT_ITERATION_END ]] do
SCRYING_ACTIVE_SKILL_ITERATION_BEGIN = nil --/esoui/InternalIngame/Scrying/Scrying.lua:1462:21 | for skill = [[ SCRYING_ACTIVE_SKILL_ITERATION_BEGIN ]], SCRYING_ACTIVE_SKILL_ITERATION_END do
SCRYING_ACTIVE_SKILL_ITERATION_END = nil --/esoui/InternalIngame/Scrying/Scrying.lua:1462:59 | for skill = SCRYING_ACTIVE_SKILL_ITERATION_BEGIN, [[ SCRYING_ACTIVE_SKILL_ITERATION_END ]] do
SETTING_PANEL_MAX_VALUE = nil --/esoui/PregameAndIngame/ZO_Options/Keyboard/ZO_Options_Keyboard.lua:10:42 | internalassert(self.currentPanelId > [[ SETTING_PANEL_MAX_VALUE ]])
SETTING_TYPE_MAX_VALUE = nil --/esoui/PregameAndIngame/ZO_Options/ZO_SharedOptions.lua:5:39 | internalassert(SETTING_TYPE_CUSTOM > ([[ SETTING_TYPE_MAX_VALUE ]] + 1))
SKILL_TYPE_ITERATION_BEGIN = nil --/esoui/Ingame/Skills/SkillsDataManager.lua:121:21 | for skillType = [[ SKILL_TYPE_ITERATION_BEGIN ]], SKILL_TYPE_ITERATION_END do
SKILL_TYPE_ITERATION_END = nil --/esoui/Ingame/Skills/SkillsDataManager.lua:121:49 | for skillType = SKILL_TYPE_ITERATION_BEGIN, [[ SKILL_TYPE_ITERATION_END ]] do
TAG_CATEGORY_MAX_VALUE = nil --/esoui/PublicAllIngames/Tooltip/CollectionsTooltips.lua:366:41 | for i = TAG_CATEGORY_MIN_VALUE, [[ TAG_CATEGORY_MAX_VALUE ]] do
TAG_CATEGORY_MIN_VALUE = nil --/esoui/PublicAllIngames/Tooltip/CollectionsTooltips.lua:366:17 | for i = [[ TAG_CATEGORY_MIN_VALUE ]], TAG_CATEGORY_MAX_VALUE do
TAMRIEL_TOME_PRODUCT_TYPE_ITERATION_BEGIN = nil --/esoui/Ingame/TamrielTomes/TamrielTomes_Manager.lua:406:23 | for productType = [[ TAMRIEL_TOME_PRODUCT_TYPE_ITERATION_BEGIN ]], TAMRIEL_TOME_PRODUCT_TYPE_ITERATION_END do
TAMRIEL_TOME_PRODUCT_TYPE_ITERATION_END = nil --/esoui/Ingame/TamrielTomes/TamrielTomes_Manager.lua:406:66 | for productType = TAMRIEL_TOME_PRODUCT_TYPE_ITERATION_BEGIN, [[ TAMRIEL_TOME_PRODUCT_TYPE_ITERATION_END ]] do
TIMED_ACTIVITY_TYPE_MAX_VALUE = nil --/esoui/Ingame/TimedActivities/TimedActivities_Manager.lua:344:55 | for activityType = TIMED_ACTIVITY_TYPE_MIN_VALUE, [[ TIMED_ACTIVITY_TYPE_MAX_VALUE ]] do
TIMED_ACTIVITY_TYPE_MIN_VALUE = nil --/esoui/Ingame/TimedActivities/TimedActivities_Manager.lua:344:24 | for activityType = [[ TIMED_ACTIVITY_TYPE_MIN_VALUE ]], TIMED_ACTIVITY_TYPE_MAX_VALUE do
TRIBUTE_LEADERBOARD_TIER_ITERATION_BEGIN = nil --/esoui/PublicAllIngames/Tribute/TributeRewardsDataManager.lua:45:33 | for tierIndex = [[ TRIBUTE_LEADERBOARD_TIER_ITERATION_BEGIN ]], TRIBUTE_LEADERBOARD_TIER_ITERATION_END do
TRIBUTE_LEADERBOARD_TIER_ITERATION_END = nil --/esoui/PublicAllIngames/Tribute/TributeRewardsDataManager.lua:45:75 | for tierIndex = TRIBUTE_LEADERBOARD_TIER_ITERATION_BEGIN, [[ TRIBUTE_LEADERBOARD_TIER_ITERATION_END ]] do
TRIBUTE_MECHANIC_ACTIVATION_SOURCE_ITERATION_BEGIN = nil --/esoui/PublicAllIngames/Tribute/TributeData.lua:556:28 | for activationSource = [[ TRIBUTE_MECHANIC_ACTIVATION_SOURCE_ITERATION_BEGIN ]], TRIBUTE_MECHANIC_ACTIVATION_SOURCE_ITERATION_END do
TRIBUTE_PATRON_DRAFT_ID_ITERATION_BEGIN = nil --/esoui/InternalIngame/Tribute/Tribute.lua:216:19 | for draftId = [[ TRIBUTE_PATRON_DRAFT_ID_ITERATION_BEGIN ]], TRIBUTE_PATRON_DRAFT_ID_ITERATION_END do
TRIBUTE_PATRON_DRAFT_ID_ITERATION_END = nil --/esoui/InternalIngame/Tribute/Tribute.lua:216:60 | for draftId = TRIBUTE_PATRON_DRAFT_ID_ITERATION_BEGIN, [[ TRIBUTE_PATRON_DRAFT_ID_ITERATION_END ]] do
TRIBUTE_PATRON_DRAFT_ID_MAX_VALUE = nil --/esoui/Ingame/CenterScreenAnnounce/CenterScreenAnnounceHandlers.lua:1346:35 | if opponentFavorCount == ([[ TRIBUTE_PATRON_DRAFT_ID_MAX_VALUE ]] - 1) then
TRIBUTE_PLAYER_PERSPECTIVE_ITERATION_BEGIN = nil --/esoui/Ingame/Tribute/Tribute.lua:110:23 | for perspective = [[ TRIBUTE_PLAYER_PERSPECTIVE_ITERATION_BEGIN ]], TRIBUTE_PLAYER_PERSPECTIVE_ITERATION_END do
TRIBUTE_PLAYER_PERSPECTIVE_ITERATION_END = nil --/esoui/Ingame/Tribute/Tribute.lua:110:67 | for perspective = TRIBUTE_PLAYER_PERSPECTIVE_ITERATION_BEGIN, [[ TRIBUTE_PLAYER_PERSPECTIVE_ITERATION_END ]] do
TRIBUTE_RESOURCE_ITERATION_BEGIN = nil --/esoui/InternalIngame/Tribute/Tribute.lua:155:24 | for resource = [[ TRIBUTE_RESOURCE_ITERATION_BEGIN ]], TRIBUTE_RESOURCE_ITERATION_END do
TRIBUTE_RESOURCE_ITERATION_END = nil --/esoui/InternalIngame/Tribute/Tribute.lua:155:58 | for resource = TRIBUTE_RESOURCE_ITERATION_BEGIN, [[ TRIBUTE_RESOURCE_ITERATION_END ]] do
TRIBUTE_TIER_ITERATION_BEGIN = nil --/esoui/PublicAllIngames/Tribute/TributeRewardsDataManager.lua:41:33 | for tierIndex = [[ TRIBUTE_TIER_ITERATION_BEGIN ]], TRIBUTE_TIER_ITERATION_END do
TRIBUTE_TIER_ITERATION_END = nil --/esoui/PublicAllIngames/Tribute/TributeRewardsDataManager.lua:41:63 | for tierIndex = TRIBUTE_TIER_ITERATION_BEGIN, [[ TRIBUTE_TIER_ITERATION_END ]] do
VISUAL_ARMORTYPE_ITERATION_BEGIN = nil --/esoui/Ingame/Outfits/Keyboard/OutfitStylesPanel_Keyboard.lua:267:35 | for visualArmorType = [[ VISUAL_ARMORTYPE_ITERATION_BEGIN ]], VISUAL_ARMORTYPE_ITERATION_END do
VISUAL_ARMORTYPE_ITERATION_END = nil --/esoui/Ingame/Outfits/Keyboard/OutfitStylesPanel_Keyboard.lua:267:69 | for visualArmorType = VISUAL_ARMORTYPE_ITERATION_BEGIN, [[ VISUAL_ARMORTYPE_ITERATION_END ]] do
VISUAL_ARMORTYPE_MAX_VALUE = nil --/esoui/Ingame/Collections/CollectibleDataManager.lua:20:43 | assert(BLOCKED_ARMOR_OR_WEAPON_CATEGORY > [[ VISUAL_ARMORTYPE_MAX_VALUE ]] and BLOCKED_ARMOR_OR_WEAPON_CATEGORY > WEAPON_MODEL_TYPE_MAX_VALUE)
WEAPON_MODEL_TYPE_ITERATION_BEGIN = nil --/esoui/Ingame/Outfits/Keyboard/OutfitStylesPanel_Keyboard.lua:279:35 | for weaponModelType = [[ WEAPON_MODEL_TYPE_ITERATION_BEGIN ]], WEAPON_MODEL_TYPE_ITERATION_END do
WEAPON_MODEL_TYPE_ITERATION_END = nil --/esoui/Ingame/Outfits/Keyboard/OutfitStylesPanel_Keyboard.lua:279:70 | for weaponModelType = WEAPON_MODEL_TYPE_ITERATION_BEGIN, [[ WEAPON_MODEL_TYPE_ITERATION_END ]] do
WEAPON_MODEL_TYPE_MAX_VALUE = nil --/esoui/Ingame/Collections/CollectibleDataManager.lua:20:109 | assert(BLOCKED_ARMOR_OR_WEAPON_CATEGORY > VISUAL_ARMORTYPE_MAX_VALUE and BLOCKED_ARMOR_OR_WEAPON_CATEGORY > [[ WEAPON_MODEL_TYPE_MAX_VALUE ]])

-- 2. Global Constants (General All-Caps & Flags) --
ACCOUNT_CREATE_LINK_ERROR_ACCOUNT_BANNED = nil --/esoui/Pregame/Gamepad/LinkAccountScreen/LinkAccountScreen_Gamepad.lua:231:30 | linkErrorCode ~= [[ ACCOUNT_CREATE_LINK_ERROR_ACCOUNT_BANNED ]])
ACCOUNT_CREATE_LINK_ERROR_ACCOUNT_DELETED = nil --/esoui/Pregame/Gamepad/LinkAccountScreen/LinkAccountScreen_Gamepad.lua:230:30 | linkErrorCode ~= [[ ACCOUNT_CREATE_LINK_ERROR_ACCOUNT_DELETED ]]         and
ACCOUNT_CREATE_LINK_ERROR_ACCOUNT_NOT_FOUND = nil --/esoui/Pregame/Gamepad/LinkAccountScreen/LinkAccountScreen_Gamepad.lua:226:30 | return (linkErrorCode ~= [[ ACCOUNT_CREATE_LINK_ERROR_ACCOUNT_NOT_FOUND ]]       and
ACCOUNT_CREATE_LINK_ERROR_ACCOUNT_NOT_VERIFIED = nil --/esoui/Pregame/AccountLogin/Gamepad/CreateLinkLoadingScreen_Gamepad.lua:231:139 | if loginError == LOGIN_AUTH_ERROR_ACCOUNT_NOT_VERIFIED or loginError == LOGIN_AUTH_ERROR_GAME_ACCOUNT_NOT_VERIFIED or linkingError == [[ ACCOUNT_CREATE_LINK_ERROR_ACCOUNT_NOT_VERIFIED ]] then
ACCOUNT_CREATE_LINK_ERROR_EXTERNAL_REFERENCE_ALREADY_USED = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_LoginManager.lua:183:28 | if linkingError == [[ ACCOUNT_CREATE_LINK_ERROR_EXTERNAL_REFERENCE_ALREADY_USED ]] or linkingError == ACCOUNT_CREATE_LINK_ERROR_USER_ALREADY_LINKED then
ACCOUNT_CREATE_LINK_ERROR_INVALID_CREDENTIALS = nil --/esoui/Pregame/Gamepad/LinkAccountScreen/LinkAccountScreen_Gamepad.lua:229:30 | linkErrorCode ~= [[ ACCOUNT_CREATE_LINK_ERROR_INVALID_CREDENTIALS ]]     and
ACCOUNT_CREATE_LINK_ERROR_NO_ERROR = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_LoginManager.lua:179:28 | elseif linkingError ~= [[ ACCOUNT_CREATE_LINK_ERROR_NO_ERROR ]] then
ACCOUNT_CREATE_LINK_ERROR_USER_ALREADY_LINKED = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_LoginManager.lua:183:105 | if linkingError == ACCOUNT_CREATE_LINK_ERROR_EXTERNAL_REFERENCE_ALREADY_USED or linkingError == [[ ACCOUNT_CREATE_LINK_ERROR_USER_ALREADY_LINKED ]] then
ACTIVATE_LIST_ON_SHOW = nil --/esoui/Ingame/Vengeance/Gamepad/Vengeance_Loadouts_Gamepad.lua:9:102 | ZO_Gamepad_ParametricList_Screen.Initialize(self, control, ZO_GAMEPAD_HEADER_TABBAR_DONT_CREATE, [[ ACTIVATE_LIST_ON_SHOW ]], GAMEPAD_VENGEANCE_LOADOUTS_SCENE)
ADDITIONAL_OVERBINDS = nil --/esoui/Ingame/Retrait/Gamepad/ZO_RetraitStation_Retrait_Gamepad.lua:76:83 | self.itemActions = ZO_ItemSlotActionsController:New(KEYBIND_STRIP_ALIGN_LEFT, [[ ADDITIONAL_OVERBINDS ]], DONT_USE_KEYBIND_STRIP)
ALERT = nil --/esoui/Ingame/Globals/InGameDialogs.lua:1423:38 | ZO_Alert([[ ALERT ]], nil, zo_strformat(GetString("SI_GROUPINVITERESPONSE", GROUP_INVITE_RESPONSE_INVITED), ZO_FormatUserFacingDisplayName(characterOrDisplayName)))
ALLIANCE_ICON_SIZE = nil --/esoui/Ingame/Guild/Keyboard/GuildRoster_Keyboard.lua:259:113 | local allianceIcon = zo_iconFormat(ZO_GetAllianceSymbolIcon(guildAlliance), [[ ALLIANCE_ICON_SIZE ]], ALLIANCE_ICON_SIZE)
APPEARANCE_NAME_ACCESSORY = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:100:55 | { GAMEPAD_BUCKET_CONTROL_TYPE_APPEARANCE, [[ APPEARANCE_NAME_ACCESSORY ]] },  -- "adornment"
APPEARANCE_NAME_AGE = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:99:55 | { GAMEPAD_BUCKET_CONTROL_TYPE_APPEARANCE, [[ APPEARANCE_NAME_AGE ]] },
APPEARANCE_NAME_BODY_MARKING = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:65:55 | { GAMEPAD_BUCKET_CONTROL_TYPE_APPEARANCE, [[ APPEARANCE_NAME_BODY_MARKING ]] },
APPEARANCE_NAME_EYEBROW = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:133:55 | { GAMEPAD_BUCKET_CONTROL_TYPE_APPEARANCE, [[ APPEARANCE_NAME_EYEBROW ]] },
APPEARANCE_NAME_EYE_TINT = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:127:55 | { GAMEPAD_BUCKET_CONTROL_TYPE_APPEARANCE, [[ APPEARANCE_NAME_EYE_TINT ]] },
APPEARANCE_NAME_HAIR_STYLE = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:101:55 | { GAMEPAD_BUCKET_CONTROL_TYPE_APPEARANCE, [[ APPEARANCE_NAME_HAIR_STYLE ]] },
APPEARANCE_NAME_HAIR_TINT = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:102:55 | { GAMEPAD_BUCKET_CONTROL_TYPE_APPEARANCE, [[ APPEARANCE_NAME_HAIR_TINT ]] },
APPEARANCE_NAME_HEAD_MARKING = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:103:55 | { GAMEPAD_BUCKET_CONTROL_TYPE_APPEARANCE, [[ APPEARANCE_NAME_HEAD_MARKING ]] },
APPEARANCE_NAME_SKIN_TINT = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:64:55 | { GAMEPAD_BUCKET_CONTROL_TYPE_APPEARANCE, [[ APPEARANCE_NAME_SKIN_TINT ]] },
APPEARANCE_NAME_VOICE = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:126:55 | { GAMEPAD_BUCKET_CONTROL_TYPE_APPEARANCE, [[ APPEARANCE_NAME_VOICE ]] },
ATTRIBUTE_POINT_ALLOCATION_MODE_PURCHASE_FULL = nil --/esoui/Ingame/Stats/Keyboard/ZO_Stats_Keyboard.lua:415:58 | self:SetAttributePointAllocationMode([[ ATTRIBUTE_POINT_ALLOCATION_MODE_PURCHASE_FULL ]])
AUTHENTICATION_ERROR_ACCOUNT_BANNED = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_LoginManager.lua:278:25 | elseif errorCode == [[ AUTHENTICATION_ERROR_ACCOUNT_BANNED ]] then
AUTHENTICATION_ERROR_ACCOUNT_IS_CHILD = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_LoginManager.lua:282:25 | elseif errorCode == [[ AUTHENTICATION_ERROR_ACCOUNT_IS_CHILD ]] then
AUTHENTICATION_ERROR_ACCOUNT_SUSPENDED = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_LoginManager.lua:280:25 | elseif errorCode == [[ AUTHENTICATION_ERROR_ACCOUNT_SUSPENDED ]] then
AUTHENTICATION_ERROR_PAYMENT_EXPIRED = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_LoginManager.lua:276:21 | if errorCode == [[ AUTHENTICATION_ERROR_PAYMENT_EXPIRED ]] then
AUTO_COMPLETION_ONLINE = nil --/esoui/Ingame/Globals/InGameDialogs.lua:1373:26 | onlineOnly = [[ AUTO_COMPLETION_ONLINE ]],
BLOCK_TABBAR_CALLBACK = nil --/esoui/Ingame/Companion/Gamepad/CompanionEquipment_Gamepad.lua:87:32 | self:RefreshHeader([[ BLOCK_TABBAR_CALLBACK ]])
BRACKET_COMMANDS = nil --/esoui/Ingame/SlashCommands/SlashCommandAutoComplete.lua:83:8 | if [[ BRACKET_COMMANDS ]] then
CAST_BAR_BEGIN_MAGIC = nil --/esoui/Libraries/Globals/DefaultColorDefs.lua:23:112 | [ZO_CAST_STATE_BEGIN_MAGIC]     = { ZO_ColorDef:New(GetInterfaceColor(INTERFACE_COLOR_TYPE_CAST_BAR_START, [[ CAST_BAR_BEGIN_MAGIC ]])), ZO_ColorDef:New(GetInterfaceColor(INTERFACE_COLOR_TYPE_CAST_BAR_END, CAST_BAR_END_MAGIC)), },
CAST_BAR_BEGIN_MELEE = nil --/esoui/Libraries/Globals/DefaultColorDefs.lua:24:112 | [ZO_CAST_STATE_BEGIN_MELEE]     = { ZO_ColorDef:New(GetInterfaceColor(INTERFACE_COLOR_TYPE_CAST_BAR_START, [[ CAST_BAR_BEGIN_MELEE ]])), ZO_ColorDef:New(GetInterfaceColor(INTERFACE_COLOR_TYPE_CAST_BAR_END, CAST_BAR_END_MELEE)), },
CAST_BAR_DEFAULT = nil --/esoui/Libraries/Globals/DefaultColorDefs.lua:19:112 | [ZO_CAST_STATE_BEGIN]           = { ZO_ColorDef:New(GetInterfaceColor(INTERFACE_COLOR_TYPE_CAST_BAR_START, [[ CAST_BAR_DEFAULT ]])), ZO_ColorDef:New(GetInterfaceColor(INTERFACE_COLOR_TYPE_CAST_BAR_END, CAST_BAR_DEFAULT)), },
CAST_BAR_END_MAGIC = nil --/esoui/Libraries/Globals/DefaultColorDefs.lua:23:205 | [ZO_CAST_STATE_BEGIN_MAGIC]     = { ZO_ColorDef:New(GetInterfaceColor(INTERFACE_COLOR_TYPE_CAST_BAR_START, CAST_BAR_BEGIN_MAGIC)), ZO_ColorDef:New(GetInterfaceColor(INTERFACE_COLOR_TYPE_CAST_BAR_END, [[ CAST_BAR_END_MAGIC ]])), },
CAST_BAR_END_MELEE = nil --/esoui/Libraries/Globals/DefaultColorDefs.lua:24:205 | [ZO_CAST_STATE_BEGIN_MELEE]     = { ZO_ColorDef:New(GetInterfaceColor(INTERFACE_COLOR_TYPE_CAST_BAR_START, CAST_BAR_BEGIN_MELEE)), ZO_ColorDef:New(GetInterfaceColor(INTERFACE_COLOR_TYPE_CAST_BAR_END, [[ CAST_BAR_END_MELEE ]])), },
CHAMPION_POINT_UPDATE = nil --/esoui/Ingame/AddonCompatibilityAliases/PC/AddonCompatibilityAliases_PC.lua:116:25 | VETERAN_POINTS_UPDATE = [[ CHAMPION_POINT_UPDATE ]]
CHARACTER_CREATE_EDIT_ERROR_DUPLICATE_NAME = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreate_Keyboard.lua:129:10 | [[[ CHARACTER_CREATE_EDIT_ERROR_DUPLICATE_NAME ]]] = true,
CHARACTER_CREATE_EDIT_ERROR_INVALID_NAME = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreate_Keyboard.lua:128:10 | [[[ CHARACTER_CREATE_EDIT_ERROR_INVALID_NAME ]]] = true,
CHARACTER_CREATE_EDIT_ERROR_NAME_TOO_LONG = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreate_Keyboard.lua:131:10 | [[[ CHARACTER_CREATE_EDIT_ERROR_NAME_TOO_LONG ]]] = true,
CHARACTER_CREATE_EDIT_ERROR_NAME_TOO_SHORT = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreate_Keyboard.lua:130:10 | [[[ CHARACTER_CREATE_EDIT_ERROR_NAME_TOO_SHORT ]]] = true,
CHARACTER_WINDOW_TOOLTIP_ANCHOR_SIDE = nil --/esoui/Ingame/Vengeance/Keyboard/Vengeance_Loadouts_Keyboard.lua:174:47 | statEntry.tooltipAnchorSide = [[ CHARACTER_WINDOW_TOOLTIP_ANCHOR_SIDE ]]
CHARNAME_MAX_LENGTH = nil --/esoui/Libraries/Globals/Globals.lua:61:51 | editControl:SetMaxInputChars(maxNameLength or [[ CHARNAME_MAX_LENGTH ]])
COLLECTIBLE_NAME_MAX_LENGTH = nil --/esoui/Ingame/Collections/Keyboard/CollectionsBook.lua:716:42 | editControl:SetMaxInputChars([[ COLLECTIBLE_NAME_MAX_LENGTH ]])
COMBAT_MECHANIC_FLAGS_INVALID = nil --/esoui/Ingame/UnitFrames/UnitFrames.lua:1543:38 | currentBar:Hide(powerType == [[ COMBAT_MECHANIC_FLAGS_INVALID ]])
COMBAT_MECHANIC_FLAGS_MAX_INDEX = nil --/esoui/Ingame/UnitFrames/UnitFrames.lua:1409:24 | for i = 1, [[ COMBAT_MECHANIC_FLAGS_MAX_INDEX ]] do
CURRENCY_OPTIONS = nil --/esoui/Ingame/Skills/Keyboard/ZO_Skills.lua:335:83 | ZO_CurrencyControl_SetSimpleCurrency(balanceControl, CURT_MONEY, balance, [[ CURRENCY_OPTIONS ]])
DEFAULT_MOVEMENT_CONTROLLER = nil --/esoui/Ingame/AdventureZone/Gamepad/AdventureZoneBossTree_Gamepad.lua:20:62 | self.easyFocus = ZO_GamepadFocus:New(self.easyContainer, [[ DEFAULT_MOVEMENT_CONTROLLER ]], MOVEMENT_CONTROLLER_DIRECTION_HORIZONTAL)
DESCRIPTIVE_MINIMAL_HIDE_ZEROES = nil --/esoui/InternalIngame/Tribute/TributeSummary.lua:1426:80 | self.statisticsDuration:SetText(ZO_FormatTimeMilliseconds(matchDurationMS, [[ DESCRIPTIVE_MINIMAL_HIDE_ZEROES ]]))
DONT_ACTIVATE_ON_SHOW = nil --/esoui/Ingame/Crafting/Gamepad/Scribing_Gamepad.lua:7:83 | ZO_ScribingLayout_Gamepad.Initialize(self, control, ZO_DO_NOT_CREATE_TAB_BAR, [[ DONT_ACTIVATE_ON_SHOW ]], self.interactScene)
DONT_USE_KEYBIND_STRIP = nil --/esoui/Ingame/Retrait/Gamepad/ZO_RetraitStation_Retrait_Gamepad.lua:76:105 | self.itemActions = ZO_ItemSlotActionsController:New(KEYBIND_STRIP_ALIGN_LEFT, ADDITIONAL_OVERBINDS, [[ DONT_USE_KEYBIND_STRIP ]])
DRESSING_OPTION_NUDE = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreate_Gamepad.lua:20:45 | local PREVIEW_NO_GEAR = CreatePreviewOption([[ DRESSING_OPTION_NUDE ]])
DRESSING_OPTION_STARTING_GEAR = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreate_Gamepad.lua:21:49 | local PREVIEW_NOVICE_GEAR = CreatePreviewOption([[ DRESSING_OPTION_STARTING_GEAR ]])
DRESSING_OPTION_WARDROBE_1 = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreate_Gamepad.lua:22:51 | local PREVIEW_CHAMPION_GEAR = CreatePreviewOption([[ DRESSING_OPTION_WARDROBE_1 ]])
DRESSING_OPTION_YOUR_GEAR = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreateSlider_Keyboard.lua:19:171 | local previewTypeToShow = ZO_SELECTED_TEXT:Colorize(zo_strformat(SI_CREATE_CHARACTER_GAMEPAD_PREVIEW_OPTION_FORMAT, GetString("SI_CHARACTERCREATEDRESSINGOPTION", [[ DRESSING_OPTION_YOUR_GEAR ]])))
DRESSING_OPTION_YOUR_GEAR_AND_COLLECTIBLES = nil --/esoui/Pregame/CharacterCreate/ZO_CharacterCreate_Shared.lua:210:20 | SelectClothing([[ DRESSING_OPTION_YOUR_GEAR_AND_COLLECTIBLES ]])
FLOW_UNLOCKED = nil --/esoui/InternalIngame/Market/Gamepad/MarketDialogs_Gamepad.lua:1785:20 | if position == [[ FLOW_UNLOCKED ]] then
FULL_WIDTH = nil --/esoui/Ingame/LFG/VeterancyRank.lua:24:99 | , "ZoFontGameMedium", r, g, b, TOPLEFT, MODIFY_TEXT_TYPE_NONE, TEXT_ALIGN_CENTER, [[ FULL_WIDTH ]])
GAMEPAD_LEFT_TOOLTIP_BACKGROUND_FRAGMENT = nil --/esoui/Ingame/Skills/Gamepad/GamepadSkills.lua:2312:31 | SCENE_MANAGER:AddFragment([[ GAMEPAD_LEFT_TOOLTIP_BACKGROUND_FRAGMENT ]])
GAMEPAD_SECTION_HEADER_ID = nil --/esoui/Pregame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:46:22 | header = [[ GAMEPAD_SECTION_HEADER_ID ]],
GIFT_NOTE_MAX_LENGTH = nil --/esoui/Ingame/GiftInventory/Gamepad/GiftInventoryDialogs_Gamepad.lua:14:49 | control.editBoxControl:SetMaxInputChars([[ GIFT_NOTE_MAX_LENGTH ]])
GLOBAL_ERROR_CODE_DBW_TRANSFER_FAILED_0 = nil --/esoui/Pregame/StateManager/Keyboard/PregameStates_Keyboard.lua:207:6 | [[[ GLOBAL_ERROR_CODE_DBW_TRANSFER_FAILED_0 ]]] = "CharacterSelect_FromIngame",
GLOBAL_ERROR_CODE_DBW_TRANSFER_FAILED_1 = nil --/esoui/Pregame/StateManager/Keyboard/PregameStates_Keyboard.lua:208:6 | [[[ GLOBAL_ERROR_CODE_DBW_TRANSFER_FAILED_1 ]]] = "CharacterSelect_FromIngame",
GLOBAL_ERROR_CODE_DBW_TRANSFER_FAILED_2 = nil --/esoui/Pregame/StateManager/Keyboard/PregameStates_Keyboard.lua:209:6 | [[[ GLOBAL_ERROR_CODE_DBW_TRANSFER_FAILED_2 ]]] = "CharacterSelect_FromIngame",
GLOBAL_ERROR_CODE_DBW_TRANSFER_FAILED_3 = nil --/esoui/Pregame/StateManager/Keyboard/PregameStates_Keyboard.lua:210:6 | [[[ GLOBAL_ERROR_CODE_DBW_TRANSFER_FAILED_3 ]]] = "CharacterSelect_FromIngame",
GLOBAL_ERROR_CODE_DBW_TRANSFER_FAILED_4 = nil --/esoui/Pregame/StateManager/Keyboard/PregameStates_Keyboard.lua:211:6 | [[[ GLOBAL_ERROR_CODE_DBW_TRANSFER_FAILED_4 ]]] = "CharacterSelect_FromIngame",
GLOBAL_ERROR_CODE_DBW_TRANSFER_FAILED_5 = nil --/esoui/Pregame/StateManager/Keyboard/PregameStates_Keyboard.lua:212:6 | [[[ GLOBAL_ERROR_CODE_DBW_TRANSFER_FAILED_5 ]]] = "CharacterSelect_FromIngame",
GLOBAL_ERROR_CODE_LOBBY_CHARACTER_LOCKED = nil --/esoui/Pregame/StateManager/Keyboard/PregameStates_Keyboard.lua:204:6 | [[[ GLOBAL_ERROR_CODE_LOBBY_CHARACTER_LOCKED ]]] = "CharacterSelect_FromIngame",
GLOBAL_ERROR_CODE_LOBBY_CHARACTER_RENAME_NEEDED = nil --/esoui/Pregame/StateManager/Keyboard/PregameStates_Keyboard.lua:205:6 | [[[ GLOBAL_ERROR_CODE_LOBBY_CHARACTER_RENAME_NEEDED ]]] = "CharacterSelect_FromIngame",
GLOBAL_ERROR_CODE_LOBBY_CHAR_STILL_IN_GAME = nil --/esoui/Pregame/StateManager/Keyboard/PregameStates_Keyboard.lua:213:6 | [[[ GLOBAL_ERROR_CODE_LOBBY_CHAR_STILL_IN_GAME ]]] = "CharacterSelect_FromIngame",
GLOBAL_ERROR_CODE_LOBBY_TRANSFER_FAILED = nil --/esoui/Pregame/StateManager/Keyboard/PregameStates_Keyboard.lua:206:6 | [[[ GLOBAL_ERROR_CODE_LOBBY_TRANSFER_FAILED ]]] = "CharacterSelect_FromIngame",
GLOBAL_ERROR_CODE_LOBBY_WORLD_PERMISSIONS = nil --/esoui/Pregame/StateManager/Keyboard/PregameStates_Keyboard.lua:203:6 | [[[ GLOBAL_ERROR_CODE_LOBBY_WORLD_PERMISSIONS ]]] = "CharacterSelect_FromIngame",
GLOBAL_ERROR_CODE_NO_ERROR = nil --/esoui/Pregame/StateManager/PregameStateManager.lua:853:31 | elseif globalErrorCode ~= [[ GLOBAL_ERROR_CODE_NO_ERROR ]] then
GROUP_FINDER_GROUP_LISTING_APPLICATION_MESSAGE_MAX_LENGTH = nil --/esoui/Ingame/GroupFinder/Gamepad/GroupFinder_SearchResults_Gamepad.lua:404:65 | control.editBoxControl:SetMaxInputChars([[ GROUP_FINDER_GROUP_LISTING_APPLICATION_MESSAGE_MAX_LENGTH ]])
GROUP_FINDER_GROUP_LISTING_DESCRIPTION_MAX_LENGTH = nil --/esoui/Ingame/GroupFinder/Gamepad/GroupFinder_CreateEditGroupListing_Gamepad.lua:372:61 | control.editBoxControl:SetMaxInputChars([[ GROUP_FINDER_GROUP_LISTING_DESCRIPTION_MAX_LENGTH ]])
GROUP_FINDER_GROUP_LISTING_TITLE_MAX_LENGTH = nil --/esoui/Ingame/GroupFinder/Gamepad/GroupFinder_CreateEditGroupListing_Gamepad.lua:342:61 | control.editBoxControl:SetMaxInputChars([[ GROUP_FINDER_GROUP_LISTING_TITLE_MAX_LENGTH ]])
IS_PLURAL = nil --/esoui/Ingame/Inventory/Gamepad/BuySpaceCommon_Gamepad.lua:98:112 | ZO_AppendNarration(narrations, SCREEN_NARRATION_MANAGER:CreateNarratableObject(GetCurrencyName(CURT_MONEY, [[ IS_PLURAL ]], IS_UPPER)))
IS_UPPER = nil --/esoui/Ingame/Inventory/Gamepad/BuySpaceCommon_Gamepad.lua:98:123 | ZO_AppendNarration(narrations, SCREEN_NARRATION_MANAGER:CreateNarratableObject(GetCurrencyName(CURT_MONEY, IS_PLURAL, [[ IS_UPPER ]])))
ITEMTYPE_JEWELRY = nil --/esoui/Ingame/TradingHouse/TradingHouseCategories_Shared.lua:1196:93 | search:SetFilter(TRADING_HOUSE_FILTER_TYPE_ITEM, { ITEMTYPE_WEAPON, ITEMTYPE_ARMOR, [[ ITEMTYPE_JEWELRY ]] })
LOGIN_AUTH_ERROR_ACCOUNT_BANNED = nil --/esoui/Pregame/Globals/PreGameDialogs.lua:535:60 | text = zo_strformat(GetString("SI_LOGINAUTHERROR", [[ LOGIN_AUTH_ERROR_ACCOUNT_BANNED ]]), GetURLTextByType(APPROVED_URL_ESO_HELP)),
LOGIN_AUTH_ERROR_ACCOUNT_NOT_LINKED = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_LoginManager.lua:142:26 | if loginError == [[ LOGIN_AUTH_ERROR_ACCOUNT_NOT_LINKED ]] then
LOGIN_AUTH_ERROR_ACCOUNT_NOT_VERIFIED = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_LoginManager.lua:153:34 | elseif loginError == [[ LOGIN_AUTH_ERROR_ACCOUNT_NOT_VERIFIED ]] or loginError == LOGIN_AUTH_ERROR_GAME_ACCOUNT_NOT_VERIFIED then
LOGIN_AUTH_ERROR_ACCOUNT_SUSPENDED = nil --/esoui/Pregame/Globals/PreGameDialogs.lua:571:60 | text = zo_strformat(GetString("SI_LOGINAUTHERROR", [[ LOGIN_AUTH_ERROR_ACCOUNT_SUSPENDED ]]), GetURLTextByType(APPROVED_URL_ESO_HELP)),
LOGIN_AUTH_ERROR_BAD_DMM_TOKEN = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_LoginManager.lua:149:82 | if loginError == LOGIN_AUTH_ERROR_MISSING_DMM_TOKEN or loginError == [[ LOGIN_AUTH_ERROR_BAD_DMM_TOKEN ]] then
LOGIN_AUTH_ERROR_GAME_ACCOUNT_BANNED = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_LoginManager.lua:158:83 | elseif loginError == LOGIN_AUTH_ERROR_ACCOUNT_BANNED or loginError == [[ LOGIN_AUTH_ERROR_GAME_ACCOUNT_BANNED ]] then
LOGIN_AUTH_ERROR_GAME_ACCOUNT_IS_CHILD_ACCOUNT = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_LoginManager.lua:168:34 | elseif loginError == [[ LOGIN_AUTH_ERROR_GAME_ACCOUNT_IS_CHILD_ACCOUNT ]] then
LOGIN_AUTH_ERROR_GAME_ACCOUNT_NOT_VERIFIED = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_LoginManager.lua:153:89 | elseif loginError == LOGIN_AUTH_ERROR_ACCOUNT_NOT_VERIFIED or loginError == [[ LOGIN_AUTH_ERROR_GAME_ACCOUNT_NOT_VERIFIED ]] then
LOGIN_AUTH_ERROR_GAME_ACCOUNT_SUSPENDED = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_LoginManager.lua:163:86 | elseif loginError == LOGIN_AUTH_ERROR_ACCOUNT_SUSPENDED or loginError == [[ LOGIN_AUTH_ERROR_GAME_ACCOUNT_SUSPENDED ]] then
LOGIN_AUTH_ERROR_MISSING_DMM_TOKEN = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_LoginManager.lua:149:30 | if loginError == [[ LOGIN_AUTH_ERROR_MISSING_DMM_TOKEN ]] or loginError == LOGIN_AUTH_ERROR_BAD_DMM_TOKEN then
LOGIN_AUTH_ERROR_NO_ERROR = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_LoginManager.lua:141:22 | if loginError ~= [[ LOGIN_AUTH_ERROR_NO_ERROR ]] then
LOGIN_AUTH_ERROR_SERVER_PSN_FREE_TRIAL_END = nil --/esoui/Pregame/AccountLogin/Gamepad/CreateLinkLoadingScreen_Gamepad.lua:192:22 | if loginError == [[ LOGIN_AUTH_ERROR_SERVER_PSN_FREE_TRIAL_END ]] then
LOGOUT_ERROR_NO_ERROR = nil --/esoui/Pregame/StateManager/PregameStateManager.lua:847:23 | if logoutError ~= [[ LOGOUT_ERROR_NO_ERROR ]] and logoutError ~= LOGOUT_ERROR_UNKNOWN_ERROR and logoutError ~= LOGOUT_ERROR_TRANSFER_FAILED then
LOGOUT_ERROR_TRANSFER_FAILED = nil --/esoui/Pregame/StateManager/PregameStateManager.lua:847:110 | if logoutError ~= LOGOUT_ERROR_NO_ERROR and logoutError ~= LOGOUT_ERROR_UNKNOWN_ERROR and logoutError ~= [[ LOGOUT_ERROR_TRANSFER_FAILED ]] then
LOGOUT_ERROR_UNKNOWN_ERROR = nil --/esoui/Pregame/StateManager/PregameStateManager.lua:847:64 | if logoutError ~= LOGOUT_ERROR_NO_ERROR and logoutError ~= [[ LOGOUT_ERROR_UNKNOWN_ERROR ]] and logoutError ~= LOGOUT_ERROR_TRANSFER_FAILED then
LOGOUT_RESULT_DEFERRED = nil --/esoui/Ingame/Globals/InGameDialogs.lua:2202:57 | ConfirmLogout(true, LOGOUT_TYPE_FORCED, [[ LOGOUT_RESULT_DEFERRED ]])
LOOT_TYPE_ARCHIVAL_FORTUNES = nil --/esoui/Ingame/AddonCompatibilityAliases/PC/AddonCompatibilityAliases_PC.lua:1351:38 | LOOT_TYPE_ENDLESS_DUNGEON_CURRENCY = [[ LOOT_TYPE_ARCHIVAL_FORTUNES ]]
MAIL_MAX_BODY_CHARACTERS = nil --/esoui/Ingame/Mail/Keyboard/MailSend_Keyboard.lua:21:32 | self.body:SetMaxInputChars([[ MAIL_MAX_BODY_CHARACTERS ]])
MAIL_MAX_SUBJECT_CHARACTERS = nil --/esoui/Ingame/Mail/Keyboard/MailSend_Keyboard.lua:16:35 | self.subject:SetMaxInputChars([[ MAIL_MAX_SUBJECT_CHARACTERS ]])
MAX_ARMORY_BUILD_NAME_LENGTH = nil --/esoui/Ingame/Armory/Keyboard/ArmoryDialogs_Keyboard.lua:56:42 | editControl:SetMaxInputChars([[ MAX_ARMORY_BUILD_NAME_LENGTH ]])
MAX_AUTO_COMPLETION_RESULTS = nil --/esoui/Ingame/Globals/InGameDialogs.lua:1291:26 | maxResults = [[ MAX_AUTO_COMPLETION_RESULTS ]],
MAX_GUILD_APPLICATION_DECLINE_MESSAGE_LENGTH = nil --/esoui/Ingame/GuildFinder/Keyboard/GuildRecruitment_ApplicationsList_Keyboard.lua:209:49 | declineMessageEdit:SetMaxInputChars([[ MAX_GUILD_APPLICATION_DECLINE_MESSAGE_LENGTH ]])
MAX_GUILD_APPLICATION_MESSAGE_LENGTH = nil --/esoui/Ingame/GuildFinder/Keyboard/GuildBrowser_GuildInfo_Keyboard.lua:273:32 | editLabel:SetMaxInputChars([[ MAX_GUILD_APPLICATION_MESSAGE_LENGTH ]])
MAX_GUILD_BLACKLIST_MESSAGE_LENGTH = nil --/esoui/Ingame/Guild/Gamepad/GuildRoster_Gamepad.lua:488:65 | control.editBoxControl:SetMaxInputChars([[ MAX_GUILD_BLACKLIST_MESSAGE_LENGTH ]])
MAX_GUILD_DESCRIPTION_LENGTH = nil --/esoui/Ingame/Guild/Keyboard/GuildHome_Keyboard.lua:40:45 | descriptionEditControl:SetMaxInputChars([[ MAX_GUILD_DESCRIPTION_LENGTH ]])
MAX_GUILD_MOTD_LENGTH = nil --/esoui/Ingame/Guild/Keyboard/GuildHome_Keyboard.lua:31:38 | motdEditControl:SetMaxInputChars([[ MAX_GUILD_MOTD_LENGTH ]])
MAX_GUILD_NAME_LENGTH = nil --/esoui/Ingame/Guild/Gamepad/ZO_GuildHub_Gamepad.lua:576:65 | control.editBoxControl:SetMaxInputChars([[ MAX_GUILD_NAME_LENGTH ]])
MAX_GUILD_RANK_NAME_LENGTH = nil --/esoui/Ingame/Guild/ZO_GuildRanks_Shared.lua:325:31 | nameEdit:SetMaxInputChars([[ MAX_GUILD_RANK_NAME_LENGTH ]])
MAX_HELP_DESCRIPTION_BODY = nil --/esoui/Ingame/Help/Keyboard/HelpSubmitFeedback_Keyboard.lua:113:39 | self.description:SetMaxInputChars([[ MAX_HELP_DESCRIPTION_BODY ]])
MAX_HELP_DETAILS_TEXT = nil --/esoui/Ingame/Help/Keyboard/HelpSubmitFeedback_Keyboard.lua:105:35 | self.details:SetMaxInputChars([[ MAX_HELP_DETAILS_TEXT ]])
MOUSE_CONTENT_QUEST_TOOL = nil --/esoui/Ingame/ActionBar/ActionBar.lua:495:152 | if cursorType == MOUSE_CONTENT_ACTION or cursorType == MOUSE_CONTENT_INVENTORY_ITEM or cursorType == MOUSE_CONTENT_QUEST_ITEM or cursorType == [[ MOUSE_CONTENT_QUEST_TOOL ]] then
NOT_SUMMARY = nil --/esoui/Ingame/Achievements/Keyboard/Achievements.lua:2013:196 | self:AddCategory(lookup, tree, "ZO_Achievements_SubCategory", parentNode, categoryIndex, GetString(SI_JOURNAL_PROGRESS_CATEGORY_GENERAL), hidesUnearned, NO_ICONS, NO_ICONS, NO_ICONS, [[ NOT_SUMMARY ]], IS_FAKED_SUBCATEGORY)
NO_AMOUNT = nil --/esoui/Common/Globals/PlatformStoreDialogs.lua:46:139 | ZO_Dialogs_ShowPlatformDialog("BUY_CROWNS_FROM_PLATFORM_STORE", nil, { mainTextParams = { ZO_Currency_FormatKeyboard(CURT_CROWNS, [[ NO_AMOUNT ]], ZO_CURRENCY_FORMAT_PLURAL_NAME_ICON), ZO_GetPlatformStoreName() } })
NO_SOUND = nil --/esoui/Ingame/Restyle/Gamepad/Outfit_Slots_Panel_Gamepad.lua:502:29 | ZO_Alert(ALERT, [[ NO_SOUND ]], GetString(SI_GAMEPAD_OUTFITS_CANT_ADD_LOCKED_STYLE))
OFFLINE_TIME_UPDATE = nil --/esoui/Ingame/Guild/GuildRoster_Shared.lua:405:44 | if currentTime - self.lastUpdateTime > [[ OFFLINE_TIME_UPDATE ]] then
OUTFIT_NAME_MAX_LENGTH = nil --/esoui/Ingame/Globals/InGameDialogs.lua:4307:30 | maxInputCharacters = [[ OUTFIT_NAME_MAX_LENGTH ]],
PROFILE_LOGIN_ERROR_NO_PROFILE = nil --/esoui/Pregame/StateManager/Console/PregameStates_Console.lua:3:52 | if isSuccess == false and not (profileError == [[ PROFILE_LOGIN_ERROR_NO_PROFILE ]] and SCENE_MANAGER:IsShowing("GameStartup")) then
PROFILE_LOGIN_ERROR_UNKNOWN_ERROR = nil --/esoui/Pregame/StateManager/Console/PregameStates_Console.lua:7:67 | errorStringFormat = GetString("SI_PROFILELOGINERROR", [[ PROFILE_LOGIN_ERROR_UNKNOWN_ERROR ]])
QUEST_MAIN_STEP_INDEX = nil --/esoui/Ingame/Utility/TextSearchManager.lua:13:29 | for stepIndex = [[ QUEST_MAIN_STEP_INDEX ]], GetJournalQuestNumSteps(questIndex) do
REQUEST_DATA = nil --/esoui/Ingame/Contacts/Keyboard/Notifications_Keyboard.lua:530:65 | local dataEntry = ZO_ScrollList_CreateDataEntry(dataType or [[ REQUEST_DATA ]], data)
REWARD_DISPLAY_FLAGS_NONE = nil --/esoui/PublicAllIngames/Tooltip/RewardTooltips.lua:62:47 | self:LayoutReward(rewardId, quantity, [[ REWARD_DISPLAY_FLAGS_NONE ]])
REWARD_TRACK_TYPE_REWARD_TRACK_TYPE_AVA_VETERANCY = nil --/esoui/Ingame/Veterancy/Veterancy_Manager.lua:104:31 | if rewardTrackType == [[ REWARD_TRACK_TYPE_REWARD_TRACK_TYPE_AVA_VETERANCY ]] then
REWARD_TYPE_ITEM = nil --/esoui/InternalIngame/Market/Market_Shared.lua:943:63 | local previewInEmptyWorld = rewardInfo:GetRewardType() == [[ REWARD_TYPE_ITEM ]]
SCRIBING_TOOLTIP_DISPLAY_FLAGS_NONE = nil --/esoui/Ingame/Tooltip/ScribingTooltips.lua:47:62 | local displayFlags = options and options.displayFlags or [[ SCRIBING_TOOLTIP_DISPLAY_FLAGS_NONE ]]
SERVER_STATUS_DOWN = nil --/esoui/Pregame/AccountLogin/Keyboard/WorldSelect.lua:5:6 | [[[ SERVER_STATUS_DOWN ]]]    = SI_SERVER_STATUS_DOWN,
SERVER_STATUS_LOCKED = nil --/esoui/Pregame/AccountLogin/Keyboard/WorldSelect.lua:8:6 | [[[ SERVER_STATUS_LOCKED ]]]  = SI_SERVER_STATUS_LOCKED,
SERVER_STATUS_OUT = nil --/esoui/Pregame/AccountLogin/Keyboard/WorldSelect.lua:7:6 | [[[ SERVER_STATUS_OUT ]]]     = SI_SERVER_STATUS_OUT,
SERVER_STATUS_UP = nil --/esoui/Pregame/AccountLogin/Keyboard/WorldSelect.lua:6:6 | [[[ SERVER_STATUS_UP ]]]      = SI_SERVER_STATUS_UP,
SHOW_COMBINED_COUNT = nil --/esoui/Ingame/Crafting/Gamepad/ZO_CraftingOptionsDialog_Gamepad.lua:158:106 | GAMEPAD_TOOLTIPS:LayoutBagItem(GAMEPAD_LEFT_TOOLTIP, targetData.bagId, targetData.slotIndex, [[ SHOW_COMBINED_COUNT ]])
SLIDER_CATEGORY_AGE = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreate_Keyboard.lua:566:10 | [[[ SLIDER_CATEGORY_AGE ]]] = CREATE_BUCKET_BODY,
SLIDER_CATEGORY_BODY = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreate_Keyboard.lua:567:10 | [[[ SLIDER_CATEGORY_BODY ]]] = CREATE_BUCKET_BODY,
SLIDER_CATEGORY_FACE = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreate_Keyboard.lua:568:10 | [[[ SLIDER_CATEGORY_FACE ]]] = CREATE_BUCKET_FACE,
SLIDER_NAME_ARM_SIZE = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:70:51 | { GAMEPAD_BUCKET_CONTROL_TYPE_SLIDER, [[ SLIDER_NAME_ARM_SIZE ]] },
SLIDER_NAME_BUTTOCKS_SIZE = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:73:51 | { GAMEPAD_BUCKET_CONTROL_TYPE_SLIDER, [[ SLIDER_NAME_BUTTOCKS_SIZE ]] },
SLIDER_NAME_CHARACTER_HEIGHT = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:63:51 | { GAMEPAD_BUCKET_CONTROL_TYPE_SLIDER, [[ SLIDER_NAME_CHARACTER_HEIGHT ]] },
SLIDER_NAME_CHEEK_BONE_HEIGHT = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:106:51 | { GAMEPAD_BUCKET_CONTROL_TYPE_SLIDER, [[ SLIDER_NAME_CHEEK_BONE_HEIGHT ]] },
SLIDER_NAME_CHEEK_BONE_SIZE = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:105:51 | { GAMEPAD_BUCKET_CONTROL_TYPE_SLIDER, [[ SLIDER_NAME_CHEEK_BONE_SIZE ]] },
SLIDER_NAME_CHEST_SIZE = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:67:51 | { GAMEPAD_BUCKET_CONTROL_TYPE_SLIDER, [[ SLIDER_NAME_CHEST_SIZE ]] },
SLIDER_NAME_CHIN_HEIGHT = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:108:51 | { GAMEPAD_BUCKET_CONTROL_TYPE_SLIDER, [[ SLIDER_NAME_CHIN_HEIGHT ]] },
SLIDER_NAME_CHIN_SIZE = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:109:51 | { GAMEPAD_BUCKET_CONTROL_TYPE_SLIDER, [[ SLIDER_NAME_CHIN_SIZE ]] },
SLIDER_NAME_EAR_HEIGHT = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:113:51 | { GAMEPAD_BUCKET_CONTROL_TYPE_SLIDER, [[ SLIDER_NAME_EAR_HEIGHT ]] },
SLIDER_NAME_EAR_ROTATION = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:112:51 | { GAMEPAD_BUCKET_CONTROL_TYPE_SLIDER, [[ SLIDER_NAME_EAR_ROTATION ]] },
SLIDER_NAME_EAR_SIZE = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:111:51 | { GAMEPAD_BUCKET_CONTROL_TYPE_SLIDER, [[ SLIDER_NAME_EAR_SIZE ]] },
SLIDER_NAME_EAR_TIP_FLARE = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:114:51 | { GAMEPAD_BUCKET_CONTROL_TYPE_SLIDER, [[ SLIDER_NAME_EAR_TIP_FLARE ]] },
SLIDER_NAME_EYEBROW_ANGLE = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreate_Keyboard.lua:520:13 | [[ SLIDER_NAME_EYEBROW_ANGLE ]],
SLIDER_NAME_EYEBROW_DEPTH = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:137:51 | { GAMEPAD_BUCKET_CONTROL_TYPE_SLIDER, [[ SLIDER_NAME_EYEBROW_DEPTH ]] },
SLIDER_NAME_EYEBROW_HEIGHT = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:134:51 | { GAMEPAD_BUCKET_CONTROL_TYPE_SLIDER, [[ SLIDER_NAME_EYEBROW_HEIGHT ]] },
SLIDER_NAME_EYEBROW_SKEW = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:136:51 | { GAMEPAD_BUCKET_CONTROL_TYPE_SLIDER, [[ SLIDER_NAME_EYEBROW_SKEW ]] },
SLIDER_NAME_EYE_ANGLE = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:129:51 | { GAMEPAD_BUCKET_CONTROL_TYPE_SLIDER, [[ SLIDER_NAME_EYE_ANGLE ]] },
SLIDER_NAME_EYE_HEIGHT = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:131:51 | { GAMEPAD_BUCKET_CONTROL_TYPE_SLIDER, [[ SLIDER_NAME_EYE_HEIGHT ]] },
SLIDER_NAME_EYE_SEPARATION = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:130:51 | { GAMEPAD_BUCKET_CONTROL_TYPE_SLIDER, [[ SLIDER_NAME_EYE_SEPARATION ]] },
SLIDER_NAME_EYE_SIZE = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:128:51 | { GAMEPAD_BUCKET_CONTROL_TYPE_SLIDER, [[ SLIDER_NAME_EYE_SIZE ]] },
SLIDER_NAME_EYE_SQUINT = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:132:51 | { GAMEPAD_BUCKET_CONTROL_TYPE_SLIDER, [[ SLIDER_NAME_EYE_SQUINT ]] },
SLIDER_NAME_FOOT_SIZE = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:75:51 | { GAMEPAD_BUCKET_CONTROL_TYPE_SLIDER, [[ SLIDER_NAME_FOOT_SIZE ]] },
SLIDER_NAME_FOREHEAD_SLOPE = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:104:51 | { GAMEPAD_BUCKET_CONTROL_TYPE_SLIDER, [[ SLIDER_NAME_FOREHEAD_SLOPE ]] },
SLIDER_NAME_GUT_SIZE = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:68:51 | { GAMEPAD_BUCKET_CONTROL_TYPE_SLIDER, [[ SLIDER_NAME_GUT_SIZE ]] },
SLIDER_NAME_HAND_SIZE = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:71:51 | { GAMEPAD_BUCKET_CONTROL_TYPE_SLIDER, [[ SLIDER_NAME_HAND_SIZE ]] },
SLIDER_NAME_HIP_SIZE = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:72:51 | { GAMEPAD_BUCKET_CONTROL_TYPE_SLIDER, [[ SLIDER_NAME_HIP_SIZE ]] },
SLIDER_NAME_JAW_SIZE = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:107:51 | { GAMEPAD_BUCKET_CONTROL_TYPE_SLIDER, [[ SLIDER_NAME_JAW_SIZE ]] },
SLIDER_NAME_LEG_SIZE = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:74:51 | { GAMEPAD_BUCKET_CONTROL_TYPE_SLIDER, [[ SLIDER_NAME_LEG_SIZE ]] },
SLIDER_NAME_LIP_FULLNESS = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:145:51 | { GAMEPAD_BUCKET_CONTROL_TYPE_SLIDER, [[ SLIDER_NAME_LIP_FULLNESS ]] },
SLIDER_NAME_MOUTH_CURVE = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:144:51 | { GAMEPAD_BUCKET_CONTROL_TYPE_SLIDER, [[ SLIDER_NAME_MOUTH_CURVE ]] },
SLIDER_NAME_MOUTH_HEIGHT = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:142:51 | { GAMEPAD_BUCKET_CONTROL_TYPE_SLIDER, [[ SLIDER_NAME_MOUTH_HEIGHT ]] },
SLIDER_NAME_MOUTH_WIDTH = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreate_Keyboard.lua:536:13 | [[ SLIDER_NAME_MOUTH_WIDTH ]],
SLIDER_NAME_NECK_SIZE = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:110:51 | { GAMEPAD_BUCKET_CONTROL_TYPE_SLIDER, [[ SLIDER_NAME_NECK_SIZE ]] },
SLIDER_NAME_NOSE_HEIGHT = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:139:51 | { GAMEPAD_BUCKET_CONTROL_TYPE_SLIDER, [[ SLIDER_NAME_NOSE_HEIGHT ]] },
SLIDER_NAME_NOSE_LENGTH = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:141:51 | { GAMEPAD_BUCKET_CONTROL_TYPE_SLIDER, [[ SLIDER_NAME_NOSE_LENGTH ]] },
SLIDER_NAME_NOSE_SHAPE = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:138:51 | { GAMEPAD_BUCKET_CONTROL_TYPE_SLIDER, [[ SLIDER_NAME_NOSE_SHAPE ]] },
SLIDER_NAME_NOSE_WIDTH = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:140:51 | { GAMEPAD_BUCKET_CONTROL_TYPE_SLIDER, [[ SLIDER_NAME_NOSE_WIDTH ]] },
SLIDER_NAME_TAIL_SIZE = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreate_Keyboard.lua:469:13 | [[ SLIDER_NAME_TAIL_SIZE ]],
SLIDER_NAME_TOOTH_SIZE = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreate_Keyboard.lua:503:13 | [[ SLIDER_NAME_TOOTH_SIZE ]],
SLIDER_NAME_TORSO_SIZE = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:66:51 | { GAMEPAD_BUCKET_CONTROL_TYPE_SLIDER, [[ SLIDER_NAME_TORSO_SIZE ]] },
SLIDER_NAME_WAIST_SIZE = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreateBucket_Gamepad.lua:69:51 | { GAMEPAD_BUCKET_CONTROL_TYPE_SLIDER, [[ SLIDER_NAME_WAIST_SIZE ]] },
SLIDER_SUBCAT_BODY_FEATURES = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreateBucket_Keyboard.lua:52:20 | { id = [[ SLIDER_SUBCAT_BODY_FEATURES ]], anchorYOffsetOverride = SUBCATEGORY_PAD, },
SLIDER_SUBCAT_BODY_LOWER = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreateBucket_Keyboard.lua:54:20 | { id = [[ SLIDER_SUBCAT_BODY_LOWER ]], anchorYOffsetOverride = SUBCATEGORY_PAD, },
SLIDER_SUBCAT_BODY_TYPE = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreateBucket_Keyboard.lua:51:20 | { id = [[ SLIDER_SUBCAT_BODY_TYPE ]], anchorYOffsetOverride = SUBCATEGORY_PAD, },
SLIDER_SUBCAT_BODY_UPPER = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreateBucket_Keyboard.lua:53:20 | { id = [[ SLIDER_SUBCAT_BODY_UPPER ]], anchorYOffsetOverride = SUBCATEGORY_PAD, },
SLIDER_SUBCAT_FACE_BROW = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreateBucket_Keyboard.lua:79:20 | { id = [[ SLIDER_SUBCAT_FACE_BROW ]], anchorYOffsetOverride = SUBCATEGORY_PAD, },
SLIDER_SUBCAT_FACE_EARS = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreateBucket_Keyboard.lua:82:20 | { id = [[ SLIDER_SUBCAT_FACE_EARS ]], anchorYOffsetOverride = SUBCATEGORY_PAD, },
SLIDER_SUBCAT_FACE_EYES = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreateBucket_Keyboard.lua:78:20 | { id = [[ SLIDER_SUBCAT_FACE_EYES ]], anchorYOffsetOverride = SUBCATEGORY_PAD, },
SLIDER_SUBCAT_FACE_FACE = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreateBucket_Keyboard.lua:77:20 | { id = [[ SLIDER_SUBCAT_FACE_FACE ]], anchorYOffsetOverride = SUBCATEGORY_PAD, },
SLIDER_SUBCAT_FACE_FEATURES = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreateBucket_Keyboard.lua:76:20 | { id = [[ SLIDER_SUBCAT_FACE_FEATURES ]], anchorYOffsetOverride = SUBCATEGORY_PAD, },
SLIDER_SUBCAT_FACE_HAIR = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreateBucket_Keyboard.lua:75:20 | { id = [[ SLIDER_SUBCAT_FACE_HAIR ]], anchorYOffsetOverride = SUBCATEGORY_PAD, },
SLIDER_SUBCAT_FACE_MOUTH = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreateBucket_Keyboard.lua:81:20 | { id = [[ SLIDER_SUBCAT_FACE_MOUTH ]], anchorYOffsetOverride = SUBCATEGORY_PAD, },
SLIDER_SUBCAT_FACE_NOSE = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreateBucket_Keyboard.lua:80:20 | { id = [[ SLIDER_SUBCAT_FACE_NOSE ]], anchorYOffsetOverride = SUBCATEGORY_PAD, },
SLIDER_SUBCAT_FACE_TYPE = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreateBucket_Keyboard.lua:73:20 | { id = [[ SLIDER_SUBCAT_FACE_TYPE ]], anchorYOffsetOverride = SUBCATEGORY_PAD, },
SLIDER_SUBCAT_VOICE = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreateBucket_Keyboard.lua:74:20 | { id = [[ SLIDER_SUBCAT_VOICE ]], anchorYOffsetOverride = -42, },
SLOT_TYPE_ACHIEVEMENT_REWARD = nil --/esoui/Ingame/Inventory/InventorySlot.lua:1637:6 | [[[ SLOT_TYPE_ACHIEVEMENT_REWARD ]]] =            function(inventorySlot, slotActions, actionName) LinkHelper(slotActions, actionName, ZO_LinkHandler_CreateChatLink(GetAchievementRewardLink, inventorySlot)) end,
SLOT_TYPE_BANK_ITEM = nil --/esoui/Ingame/Inventory/InventorySlot.lua:67:6 | [[[ SLOT_TYPE_BANK_ITEM ]]] = true,
SLOT_TYPE_BUY_MULTIPLE = nil --/esoui/Ingame/Inventory/InventorySlot.lua:1631:6 | [[[ SLOT_TYPE_BUY_MULTIPLE ]]] =                  function(inventorySlot, slotActions, actionName) LinkHelper(slotActions, actionName, ZO_LinkHandler_CreateChatLink(GetStoreItemLink, inventorySlot.index)) end,
SLOT_TYPE_COLLECTIONS_INVENTORY = nil --/esoui/Ingame/Inventory/InventorySlot.lua:338:6 | [[[ SLOT_TYPE_COLLECTIONS_INVENTORY ]]] =
SLOT_TYPE_CRAFTING_COMPONENT = nil --/esoui/Ingame/Inventory/InventorySlot.lua:1421:24 | return slotType == [[ SLOT_TYPE_CRAFTING_COMPONENT ]]
SLOT_TYPE_CRAFT_BAG_ITEM = nil --/esoui/Ingame/Inventory/InventorySlot.lua:1158:6 | [[[ SLOT_TYPE_CRAFT_BAG_ITEM ]]] = false, -- There's no good reason to destroy from the Craft Bag
SLOT_TYPE_DYEABLE_EQUIPMENT = nil --/esoui/Ingame/Inventory/InventorySlot.lua:1524:55 | if(slotType == SLOT_TYPE_EQUIPMENT or slotType == [[ SLOT_TYPE_DYEABLE_EQUIPMENT ]]) then
SLOT_TYPE_ENCHANTMENT = nil --/esoui/Ingame/Inventory/InventorySlot.lua:2410:6 | [[[ SLOT_TYPE_ENCHANTMENT ]]] =
SLOT_TYPE_ENCHANTMENT_RESULT = nil --/esoui/Ingame/Inventory/InventorySlot.lua:2418:6 | [[[ SLOT_TYPE_ENCHANTMENT_RESULT ]]] =
SLOT_TYPE_EQUIPMENT = nil --/esoui/Ingame/Inventory/InventorySlot.lua:1155:6 | [[[ SLOT_TYPE_EQUIPMENT ]]] = true,
SLOT_TYPE_FURNITURE_VAULT = nil --/esoui/Ingame/Inventory/InventorySlot.lua:1485:6 | [[[ SLOT_TYPE_FURNITURE_VAULT ]]] = DefaultUseItemFunction,
SLOT_TYPE_GAMEPAD_INVENTORY_ITEM = nil --/esoui/Ingame/Inventory/InventorySlot.lua:69:6 | [[[ SLOT_TYPE_GAMEPAD_INVENTORY_ITEM ]]] = true,
SLOT_TYPE_GUILD_BANK_ITEM = nil --/esoui/Ingame/Inventory/InventorySlot.lua:794:26 | elseif targetType == [[ SLOT_TYPE_GUILD_BANK_ITEM ]] then
SLOT_TYPE_GUILD_SPECIFIC_ITEM = nil --/esoui/Ingame/Inventory/InventorySlot.lua:1651:6 | [[[ SLOT_TYPE_GUILD_SPECIFIC_ITEM ]]] =           function(inventorySlot, slotActions, actionName) LinkHelper(slotActions, actionName, ZO_LinkHandler_CreateChatLink(GetGuildSpecificLink, inventorySlot)) end,
SLOT_TYPE_ITEM = nil --/esoui/Ingame/Inventory/InventorySlot.lua:68:6 | [[[ SLOT_TYPE_ITEM ]]] = true,
SLOT_TYPE_LIST_DIALOG_ITEM = nil --/esoui/Ingame/Inventory/InventorySlot.lua:476:54 | ZO_Inventory_BindSlot(inventorySlot, [[ SLOT_TYPE_LIST_DIALOG_ITEM ]], index, bag)
SLOT_TYPE_LOOT = nil --/esoui/Ingame/Inventory/InventorySlot.lua:1638:6 | [[[ SLOT_TYPE_LOOT ]]] =                          function(inventorySlot, slotActions, actionName) LinkHelper(slotActions, actionName, ZO_LinkHandler_CreateChatLink(GetLootLink, inventorySlot)) end,
SLOT_TYPE_MAIL_ATTACHMENT = nil --/esoui/Ingame/Inventory/InventorySlot.lua:1635:6 | [[[ SLOT_TYPE_MAIL_ATTACHMENT ]]] =               function(inventorySlot, slotActions, actionName) LinkHelper(slotActions, actionName, ZO_LinkHandler_CreateChatLink(GetAttachedItemLink, MAIL_INBOX:GetOpenMailId(), ZO_Inventory_GetSlotIndex(inventorySlot))) end,
SLOT_TYPE_MAIL_QUEUED_ATTACHMENT = nil --/esoui/Ingame/Inventory/InventorySlot.lua:1633:6 | [[[ SLOT_TYPE_MAIL_QUEUED_ATTACHMENT ]]] =        function(inventorySlot, slotActions, actionName) LinkHelper(slotActions, actionName, ZO_LinkHandler_CreateChatLink(GetMailQueuedAttachmentLink, GetQueuedItemAttachmentSlotIndex(inventorySlot))) end,
SLOT_TYPE_MULTIPLE_PENDING_CRAFTING_COMPONENTS = nil --/esoui/Ingame/Inventory/InventorySlot.lua:1423:24 | or slotType == [[ SLOT_TYPE_MULTIPLE_PENDING_CRAFTING_COMPONENTS ]]
SLOT_TYPE_MY_TRADE = nil --/esoui/Ingame/Inventory/InventorySlot.lua:973:51 | if ZO_InventorySlot_GetType(inventorySlot) == [[ SLOT_TYPE_MY_TRADE ]] then
SLOT_TYPE_PENDING_CHARGE = nil --/esoui/Ingame/Inventory/InventorySlot.lua:2402:6 | [[[ SLOT_TYPE_PENDING_CHARGE ]]] =
SLOT_TYPE_PENDING_CRAFTING_COMPONENT = nil --/esoui/Ingame/Inventory/InventorySlot.lua:1422:24 | or slotType == [[ SLOT_TYPE_PENDING_CRAFTING_COMPONENT ]]
SLOT_TYPE_PENDING_REPAIR = nil --/esoui/Ingame/Inventory/InventorySlot.lua:2137:6 | [[[ SLOT_TYPE_PENDING_REPAIR ]]] =                       NON_INTERACTABLE_ITEM_ACTIONS,
SLOT_TYPE_PENDING_RETRAIT_ITEM = nil --/esoui/Ingame/Inventory/InventorySlot.lua:1428:24 | or slotType == [[ SLOT_TYPE_PENDING_RETRAIT_ITEM ]]
SLOT_TYPE_QUEST_ITEM = nil --/esoui/Ingame/Inventory/InventorySlot.lua:332:6 | [[[ SLOT_TYPE_QUEST_ITEM ]]] =
SLOT_TYPE_REPAIR = nil --/esoui/Ingame/Inventory/InventorySlot.lua:1641:6 | [[[ SLOT_TYPE_REPAIR ]]] =                        function(inventorySlot, slotActions, actionName) LinkHelper(slotActions, actionName, ZO_LinkHandler_CreateChatLink(GetBagItemLink, inventorySlot)) end,
SLOT_TYPE_SMITHING_BOOSTER = nil --/esoui/Ingame/Inventory/InventorySlot.lua:1427:24 | or slotType == [[ SLOT_TYPE_SMITHING_BOOSTER ]]
SLOT_TYPE_SMITHING_MATERIAL = nil --/esoui/Ingame/Inventory/InventorySlot.lua:1424:24 | or slotType == [[ SLOT_TYPE_SMITHING_MATERIAL ]]
SLOT_TYPE_SMITHING_STYLE = nil --/esoui/Ingame/Inventory/InventorySlot.lua:1425:24 | or slotType == [[ SLOT_TYPE_SMITHING_STYLE ]]
SLOT_TYPE_SMITHING_TRAIT = nil --/esoui/Ingame/Inventory/InventorySlot.lua:1426:24 | or slotType == [[ SLOT_TYPE_SMITHING_TRAIT ]]
SLOT_TYPE_STACK_SPLIT = nil --/esoui/Ingame/Inventory/InventorySlot.lua:2468:6 | [[[ SLOT_TYPE_STACK_SPLIT ]]] =
SLOT_TYPE_STORE_BUY = nil --/esoui/Ingame/Inventory/InventorySlot.lua:1630:6 | [[[ SLOT_TYPE_STORE_BUY ]]] =                     function(inventorySlot, slotActions, actionName) LinkHelper(slotActions, actionName, ZO_LinkHandler_CreateChatLink(GetStoreItemLink, inventorySlot.index)) end,
SLOT_TYPE_STORE_BUYBACK = nil --/esoui/Ingame/Inventory/InventorySlot.lua:1632:6 | [[[ SLOT_TYPE_STORE_BUYBACK ]]] =                 function(inventorySlot, slotActions, actionName) LinkHelper(slotActions, actionName, ZO_LinkHandler_CreateChatLink(GetBuybackItemLink, inventorySlot.index)) end,
SLOT_TYPE_THEIR_TRADE = nil --/esoui/Ingame/Inventory/InventorySlot.lua:1629:6 | [[[ SLOT_TYPE_THEIR_TRADE ]]] =                   function(inventorySlot, slotActions, actionName) LinkHelper(slotActions, actionName, ZO_LinkHandler_CreateChatLink(GetTradeItemLink, TRADE_THEM, inventorySlot.index)) end,
SLOT_TYPE_TRADING_HOUSE_ITEM_LISTING = nil --/esoui/Ingame/Inventory/InventorySlot.lua:1650:6 | [[[ SLOT_TYPE_TRADING_HOUSE_ITEM_LISTING ]]] =    function(inventorySlot, slotActions, actionName) LinkHelper(slotActions, actionName, ZO_LinkHandler_CreateChatLink(GetTradingHouseListingLink, inventorySlot)) end,
SLOT_TYPE_TRADING_HOUSE_ITEM_RESULT = nil --/esoui/Ingame/Inventory/InventorySlot.lua:1649:6 | [[[ SLOT_TYPE_TRADING_HOUSE_ITEM_RESULT ]]] =     function(inventorySlot, slotActions, actionName) LinkHelper(slotActions, actionName, ZO_LinkHandler_CreateChatLink(GetTradingHouseSearchResultLink, inventorySlot)) end,
SLOT_TYPE_TRADING_HOUSE_POST_ITEM = nil --/esoui/Ingame/Inventory/InventorySlot.lua:1295:51 | if ZO_InventorySlot_GetType(inventorySlot) == [[ SLOT_TYPE_TRADING_HOUSE_POST_ITEM ]] then
SORT_ARROW_UP = nil --/esoui/Ingame/Inventory/Gamepad/GuildBank_Gamepad.lua:607:102 | local sortIconPath = self.withdrawList.currentSortOrder == ZO_ICON_SORT_ARROW_UP and [[ SORT_ARROW_UP ]] or ZO_ICON_SORT_ARROW_DOWN
STORE_FAILURE_NOT_ENOUGH_ARCHIVAL_FORTUNES = nil --/esoui/Ingame/AddonCompatibilityAliases/PC/AddonCompatibilityAliases_PC.lua:1350:53 | STORE_FAILURE_NOT_ENOUGH_ENDLESS_DUNGEON_CURRENCY = [[ STORE_FAILURE_NOT_ENOUGH_ARCHIVAL_FORTUNES ]]
THS_LEFT = nil --/esoui/Pregame/CharacterSelect/Keyboard/ZO_CharacterSelect_Keyboard.lua:820:86 | self.tooltip:AddHeaderLine(GetString(SI_SERVICE_TOOLTIP_TYPE), "ZoFontWinH5", 1, [[ THS_LEFT ]], r, g, b)
TIME_NEW_PERSISTS_WHILE_SELECTED_MS = nil --/esoui/Ingame/Companion/Gamepad/CompanionCollectionBook_Gamepad.lua:669:91 | self.clearNewStatusCallId = zo_callLater(self.trySetClearNewFlagCallback, [[ TIME_NEW_PERSISTS_WHILE_SELECTED_MS ]])
UNEQUIP_OUTFIT = nil --/esoui/Ingame/Companion/Keyboard/CompanionOverview_Keyboard.lua:118:40 | self.pendingEquipOutfitIndex = [[ UNEQUIP_OUTFIT ]]
UNIT_TYPE_INTERACTFIXTURE = nil --/esoui/Ingame/UnitFrames/UnitFrames.lua:1556:6 | [[[ UNIT_TYPE_INTERACTFIXTURE ]]] = true,
UNIT_TYPE_INTERACTOBJ = nil --/esoui/Ingame/UnitFrames/UnitFrames.lua:1557:6 | [[[ UNIT_TYPE_INTERACTOBJ ]]] = true,
UNIT_TYPE_SIEGEWEAPON = nil --/esoui/Ingame/UnitFrames/UnitFrames.lua:1555:6 | [[[ UNIT_TYPE_SIEGEWEAPON ]]] = true,
UNIT_TYPE_SIMPLEINTERACTFIXTURE = nil --/esoui/Ingame/UnitFrames/UnitFrames.lua:1558:6 | [[[ UNIT_TYPE_SIMPLEINTERACTFIXTURE ]]] = true,
UNIT_TYPE_SIMPLEINTERACTOBJ = nil --/esoui/Ingame/UnitFrames/UnitFrames.lua:1559:6 | [[[ UNIT_TYPE_SIMPLEINTERACTOBJ ]]] = true,
UPDATE_FILTER = nil --/esoui/Ingame/Leaderboards/Gamepad/LeaderboardList_Gamepad.lua:234:43 | self:UpdatePendingUpdateLevel([[ UPDATE_FILTER ]])
USABILITY_TYPE_USABLE = nil --/esoui/Ingame/Retrait/Keyboard/RetraitStation_Reconstruct_Keyboard.lua:108:38 | self.isTraitUsable = [[ USABILITY_TYPE_USABLE ]]
USABILITY_TYPE_VALID_BUT_MISSING_REQUIREMENT = nil --/esoui/Ingame/Retrait/Keyboard/RetraitStation_Reconstruct_Keyboard.lua:111:38 | self.isTraitUsable = [[ USABILITY_TYPE_VALID_BUT_MISSING_REQUIREMENT ]]
USE_LOWERCASE_NUMBER_SUFFIXES = nil --/esoui/Ingame/Battleground/BattlegroundScoreboard.lua:619:105 | damage = ZO_AbbreviateAndLocalizeNumber(damage, NUMBER_ABBREVIATION_PRECISION_LARGEST_UNIT, [[ USE_LOWERCASE_NUMBER_SUFFIXES ]])
VENGENCE_CATEGORY_ITEM_ACTION_MODE = nil --/esoui/Ingame/Inventory/Gamepad/GamepadInventory.lua:613:35 | or self.actionMode == [[ VENGENCE_CATEGORY_ITEM_ACTION_MODE ]] then
VISIBLE_ICON = nil --/esoui/Ingame/Collections/Keyboard/TributePatronBook_Keyboard.lua:302:48 | categoryControl.statusIcon:AddIcon([[ VISIBLE_ICON ]])
WEAPON_TYPE_NONE = nil --/esoui/Ingame/TradingHouse/TradingHouseCategories_Shared.lua:429:9 | [[ WEAPON_TYPE_NONE ]],
WEAPON_TYPE_SHIELD = nil --/esoui/Ingame/TradingHouse/TradingHouseCategories_Shared.lua:430:9 | [[ WEAPON_TYPE_SHIELD ]]

-- 3. Global Events (EVENT_*) --
EVENT_ACCOUNT_LINK_ACTIVATION_CODE_RECEIVED = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_CreateLinkAccount.lua:116:35 | self.control:RegisterForEvent([[ EVENT_ACCOUNT_LINK_ACTIVATION_CODE_RECEIVED ]], OnActivationCodeReceived)
EVENT_ACCOUNT_LINK_SUCCESSFUL = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_LoginManager.lua:23:56 | EVENT_MANAGER:RegisterForEvent("LoginManager", [[ EVENT_ACCOUNT_LINK_SUCCESSFUL ]], FilterMethodCallback(self.OnCreateLinkAccountSuccessful))
EVENT_ANNOUNCEMENTS_RESULT = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_Login.lua:182:45 | EVENT_MANAGER:RegisterForEvent("Login", [[ EVENT_ANNOUNCEMENTS_RESULT ]], OnAnnouncementsResult)
EVENT_ANTIQUITY_DIGGING_ACTIVE_SKILL_CHANGED = nil --/esoui/InternalIngame/AntiquityDigging/AntiquityDigging.lua:139:30 | control:RegisterForEvent([[ EVENT_ANTIQUITY_DIGGING_ACTIVE_SKILL_CHANGED ]], function()
EVENT_ANTIQUITY_DIGGING_TRANSITION_TO_NEXT_DAY_COMPLETE = nil --/esoui/InternalIngame/AntiquityDigging/AntiquityDiggingSummary.lua:785:137 | local transferToNextDayCompleteTrigger = fanfareStateMachine:AddTrigger("TRANSFER_TO_LORE_IN", ZO_StateMachine_TriggerEventManager, [[ EVENT_ANTIQUITY_DIGGING_TRANSITION_TO_NEXT_DAY_COMPLETE ]])
EVENT_AREA_LOAD_STARTED = nil --/esoui/Pregame/StateManager/PregameStateManager.lua:654:65 | EVENT_MANAGER:UnregisterForEvent("PregameStateManager", [[ EVENT_AREA_LOAD_STARTED ]])
EVENT_BAD_CLIENT_VERSION = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_LoginManager.lua:32:52 | EVENT_MANAGER:RegisterForEvent("LoginManager", [[ EVENT_BAD_CLIENT_VERSION ]], FilterMethodCallback(self.OnBadClientVersion))
EVENT_CHARACTER_CREATED = nil --/esoui/Pregame/CharacterCreate/ZO_CharacterCreate_Shared.lua:132:66 | EVENT_MANAGER:RegisterForEvent("ZO_CharacterCreate_Gamepad", [[ EVENT_CHARACTER_CREATED ]], OnCharacterCreated)
EVENT_CHARACTER_CREATE_FAILED = nil --/esoui/Pregame/CharacterCreate/ZO_CharacterCreate_Shared.lua:133:66 | EVENT_MANAGER:RegisterForEvent("ZO_CharacterCreate_Gamepad", [[ EVENT_CHARACTER_CREATE_FAILED ]], OnCharacterCreateFailed)
EVENT_CHARACTER_CREATE_ZOOM_CHANGED = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreate_Keyboard.lua:95:58 | EVENT_MANAGER:RegisterForEvent("ZO_CharacterCreate", [[ EVENT_CHARACTER_CREATE_ZOOM_CHANGED ]], HandleZoomChanged)
EVENT_CHARACTER_DELETED = nil --/esoui/Pregame/CharacterSelect/ZO_CharacterSelect_Manager.lua:60:66 | EVENT_MANAGER:RegisterForEvent("ZO_CharacterSelect_Manager", [[ EVENT_CHARACTER_DELETED ]], function(_, ...)
EVENT_CHARACTER_EDIT_FAILED = nil --/esoui/Pregame/CharacterCreate/ZO_CharacterCreate_Shared.lua:135:66 | EVENT_MANAGER:RegisterForEvent("ZO_CharacterCreate_Gamepad", [[ EVENT_CHARACTER_EDIT_FAILED ]], OnCharacterEditFailed)
EVENT_CHARACTER_EDIT_SUCCEEDED = nil --/esoui/Pregame/CharacterCreate/ZO_CharacterCreate_Shared.lua:134:66 | EVENT_MANAGER:RegisterForEvent("ZO_CharacterCreate_Gamepad", [[ EVENT_CHARACTER_EDIT_SUCCEEDED ]], OnCharacterEditSucceeded)
EVENT_CHARACTER_LIST_RECEIVED = nil --/esoui/Pregame/StateManager/PregameStateManager.lua:974:55 | EVENT_MANAGER:RegisterForEvent("PregameStateManager", [[ EVENT_CHARACTER_LIST_RECEIVED ]], OnCharacterListReceived)
EVENT_CHARACTER_RENAME_RESULT = nil --/esoui/Pregame/CharacterSelect/ZO_CharacterSelect_Manager.lua:56:66 | EVENT_MANAGER:RegisterForEvent("ZO_CharacterSelect_Manager", [[ EVENT_CHARACTER_RENAME_RESULT ]], function(_, ...)
EVENT_CHARACTER_SELECTED_FOR_PLAY = nil --/esoui/Pregame/StateManager/PregameStateManager.lua:976:55 | EVENT_MANAGER:RegisterForEvent("PregameStateManager", [[ EVENT_CHARACTER_SELECTED_FOR_PLAY ]], OnCharacterSelected)
EVENT_CODE_REDEMPTION_COMPLETE = nil --/esoui/InternalIngame/CodeRedemption/Gamepad/CodeRedemption_Gamepad.lua:183:65 | EVENT_MANAGER:UnregisterForEvent("GAMEPAD_CODE_REDEMPTION", [[ EVENT_CODE_REDEMPTION_COMPLETE ]])
EVENT_CONFIRM_DELETE_MAIL = nil --/esoui/InternalIngame/Mail/ConfirmMail.lua:154:48 | EVENT_MANAGER:RegisterForEvent("ZoDeleteMail", [[ EVENT_CONFIRM_DELETE_MAIL ]], function(eventCode, mailId)
EVENT_CONFIRM_SEND_GIFT = nil --/esoui/InternalIngame/Gifting/Keyboard/ConfirmSendGift_Keyboard.lua:124:65 | EVENT_MANAGER:RegisterForEvent("ZoConfirmSendGiftKeyboard", [[ EVENT_CONFIRM_SEND_GIFT ]], function(eventCode, giftId)
EVENT_CONFIRM_SEND_MAIL = nil --/esoui/InternalIngame/Mail/ConfirmMail.lua:37:49 | EVENT_MANAGER:RegisterForEvent("ZoConfirmMail", [[ EVENT_CONFIRM_SEND_MAIL ]], function(eventCode, to, subject, body, numAttachments, attachedMoney)
EVENT_CONFIRM_UNSAFE_URL = nil --/esoui/InternalIngame/URL/ConfirmURL.lua:34:48 | EVENT_MANAGER:RegisterForEvent("ZoConfirmURL", [[ EVENT_CONFIRM_UNSAFE_URL ]], function(eventCode, URL)
EVENT_CREATE_LINK_LOADING_ERROR = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_LoginManager.lua:22:56 | EVENT_MANAGER:RegisterForEvent("LoginManager", [[ EVENT_CREATE_LINK_LOADING_ERROR ]], FilterMethodCallback(self.OnCreateLinkLoadingError))
EVENT_DIRECT_PURCHASE_CONFIRM_PURCHASE = nil --/esoui/InternalIngame/DirectPurchase/DirectPurchaseInternal_Manager.lua:35:62 | EVENT_MANAGER:RegisterForEvent("DirectPurchase_Manager", [[ EVENT_DIRECT_PURCHASE_CONFIRM_PURCHASE ]], OnConfirmPurchase)
EVENT_DISCONNECTED_FROM_SERVER = nil --/esoui/Pregame/StateManager/PregameStateManager.lua:978:55 | EVENT_MANAGER:RegisterForEvent("PregameStateManager", [[ EVENT_DISCONNECTED_FROM_SERVER ]], OnDisconnectedFromServer)
EVENT_DISPLAY_NAME_READY = nil --/esoui/Pregame/StateManager/PregameStateManager.lua:970:48 | EVENT_MANAGER:RegisterForEvent(systemName, [[ EVENT_DISPLAY_NAME_READY ]], OnReady)
EVENT_ENTITLEMENT_STATE_CHANGED = nil --/esoui/Pregame/CharacterCreate/ZO_CharacterCreate_Shared.lua:136:66 | EVENT_MANAGER:RegisterForEvent("ZO_CharacterCreate_Gamepad", [[ EVENT_ENTITLEMENT_STATE_CHANGED ]], OnChapterUpgraded)
EVENT_EVENT_ANNOUNCEMENTS_RECEIVED = nil --/esoui/InternalIngame/MarketAnnouncement/MarketAnnouncement_Manager.lua:87:74 | EVENT_MANAGER:RegisterForEvent("EVENT_EVENT_ANNOUNCEMENTS_RECEIVED", [[ EVENT_EVENT_ANNOUNCEMENTS_RECEIVED ]], OnEventAnnouncementsUpdated)
EVENT_EVENT_ANNOUNCEMENTS_UPDATED = nil --/esoui/InternalIngame/MarketAnnouncement/MarketAnnouncement_Manager.lua:86:73 | EVENT_MANAGER:RegisterForEvent("EVENT_EVENT_ANNOUNCEMENTS_UPDATED", [[ EVENT_EVENT_ANNOUNCEMENTS_UPDATED ]], OnEventAnnouncementsUpdated)
EVENT_FETCHED_LEGAL_DOCS = nil --/esoui/Pregame/AccountLogin/LegalDocsProvider.lua:16:66 | EVENT_MANAGER:RegisterForEvent("ZO_RemoteLegalDocsProvider", [[ EVENT_FETCHED_LEGAL_DOCS ]], function()
EVENT_GLOBAL_ERROR = nil --/esoui/Pregame/StateManager/Keyboard/PregameStates_Keyboard.lua:268:59 | EVENT_MANAGER:RegisterForEvent("PregameStateManager", [[ EVENT_GLOBAL_ERROR ]],                       GlobalError)
EVENT_LOGIN_FAILED_INVALID_CREDENTIALS = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_LoginManager.lua:27:52 | EVENT_MANAGER:RegisterForEvent("LoginManager", [[ EVENT_LOGIN_FAILED_INVALID_CREDENTIALS ]], FilterMethodCallback(self.OnBadLogin))
EVENT_LOGIN_OTP_PENDING = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_LoginManager.lua:31:52 | EVENT_MANAGER:RegisterForEvent("LoginManager", [[ EVENT_LOGIN_OTP_PENDING ]], FilterMethodCallback(self.OnOTPPending))
EVENT_LOGIN_QUEUED = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_LoginManager.lua:29:52 | EVENT_MANAGER:RegisterForEvent("LoginManager", [[ EVENT_LOGIN_QUEUED ]], FilterMethodCallback(self.OnLoginQueued))
EVENT_LOGIN_REQUESTED = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_LoginManager.lua:30:52 | EVENT_MANAGER:RegisterForEvent("LoginManager", [[ EVENT_LOGIN_REQUESTED ]], FilterMethodCallback(self.OnLoginRequested))
EVENT_LOGIN_SUCCESSFUL = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_LoginManager.lua:28:52 | EVENT_MANAGER:RegisterForEvent("LoginManager", [[ EVENT_LOGIN_SUCCESSFUL ]], FilterMethodCallback(self.OnLoginSuccessful))
EVENT_LOGOUT_SUCCESSFUL = nil --/esoui/Pregame/CharacterCreate/ZO_CharacterCreate_Shared.lua:131:66 | EVENT_MANAGER:RegisterForEvent("ZO_CharacterCreate_Gamepad", [[ EVENT_LOGOUT_SUCCESSFUL ]], OnLogoutSuccessful)
EVENT_MARKET_PRODUCT_SEARCH_CANCELED = nil --/esoui/InternalIngame/Market/Market_Manager.lua:77:54 | EVENT_MANAGER:RegisterForEvent(ZO_MARKET_EVENTS, [[ EVENT_MARKET_PRODUCT_SEARCH_CANCELED ]], OnMarketSearchResultsCanceled)
EVENT_MARKET_PRODUCT_SEARCH_RESULTS_READY = nil --/esoui/InternalIngame/Market/Market_Manager.lua:76:54 | EVENT_MANAGER:RegisterForEvent(ZO_MARKET_EVENTS, [[ EVENT_MARKET_PRODUCT_SEARCH_RESULTS_READY ]], OnMarketSearchResultsReady)
EVENT_MARKET_REQUEST_PURCHASE_MARKET_PRODUCT = nil --/esoui/InternalIngame/Market/Market_Manager.lua:81:54 | EVENT_MANAGER:RegisterForEvent(ZO_MARKET_EVENTS, [[ EVENT_MARKET_REQUEST_PURCHASE_MARKET_PRODUCT ]], OnRequestPurchaseMarketProduct)
EVENT_MARKET_SHOW_CHAPTER_UPGRADE = nil --/esoui/InternalIngame/Market/Market_Manager.lua:83:54 | EVENT_MANAGER:RegisterForEvent(ZO_MARKET_EVENTS, [[ EVENT_MARKET_SHOW_CHAPTER_UPGRADE ]], OnShowChapterUpgrade)
EVENT_MARKET_SHOW_ESO_PLUS_PAGE = nil --/esoui/InternalIngame/Market/Market_Manager.lua:82:54 | EVENT_MANAGER:RegisterForEvent(ZO_MARKET_EVENTS, [[ EVENT_MARKET_SHOW_ESO_PLUS_PAGE ]], OnShowEsoPlusPage)
EVENT_MARKET_SHOW_MARKET_AND_SEARCH = nil --/esoui/InternalIngame/Market/Market_Manager.lua:80:54 | EVENT_MANAGER:RegisterForEvent(ZO_MARKET_EVENTS, [[ EVENT_MARKET_SHOW_MARKET_AND_SEARCH ]], OnShowMarketAndSearch)
EVENT_MARKET_SHOW_MARKET_PRODUCT = nil --/esoui/InternalIngame/Market/Market_Manager.lua:79:54 | EVENT_MANAGER:RegisterForEvent(ZO_MARKET_EVENTS, [[ EVENT_MARKET_SHOW_MARKET_PRODUCT ]], OnShowMarketProduct)
EVENT_NAME_LOOKUP = nil --/esoui/Libraries/Globals/DebugUtils.lua:90:8 | if([[ EVENT_NAME_LOOKUP ]]) -- nice, we can get a string look up for this event code!  (TODO: just expose these as strings?)
EVENT_PLATFORM_ENTITLEMENT_STATE_CHANGED = nil --/esoui/Pregame/AccountLogin/Gamepad/GameStartup_Gamepad.lua:312:62 | EVENT_MANAGER:RegisterForEvent("ZO_GameStartup_Gamepad", [[ EVENT_PLATFORM_ENTITLEMENT_STATE_CHANGED ]], OnEntitlementUpdated)
EVENT_PROFILE_NOT_LINKED = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_LoginManager.lua:24:56 | EVENT_MANAGER:RegisterForEvent("LoginManager", [[ EVENT_PROFILE_NOT_LINKED ]], FilterMethodCallback(self.OnProfileNotLinked))
EVENT_REQUEST_ANTIQUITY_DIGGING_EXIT = nil --/esoui/InternalIngame/AntiquityDigging/AntiquityDiggingSummary.lua:60:30 | control:RegisterForEvent([[ EVENT_REQUEST_ANTIQUITY_DIGGING_EXIT ]], function()
EVENT_REQUEST_SCRYING_EXIT = nil --/esoui/InternalIngame/Scrying/Scrying.lua:1352:30 | control:RegisterForEvent([[ EVENT_REQUEST_SCRYING_EXIT ]], function()
EVENT_REQUEST_TRIBUTE_EXIT = nil --/esoui/InternalIngame/Tribute/Tribute.lua:883:34 | control:RegisterForEvent([[ EVENT_REQUEST_TRIBUTE_EXIT ]], function(...) self:RequestExitTribute(...) end)
EVENT_RUMOR_DATA_CHANGED = nil --/esoui/Ingame/ZO_Quest/RumorManager.lua:29:8 | if [[ EVENT_RUMOR_DATA_CHANGED ]] then
EVENT_SCRYING_GAME_OVER = nil --/esoui/InternalIngame/Scrying/Scrying.lua:1357:30 | control:RegisterForEvent([[ EVENT_SCRYING_GAME_OVER ]], function()
EVENT_SCRYING_INTRO_COMPLETE = nil --/esoui/InternalIngame/Scrying/Scrying.lua:1330:30 | control:RegisterForEvent([[ EVENT_SCRYING_INTRO_COMPLETE ]], function()
EVENT_SCRYING_OUTRO_COMPLETE = nil --/esoui/InternalIngame/Scrying/Scrying.lua:1335:30 | control:RegisterForEvent([[ EVENT_SCRYING_OUTRO_COMPLETE ]], function()
EVENT_SERVER_IN_MAINTENANCE_MODE = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_Login.lua:183:45 | EVENT_MANAGER:RegisterForEvent("Login", [[ EVENT_SERVER_IN_MAINTENANCE_MODE ]], OnEnterMaintenanceMode)
EVENT_SERVER_LOCKED = nil --/esoui/Pregame/StateManager/Keyboard/PregameStates_Keyboard.lua:266:59 | EVENT_MANAGER:RegisterForEvent("PregameStateManager", [[ EVENT_SERVER_LOCKED ]],                      OnServerLocked)
EVENT_SERVICE_TOKENS_UPDATED = nil --/esoui/Pregame/CharacterSelect/Keyboard/ZO_CharacterSelect_Keyboard.lua:740:30 | control:RegisterForEvent([[ EVENT_SERVICE_TOKENS_UPDATED ]], OnTokensUpdated)
EVENT_START_ANTIQUITY_DIGGING = nil --/esoui/InternalIngame/AntiquityDigging/AntiquityDiggingSummary.lua:55:30 | control:RegisterForEvent([[ EVENT_START_ANTIQUITY_DIGGING ]], function()
EVENT_START_SCRYING = nil --/esoui/InternalIngame/Scrying/Scrying.lua:1348:30 | control:RegisterForEvent([[ EVENT_START_SCRYING ]], function()
EVENT_STREAMING_INSTALL_DIALOG_FINISHED = nil --/esoui/Pregame/AccountLogin/Gamepad/GameStartup_Gamepad.lua:314:62 | EVENT_MANAGER:RegisterForEvent("ZO_GameStartup_Gamepad", [[ EVENT_STREAMING_INSTALL_DIALOG_FINISHED ]], OnStreamingInstallDialogResult)
EVENT_SUBSYSTEM_LOAD_STATE_CHANGED = nil --/esoui/Pregame/StateManager/PregameStateManager.lua:655:65 | EVENT_MANAGER:UnregisterForEvent("PregameStateManager", [[ EVENT_SUBSYSTEM_LOAD_STATE_CHANGED ]])
EVENT_TRIBUTE_AGENT_CONFINEMENTS_CHANGED = nil --/esoui/InternalIngame/Tribute/TributeConfinementViewer_Manager.lua:53:48 | EVENT_MANAGER:RegisterForEvent(systemName, [[ EVENT_TRIBUTE_AGENT_CONFINEMENTS_CHANGED ]], function(_, agentInstanceId)
EVENT_TRIBUTE_AGENT_DEFEAT_COST_CHANGED = nil --/esoui/InternalIngame/Tribute/TributePileViewer_Manager.lua:137:48 | EVENT_MANAGER:RegisterForEvent(systemName, [[ EVENT_TRIBUTE_AGENT_DEFEAT_COST_CHANGED ]], function(_, cardInstanceId, delta, newDefeatCost, shouldPlayFx)
EVENT_TRIBUTE_BEGIN_MECHANIC_SELECTION = nil --/esoui/InternalIngame/Tribute/TributeConfinementViewer_Manager.lua:46:48 | EVENT_MANAGER:RegisterForEvent(systemName, [[ EVENT_TRIBUTE_BEGIN_MECHANIC_SELECTION ]], function(_, cardInstanceId)
EVENT_TRIBUTE_BEGIN_TARGET_SELECTION = nil --/esoui/InternalIngame/Tribute/TributeConfinementViewer_Manager.lua:32:48 | EVENT_MANAGER:RegisterForEvent(systemName, [[ EVENT_TRIBUTE_BEGIN_TARGET_SELECTION ]], function(_, needsTargetViewer)
EVENT_TRIBUTE_CARD_ADDED = nil --/esoui/InternalIngame/Tribute/Tribute.lua:562:34 | control:RegisterForEvent([[ EVENT_TRIBUTE_CARD_ADDED ]], function(_, cardInstanceId)
EVENT_TRIBUTE_CARD_MECHANIC_RESOLUTION_STATE_CHANGED = nil --/esoui/InternalIngame/Tribute/TributeMechanic_Manager.lua:863:66 | EVENT_MANAGER:RegisterForEvent("ZO_TributeMechanic_Manager", [[ EVENT_TRIBUTE_CARD_MECHANIC_RESOLUTION_STATE_CHANGED ]], OnCardMechanicResolutionStateChanged)
EVENT_TRIBUTE_CARD_REMOVED = nil --/esoui/InternalIngame/Tribute/Tribute.lua:567:34 | control:RegisterForEvent([[ EVENT_TRIBUTE_CARD_REMOVED ]], function(_, cardInstanceId)
EVENT_TRIBUTE_CARD_STATE_FLAGS_CHANGED = nil --/esoui/InternalIngame/Tribute/TributePileViewer_Manager.lua:131:48 | EVENT_MANAGER:RegisterForEvent(systemName, [[ EVENT_TRIBUTE_CARD_STATE_FLAGS_CHANGED ]], function(_, cardInstanceId, stateFlags)
EVENT_TRIBUTE_CLEAR_BOARD_CARDS = nil --/esoui/InternalIngame/Tribute/TributePileViewer_Manager.lua:103:48 | EVENT_MANAGER:RegisterForEvent(systemName, [[ EVENT_TRIBUTE_CLEAR_BOARD_CARDS ]], function()
EVENT_TRIBUTE_END_MECHANIC_SELECTION = nil --/esoui/InternalIngame/Tribute/TributeMechanicSelector.lua:186:30 | control:RegisterForEvent([[ EVENT_TRIBUTE_END_MECHANIC_SELECTION ]], function()
EVENT_TRIBUTE_END_TARGET_SELECTION = nil --/esoui/InternalIngame/Tribute/TributeConfinementViewer_Manager.lua:39:48 | EVENT_MANAGER:RegisterForEvent(systemName, [[ EVENT_TRIBUTE_END_TARGET_SELECTION ]], function()
EVENT_TRIBUTE_FORCE_DISCARD_COUNT_CHANGED = nil --/esoui/InternalIngame/Tribute/Tribute.lua:1638:35 | self.control:RegisterForEvent([[ EVENT_TRIBUTE_FORCE_DISCARD_COUNT_CHANGED ]], function(_, playerPerspective, newCount)
EVENT_TRIBUTE_PATRON_DRAFTED = nil --/esoui/InternalIngame/Tribute/TributePatronSelection_Manager.lua:15:70 | EVENT_MANAGER:RegisterForEvent("TributePatronSelection_Manager", [[ EVENT_TRIBUTE_PATRON_DRAFTED ]], function(_, patronDraftId, patronDefId)
EVENT_TRIBUTE_PATRON_FAVOR_STATE_CHANGED = nil --/esoui/InternalIngame/Tribute/TributePatronStall.lua:130:30 | control:RegisterForEvent([[ EVENT_TRIBUTE_PATRON_FAVOR_STATE_CHANGED ]], function(_, _, favorState)
EVENT_TRIBUTE_PATRON_MECHANIC_RESOLUTION_STATE_CHANGED = nil --/esoui/InternalIngame/Tribute/TributeMechanic_Manager.lua:869:66 | EVENT_MANAGER:RegisterForEvent("ZO_TributeMechanic_Manager", [[ EVENT_TRIBUTE_PATRON_MECHANIC_RESOLUTION_STATE_CHANGED ]], OnPatronMechanicResolutionStateChanged)
EVENT_TRIBUTE_PATRON_START_NEXT_DRAFT = nil --/esoui/InternalIngame/Tribute/TributePatronSelection_Manager.lua:39:70 | EVENT_MANAGER:RegisterForEvent("TributePatronSelection_Manager", [[ EVENT_TRIBUTE_PATRON_START_NEXT_DRAFT ]], function()
EVENT_TRIBUTE_PATRON_STATE_FLAGS_CHANGED = nil --/esoui/InternalIngame/Tribute/TributePatronStall.lua:126:30 | control:RegisterForEvent([[ EVENT_TRIBUTE_PATRON_STATE_FLAGS_CHANGED ]], function(_, _, stateFlags)
EVENT_TRIBUTE_PATRON_USAGE_COUNTER_HIGHLIGHTED = nil --/esoui/InternalIngame/Tribute/Tribute.lua:611:34 | control:RegisterForEvent([[ EVENT_TRIBUTE_PATRON_USAGE_COUNTER_HIGHLIGHTED ]], function(_, perspective)
EVENT_TRIBUTE_PATRON_USAGE_COUNT_CHANGED = nil --/esoui/InternalIngame/Tribute/Tribute.lua:594:34 | control:RegisterForEvent([[ EVENT_TRIBUTE_PATRON_USAGE_COUNT_CHANGED ]], function(_, perspective, newAmount)
EVENT_TRIBUTE_PILE_UPDATED = nil --/esoui/InternalIngame/Tribute/TributePileViewer_Manager.lua:79:48 | EVENT_MANAGER:RegisterForEvent(systemName, [[ EVENT_TRIBUTE_PILE_UPDATED ]], function(_, boardLocation)
EVENT_TRIBUTE_RESOURCE_CHANGED = nil --/esoui/InternalIngame/Tribute/Tribute.lua:584:34 | control:RegisterForEvent([[ EVENT_TRIBUTE_RESOURCE_CHANGED ]], function(_, perspective, resource, newAmount, delta)
EVENT_TRIBUTE_RESOURCE_TOKEN_HIGHLIGHTED = nil --/esoui/InternalIngame/Tribute/Tribute.lua:601:34 | control:RegisterForEvent([[ EVENT_TRIBUTE_RESOURCE_TOKEN_HIGHLIGHTED ]], function(_, perspective, resource)
EVENT_TRIBUTE_VIEW_PILE = nil --/esoui/InternalIngame/Tribute/TributePileViewer_Manager.lua:124:48 | EVENT_MANAGER:RegisterForEvent(systemName, [[ EVENT_TRIBUTE_VIEW_PILE ]], function(_, boardLocation)
EVENT_WORLD_LIST_RECEIVED = nil --/esoui/Pregame/StateManager/Keyboard/PregameStates_Keyboard.lua:267:59 | EVENT_MANAGER:RegisterForEvent("PregameStateManager", [[ EVENT_WORLD_LIST_RECEIVED ]],                OnWorldListReceived)
EVENT_WORLD_SELECTED = nil --/esoui/Pregame/AccountLogin/Gamepad/CreateLinkLoadingScreen_Gamepad.lua:252:27 | self:RegisterForEvent([[ EVENT_WORLD_SELECTED ]],  function(...) self:OnWorldSelected(...) end)

-- 4. Global Settings (*_SETTING_*) --
GRAPHICS_SETTING_ACTIVE_DISPLAY = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:59:25 | settingId = [[ GRAPHICS_SETTING_ACTIVE_DISPLAY ]],
GRAPHICS_SETTING_AMBIENT_OCCLUSION_TYPE = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:229:25 | settingId = [[ GRAPHICS_SETTING_AMBIENT_OCCLUSION_TYPE ]],
GRAPHICS_SETTING_ANTIALIASING_TYPE = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:169:25 | settingId = [[ GRAPHICS_SETTING_ANTIALIASING_TYPE ]],
GRAPHICS_SETTING_BACKGROUND_FPS_LIMIT = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:90:25 | settingId = [[ GRAPHICS_SETTING_BACKGROUND_FPS_LIMIT ]],
GRAPHICS_SETTING_BLOOM = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:259:25 | settingId = [[ GRAPHICS_SETTING_BLOOM ]],
GRAPHICS_SETTING_CAP_CONSOLE_FRAMERATE_IN_MENUS = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:47:25 | settingId = [[ GRAPHICS_SETTING_CAP_CONSOLE_FRAMERATE_IN_MENUS ]],
GRAPHICS_SETTING_CHARACTER_RESOLUTION = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:253:25 | settingId = [[ GRAPHICS_SETTING_CHARACTER_RESOLUTION ]],
GRAPHICS_SETTING_CLUTTER_2D_QUALITY = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:241:25 | settingId = [[ GRAPHICS_SETTING_CLUTTER_2D_QUALITY ]],
GRAPHICS_SETTING_CONSOLE_ENHANCED_RENDER_QUALITY = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:23:25 | settingId = [[ GRAPHICS_SETTING_CONSOLE_ENHANCED_RENDER_QUALITY ]],
GRAPHICS_SETTING_DEPTH_OF_FIELD_MODE = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:247:25 | settingId = [[ GRAPHICS_SETTING_DEPTH_OF_FIELD_MODE ]],
GRAPHICS_SETTING_DISTORTION = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:265:25 | settingId = [[ GRAPHICS_SETTING_DISTORTION ]],
GRAPHICS_SETTING_DLSS_MODE = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:175:25 | settingId = [[ GRAPHICS_SETTING_DLSS_MODE ]],
GRAPHICS_SETTING_ENERGY_SUSTAINABILITY_SCREEN_DIM_AND_RESOLUTION = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:80:25 | settingId = [[ GRAPHICS_SETTING_ENERGY_SUSTAINABILITY_SCREEN_DIM_AND_RESOLUTION ]],
GRAPHICS_SETTING_FSR_MODE = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:181:25 | settingId = [[ GRAPHICS_SETTING_FSR_MODE ]],
GRAPHICS_SETTING_FULLSCREEN = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:53:25 | settingId = [[ GRAPHICS_SETTING_FULLSCREEN ]],
GRAPHICS_SETTING_GAMMA_ADJUSTMENT = nil --/esoui/Pregame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:183:25 | settingId = [[ GRAPHICS_SETTING_GAMMA_ADJUSTMENT ]],
GRAPHICS_SETTING_GOD_RAYS = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:271:25 | settingId = [[ GRAPHICS_SETTING_GOD_RAYS ]],
GRAPHICS_SETTING_GRAPHICS_MODE_PS5 = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:29:25 | settingId = [[ GRAPHICS_SETTING_GRAPHICS_MODE_PS5 ]],
GRAPHICS_SETTING_GRAPHICS_MODE_XBSS = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:35:25 | settingId = [[ GRAPHICS_SETTING_GRAPHICS_MODE_XBSS ]],
GRAPHICS_SETTING_GRAPHICS_MODE_XBSX = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:41:25 | settingId = [[ GRAPHICS_SETTING_GRAPHICS_MODE_XBSX ]],
GRAPHICS_SETTING_HDR_ENABLED = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:105:25 | settingId = [[ GRAPHICS_SETTING_HDR_ENABLED ]],
GRAPHICS_SETTING_HDR_MODE = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:135:25 | settingId = [[ GRAPHICS_SETTING_HDR_MODE ]],
GRAPHICS_SETTING_HDR_PEAK_BRIGHTNESS = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:110:25 | settingId = [[ GRAPHICS_SETTING_HDR_PEAK_BRIGHTNESS ]],
GRAPHICS_SETTING_HDR_SCENE_BRIGHTNESS = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:115:25 | settingId = [[ GRAPHICS_SETTING_HDR_SCENE_BRIGHTNESS ]],
GRAPHICS_SETTING_HDR_SCENE_CONTRAST = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:120:25 | settingId = [[ GRAPHICS_SETTING_HDR_SCENE_CONTRAST ]],
GRAPHICS_SETTING_HDR_UI_BRIGHTNESS = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:125:25 | settingId = [[ GRAPHICS_SETTING_HDR_UI_BRIGHTNESS ]],
GRAPHICS_SETTING_HDR_UI_CONTRAST = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:130:25 | settingId = [[ GRAPHICS_SETTING_HDR_UI_CONTRAST ]],
GRAPHICS_SETTING_MIP_LOAD_SKIP_LEVELS = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:163:25 | settingId = [[ GRAPHICS_SETTING_MIP_LOAD_SKIP_LEVELS ]],
GRAPHICS_SETTING_OCCLUSION_CULLING_ENABLED = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:235:25 | settingId = [[ GRAPHICS_SETTING_OCCLUSION_CULLING_ENABLED ]],
GRAPHICS_SETTING_PFX_GLOBAL_MAXIMUM = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:211:25 | settingId = [[ GRAPHICS_SETTING_PFX_GLOBAL_MAXIMUM ]],
GRAPHICS_SETTING_PFX_SUPPRESS_DISTANCE = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:217:25 | settingId = [[ GRAPHICS_SETTING_PFX_SUPPRESS_DISTANCE ]],
GRAPHICS_SETTING_PLANAR_WATER_REFLECTION_QUALITY = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:205:25 | settingId = [[ GRAPHICS_SETTING_PLANAR_WATER_REFLECTION_QUALITY ]],
GRAPHICS_SETTING_PRESETS = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:157:25 | settingId = [[ GRAPHICS_SETTING_PRESETS ]],
GRAPHICS_SETTING_RENDERTHREAD = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:75:25 | settingId = [[ GRAPHICS_SETTING_RENDERTHREAD ]],
GRAPHICS_SETTING_RESOLUTION = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:65:25 | settingId = [[ GRAPHICS_SETTING_RESOLUTION ]],
GRAPHICS_SETTING_SCREENSPACE_WATER_REFLECTION_QUALITY = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:199:25 | settingId = [[ GRAPHICS_SETTING_SCREENSPACE_WATER_REFLECTION_QUALITY ]],
GRAPHICS_SETTING_SHADOWS = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:193:25 | settingId = [[ GRAPHICS_SETTING_SHADOWS ]],
GRAPHICS_SETTING_SHOW_ADDITIONAL_ALLY_EFFECTS = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:277:25 | settingId = [[ GRAPHICS_SETTING_SHOW_ADDITIONAL_ALLY_EFFECTS ]],
GRAPHICS_SETTING_SUB_SAMPLING = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:187:25 | settingId = [[ GRAPHICS_SETTING_SUB_SAMPLING ]],
GRAPHICS_SETTING_USE_BACKGROUND_FPS_LIMIT = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:85:25 | settingId = [[ GRAPHICS_SETTING_USE_BACKGROUND_FPS_LIMIT ]],
GRAPHICS_SETTING_VFX_ENEMY_INTENSITY = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:295:25 | settingId = [[ GRAPHICS_SETTING_VFX_ENEMY_INTENSITY ]],
GRAPHICS_SETTING_VFX_FRIENDLY_INTENSITY = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:289:25 | settingId = [[ GRAPHICS_SETTING_VFX_FRIENDLY_INTENSITY ]],
GRAPHICS_SETTING_VFX_SELF_INTENSITY = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:283:25 | settingId = [[ GRAPHICS_SETTING_VFX_SELF_INTENSITY ]],
GRAPHICS_SETTING_VIEW_DISTANCE = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:223:25 | settingId = [[ GRAPHICS_SETTING_VIEW_DISTANCE ]],
GRAPHICS_SETTING_VSYNC = nil --/esoui/Ingame/OptionsPanels/Gamepad/OptionsPanels_Gamepad.lua:70:25 | settingId = [[ GRAPHICS_SETTING_VSYNC ]],

-- 5. Event Handlers (On[A-Z]*) --
OnEnterEntry = nil --/esoui/Ingame/HousingEditor/Gamepad/HousingFurnitureRetrieval_Gamepad.lua:290:41 | entryData.onEnter = [[ OnEnterEntry ]]
OnExitEntry = nil --/esoui/Ingame/HousingEditor/Gamepad/HousingFurnitureRetrieval_Gamepad.lua:291:40 | entryData.onExit = [[ OnExitEntry ]]
OnHorizonalScrollListShown = nil --/esoui/Ingame/Retrait/Gamepad/RetraitStation_Reconstruct_Gamepad.lua:128:144 | self.traitList = scrollListClass:New(listContainer.listControl, listSlotTemplate, BASE_NUM_ITEMS_IN_LIST, SetupFunction, EqualityFunction, [[ OnHorizonalScrollListShown ]], OnHorizonalScrollListCleared)
OnMarketCategorySelected = nil --/esoui/InternalIngame/Market/Keyboard/Market_Keyboard.lua:400:17 | [[ OnMarketCategorySelected ]](self:GetDisplayGroup(), categoryIndex, subcategoryIndex, self.suppressMarketCategoryTutorials, isFeaturedCategory)
OnMarketEndPurchase = nil --/esoui/InternalIngame/Globals/MarketDialogs.lua:10:13 | [[ OnMarketEndPurchase ]](dialog.data.marketProductData:GetId())
OnMarketStartPurchase = nil --/esoui/InternalIngame/Market/Gamepad/MarketDialogs_Gamepad.lua:1656:5 | [[ OnMarketStartPurchase ]](marketProductData:GetId())
OnModBrowserClosed = nil --/esoui/PregameAndIngame/AddOns/Gamepad/ModBrowser_Gamepad.lua:1375:9 | [[ OnModBrowserClosed ]]()
OnModBrowserOpened = nil --/esoui/PregameAndIngame/AddOns/Gamepad/ModBrowser_Gamepad.lua:1275:9 | [[ OnModBrowserOpened ]]()
OnReleaseDialog = nil --/esoui/Ingame/HouseTours/Gamepad/HouseTours_Dialogs_Gamepad.lua:10:28 | onHidingCallback = [[ OnReleaseDialog ]],
OnTributeUIHiding = nil --/esoui/InternalIngame/Tribute/Tribute.lua:45:13 | [[ OnTributeUIHiding ]]()

-- 6. String Constants (SI_) --
SI_GAMEPAD_CAMPAIGN_BROWSER_CHOOSE_HOME_CAMPAIGN_MESSAGE = nil --/esoui/Ingame/Campaign/Gamepad/CampaignBrowserDialogs_Gamepad.lua:408:20 | text = [[ SI_GAMEPAD_CAMPAIGN_BROWSER_CHOOSE_HOME_CAMPAIGN_MESSAGE ]],
SI_GAMEPAD_ITEM_SETS_BOOK_OPTIONS = nil --/esoui/Ingame/Collections/ItemSetCollectionsManager.lua:90:67 | ZO_GenericGamepadDialog_RefreshText(dialog, GetString([[ SI_GAMEPAD_ITEM_SETS_BOOK_OPTIONS ]]))
SI_GAMEPAD_SMITHING_SELECTED_PATTERN = nil --/esoui/Ingame/Crafting/Gamepad/SmithingCreation_Gamepad.lua:906:42 | [SI_SMITHING_SELECTED_PATTERN] = [[ SI_GAMEPAD_SMITHING_SELECTED_PATTERN ]],
SI_PROMOTIONAL_EVENT_CAPSTONE_DIALOG_TITLE_FORMATTER = nil --/esoui/Ingame/PromotionalEvents/Gamepad/PromotionalEvents_Gamepad.lua:1154:41 | local titleText = GetString([[ SI_PROMOTIONAL_EVENT_CAPSTONE_DIALOG_TITLE_FORMATTER ]])
SI_QUEST_USE_QUEST_ITEM_PROMPT = nil --/esoui/Ingame/QuestToolMonitor/QuestToolMonitor.lua:20:48 | self.prompt:SetText(zo_strformat(GetString([[ SI_QUEST_USE_QUEST_ITEM_PROMPT ]]), questToolName))
SI_UNKNOWN_RACE = nil --/esoui/Pregame/Tooltip/CharacterSelectTooltips.lua:60:116 | local raceName = characterData.race and GetRaceName(characterData.gender, characterData.race) or GetString([[ SI_UNKNOWN_RACE ]])

-- 7. ZOs Special API --
hmake = nil --/esoui/Libraries/ZO_SceneGraph/ZO_SceneGraphNode.lua:139:29 | self.workingMatrix = [[ hmake ]] Matrix33 { }
hstructure = nil --/esoui/Libraries/ZO_Matrix/ZO_Matrix.lua:1:1 | [[ hstructure ]] Matrix33
internalassert = nil --/esoui/Common/Gamepad/GenericHeaders/GenericHeaders.lua:485:9 | [[ internalassert ]](false, "Unsupported data type. A custom narration function will need to be set for this control that returns a string or number.")

-- 8. Variables to check (missing local definition?) --
confirmButtonLocked = nil --/esoui/Ingame/GuildFinder/Keyboard/GuildRecruitment_Blacklist_Keyboard.lua:262:52 | confirmButton:SetState(confirmButtonState, [[ confirmButtonLocked ]])
currentFrameTimeSeconds = nil --/esoui/Ingame/Veterancy/Veterancy_Shared.lua:597:27 | self:UpdateSeasonInfo([[ currentFrameTimeSeconds ]])
formattedString = nil --/esoui/Ingame/TradingHouse/Keyboard/TradingHouseSearchHistory_Keyboard.lua:59:103 | local historyData = {searchTable = searchEntry.searchTable, formattedSearchTableDescription = [[ formattedString ]]}
newTileControl = nil --/esoui/PublicAllIngames/ItemPreview/PreviewScreen_Shared.lua:244:46 | self:OnFocusedRewardDataChanged(newData, [[ newTileControl ]])
nextLevelTitle = nil --/esoui/Ingame/LevelUpRewards/Gamepad/LevelUpRewardsUpcoming_Gamepad.lua:116:84 | ZO_AppendNarration(narrations, SCREEN_NARRATION_MANAGER:CreateNarratableObject([[ nextLevelTitle ]]))
overrideAppearanceName = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreateSlider_Keyboard.lua:18:62 | local appearanceTypeText = ZO_SELECTED_TEXT:Colorize([[ overrideAppearanceName ]] or GetString("SI_CHARACTERAPPEARANCENAME", category))
selectedDuringRebuild = nil --/esoui/Ingame/HousingEditor/Gamepad/HousingFurnitureSettings_Gamepad.lua:266:68 | ZO_SharedGamepadEntry_OnSetup(control, data, selected, [[ selectedDuringRebuild ]], enabled, active)

-- 9. Other Undocumented Variables --
AcceptLegalDocs = nil --/esoui/Pregame/StateManager/Keyboard/PregameStates_Keyboard.lua:170:13 | [[ AcceptLegalDocs ]]()
AgreeToPEGI = nil --/esoui/Pregame/AccountLogin/Gamepad/PEGI_Gamepad.lua:156:9 | [[ AgreeToPEGI ]]()
AntiquityDiggingExitResponse = nil --/esoui/InternalIngame/AntiquityDigging/AntiquityDiggingSummary.lua:62:13 | [[ AntiquityDiggingExitResponse ]](ACCEPT)
ApplySwapAnimationStyle = nil --/esoui/Ingame/ActionBar/ActionButton.lua:1091:55 | timeline:GetFirstAnimation():SetHandler("OnPlay", [[ ApplySwapAnimationStyle ]])
AreModListingDependenciesReady = nil --/esoui/PregameAndIngame/AddOns/ModBrowserData.lua:153:12 | return [[ AreModListingDependenciesReady ]](self.listingIndex)
AssignControlToTributeCard = nil --/esoui/PublicAllIngames/Tribute/TributeCard.lua:758:9 | [[ AssignControlToTributeCard ]](cardInstanceId, self.control)
AttemptCharacterRename = nil --/esoui/Pregame/CharacterSelect/ZO_CharacterSelect_Manager.lua:411:5 | [[ AttemptCharacterRename ]](characterId, requestedName)
BuyMarketProduct = nil --/esoui/InternalIngame/Market/MarketProductData.lua:297:5 | [[ BuyMarketProduct ]](self.marketProductId, self.presentationIndex, purchaseQuantity)
Callback = nil --/esoui/Ingame/Crafting/Gamepad/ZO_CraftingOptionsDialog_Gamepad.lua:210:85 | return self:BuildCheckboxEntry(header, label, CraftingFilterCheckboxEntrySetup, [[ Callback ]], CraftingFilterCheckboxEntryNarrationText, GAMEPAD_LEFT_TOOLTIP)
CanConfirmTributeTargetSelection = nil --/esoui/InternalIngame/Tribute/TributeTargetViewer_Shared.lua:45:52 | local canConfirm, expectedResult = [[ CanConfirmTributeTargetSelection ]]()
CanDownloadAdditionalContent = nil --/esoui/Pregame/AccountLogin/Gamepad/GameStartup_Gamepad.lua:272:16 | if not [[ CanDownloadAdditionalContent ]](ADDITIONAL_CONTENT_TYPE_VO) then
CanFurnitureBePathed = nil --/esoui/Ingame/HousingEditor/FurnitureClasses_Shared.lua:507:12 | return [[ CanFurnitureBePathed ]](self:GetFurnitureId())
CanPerformScryingAction = nil --/esoui/InternalIngame/Scrying/Scrying.lua:1203:24 | local result = [[ CanPerformScryingAction ]](self:GetScryingActionParameters())
CanPlaceMarketProductInCurrentHouse = nil --/esoui/InternalIngame/Market/Market_Shared.lua:622:64 | elseif marketProductData:GetFurnitureDataId() ~= 0 and [[ CanPlaceMarketProductInCurrentHouse ]](marketProductData:GetId()) then
CanPlayAnyRaceAsAnyAlliance = nil --/esoui/Pregame/Tooltip/CharacterSelectTooltips.lua:21:12 | if [[ CanPlayAnyRaceAsAnyAlliance ]]() then
CanPreviewScryingAction = nil --/esoui/InternalIngame/Scrying/Scrying.lua:1083:34 | local canPreviewAction = [[ CanPreviewScryingAction ]](self:GetScryingActionParameters()) == SCRYING_ACTIVE_SKILL_USE_RESULT_SUCCESS
CanSkipTutorialArea = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreate_Keyboard.lua:901:76 | if ZO_CHARACTERCREATE_MANAGER:GetShouldPromptForTutorialSkip() and [[ CanSkipTutorialArea ]]() and (currentTemplateId == 0 or not templateSkipsTutorial) and startLocation ~= CHARACTER_OPTION_CLEAN_TEST_AREA and startLocation ~= "CharacterSelect_FromIngame" then
CancelDeleteMail = nil --/esoui/InternalIngame/Mail/ConfirmMail.lua:74:13 | [[ CancelDeleteMail ]](dialog.data.mailId)
CancelLogin = nil --/esoui/Pregame/Globals/PreGameDialogs.lua:62:29 | [[ CancelLogin ]]()
CancelSendMail = nil --/esoui/InternalIngame/Mail/ConfirmMail.lua:30:37 | [[ CancelSendMail ]]()
ChangeCharacterOrder = nil --/esoui/Pregame/CharacterSelect/ZO_CharacterSelect_Manager.lua:199:9 | [[ ChangeCharacterOrder ]](characterData.index, characterData.order)
CharacterCreateGetAlliance = nil --/esoui/Pregame/CharacterCreate/ZO_CharacterCreate_Shared.lua:332:29 | local currentAlliance = [[ CharacterCreateGetAlliance ]](characterMode)
CharacterCreateGetClass = nil --/esoui/Pregame/CharacterCreate/ZO_CharacterCreate_Shared.lua:381:26 | local currentClass = [[ CharacterCreateGetClass ]](characterMode)
CharacterCreateGetGender = nil --/esoui/Pregame/CharacterCreate/ZO_CharacterCreate_Shared.lua:370:27 | local currentGender = [[ CharacterCreateGetGender ]](characterMode)
CharacterCreateGetRace = nil --/esoui/Pregame/CharacterCreate/ZO_CharacterCreateData.lua:246:52 | local currentRace = self:GetRaceForRaceDef([[ CharacterCreateGetRace ]](characterMode))
CharacterCreateGetTemplate = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreate_Keyboard.lua:324:41 | if not templateData.isSelectable or [[ CharacterCreateGetTemplate ]](characterMode) == templateId then
CharacterCreateQueueCurrentClassFx = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreateBucket_Keyboard.lua:32:13 | [[ CharacterCreateQueueCurrentClassFx ]]()
CharacterCreateSetAlliance = nil --/esoui/Pregame/CharacterCreate/ZO_CharacterCreate_Shared.lua:671:5 | [[ CharacterCreateSetAlliance ]](alliance)
CharacterCreateSetClass = nil --/esoui/Pregame/CharacterCreate/ZO_CharacterCreate_Shared.lua:386:5 | [[ CharacterCreateSetClass ]](class)
CharacterCreateSetFirstTimePosture = nil --/esoui/Pregame/CharacterCreate/ZO_CharacterCreate_Shared.lua:112:13 | [[ CharacterCreateSetFirstTimePosture ]]()
CharacterCreateSetGender = nil --/esoui/Pregame/CharacterCreate/ZO_CharacterCreate_Shared.lua:375:5 | [[ CharacterCreateSetGender ]](gender)
CharacterCreateSetIdlePosture = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreateBucket_Keyboard.lua:15:17 | [[ CharacterCreateSetIdlePosture ]]()
CharacterCreateSetRace = nil --/esoui/Pregame/CharacterCreate/ZO_CharacterCreate_Shared.lua:303:5 | [[ CharacterCreateSetRace ]](race)
CharacterCreateSetTemplate = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreate_Keyboard.lua:328:5 | [[ CharacterCreateSetTemplate ]](templateId)
CharacterCreateStartMouseSpin = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreate_Gamepad.lua:1649:21 | [[ CharacterCreateStartMouseSpin ]](mx * scalex)
CharacterCreateStopMouseSpin = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreate_Keyboard.lua:1292:50 | self:RegisterForEvent(EVENT_GLOBAL_MOUSE_UP, [[ CharacterCreateStopMouseSpin ]])
CharacterEditSaveCharacterChanges = nil --/esoui/Pregame/Globals/PreGameDialogs.lua:1250:29 | [[ CharacterEditSaveCharacterChanges ]](tokenType)
ConfirmDeleteMail = nil --/esoui/InternalIngame/Mail/ConfirmMail.lua:158:9 | [[ ConfirmDeleteMail ]](mailId)
ConfirmOpenURL = nil --/esoui/InternalIngame/URL/ConfirmURL.lua:22:37 | [[ ConfirmOpenURL ]](dialog.data.URL)
ConfirmPurchaseSku = nil --/esoui/InternalIngame/DirectPurchase/DirectPurchaseInternal_Manager.lua:54:31 | local purchaseRequestId = [[ ConfirmPurchaseSku ]](skuId)
ConfirmSendMail = nil --/esoui/InternalIngame/Mail/ConfirmMail.lua:22:37 | [[ ConfirmSendMail ]](ZO_FormatManualNameEntry(dialog.data.to), dialog.data.subject, dialog.data.body)
CorrectCharacterNameCase = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreate_Keyboard.lua:1112:25 | editControl:SetText([[ CorrectCharacterNameCase ]](nameText))
CreateCharacter = nil --/esoui/Pregame/CharacterCreate/ZO_CharacterCreate_Shared.lua:463:5 | [[ CreateCharacter ]](self.characterName, requestSkipTutorial)
CustomTooltipAnchor = nil --/esoui/Ingame/Retrait/Gamepad/RetraitStation_Reconstruct_Gamepad.lua:209:35 | control.customTooltipAnchor = [[ CustomTooltipAnchor ]]
DeleteCharacter = nil --/esoui/Pregame/CharacterSelect/ZO_CharacterSelect_Manager.lua:426:5 | [[ DeleteCharacter ]](characterId)
DeleteSavedVariablesForModListing = nil --/esoui/PregameAndIngame/AddOns/ModBrowserData.lua:221:9 | [[ DeleteSavedVariablesForModListing ]](self.listingIndex)
DidDigSpotCompleteAntiquitySet = nil --/esoui/InternalIngame/AntiquityDigging/AntiquityDiggingSummary.lua:945:40 | local isAntiquitySetComplete = [[ DidDigSpotCompleteAntiquitySet ]]()
DidDigSpotSpawnWithFissures = nil --/esoui/InternalIngame/AntiquityDigging/AntiquityDigging.lua:362:12 | if [[ DidDigSpotSpawnWithFissures ]]() then
DisplayScryingActiveSkillUseResult = nil --/esoui/InternalIngame/Scrying/Scrying.lua:1194:13 | [[ DisplayScryingActiveSkillUseResult ]](result)
DoesCurrentChapterShowRegistration = nil --/esoui/Pregame/ChapterUpgrade/ChapterUpgrade_Manager.lua:14:8 | if [[ DoesCurrentChapterShowRegistration ]]() then
DoesFilteredMarketProductExist = nil --/esoui/InternalIngame/Market/Market_Shared.lua:406:12 | return [[ DoesFilteredMarketProductExist ]](self:GetDisplayGroup(), REQUIRED_FILTER_TYPES, self.featuredMarketProductFiltersMask)
DoesLocalPlayerHaveBadReputation = nil --/esoui/Ingame/VoiceChat/Console/ZO_VoiceChat_Manager.lua:207:32 | hasBadReputation = [[ DoesLocalPlayerHaveBadReputation ]](),
DoesMarketProductContainConsumables = nil --/esoui/InternalIngame/Market/MarketProductData.lua:239:12 | return [[ DoesMarketProductContainConsumables ]](self.marketProductId)
DoesMarketProductContainServiceToken = nil --/esoui/InternalIngame/Market/MarketProductData.lua:243:12 | return [[ DoesMarketProductContainServiceToken ]](self.marketProductId)
DoesMarketProductHaveActivationRequirement = nil --/esoui/InternalIngame/Market/MarketProductData.lua:191:12 | return [[ DoesMarketProductHaveActivationRequirement ]](self.marketProductId)
DoesMarketProductHaveSubscriptionUnlockedAttachments = nil --/esoui/InternalIngame/Market/MarketProductData.lua:211:12 | return [[ DoesMarketProductHaveSubscriptionUnlockedAttachments ]](self.marketProductId)
DoesPlatformAllowForEmailSubscription = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_CreateLinkAccount.lua:246:46 | local platformDisablesSubscription = not [[ DoesPlatformAllowForEmailSubscription ]]()
DoesPlatformRequirePregamePEGI = nil --/esoui/Pregame/StateManager/PregameStateManager.lua:167:20 | if [[ DoesPlatformRequirePregamePEGI ]]() and not HasAgreedToPEGI() then
DoesPlatformSelectServer = nil --/esoui/Pregame/StateManager/PregameStateManager.lua:465:50 | if ZO_IsConsoleOrGameCoreUI() or not [[ DoesPlatformSelectServer ]]() then
DownloadAdditionalContent = nil --/esoui/Pregame/AccountLogin/Gamepad/GameStartup_Gamepad.lua:322:17 | [[ DownloadAdditionalContent ]](ADDITIONAL_CONTENT_TYPE_VO)
DraftPatron = nil --/esoui/InternalIngame/Tribute/TributePatronSelection_Manager.lua:126:9 | [[ DraftPatron ]](self.selectedPatron)
EndCurrentMarketPreview = nil --/esoui/InternalIngame/Market/Market_Shared.lua:302:5 | [[ EndCurrentMarketPreview ]]()
FinishAntiquityDiggingEarly = nil --/esoui/InternalIngame/AntiquityDigging/AntiquityDigging.lua:41:21 | [[ FinishAntiquityDiggingEarly ]]()
FinishResendingGift = nil --/esoui/InternalIngame/Gifting/Keyboard/ConfirmSendGift_Keyboard.lua:87:21 | [[ FinishResendingGift ]](dialog.data.giftId)
GetActiveCollectibleIdForCharacterAppearance = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreateSlider_Keyboard.lua:14:31 | local collectibleId = [[ GetActiveCollectibleIdForCharacterAppearance ]](category)
GetActiveCompanionType = nil --/esoui/Ingame/Inventory/ItemFilterUtils.lua:2001:66 | if filter == currentFilter and itemData.companionType == [[ GetActiveCompanionType ]]() then
GetActiveMarketProductListingsForEsoPlus = nil --/esoui/InternalIngame/Market/Market_Manager.lua:232:42 | local productId, presentationIndex = [[ GetActiveMarketProductListingsForEsoPlus ]](MARKET_DISPLAY_GROUP_CROWN_STORE)
GetAffectedScryingHex = nil --/esoui/InternalIngame/Scrying/Scrying.lua:1096:46 | local hex = self.hexList[[[ GetAffectedScryingHex ]](index, self:GetScryingActionParameters())]
GetAllianceInfo = nil --/esoui/Pregame/CharacterCreate/ZO_CharacterCreateData.lua:32:156 | local alliance, name, normalIcon, pressedIcon, mouseoverIcon, backdropTop, backdropBottom, position, lore, gamepadNormalIcon, gamepadPressedIcon = [[ GetAllianceInfo ]](i)
GetAngleFromUpForScryingGridDirection = nil --/esoui/InternalIngame/Scrying/Scrying.lua:534:23 | local angle = [[ GetAngleFromUpForScryingGridDirection ]](direction)
GetAnnouncementMessage = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_Login.lua:139:37 | local message = success and [[ GetAnnouncementMessage ]]() or GetString(SI_LOGIN_ANNOUNCEMENTS_FAILURE)
GetAnyRaceAnyAllianceCollectibleId = nil --/esoui/Pregame/Tooltip/CharacterSelectTooltips.lua:15:38 | local anyRaceCollectibleId = [[ GetAnyRaceAnyAllianceCollectibleId ]]()
GetAppearanceInfo = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreate_Keyboard.lua:720:76 | local appearanceName, appearanceType, numValues, displayName = [[ GetAppearanceInfo ]](i)
GetAppearanceValue = nil --/esoui/Pregame/CharacterCreate/ZO_CharacterCreateSlider_Base.lua:175:12 | return [[ GetAppearanceValue ]](self.category)
GetAppearanceValueInfo = nil --/esoui/Pregame/CharacterCreate/ZO_CharacterCreateSlider_Base.lua:161:47 | local legalInitialSetting = select(4, [[ GetAppearanceValueInfo ]](appearanceName, appearanceIndex))
GetBillingInfo = nil --/esoui/InternalIngame/DirectPurchase/Keyboard/DirectPurchaseInternalDialogs_Keyboard.lua:9:44 | local billingInfo, hasBillingAddress = [[ GetBillingInfo ]]()
GetCategoryIndicesFromMarketProductCategoryId = nil --/esoui/InternalIngame/Market/Keyboard/Market_Keyboard.lua:1231:49 | local categoryIndex, subcategoryIndex = [[ GetCategoryIndicesFromMarketProductCategoryId ]](self:GetDisplayGroup(), categoryId)
GetClassRestrictionReason = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreate_Keyboard.lua:1231:92 | local restrictionReasonFunction = raceSelector and GetRaceRestrictionReason or [[ GetClassRestrictionReason ]]
GetConfinedTributeCardInstanceId = nil --/esoui/InternalIngame/Tribute/TributeConfinementViewer_Manager.lua:103:36 | local cardInstanceId = [[ GetConfinedTributeCardInstanceId ]](viewingAgentInstanceId, confinedIndex)
GetConsoleInfoFromAccountId = nil --/esoui/Common/Console/ZO_PlayerConsoleInfoRequestManager.lua:57:39 | [ZO_ID_REQUEST_TYPE_ACCOUNT_ID] = [[ GetConsoleInfoFromAccountId ]],
GetConsoleInfoFromAllianceLeaderboardEntry = nil --/esoui/Common/Console/ZO_PlayerConsoleInfoRequestManager.lua:70:58 | [ZO_ID_REQUEST_TYPE_CAMPAIGN_ALLIANCE_LEADERBOARD] = [[ GetConsoleInfoFromAllianceLeaderboardEntry ]],
GetConsoleInfoFromBattlegroundLeaderboardEntry = nil --/esoui/Common/Console/ZO_PlayerConsoleInfoRequestManager.lua:75:53 | [ZO_ID_REQUEST_TYPE_BATTLEGROUND_LEADERBOARD] = [[ GetConsoleInfoFromBattlegroundLeaderboardEntry ]],
GetConsoleInfoFromChallengeLeaderboardEntry = nil --/esoui/Common/Console/ZO_PlayerConsoleInfoRequestManager.lua:73:50 | [ZO_ID_REQUEST_TYPE_CHALLENGE_LEADERBOARD] = [[ GetConsoleInfoFromChallengeLeaderboardEntry ]],
GetConsoleInfoFromChallengeOfTheWeekLeaderboardEntry = nil --/esoui/Common/Console/ZO_PlayerConsoleInfoRequestManager.lua:74:62 | [ZO_ID_REQUEST_TYPE_CHALLENGE_OF_THE_WEEK_LEADERBOARD] = [[ GetConsoleInfoFromChallengeOfTheWeekLeaderboardEntry ]],
GetConsoleInfoFromCharName = nil --/esoui/Common/Console/ZO_PlayerConsoleInfoRequestManager.lua:58:43 | [ZO_ID_REQUEST_TYPE_CHARACTER_NAME] = [[ GetConsoleInfoFromCharName ]],
GetConsoleInfoFromDisplayName = nil --/esoui/Common/Console/ZO_PlayerConsoleInfoRequestManager.lua:59:41 | [ZO_ID_REQUEST_TYPE_DISPLAY_NAME] = [[ GetConsoleInfoFromDisplayName ]],
GetConsoleInfoFromEndlessDungeonDuoLeaderboardEntry = nil --/esoui/Common/Console/ZO_PlayerConsoleInfoRequestManager.lua:79:60 | [ZO_ID_REQUEST_TYPE_ENDLESS_DUNGEON_DUO_LEADERBOARD] = [[ GetConsoleInfoFromEndlessDungeonDuoLeaderboardEntry ]],
GetConsoleInfoFromEndlessDungeonOfTheWeekDuoLeaderboardEntry = nil --/esoui/Common/Console/ZO_PlayerConsoleInfoRequestManager.lua:80:72 | [ZO_ID_REQUEST_TYPE_ENDLESS_DUNGEON_OF_THE_WEEK_DUO_LEADERBOARD] = [[ GetConsoleInfoFromEndlessDungeonOfTheWeekDuoLeaderboardEntry ]],
GetConsoleInfoFromEndlessDungeonOfTheWeekSoloLeaderboardEntry = nil --/esoui/Common/Console/ZO_PlayerConsoleInfoRequestManager.lua:78:73 | [ZO_ID_REQUEST_TYPE_ENDLESS_DUNGEON_OF_THE_WEEK_SOLO_LEADERBOARD] = [[ GetConsoleInfoFromEndlessDungeonOfTheWeekSoloLeaderboardEntry ]],
GetConsoleInfoFromEndlessDungeonSoloLeaderboardEntry = nil --/esoui/Common/Console/ZO_PlayerConsoleInfoRequestManager.lua:77:61 | [ZO_ID_REQUEST_TYPE_ENDLESS_DUNGEON_SOLO_LEADERBOARD] = [[ GetConsoleInfoFromEndlessDungeonSoloLeaderboardEntry ]],
GetConsoleInfoFromFriend = nil --/esoui/Common/Console/ZO_PlayerConsoleInfoRequestManager.lua:64:40 | [ZO_ID_REQUEST_TYPE_FRIEND_INFO] = [[ GetConsoleInfoFromFriend ]],
GetConsoleInfoFromGroupMember = nil --/esoui/Common/Console/ZO_PlayerConsoleInfoRequestManager.lua:66:39 | [ZO_ID_REQUEST_TYPE_GROUP_INFO] = [[ GetConsoleInfoFromGroupMember ]],
GetConsoleInfoFromGuildApplicationIndex = nil --/esoui/Common/Console/ZO_PlayerConsoleInfoRequestManager.lua:62:51 | [ZO_ID_REQUEST_TYPE_GUILD_APPLICATION_INFO] = [[ GetConsoleInfoFromGuildApplicationIndex ]],
GetConsoleInfoFromGuildBlacklistIndex = nil --/esoui/Common/Console/ZO_PlayerConsoleInfoRequestManager.lua:63:49 | [ZO_ID_REQUEST_TYPE_GUILD_BLACKLIST_INFO] = [[ GetConsoleInfoFromGuildBlacklistIndex ]],
GetConsoleInfoFromGuildInvitee = nil --/esoui/Common/Console/ZO_PlayerConsoleInfoRequestManager.lua:61:47 | [ZO_ID_REQUEST_TYPE_GUILD_INVITEE_INFO] = [[ GetConsoleInfoFromGuildInvitee ]],
GetConsoleInfoFromGuildMember = nil --/esoui/Common/Console/ZO_PlayerConsoleInfoRequestManager.lua:60:39 | [ZO_ID_REQUEST_TYPE_GUILD_INFO] = [[ GetConsoleInfoFromGuildMember ]],
GetConsoleInfoFromIgnore = nil --/esoui/Common/Console/ZO_PlayerConsoleInfoRequestManager.lua:65:40 | [ZO_ID_REQUEST_TYPE_IGNORE_INFO] = [[ GetConsoleInfoFromIgnore ]],
GetConsoleInfoFromIncomingFriendRequest = nil --/esoui/Common/Console/ZO_PlayerConsoleInfoRequestManager.lua:67:43 | [ZO_ID_REQUEST_TYPE_FRIEND_REQUEST] = [[ GetConsoleInfoFromIncomingFriendRequest ]],
GetConsoleInfoFromLeaderboardEntry = nil --/esoui/Common/Console/ZO_PlayerConsoleInfoRequestManager.lua:69:49 | [ZO_ID_REQUEST_TYPE_CAMPAIGN_LEADERBOARD] = [[ GetConsoleInfoFromLeaderboardEntry ]],
GetConsoleInfoFromMailId = nil --/esoui/Common/Console/ZO_PlayerConsoleInfoRequestManager.lua:68:36 | [ZO_ID_REQUEST_TYPE_MAIL_ID] = [[ GetConsoleInfoFromMailId ]],
GetConsoleInfoFromTrialLeaderboardEntry = nil --/esoui/Common/Console/ZO_PlayerConsoleInfoRequestManager.lua:71:46 | [ZO_ID_REQUEST_TYPE_TRIAL_LEADERBOARD] = [[ GetConsoleInfoFromTrialLeaderboardEntry ]],
GetConsoleInfoFromTrialOfTheWeekLeaderboardEntry = nil --/esoui/Common/Console/ZO_PlayerConsoleInfoRequestManager.lua:72:58 | [ZO_ID_REQUEST_TYPE_TRIAL_OF_THE_WEEK_LEADERBOARD] = [[ GetConsoleInfoFromTrialOfTheWeekLeaderboardEntry ]],
GetConsoleInfoFromTributeLeaderboardEntry = nil --/esoui/Common/Console/ZO_PlayerConsoleInfoRequestManager.lua:76:48 | [ZO_ID_REQUEST_TYPE_TRIBUTE_LEADERBOARD] = [[ GetConsoleInfoFromTributeLeaderboardEntry ]],
GetCountryDataForIndex = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_CreateLinkAccount.lua:134:97 | local countryName, countryCode, _, isAllowedInAccountCreation, autoEmailSubscribe = [[ GetCountryDataForIndex ]](i)
GetCrownCrateTierDisplayName = nil --/esoui/InternalIngame/Market/Market_Shared.lua:479:37 | local tierDisplayName = [[ GetCrownCrateTierDisplayName ]](tierId)
GetCrownCrateTierDisplayNameColor = nil --/esoui/InternalIngame/Market/Market_Shared.lua:485:56 | tierDisplayNameColor = ZO_ColorDef:New([[ GetCrownCrateTierDisplayNameColor ]](tierId))
GetCrownCrateTierIds = nil --/esoui/InternalIngame/Market/Market_Shared.lua:475:32 | local crateTierIds = { [[ GetCrownCrateTierIds ]](crateId) }
GetCurrentChapterLargeLogoFileIndex = nil --/esoui/Pregame/ChapterUpgrade/ChapterUpgrade_Shared.lua:75:29 | local logoTexture = [[ GetCurrentChapterLargeLogoFileIndex ]]()
GetCurrentChapterMediumLogoFileIndex = nil --/esoui/Pregame/CharacterSelect/Keyboard/ZO_CharacterSelect_Keyboard.lua:363:62 | ZO_CharacterSelectChapterUpgradeImage:SetTexture([[ GetCurrentChapterMediumLogoFileIndex ]]())
GetCurrentChapterRegistrationInfo = nil --/esoui/Pregame/ChapterUpgrade/ChapterUpgrade_Shared.lua:74:94 | local backgroundTexture, registrationSummary, chapterSummaryHeader, chapterSummary = [[ GetCurrentChapterRegistrationInfo ]]()
GetCurrentChapterSmallLogoFileIndex = nil --/esoui/Pregame/CharacterSelect/Gamepad/ZO_CharacterSelect_Gamepad.lua:414:24 | icon = [[ GetCurrentChapterSmallLogoFileIndex ]](),
GetCurrentChapterVersion = nil --/esoui/Pregame/ChapterUpgrade/ChapterUpgrade_Manager.lua:29:28 | local currentVersion = [[ GetCurrentChapterVersion ]]()
GetCurrentTributeTargetSelectionSourceType = nil --/esoui/InternalIngame/Tribute/TributeTargetViewer_Manager.lua:122:24 | local sourceType = [[ GetCurrentTributeTargetSelectionSourceType ]]()
GetDefaultPlatformOfficialLanguage = nil --/esoui/Pregame/AccountLogin/Gamepad/GameStartup_Gamepad.lua:746:90 | local consoleLanguageText = zo_strupper(GetString("SI_OFFICIALLANGUAGE", [[ GetDefaultPlatformOfficialLanguage ]]()))
GetDefaultTemplate = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreate_Keyboard.lua:289:29 | local defaultTemplate = [[ GetDefaultTemplate ]]()
GetDigSpotBonusLootRewardInfo = nil --/esoui/InternalIngame/AntiquityDigging/AntiquityDiggingSummary.lua:869:58 | local lootType, id, name, icon, count, quality = [[ GetDigSpotBonusLootRewardInfo ]](i)
GetDigSpotDimensions = nil --/esoui/InternalIngame/AntiquityDigging/AntiquityDigging.lua:220:41 | self.numRows, self.numColumns = [[ GetDigSpotDimensions ]]()
GetDigSpotNewLeadRewardAntiquityId = nil --/esoui/InternalIngame/AntiquityDigging/AntiquityDiggingSummary.lua:847:32 | local newLeadAntiquityId = [[ GetDigSpotNewLeadRewardAntiquityId ]]()
GetErrorQueuedFromIngame = nil --/esoui/Pregame/StateManager/PregameStateManager.lua:840:42 | local logoutError, globalErrorCode = [[ GetErrorQueuedFromIngame ]]()
GetEventAnnouncementDescriptionByIndex = nil --/esoui/InternalIngame/MarketAnnouncement/MarketAnnouncement_Manager.lua:129:27 | description = [[ GetEventAnnouncementDescriptionByIndex ]](i),
GetEventAnnouncementIngameTileImageByIndex = nil --/esoui/InternalIngame/MarketAnnouncement/MarketAnnouncement_Manager.lua:130:25 | tileImage = [[ GetEventAnnouncementIngameTileImageByIndex ]](i),
GetEventAnnouncementIngameTileMarketProductIdByIndex = nil --/esoui/InternalIngame/MarketAnnouncement/MarketAnnouncement_Manager.lua:133:31 | marketProductId = [[ GetEventAnnouncementIngameTileMarketProductIdByIndex ]](i),
GetEventAnnouncementNameByIndex = nil --/esoui/InternalIngame/MarketAnnouncement/MarketAnnouncement_Manager.lua:128:20 | name = [[ GetEventAnnouncementNameByIndex ]](i),
GetEventAnnouncementPregameImageByIndex = nil --/esoui/Pregame/CharacterSelect/ZO_CharacterSelect_Manager.lua:99:25 | image = [[ GetEventAnnouncementPregameImageByIndex ]](i),
GetEventAnnouncementRemainingTimeByIndex = nil --/esoui/InternalIngame/MarketAnnouncement/MarketAnnouncement_Manager.lua:132:29 | remainingTime = [[ GetEventAnnouncementRemainingTimeByIndex ]](i),
GetEventAnnouncementStartTimeByIndex = nil --/esoui/InternalIngame/MarketAnnouncement/MarketAnnouncement_Manager.lua:131:25 | startTime = [[ GetEventAnnouncementStartTimeByIndex ]](i),
GetEventManager = nil --/esoui/Ingame/ZO_Loot/Loot_Shared.lua:69:20 | local EvtMgr = [[ GetEventManager ]]()
GetExampleCodeForCodeRedemption = nil --/esoui/InternalIngame/Tooltip/InternalIngameTooltips.lua:9:28 | statValuePair:SetValue([[ GetExampleCodeForCodeRedemption ]](), self:GetStyle("currencyStatValuePairValue"))
GetExternalName = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_CreateLinkAccount.lua:213:50 | partnerAccount = [[ GetExternalName ]](),
GetFace = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreate_Keyboard.lua:171:79 | self.faceTriangle = CreateTriangle(self.faceTriangleControl, SetFace, [[ GetFace ]], SI_CREATE_CHARACTER_FACE_TRIANGLE_LABEL, SI_CREATE_CHARACTER_TRIANGLE_FACE_MUSCULAR, SI_CREATE_CHARACTER_TRIANGLE_FACE_FAT, SI_CREATE_CHARACTER_TRIANGLE_FACE_THIN)
GetGameCreditsEntry = nil --/esoui/Pregame/GameCredits/SharedGameCredits.lua:171:58 | local entryType, entryData, additionalData = [[ GetGameCreditsEntry ]](self.currentEntryIndex)
GetGameURL = nil --/esoui/Pregame/StateManager/PregameStateManager.lua:851:59 | errorString = zo_strformat(errorStringFormat, [[ GetGameURL ]]())
GetGamepadMarketSubscriptionBenefitLineInfo = nil --/esoui/PregameAndInternalIngame/Gamepad/EsoPlusMembershipInfoDialog_Gamepad.lua:79:44 | local lineText, headerText, icon = [[ GetGamepadMarketSubscriptionBenefitLineInfo ]](i);
GetGrammarDecoratedName = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreate_Keyboard.lua:905:76 | local genderDecoratedCharacterName = ZO_SELECTED_TEXT:Colorize([[ GetGrammarDecoratedName ]](characterName, CharacterCreateGetGender(characterMode)))
GetHexOffsetsForScryingGridDirection = nil --/esoui/InternalIngame/Scrying/Scrying.lua:657:49 | local rowOffset, columnOffset = [[ GetHexOffsetsForScryingGridDirection ]](angleDirection)
GetIngameHighestPriorityActionBindingInfoFromNameAndInputDevice = nil --/esoui/InternalIngame/Market/MarketDialogs_Shared.lua:42:45 | local key, mod1, mod2, mod3, mod4 = [[ GetIngameHighestPriorityActionBindingInfoFromNameAndInputDevice ]]("SHOW_HOUSING_PANEL", preferredKeybindType)
GetInstallationProgress = nil --/esoui/Pregame/Gamepad/DownloadBar/DownloadBar.lua:15:41 | local downloadPercentage = zo_clamp([[ GetInstallationProgress ]](), 0, TOTAL_DOWNLOAD_PERCENTAGE)
GetJerallPassMapIndex = nil --/esoui/Ingame/Map/MapPin.lua:2308:39 | or currentMapIndex == [[ GetJerallPassMapIndex ]]() then
GetKeyboardMarketSubscriptionBenefitLineInfo = nil --/esoui/InternalIngame/EsoPlusOffers/Keyboard/EsoPlusOffers.lua:138:44 | local lineText, headerText, icon = [[ GetKeyboardMarketSubscriptionBenefitLineInfo ]](i)
GetLatestActivityTeamId = nil --/esoui/Ingame/AddonCompatibilityAliases/PC/AddonCompatibilityAliases_PC.lua:269:29 | GetLatestActivityAlliance = [[ GetLatestActivityTeamId ]]
GetLegalDocContent = nil --/esoui/Pregame/AccountLogin/LegalDocsProvider.lua:69:24 | text = [[ GetLegalDocContent ]](i),
GetLegalDocTitle = nil --/esoui/Pregame/AccountLogin/LegalDocsProvider.lua:68:24 | name = [[ GetLegalDocTitle ]](i),
GetLegalDocType = nil --/esoui/Pregame/AccountLogin/LegalDocsProvider.lua:50:29 | local docType = [[ GetLegalDocType ]](i)
GetMarketAnnouncementCrownStoreLocked = nil --/esoui/InternalIngame/MarketAnnouncement/MarketAnnouncement_Manager.lua:158:12 | return [[ GetMarketAnnouncementCrownStoreLocked ]]() or self:GetNumMarketProductAnnouncements() == 0
GetMarketAnnouncementCrownStoreLockedBackground = nil --/esoui/InternalIngame/MarketAnnouncement/MarketAnnouncement_Shared.lua:142:49 | self.crownStoreLockedTexture:SetTexture([[ GetMarketAnnouncementCrownStoreLockedBackground ]]())
GetMarketAnnouncementProductDefId = nil --/esoui/InternalIngame/MarketAnnouncement/MarketAnnouncement_Manager.lua:42:35 | local productId = [[ GetMarketAnnouncementProductDefId ]](i)
GetMarketProductAnnouncementBackground = nil --/esoui/InternalIngame/MarketAnnouncement/MarketAnnouncementMarketProduct_Shared.lua:78:12 | return [[ GetMarketProductAnnouncementBackground ]](self:GetId())
GetMarketProductGamepadBackground = nil --/esoui/InternalIngame/Market/LargeSingleMarketProduct_Base.lua:33:12 | return [[ GetMarketProductGamepadBackground ]](self:GetId())
GetMarketProductIdFromCrownCrateTier = nil --/esoui/InternalIngame/Market/Market_Shared.lua:489:35 | local productId = [[ GetMarketProductIdFromCrownCrateTier ]](tierId, productIndex)
GetMarketProductKeyboardBackground = nil --/esoui/InternalIngame/Market/Keyboard/MarketClasses_Keyboard.lua:329:12 | return [[ GetMarketProductKeyboardBackground ]](self:GetId())
GetMarketProductMaxPurchaseQuantity = nil --/esoui/InternalIngame/Market/MarketProductData.lua:128:25 | local maxQuantity = [[ GetMarketProductMaxPurchaseQuantity ]](self.marketProductId)
GetMarketProductSearchResult = nil --/esoui/InternalIngame/Market/Market_Shared.lua:1091:63 | local categoryIndex, subcategoryIndex, productIndex = [[ GetMarketProductSearchResult ]](resultIndex)
GetMarketSubscriptionGamepadInfo = nil --/esoui/PublicAllIngames/Tooltip/MarketTooltips.lua:194:22 | local overview = [[ GetMarketSubscriptionGamepadInfo ]]()
GetMarketSubscriptionKeyboardInfo = nil --/esoui/InternalIngame/EsoPlusOffers/Keyboard/EsoPlusOffers.lua:131:29 | local overview, image = [[ GetMarketSubscriptionKeyboardInfo ]]()
GetMaxAllowedTributeTargets = nil --/esoui/PublicAllIngames/Tribute/TributeCardTile_Shared.lua:249:42 | local targetsRemaining = [[ GetMaxAllowedTributeTargets ]]() - GetNumTargetedTributeCards()
GetMaxCharacterDeletes = nil --/esoui/Pregame/CharacterSelect/ZO_CharacterSelect_Manager.lua:463:33 | local maxCharacterDeletes = [[ GetMaxCharacterDeletes ]]()
GetMaxTributeCardsInStack = nil --/esoui/PublicAllIngames/Tribute/TributeCard.lua:1453:33 | local maxCardsInStack = [[ GetMaxTributeCardsInStack ]]()
GetModListingAuthor = nil --/esoui/PregameAndIngame/AddOns/ModBrowserData.lua:20:12 | return [[ GetModListingAuthor ]](self.listingIndex)
GetModListingCategory = nil --/esoui/PregameAndIngame/AddOns/ModBrowserData.lua:82:12 | return [[ GetModListingCategory ]](self.listingIndex)
GetModListingDependencyInstallState = nil --/esoui/PregameAndIngame/AddOns/ModBrowserData.lua:167:12 | return [[ GetModListingDependencyInstallState ]](self.listingIndex, dependencyIndex)
GetModListingDependencyTitle = nil --/esoui/PregameAndIngame/AddOns/ModBrowserData.lua:163:12 | return [[ GetModListingDependencyTitle ]](self.listingIndex, dependencyIndex)
GetModListingDescription = nil --/esoui/PregameAndIngame/AddOns/ModBrowserData.lua:28:12 | return [[ GetModListingDescription ]](self.listingIndex)
GetModListingIgnoresUpdates = nil --/esoui/PregameAndIngame/AddOns/ModBrowserData.lua:241:16 | return [[ GetModListingIgnoresUpdates ]](self.listingIndex)
GetModListingImage = nil --/esoui/PregameAndIngame/AddOns/ModBrowserData.lua:145:12 | return [[ GetModListingImage ]](self.listingIndex, imageIndex)
GetModListingInstallState = nil --/esoui/PregameAndIngame/AddOns/ModBrowserData.lua:36:12 | return [[ GetModListingInstallState ]](self.listingIndex)
GetModListingLastUpdatedTime = nil --/esoui/PregameAndIngame/AddOns/ModBrowserData.lua:44:29 | local lastUpdatedTime = [[ GetModListingLastUpdatedTime ]](self.listingIndex)
GetModListingLatestVersion = nil --/esoui/PregameAndIngame/AddOns/ModBrowserData.lua:50:12 | return [[ GetModListingLatestVersion ]](self.listingIndex)
GetModListingNumDependencies = nil --/esoui/PregameAndIngame/AddOns/ModBrowserData.lua:149:12 | return [[ GetModListingNumDependencies ]](self.listingIndex)
GetModListingNumImages = nil --/esoui/PregameAndIngame/AddOns/ModBrowserData.lua:124:12 | return [[ GetModListingNumImages ]](self.listingIndex)
GetModListingNumUsers = nil --/esoui/PregameAndIngame/AddOns/ModBrowserData.lua:32:12 | return [[ GetModListingNumUsers ]](self.listingIndex)
GetModListingOverview = nil --/esoui/PregameAndIngame/AddOns/ModBrowserData.lua:24:12 | return [[ GetModListingOverview ]](self.listingIndex)
GetModListingReleaseCreationTime = nil --/esoui/PregameAndIngame/AddOns/ModBrowserData.lua:62:26 | local creationTime = [[ GetModListingReleaseCreationTime ]](self.listingIndex, releaseIndex)
GetModListingReleaseNote = nil --/esoui/PregameAndIngame/AddOns/ModBrowserData.lua:78:12 | return [[ GetModListingReleaseNote ]](self.listingIndex, releaseIndex)
GetModListingReleaseVersion = nil --/esoui/PregameAndIngame/AddOns/ModBrowserData.lua:58:12 | return [[ GetModListingReleaseVersion ]](self.listingIndex, releaseIndex)
GetModListingTitle = nil --/esoui/PregameAndIngame/AddOns/ModBrowserData.lua:16:12 | return [[ GetModListingTitle ]](self.listingIndex)
GetMouseOverDigCell = nil --/esoui/InternalIngame/AntiquityDigging/AntiquityDigging.lua:269:28 | SetSelectedDigCell([[ GetMouseOverDigCell ]]())
GetNextFilteredMarketProduct = nil --/esoui/InternalIngame/Market/Market_Shared.lua:1117:16 | return [[ GetNextFilteredMarketProduct ]](lastProductId, displayGroup, matchAllFilterTypes, matchAnyFilterTypes)
GetNumAffectedScryingHexes = nil --/esoui/InternalIngame/Scrying/Scrying.lua:1095:32 | for index = 1, [[ GetNumAffectedScryingHexes ]](self:GetScryingActionParameters()) do
GetNumAlliances = nil --/esoui/Pregame/CharacterCreate/ZO_CharacterCreateData.lua:31:16 | for i = 1, [[ GetNumAlliances ]]() do
GetNumAppearances = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreate_Keyboard.lua:719:20 | for i = 1, [[ GetNumAppearances ]]() do
GetNumCharacterDeletesRemaining = nil --/esoui/Pregame/Globals/PreGameDialogs.lua:159:28 | return [[ GetNumCharacterDeletesRemaining ]]() > 0
GetNumConfinedTributeCards = nil --/esoui/InternalIngame/Tribute/TributeConfinementViewer_Manager.lua:101:29 | local numConfined = [[ GetNumConfinedTributeCards ]](viewingAgentInstanceId)
GetNumCountries = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_CreateLinkAccount.lua:125:30 | local numCountries = [[ GetNumCountries ]]()
GetNumDigSpotBonusLootRewards = nil --/esoui/InternalIngame/AntiquityDigging/AntiquityDiggingSummary.lua:862:33 | local numBonusLootRewards = [[ GetNumDigSpotBonusLootRewards ]]()
GetNumEventAnnouncements = nil --/esoui/InternalIngame/MarketAnnouncement/MarketAnnouncement_Manager.lua:123:35 | local numEventAnnouncements = [[ GetNumEventAnnouncements ]]()
GetNumGameCreditsEntries = nil --/esoui/Pregame/GameCredits/SharedGameCredits.lua:197:34 | self.numCreditsEntries = [[ GetNumGameCreditsEntries ]]()
GetNumGamepadMarketSubscriptionBenefitLines = nil --/esoui/PregameAndInternalIngame/Gamepad/EsoPlusMembershipInfoDialog_Gamepad.lua:76:22 | local numLines = [[ GetNumGamepadMarketSubscriptionBenefitLines ]]()
GetNumKeyboardMarketSubscriptionBenefitLines = nil --/esoui/InternalIngame/EsoPlusOffers/Keyboard/EsoPlusOffers.lua:135:22 | local numLines = [[ GetNumKeyboardMarketSubscriptionBenefitLines ]]()
GetNumLegalDocs = nil --/esoui/Pregame/AccountLogin/LegalDocsProvider.lua:47:73 | elseif self.haveFetchedRemoteDocs and self.nextLegalDocIndex <= [[ GetNumLegalDocs ]]() then
GetNumLoadedSubsystems = nil --/esoui/Pregame/Globals/PregameGlobals.lua:15:58 | local fullyLoaded = GetNumTotalSubsystemsToLoad() == [[ GetNumLoadedSubsystems ]]()
GetNumMarketAnnouncementProducts = nil --/esoui/InternalIngame/MarketAnnouncement/MarketAnnouncement_Manager.lua:39:41 | local numAnnouncementProducts = [[ GetNumMarketAnnouncementProducts ]]()
GetNumMarketProductSearchResults = nil --/esoui/InternalIngame/Market/Market_Shared.lua:1089:24 | local numResults = [[ GetNumMarketProductSearchResults ]]()
GetNumMarketProductsInCrownCrateTier = nil --/esoui/InternalIngame/Market/Market_Shared.lua:487:33 | local numProducts = [[ GetNumMarketProductsInCrownCrateTier ]](tierId)
GetNumMaxCharacterSlotsAvailable = nil --/esoui/Pregame/CharacterSelect/ZO_CharacterSelect_Manager.lua:453:31 | local maxSlotsAvailable = [[ GetNumMaxCharacterSlotsAvailable ]]()
GetNumModListings = nil --/esoui/PregameAndIngame/AddOns/ModBrowser_Manager.lua:132:31 | for listingIndex = 1, [[ GetNumModListings ]]() do
GetNumModsWithUpdateAvailable = nil --/esoui/PregameAndIngame/AddOns/Gamepad/ModBrowser_Gamepad.lua:995:32 | local numUpdates = [[ GetNumModsWithUpdateAvailable ]](SKIP_IGNORE_UPDATES)
GetNumPlatforms = nil --/esoui/Pregame/StateManager/Gamepad/PregameStates_Gamepad.lua:116:52 | for platformIndex = 1, [[ GetNumPlatforms ]]() do
GetNumRaces = nil --/esoui/Pregame/CharacterCreate/ZO_CharacterCreateData.lua:71:16 | for i = 1, [[ GetNumRaces ]]() do
GetNumReleasesForModListing = nil --/esoui/PregameAndIngame/AddOns/ModBrowserData.lua:54:12 | return [[ GetNumReleasesForModListing ]](self.listingIndex)
GetNumRewardIdsFromLastCodeRedemption = nil --/esoui/InternalIngame/Rewards/InternalIngame_Rewards_Manager.lua:27:24 | local numRewards = [[ GetNumRewardIdsFromLastCodeRedemption ]]()
GetNumScryingGoalsAchieved = nil --/esoui/InternalIngame/Scrying/Scrying.lua:1221:8 | if [[ GetNumScryingGoalsAchieved ]]() > 0 then
GetNumScryingNormalActions = nil --/esoui/InternalIngame/Scrying/Scrying.lua:1576:45 | self.normalActionMeter:SmoothTransition([[ GetNumScryingNormalActions ]](), GetNumScryingNormalActionsLimit(), shouldAnimateInstantly)
GetNumScryingNormalActionsLimit = nil --/esoui/InternalIngame/Scrying/Scrying.lua:1576:75 | self.normalActionMeter:SmoothTransition(GetNumScryingNormalActions(), [[ GetNumScryingNormalActionsLimit ]](), shouldAnimateInstantly)
GetNumScryingSpecialActions = nil --/esoui/InternalIngame/Scrying/Scrying.lua:1580:51 | local specialActions, partialSpecialActions = [[ GetNumScryingSpecialActions ]]()
GetNumSliders = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreate_Keyboard.lua:689:20 | for i = 1, [[ GetNumSliders ]]() do
GetNumTargetableTributeCards = nil --/esoui/InternalIngame/Tribute/TributeTargetViewer_Manager.lua:77:31 | local numTargetable = [[ GetNumTargetableTributeCards ]]()
GetNumTargetedTributeCards = nil --/esoui/PublicAllIngames/Tribute/TributeCardTile_Shared.lua:249:74 | local targetsRemaining = GetMaxAllowedTributeTargets() - [[ GetNumTargetedTributeCards ]]()
GetNumTemplates = nil --/esoui/Pregame/CharacterCreate/ZO_CharacterCreateData.lua:103:20 | for i = 1, [[ GetNumTemplates ]]() do
GetNumTotalScryingHexes = nil --/esoui/InternalIngame/Scrying/Scrying.lua:751:23 | for hexIndex = 1, [[ GetNumTotalScryingHexes ]]() do
GetNumTotalSubsystemsToLoad = nil --/esoui/Pregame/Globals/PregameGlobals.lua:15:25 | local fullyLoaded = [[ GetNumTotalSubsystemsToLoad ]]() == GetNumLoadedSubsystems()
GetNumTributeCardsAtBoardLocation = nil --/esoui/InternalIngame/Tribute/TributeData.lua:72:22 | local numCards = [[ GetNumTributeCardsAtBoardLocation ]](self.boardLocation)
GetNumWorlds = nil --/esoui/Pregame/AccountLogin/Keyboard/WorldSelect.lua:71:23 | local numWorlds = [[ GetNumWorlds ]]()
GetNumberConsoleFriends = nil --/esoui/Ingame/Group/Gamepad/ZO_GroupMenu_Gamepad.lua:255:43 | if ZO_IsConsoleOrGameCoreUI() and [[ GetNumberConsoleFriends ]]() > 0 then
GetOnlineIdForActiveProfile = nil --/esoui/Common/ZO_SaveLoadDialog/ZO_SaveLoadDialog.lua:321:21 | local profile = [[ GetOnlineIdForActiveProfile ]]()
GetPhysique = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreate_Keyboard.lua:168:91 | self.physiqueTriangle = CreateTriangle(self.physiqueTriangleControl, SetPhysique, [[ GetPhysique ]], SI_CREATE_CHARACTER_BODY_TRIANGLE_LABEL, SI_CREATE_CHARACTER_TRIANGLE_MUSCULAR, SI_CREATE_CHARACTER_TRIANGLE_FAT, SI_CREATE_CHARACTER_TRIANGLE_THIN)
GetPlatformInfo = nil --/esoui/Pregame/StateManager/Gamepad/PregameStates_Gamepad.lua:117:54 | local platformName = [[ GetPlatformInfo ]](platformIndex)
GetRaceInfo = nil --/esoui/Pregame/CharacterCreate/ZO_CharacterCreateData.lua:72:144 | local raceDef, lore, alliance, normalIcon, pressedIcon, mouseoverIcon, position, isSelectable, gamepadNormalIcon, gamepadPressedIcon = [[ GetRaceInfo ]](i)
GetRaceRestrictionReason = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreate_Keyboard.lua:1231:64 | local restrictionReasonFunction = raceSelector and [[ GetRaceRestrictionReason ]] or GetClassRestrictionReason
GetRewardIdFromLastCodeRedemption = nil --/esoui/InternalIngame/Rewards/InternalIngame_Rewards_Manager.lua:29:26 | local rewardId = [[ GetRewardIdFromLastCodeRedemption ]](rewardIndex)
GetRootScryingHexIndex = nil --/esoui/InternalIngame/Scrying/Scrying.lua:747:77 | self.rootHexRow, self.rootHexColumn = GetScryingHexCoordinatesFromIndex([[ GetRootScryingHexIndex ]]())
GetSavedVariablesDiskUsageMBForModListing = nil --/esoui/PregameAndIngame/AddOns/ModBrowserData.lua:227:16 | return [[ GetSavedVariablesDiskUsageMBForModListing ]](self.listingIndex)
GetScryingActiveSkillAbilityId = nil --/esoui/InternalIngame/Scrying/Scrying.lua:316:26 | self.abilityId = [[ GetScryingActiveSkillAbilityId ]](self.activeSkill)
GetScryingBoardSize = nil --/esoui/InternalIngame/Scrying/Scrying.lua:767:33 | local numRows, numColumns = [[ GetScryingBoardSize ]]()
GetScryingHexCoordinatesFromIndex = nil --/esoui/InternalIngame/Scrying/Scrying.lua:16:33 | self.row, self.column = [[ GetScryingHexCoordinatesFromIndex ]](hexIndex)
GetScryingHexIndexFromCoordinates = nil --/esoui/InternalIngame/Scrying/Scrying.lua:956:22 | local hexIndex = [[ GetScryingHexIndexFromCoordinates ]](row, column)
GetScryingHexState = nil --/esoui/InternalIngame/Scrying/Scrying.lua:97:22 | self.state = [[ GetScryingHexState ]](self.hexIndex)
GetScryingHexType = nil --/esoui/InternalIngame/Scrying/Scrying.lua:96:24 | self.hexType = [[ GetScryingHexType ]](self.hexIndex)
GetScryingLastAffectedLineActionInfo = nil --/esoui/InternalIngame/Scrying/Scrying.lua:595:48 | local direction, endHexIndex = [[ GetScryingLastAffectedLineActionInfo ]]()
GetSecureSetting = nil --/esoui/PregameAndIngame/OptionsPanels/OptionsPanel_Account_Shared.lua:31:16 | return [[ GetSecureSetting ]](SETTING_TYPE_ACCOUNT, ACCOUNT_SETTING_ACCOUNT_EMAIL)
GetSecureSetting_Bool = nil --/esoui/PregameAndIngame/OptionsPanels/OptionsPanel_Account_Shared.lua:124:24 | return [[ GetSecureSetting_Bool ]](control.data.system, control.data.settingId)
GetSelectedDigCell = nil --/esoui/InternalIngame/AntiquityDigging/AntiquityDigging.lua:238:49 | local selectedRow, selectedColumn = [[ GetSelectedDigCell ]]()
GetSelectedPlatformIndex = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_Login.lua:126:51 | local url = select(5, GetPlatformInfo([[ GetSelectedPlatformIndex ]]()))
GetServerAlertMessage = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_Login.lua:151:48 | local serverAlertMessage = success and [[ GetServerAlertMessage ]]()
GetServerNoticeMessage = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_Login.lua:159:53 | local serverNoticeMessage = success and [[ GetServerNoticeMessage ]]()
GetSkuPricingInfoWithTax = nil --/esoui/PublicAllIngames/TamrielTomes/TamrielTomesData.lua:415:8 | if [[ GetSkuPricingInfoWithTax ]] then
GetSkuPricingInfoWithTaxFormatted = nil --/esoui/PublicAllIngames/TamrielTomes/TamrielTomesData.lua:423:8 | if [[ GetSkuPricingInfoWithTaxFormatted ]] then
GetSliderInfo = nil --/esoui/Pregame/CharacterCreate/ZO_CharacterCreateSlider_Base.lua:127:27 | value = select(4, [[ GetSliderInfo ]](self.sliderIndex))
GetTargetableTributeCardInstanceIdByIndex = nil --/esoui/InternalIngame/Tribute/TributeTargetViewer_Manager.lua:79:36 | local cardInstanceId = [[ GetTargetableTributeCardInstanceIdByIndex ]](targetableIndex)
GetTemplateInfo = nil --/esoui/Pregame/CharacterCreate/ZO_CharacterCreateData.lua:104:104 | local templateDef, name, race, class, gender, alliance, overrideAppearance, isSelectable = [[ GetTemplateInfo ]](i)
GetTemplateSkipsTutorial = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreate_Keyboard.lua:899:39 | local templateSkipsTutorial = [[ GetTemplateSkipsTutorial ]](currentTemplateId)
GetTemplateStatus = nil --/esoui/Pregame/CharacterCreate/ZO_CharacterCreateData.lua:92:49 | local templatesAllowed, templatesRequired = [[ GetTemplateStatus ]]()
GetTotalModDiskCapacityMB = nil --/esoui/PregameAndIngame/AddOns/Gamepad/ZO_AddOnManager_Gamepad.lua:102:38 | local maxDiskUsage = [[ GetTotalModDiskCapacityMB ]]()
GetTotalModDiskUsageMB = nil --/esoui/PregameAndIngame/AddOns/Gamepad/ZO_AddOnManager_Gamepad.lua:101:42 | local currentDiskUsage = [[ GetTotalModDiskUsageMB ]]()
GetTributeBoardSurfaceTransform = nil --/esoui/InternalIngame/Tribute/Tribute.lua:1211:117 | local renderPositionX, renderPositionY, renderPositionZ, rotationXRadians, rotationYRadians, rotationZRadians = [[ GetTributeBoardSurfaceTransform ]]()
GetTributeCardInstanceBoardLocation = nil --/esoui/InternalIngame/Tribute/Tribute.lua:745:39 | local boardLocation = [[ GetTributeCardInstanceBoardLocation ]](cardInstanceId)
GetTributeCardInstanceDefIds = nil --/esoui/InternalIngame/Tribute/TributeData.lua:75:34 | local cardId, patronId = [[ GetTributeCardInstanceDefIds ]](instanceId)
GetTributeCardInstanceDefeatCost = nil --/esoui/PublicAllIngames/Tribute/TributeCard.lua:852:41 | resourceType, currentQuantity = [[ GetTributeCardInstanceDefeatCost ]](self.cardInstanceId)
GetTributeCardInstanceIdAtBoardLocation = nil --/esoui/InternalIngame/Tribute/TributeData.lua:74:28 | local instanceId = [[ GetTributeCardInstanceIdAtBoardLocation ]](self.boardLocation, index)
GetTributeCardInstanceOwner = nil --/esoui/InternalIngame/Tribute/TributeMechanic_Manager.lua:1137:36 | local ownerPlayerPerspective = [[ GetTributeCardInstanceOwner ]](cardInstanceId)
GetTributeCardPositionInPile = nil --/esoui/PublicAllIngames/Tribute/TributeCard.lua:1148:56 | local cardIndexInPile, numCardsInPile, isStacked = [[ GetTributeCardPositionInPile ]](self.cardInstanceId)
GetTributeCardStateFlags = nil --/esoui/PublicAllIngames/Tribute/TributeCard.lua:760:30 | self:OnStateFlagsChanged([[ GetTributeCardStateFlags ]](cardInstanceId))
GetTributeDiscardCountTransformInfo = nil --/esoui/InternalIngame/Tribute/Tribute.lua:1646:117 | local renderPositionX, renderPositionY, renderPositionZ, rotationXRadians, rotationYRadians, rotationZRadians = [[ GetTributeDiscardCountTransformInfo ]](self.perspective)
GetTributePatronDraftTurnTimerWarningThreshold = nil --/esoui/InternalIngame/Tribute/TributePatronSelection_Shared.lua:36:40 | self.turnTimerWarningThresholdMs = [[ GetTributePatronDraftTurnTimerWarningThreshold ]]()
GetTributePatronTabIconTransformInfo = nil --/esoui/InternalIngame/Tribute/TributePatronStall.lua:211:117 | local renderPositionX, renderPositionY, renderPositionZ, rotationXRadians, rotationYRadians, rotationZRadians = [[ GetTributePatronTabIconTransformInfo ]](self.patronDraftId)
GetTributePatronUsageCountDisplayTransformInfo = nil --/esoui/InternalIngame/Tribute/Tribute.lua:1224:115 | renderPositionX, renderPositionY, renderPositionZ, rotationXRadians, rotationYRadians, rotationZRadians = [[ GetTributePatronUsageCountDisplayTransformInfo ]](perspective)
GetTributeResourceDisplayTransformInfo = nil --/esoui/InternalIngame/Tribute/Tribute.lua:1217:119 | renderPositionX, renderPositionY, renderPositionZ, rotationXRadians, rotationYRadians, rotationZRadians = [[ GetTributeResourceDisplayTransformInfo ]](perspective, resource)
GetTributeTargetSelectionMechanicInfo = nil --/esoui/InternalIngame/Tribute/TributeTargetViewer_Manager.lua:124:96 | local mechanicType, quantity, param1, param2, param3, targetingFormatterOverrideText = [[ GetTributeTargetSelectionMechanicInfo ]]()
GetTributeTargetSelectionRequirementInfo = nil --/esoui/InternalIngame/Tribute/TributeTargetViewer_Manager.lua:127:91 | local requirementType, quantity, param1, param2, targetingFormatterOverrideText = [[ GetTributeTargetSelectionRequirementInfo ]]()
GetTributeTurnTimerLabelTransformInfo = nil --/esoui/InternalIngame/Tribute/Tribute.lua:1229:111 | renderPositionX, renderPositionY, renderPositionZ, rotationXRadians, rotationYRadians, rotationZRadians = [[ GetTributeTurnTimerLabelTransformInfo ]]()
GetTributeTurnTimerWarningThreshold = nil --/esoui/InternalIngame/Tribute/Tribute.lua:1169:40 | self.turnTimerWarningThresholdMs = [[ GetTributeTurnTimerWarningThreshold ]]()
GetUserEmailAddress = nil --/esoui/PregameAndIngame/OptionsPanels/Gamepad/OptionsPanel_Account_Gamepad.lua:126:40 | self.enteredText = [[ GetUserEmailAddress ]]()
GetUserPendingActivationEmailAddress = nil --/esoui/Ingame/Globals/Console/IngameDialogs_Console.lua:47:90 | return zo_strformat(SI_ACCOUNT_MANAGEMENT_ACTIVATION_EMAIL_SENT_DIALOG_BODY, [[ GetUserPendingActivationEmailAddress ]]());
GetWorldInfo = nil --/esoui/Pregame/AccountLogin/Keyboard/WorldSelect.lua:73:40 | local worldName, worldStatus = [[ GetWorldInfo ]](worldIndex)
GiftMarketProduct = nil --/esoui/InternalIngame/Market/MarketProductData.lua:302:5 | [[ GiftMarketProduct ]](self.marketProductId, self.presentationIndex, purchaseQuantity, giftMessage, recipientDisplayName)
GuiMouse = nil --/esoui/Ingame/Map/WorldMap.lua:6060:57 | tooltipControl:SetAnchor(RIGHT, [[ GuiMouse ]], LEFT, -32, 0)
HandleScryingAction = nil --/esoui/InternalIngame/Scrying/Scrying.lua:1209:9 | [[ HandleScryingAction ]](self:GetScryingActionParameters())
HasActivatedEmailInPregame = nil --/esoui/PregameAndIngame/OptionsPanels/OptionsPanel_Account_Shared.lua:21:16 | return [[ HasActivatedEmailInPregame ]]()
HasActivatedEmailOnConsole = nil --/esoui/PregameAndIngame/OptionsPanels/OptionsPanel_Account_Shared.lua:23:16 | return [[ HasActivatedEmailOnConsole ]]()
HasAgreedToPEGI = nil --/esoui/Pregame/StateManager/PregameStateManager.lua:167:61 | if DoesPlatformRequirePregamePEGI() and not [[ HasAgreedToPEGI ]]() then
HasZoneStoriesData = nil --/esoui/InternalIngame/MarketAnnouncement/MarketAnnouncement_Shared.lua:274:8 | if [[ HasZoneStoriesData ]](zoneId) and not IsZoneStoryComplete(zoneId) then
HidePlatformStoreIcon = nil --/esoui/Ingame/TamrielTomes/TamrielTomes_Manager.lua:62:12 | if [[ HidePlatformStoreIcon ]] then
InitializeAppearanceFromTemplate = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreate_Keyboard.lua:380:9 | [[ InitializeAppearanceFromTemplate ]](templateId)
InstallModListing = nil --/esoui/PregameAndIngame/AddOns/ModBrowserData.lua:203:9 | [[ InstallModListing ]](self.listingIndex)
InteractWithTributeBoard = nil --/esoui/InternalIngame/Tribute/Tribute.lua:257:25 | [[ InteractWithTributeBoard ]]()
InteractWithTributeCard = nil --/esoui/InternalIngame/Tribute/Tribute.lua:255:25 | [[ InteractWithTributeCard ]](object:GetCardInstanceId())
IsAccountLoggedIn = nil --/esoui/Pregame/StateManager/PregameStateManager.lua:934:16 | elseif not [[ IsAccountLoggedIn ]]() or IS_WORLD_SELECT_STATE[currentState] then -- While in world select, we're logged in but haven't yet started the character loading process
IsAdditionalContentDownloading = nil --/esoui/Pregame/AccountLogin/Gamepad/GameStartup_Gamepad.lua:320:16 | if not [[ IsAdditionalContentDownloading ]](ADDITIONAL_CONTENT_TYPE_VO) then
IsAdditionalContentUpToDate = nil --/esoui/Pregame/AccountLogin/Gamepad/GameStartup_Gamepad.lua:319:12 | if not [[ IsAdditionalContentUpToDate ]](ADDITIONAL_CONTENT_TYPE_VO) or GetCVar("SelectedEnglishVOLanguage") == "1" then
IsConnectedToLobby = nil --/esoui/Pregame/AccountLogin/Keyboard/WorldSelect.lua:118:54 | if (GetWorldName() ~= worldData.name) or not [[ IsConnectedToLobby ]]() then
IsConsoleCommunicationRestricted = nil --/esoui/Common/Console/ZO_PlayerConsoleRequestsUtils.lua:138:8 | if [[ IsConsoleCommunicationRestricted ]]() then
IsDeprioritizedInAnnouncements = nil --/esoui/InternalIngame/Market/MarketProductData.lua:276:12 | return [[ IsDeprioritizedInAnnouncements ]](self.marketProductId)
IsDiggingActiveSkillUpgraded = nil --/esoui/InternalIngame/AntiquityDigging/AntiquityDigging.lua:357:20 | if [[ IsDiggingActiveSkillUpgraded ]](skill) then
IsDiggingAntiquityUnearthed = nil --/esoui/InternalIngame/AntiquityDigging/AntiquityDigging.lua:21:16 | if [[ IsDiggingAntiquityUnearthed ]]() then
IsEditCharacterDifferentFromSelectionCharacter = nil --/esoui/Pregame/CharacterCreate/ZO_CharacterCreate_Shared.lua:553:8 | if [[ IsEditCharacterDifferentFromSelectionCharacter ]]() then
IsEligibleForEsoPlusPricing = nil --/esoui/InternalIngame/Market/MarketDialogs_Shared.lua:22:8 | if [[ IsEligibleForEsoPlusPricing ]]() then
IsErrorQueuedFromIngame = nil --/esoui/Pregame/StateManager/PregameStateManager.lua:836:12 | if not [[ IsErrorQueuedFromIngame ]]() then
IsGateInstalled = nil --/esoui/Pregame/AccountLogin/Gamepad/GameStartup_Gamepad.lua:342:93 | local isDownloading = IsAdditionalContentDownloading(ADDITIONAL_CONTENT_TYPE_VO) or not [[ IsGateInstalled ]]("BaseGame")
IsGuiShaderLoaded = nil --/esoui/Pregame/StateManager/Gamepad/PregameStates_Gamepad.lua:25:20 | return [[ IsGuiShaderLoaded ]]()
IsInJerallPass = nil --/esoui/Ingame/Map/WorldMap.lua:5354:12 | if [[ IsInJerallPass ]]() then
IsInWerewolfForm = nil --/esoui/Ingame/AddonCompatibilityAliases/PC/AddonCompatibilityAliases_PC.lua:731:12 | return [[ IsInWerewolfForm ]]() and not skillLineData:IsWerewolf()
IsLocalTributePlayersTurn = nil --/esoui/InternalIngame/Tribute/TributeMechanic_Manager.lua:1129:44 | local isLocalPlayersTurn = [[ IsLocalTributePlayersTurn ]]()
IsMarketProductPartiallyPurchased = nil --/esoui/InternalIngame/Market/MarketProductData.lua:207:12 | return [[ IsMarketProductPartiallyPurchased ]](self.marketProductId)
IsModListingImageReady = nil --/esoui/PregameAndIngame/AddOns/ModBrowserData.lua:128:12 | return [[ IsModListingImageReady ]](self.listingIndex, imageIndex)
IsModListingReleaseNoteReady = nil --/esoui/PregameAndIngame/AddOns/ModBrowserData.lua:68:12 | return [[ IsModListingReleaseNoteReady ]](self.listingIndex, releaseIndex)
IsOnESOPlusFreeTrial = nil --/esoui/InternalIngame/Market/Market_Manager.lua:272:12 | if [[ IsOnESOPlusFreeTrial ]]() then
IsPregameCharacterConstructionReady = nil --/esoui/Pregame/StateManager/PregameStateManager.lua:68:62 | if not ZO_PREGAME_FIRED_CHARACTER_CONSTRUCTION_READY and [[ IsPregameCharacterConstructionReady ]]() and ZO_PREGAME_CHARACTER_LIST_RECEIVED then
IsPreloginWorldFullyLoaded = nil --/esoui/Pregame/StateManager/PregameStateManager.lua:22:12 | return [[ IsPreloginWorldFullyLoaded ]]() or not ZO_IsPreloginWorldEnabled() or not IsInGamepadPreferredMode()
IsScryingActiveSkillUnlocked = nil --/esoui/InternalIngame/Scrying/Scrying.lua:309:16 | if not [[ IsScryingActiveSkillUnlocked ]](self.activeSkill) then
IsScryingActiveSkillUpgraded = nil --/esoui/InternalIngame/Scrying/Scrying.lua:1468:20 | if [[ IsScryingActiveSkillUpgraded ]](skill) then
IsScryingActiveSkillUsable = nil --/esoui/InternalIngame/Scrying/Scrying.lua:321:16 | elseif [[ IsScryingActiveSkillUsable ]](self.activeSkill) == SCRYING_ACTIVE_SKILL_USE_RESULT_SUCCESS then
IsScryingHexGoal = nil --/esoui/InternalIngame/Scrying/Scrying.lua:98:59 | self.isGoal, self.hasGoalBeenPreviouslyAchieved = [[ IsScryingHexGoal ]](self.hexIndex)
IsSystemLoaded = nil --/esoui/Pregame/StateManager/PregameStateManager.lua:121:20 | return [[ IsSystemLoaded ]](LOADING_SYSTEM_GAME_DATA)
IsTributeCardConfined = nil --/esoui/PublicAllIngames/Tribute/TributeCard.lua:1229:8 | if [[ IsTributeCardConfined ]](self:GetCardInstanceId()) then
IsTributeTargetSelectionAutoComplete = nil --/esoui/InternalIngame/Tribute/TributeTargetViewer_Shared.lua:58:28 | return not [[ IsTributeTargetSelectionAutoComplete ]]()
IsUsingLinkedLogin = nil --/esoui/Pregame/StateManager/Keyboard/PregameStates_Keyboard.lua:171:16 | if [[ IsUsingLinkedLogin ]]() then
IsValidAccountName = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_CreateLinkAccount.lua:323:37 | local accountNameViolations = { [[ IsValidAccountName ]](requestedAccountName) }
IsValidCharacterName = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreate_Keyboard.lua:1102:30 | local nameViolations = { [[ IsValidCharacterName ]](nameText) }
LoadPlatformsList = nil --/esoui/Pregame/AccountLogin/Gamepad/GameStartup_Gamepad.lua:130:80 | CREATE_LINK_LOADING_SCREEN_GAMEPAD:Show("WaitForPreloginWorld", function() [[ LoadPlatformsList ]](self.selectedServerChoice) end, GetString(SI_GAMEPAD_PREGAME_LOADING))
LoadString = nil --/esoui/Libraries/Globals/globalapi.lua:25:23 | zo_loadstring       = [[ LoadString ]]
MenuEntryTemplateEquality = nil --/esoui/Common/Carousel/Carousel_Shared.lua:19:137 | ZO_HorizontalScrollList_Gamepad.Initialize(self, control, template, NUM_VISIBLE_CATEGORIES, function(...) self:EntrySetup(...) end, [[ MenuEntryTemplateEquality ]])
MockOpenStreamingInstallLanguageChunkPlatformDialogResult = nil --/esoui/Pregame/Globals/PreGameDialogs.lua:1631:17 | [[ MockOpenStreamingInstallLanguageChunkPlatformDialogResult ]](PLATFORM_DIALOG_RESULT_OK)
MoveCameraToCurrentCharacter = nil --/esoui/Pregame/StateManager/PregameStateManager.lua:942:9 | [[ MoveCameraToCurrentCharacter ]]()
MoveCharacterCameraZoomAmount = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreate_Gamepad.lua:1656:21 | [[ MoveCharacterCameraZoomAmount ]](1)
OpenStreamingInstallLanguageChunkPlatformDialog = nil --/esoui/Pregame/AccountLogin/Gamepad/GameStartup_Gamepad.lua:297:21 | [[ OpenStreamingInstallLanguageChunkPlatformDialog ]]()
OverlayConfirmSkipInstruction = nil --/esoui/Overlay/Overlay.lua:46:29 | ClearConfirmationUpdate([[ OverlayConfirmSkipInstruction ]])
PlayDiggingMouseClickEffect = nil --/esoui/InternalIngame/AntiquityDigging/AntiquityDigging.lua:242:17 | [[ PlayDiggingMouseClickEffect ]]()
PlayerLeftDiggingEarly = nil --/esoui/InternalIngame/AntiquityDigging/AntiquityDigging.lua:150:32 | local fanfareDelayMs = [[ PlayerLeftDiggingEarly ]]() and ANTIQUITY_DIGGING_FANFARE_SHORT_DELAY_MS or ANTIQUITY_DIGGING_FANFARE_LONG_DELAY_MS
PregameAttemptResendVerificationEmail = nil --/esoui/Pregame/Globals/PreGameDialogs.lua:1048:17 | [[ PregameAttemptResendVerificationEmail ]]()
PregameBeginLinkedLogin = nil --/esoui/Pregame/StateManager/Gamepad/PregameStates_Gamepad.lua:249:81 | CREATE_LINK_LOADING_SCREEN_GAMEPAD:Show("WaitForPreloginWorld", [[ PregameBeginLinkedLogin ]], GetString(SI_GAMEPAD_PREGAME_LOADING))
PregameCreateAccount = nil --/esoui/Pregame/StateManager/Gamepad/PregameStates_Gamepad.lua:311:17 | [[ PregameCreateAccount ]]()
PregameDisconnect = nil --/esoui/Pregame/StateManager/PregameStateManager.lua:481:13 | [[ PregameDisconnect ]]()
PregameDisconnectOnLuaError = nil --/esoui/Pregame/StateManager/PregameStateManager.lua:733:5 | [[ PregameDisconnectOnLuaError ]]()
PregameHasProfileSelected = nil --/esoui/Pregame/AccountLogin/Gamepad/PregameInitialScreen_Gamepad.lua:248:20 | if not [[ PregameHasProfileSelected ]]() then
PregameLinkAccount = nil --/esoui/Pregame/StateManager/Gamepad/PregameStates_Gamepad.lua:409:21 | [[ PregameLinkAccount ]](username, password)
PregameLogin = nil --/esoui/Pregame/StateManager/PregameStateManager.lua:62:13 | [[ PregameLogin ]](acctName, acctPwd)
PregameLogout = nil --/esoui/Pregame/StateManager/Keyboard/PregameStates_Keyboard.lua:75:13 | [[ PregameLogout ]]()
PregamePrepareForProfile = nil --/esoui/Pregame/StateManager/Gamepad/PregameStates_Gamepad.lua:101:13 | [[ PregamePrepareForProfile ]]()
PregameQuit = nil --/esoui/Pregame/Globals/PreGameDialogs.lua:864:29 | [[ PregameQuit ]]()
PregameSelectProfile = nil --/esoui/Pregame/StateManager/Gamepad/PregameStates_Gamepad.lua:132:21 | [[ PregameSelectProfile ]]()
PregameSetAccountCreationInfo = nil --/esoui/Pregame/StateManager/Gamepad/PregameStates_Gamepad.lua:310:17 | [[ PregameSetAccountCreationInfo ]](email, emailSignup, country, requestedAccountName)
PreventEnergySustainabilityFrameCap = nil --/esoui/Ingame/Scenes/IngameFragments.lua:898:9 | [[ PreventEnergySustainabilityFrameCap ]](true)
PreviewAppearanceValue = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreateSlider_Keyboard.lua:267:5 | [[ PreviewAppearanceValue ]](self.category)
RefreshBillingAndSkuInfo = nil --/esoui/InternalIngame/DirectPurchase/Keyboard/DirectPurchaseInternalDialogs_Keyboard.lua:83:9 | [[ RefreshBillingAndSkuInfo ]](FORCE_REFRESH)
RegisterForLinkAccountActivationProgress = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_CreateLinkAccount.lua:112:13 | [[ RegisterForLinkAccountActivationProgress ]]()
ReinstallModListing = nil --/esoui/PregameAndIngame/AddOns/ModBrowserData.lua:215:9 | [[ ReinstallModListing ]](self.listingIndex)
ReportModListing = nil --/esoui/PregameAndIngame/AddOns/ModBrowserData.lua:247:12 | return [[ ReportModListing ]](self.listingIndex, reportSource, reportReason, comment)
RequestAlert = nil --/esoui/InternalIngame/Market/Keyboard/Market_Keyboard.lua:1069:9 | [[ RequestAlert ]](UI_ALERT_CATEGORY_ERROR, SOUNDS.NEGATIVE_CLICK, GetString(SI_MARKET_PREVIEW_ERROR_CANNOT_JUMP_FROM_LOCATION))
RequestAnnouncements = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_Login.lua:273:9 | [[ RequestAnnouncements ]]()
RequestCharacterDataForFriend = nil --/esoui/Ingame/Contacts/Gamepad/FriendsList_Gamepad.lua:203:17 | [[ RequestCharacterDataForFriend ]](entryData.displayName)
RequestCharacterList = nil --/esoui/Pregame/StateManager/PregameStateManager.lua:92:13 | [[ RequestCharacterList ]]()
RequestConsoleTextValidation = nil --/esoui/Common/Console/ZO_PlayerConsoleInfoRequestManager.lua:141:29 | validationKey = [[ RequestConsoleTextValidation ]](text),
RequestDebugPrintText = nil --/esoui/Libraries/Globals/DebugUtils.lua:8:12 | elseif [[ RequestDebugPrintText ]] then
RequestLinkAccountActivationCode = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_LoginManager.lua:109:5 | [[ RequestLinkAccountActivationCode ]]()
RequestLoadModListingDependencies = nil --/esoui/PregameAndIngame/AddOns/ModBrowserData.lua:158:9 | [[ RequestLoadModListingDependencies ]](self.listingIndex)
RequestLoadModListingImage = nil --/esoui/PregameAndIngame/AddOns/ModBrowserData.lua:139:13 | [[ RequestLoadModListingImage ]](self.listingIndex, imageIndex, width, height)
RequestLoadModListingReleaseNote = nil --/esoui/PregameAndIngame/AddOns/ModBrowserData.lua:73:9 | [[ RequestLoadModListingReleaseNote ]](self.listingIndex, releaseIndex)
RequestModsSearch = nil --/esoui/PregameAndIngame/AddOns/ModBrowser_Manager.lua:118:26 | local searchId = [[ RequestModsSearch ]]()
RequestReadTextOverVoiceChat = nil --/esoui/Ingame/VoiceChat/Console/VoiceChatTranscript_Gamepad.lua:139:17 | [[ RequestReadTextOverVoiceChat ]](self.textEdit:GetText())
RequestRedeemCode = nil --/esoui/InternalIngame/CodeRedemption/Gamepad/CodeRedemption_Gamepad.lua:205:8 | if [[ RequestRedeemCode ]](data.code) then
RequestResendAccountEmailVerification = nil --/esoui/PregameAndIngame/OptionsPanels/OptionsPanel_Account_Shared.lua:57:17 | [[ RequestResendAccountEmailVerification ]]()
RequestRespondToScryingExit = nil --/esoui/InternalIngame/Scrying/Scrying.lua:1692:21 | [[ RequestRespondToScryingExit ]](ACCEPT)
RequestRevealAntiquityDigSitesOnMap = nil --/esoui/InternalIngame/Scrying/Scrying.lua:1528:9 | [[ RequestRevealAntiquityDigSitesOnMap ]](GetScryingCurrentAntiquityId())
RequestShowCodexForDigSpotAntiquity = nil --/esoui/InternalIngame/AntiquityDigging/AntiquityDiggingSummary.lua:1035:5 | [[ RequestShowCodexForDigSpotAntiquity ]]()
RequestShowGamepadChapterUpgrade = nil --/esoui/InternalIngame/ChapterUpgrade/ChapterUpgradeUtils.lua:6:9 | [[ RequestShowGamepadChapterUpgrade ]](chapterUpgradeId)
RequestShowGiftInventory = nil --/esoui/InternalIngame/Globals/MarketDialogs.lua:192:17 | [[ RequestShowGiftInventory ]]()
RequestShowSpecificHelp = nil --/esoui/InternalIngame/Market/MarketDialogs_Shared.lua:3:5 | [[ RequestShowSpecificHelp ]](helpCategory, helpIndex)
RequestSocialListForActiveProfile = nil --/esoui/Ingame/Contacts/Gamepad/FriendsList_Gamepad.lua:94:39 | if ZO_IsConsoleOrGameCoreUI() and [[ RequestSocialListForActiveProfile ]] then
RequestWorldList = nil --/esoui/Pregame/StateManager/Keyboard/PregameStates_Keyboard.lua:102:13 | [[ RequestWorldList ]]()
ResendGift = nil --/esoui/InternalIngame/Gifting/Keyboard/ConfirmSendGift_Keyboard.lua:110:21 | [[ ResendGift ]](data.giftId, noteText, recipientDisplayName)
SavePlayerConsoleProfile = nil --/esoui/Libraries/Utility/ZO_PlatformUtils.lua:80:39 | if ZO_IsConsoleOrGameCoreUI() and [[ SavePlayerConsoleProfile ]] ~= nil then
SaveSettings = nil --/esoui/Pregame/AccountLogin/Gamepad/GameStartup_Gamepad.lua:918:25 | [[ SaveSettings ]]()
SelectCharacterForPlay = nil --/esoui/Pregame/StateManager/PregameStateManager.lua:762:9 | [[ SelectCharacterForPlay ]](charId, loadOption)
SelectCharacterToView = nil --/esoui/Pregame/CharacterSelect/ZO_CharacterSelect_Manager.lua:289:13 | [[ SelectCharacterToView ]](selectedCharacterData.index)
SelectClothing = nil --/esoui/Pregame/CharacterCreate/ZO_CharacterCreate_Shared.lua:210:5 | [[ SelectClothing ]](DRESSING_OPTION_YOUR_GEAR_AND_COLLECTIBLES)
SelectWorld = nil --/esoui/Pregame/StateManager/Gamepad/PregameStates_Gamepad.lua:470:17 | [[ SelectWorld ]](worldIndex)
SendOneTimePassword = nil --/esoui/Pregame/Globals/PreGameDialogs.lua:795:29 | [[ SendOneTimePassword ]](ZO_Dialogs_GetEditBoxText(dialog))
SetAppearanceValue = nil --/esoui/Pregame/CharacterCreate/ZO_CharacterCreateSlider_Base.lua:179:5 | [[ SetAppearanceValue ]](self.category, value)
SetCanMockDownloadContent = nil --/esoui/Pregame/Globals/PreGameDialogs.lua:1668:17 | [[ SetCanMockDownloadContent ]](true)
SetCharacterCameraZoomAmount = nil --/esoui/Pregame/StateManager/PregameStateManager.lua:182:13 | [[ SetCharacterCameraZoomAmount ]](-1) -- zoom all the way out when leaving this state
SetCharacterManagerMode = nil --/esoui/Pregame/CharacterCreate/ZO_CharacterCreate_Shared.lua:172:5 | [[ SetCharacterManagerMode ]](characterMode)
SetFace = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreate_Keyboard.lua:171:70 | self.faceTriangle = CreateTriangle(self.faceTriangleControl, [[ SetFace ]], GetFace, SI_CREATE_CHARACTER_FACE_TRIANGLE_LABEL, SI_CREATE_CHARACTER_TRIANGLE_FACE_MUSCULAR, SI_CREATE_CHARACTER_TRIANGLE_FACE_FAT, SI_CREATE_CHARACTER_TRIANGLE_FACE_THIN)
SetGuiReadyForWorld = nil --/esoui/Pregame/StateManager/Gamepad/PregameStates_Gamepad.lua:51:13 | [[ SetGuiReadyForWorld ]]()
SetHighlightedDiggingActiveSkill = nil --/esoui/InternalIngame/AntiquityDigging/AntiquityDigging.lua:270:9 | [[ SetHighlightedDiggingActiveSkill ]](GetMouseOverDiggingActiveSkill())
SetHighlightedTributeCard = nil --/esoui/InternalIngame/Tribute/Tribute.lua:1072:13 | [[ SetHighlightedTributeCard ]](NO_CARD)
SetHighlightedTributePatron = nil --/esoui/InternalIngame/Tribute/Gamepad/TributePatronSelection_Gamepad.lua:100:13 | [[ SetHighlightedTributePatron ]](self.currentDraftId)
SetHighlightedTributeResource = nil --/esoui/InternalIngame/Tribute/Tribute.lua:1074:13 | [[ SetHighlightedTributeResource ]](NO_RESOURCE)
SetModBrowserCategoryTypeFilter = nil --/esoui/PregameAndIngame/AddOns/ModBrowser_Manager.lua:64:27 | success = success and [[ SetModBrowserCategoryTypeFilter ]](unpack(self.categories))
SetModBrowserSearchType = nil --/esoui/PregameAndIngame/AddOns/ModBrowser_Manager.lua:62:27 | success = success and [[ SetModBrowserSearchType ]](self.searchType)
SetModBrowserTextFilter = nil --/esoui/PregameAndIngame/AddOns/ModBrowser_Manager.lua:63:27 | success = success and [[ SetModBrowserTextFilter ]](self.searchText)
SetModListingIgnoresUpdates = nil --/esoui/PregameAndIngame/AddOns/ModBrowserData.lua:235:9 | [[ SetModListingIgnoresUpdates ]](self.listingIndex, ignoreUpdates)
SetOpenMarketSource = nil --/esoui/InternalIngame/Market/Market_Shared.lua:265:5 | [[ SetOpenMarketSource ]](openSource)
SetPhysique = nil --/esoui/Pregame/CharacterCreate/Keyboard/ZO_CharacterCreate_Keyboard.lua:168:78 | self.physiqueTriangle = CreateTriangle(self.physiqueTriangleControl, [[ SetPhysique ]], GetPhysique, SI_CREATE_CHARACTER_BODY_TRIANGLE_LABEL, SI_CREATE_CHARACTER_TRIANGLE_MUSCULAR, SI_CREATE_CHARACTER_TRIANGLE_FAT, SI_CREATE_CHARACTER_TRIANGLE_THIN)
SetSecureRenderModeEnabled = nil --/esoui/InternalIngame/Market/Market_Shared.lua:82:5 | [[ SetSecureRenderModeEnabled ]](true)
SetSecureSetting = nil --/esoui/Pregame/OptionsPanels/Keyboard/OptionsPanel_Account_Keyboard.lua:36:21 | [[ SetSecureSetting ]](SETTING_TYPE_ACCOUNT, ACCOUNT_SETTING_ACCOUNT_EMAIL, newEmailEdit:GetText())
SetSelectedDigCell = nil --/esoui/InternalIngame/AntiquityDigging/AntiquityDigging.lua:269:9 | [[ SetSelectedDigCell ]](GetMouseOverDigCell())
SetSelectedDiggingActiveSkill = nil --/esoui/InternalIngame/AntiquityDigging/AntiquityDigging.lua:235:13 | [[ SetSelectedDiggingActiveSkill ]](mouseOverSkill)
SetSelectedPlatform = nil --/esoui/Pregame/StateManager/Gamepad/PregameStates_Gamepad.lua:119:37 | [[ SetSelectedPlatform ]](platformIndex)
SetSliderValue = nil --/esoui/Pregame/CharacterCreate/ZO_CharacterCreateSlider_Base.lua:37:9 | [[ SetSliderValue ]](self.sliderIndex, value)
SetSuppressCharacterChanges = nil --/esoui/Pregame/CharacterCreate/ZO_CharacterCreate_Shared.lua:102:13 | [[ SetSuppressCharacterChanges ]](true)
SetTributeAutoPlayEnabled = nil --/esoui/InternalIngame/Tribute/Tribute.lua:1141:9 | [[ SetTributeAutoPlayEnabled ]](autoPlayChecked)
SetTributeCardHidden = nil --/esoui/PublicAllIngames/Tribute/TributeCard.lua:1413:9 | [[ SetTributeCardHidden ]](self.cardInstanceId, alpha < 1)
SetTributeGamepadCursorControl = nil --/esoui/InternalIngame/Tribute/Tribute.lua:1167:5 | [[ SetTributeGamepadCursorControl ]](self.gamepadCursorControl)
SetTributeInputStyle = nil --/esoui/InternalIngame/Tribute/Tribute.lua:1047:13 | [[ SetTributeInputStyle ]](gamepadInputStyle == TRIBUTE_INPUT_STYLE_GAMEPAD and gamepadInputStyle or mouseInputStyle)
SetUsePreloginWorld = nil --/esoui/Pregame/StateManager/PregameStateManager.lua:19:1 | [[ SetUsePreloginWorld ]](ZO_IsPreloginWorldEnabled())
ShouldAttemptAutoLogin = nil --/esoui/Pregame/AccountLogin/Keyboard/ZO_Login.lua:453:8 | if [[ ShouldAttemptAutoLogin ]]() and not ZO_PREGAME_HAD_GLOBAL_ERROR then
ShouldLoadPublicTags = nil --/esoui/Ingame/BuildMarkupTest/BuildMarkupTest.lua:3:8 | if not [[ ShouldLoadPublicTags ]] or ShouldLoadPublicTags() == false then
ShowConsoleAddFriendDialog = nil --/esoui/Common/Console/ZO_PlayerConsoleRequestsUtils.lua:26:9 | [[ ShowConsoleAddFriendDialog ]](displayName, consoleId)
ShowConsoleIgnoreDialog = nil --/esoui/Common/Console/ZO_PlayerConsoleRequestsUtils.lua:46:9 | [[ ShowConsoleIgnoreDialog ]](displayName, consoleId)
ShowConsoleRedeemCodeUI = nil --/esoui/Common/Globals/SharedDialogs.lua:197:21 | [[ ShowConsoleRedeemCodeUI ]]()
ShowCredits = nil --/esoui/Pregame/GameCredits/SharedGameCredits.lua:192:5 | [[ ShowCredits ]]()
ShowDailyLoginScene = nil --/esoui/PublicAllIngames/Tile/DailyRewardsTile.lua:120:39 | if [[ ShowDailyLoginScene ]] then -- called from the announcement panel (internal ingame)
ShowGamerCard = nil --/esoui/Common/Console/ZO_PlayerConsoleRequestsUtils.lua:5:9 | [[ ShowGamerCard ]](undecoratedName, consoleId)
ShowMarketAnnouncements = nil --/esoui/Ingame/Scenes/UISystemManager.lua:137:13 | [[ ShowMarketAnnouncements ]]()
ShowPlatformESOGameClientUI = nil --/esoui/Pregame/Globals/Console/PreGameDialogs_Console.lua:25:16 | [[ ShowPlatformESOGameClientUI ]]()
ShowPlatformStoreIcon = nil --/esoui/Ingame/TamrielTomes/TamrielTomes_Manager.lua:69:12 | if [[ ShowPlatformStoreIcon ]] and SYSTEMS:IsShowing("tamrielTomesPurchase") then
ShowSelectFromUserListDialog = nil --/esoui/Common/Console/ZO_PlayerConsoleInfoRequestManager.lua:133:9 | [[ ShowSelectFromUserListDialog ]](titleText or "", includeOnlineFriends, includeOfflineFriends)
ShowXboxAccountPicker = nil --/esoui/Pregame/AccountLogin/Gamepad/GameStartup_Gamepad.lua:531:17 | [[ ShowXboxAccountPicker ]]()
ShowZoneStoriesScene = nil --/esoui/InternalIngame/ZoneStories/ZoneStoriesTile.lua:31:9 | [[ ShowZoneStoriesScene ]](data.zoneId)
StartDiggingTransitionToNextDay = nil --/esoui/InternalIngame/AntiquityDigging/AntiquityDiggingSummary.lua:572:13 | [[ StartDiggingTransitionToNextDay ]]()
StartMarketProductSearch = nil --/esoui/InternalIngame/Market/Market_Shared.lua:1064:29 | self.searchTaskId = [[ StartMarketProductSearch ]](self:GetDisplayGroup(), searchString)
StartPregameMusic = nil --/esoui/Pregame/AccountLogin/Gamepad/PregameInitialScreen_Gamepad.lua:65:13 | [[ StartPregameMusic ]]()
StartScryingOutro = nil --/esoui/InternalIngame/Scrying/Scrying.lua:1517:9 | [[ StartScryingOutro ]]()
StopCharacterCameraZoom = nil --/esoui/Pregame/CharacterCreate/Gamepad/ZO_CharacterCreate_Gamepad.lua:1653:17 | [[ StopCharacterCameraZoom ]]()
StopCredits = nil --/esoui/Pregame/GameCredits/SharedGameCredits.lua:207:5 | [[ StopCredits ]]()
SuppressWorldList = nil --/esoui/Pregame/StateManager/PregameStateManager.lua:125:13 | [[ SuppressWorldList ]]()
ToggleShowPregameGui = nil --/esoui/Pregame/StateManager/PregameStateManager.lua:552:12 | if [[ ToggleShowPregameGui ]] then
TributeCanCancelCurrentMove = nil --/esoui/InternalIngame/Tribute/TributeTargetViewer_Manager.lua:35:24 | return [[ TributeCanCancelCurrentMove ]]()
TributeCancelCurrentMove = nil --/esoui/InternalIngame/Tribute/TributeTargetViewer_Manager.lua:32:17 | [[ TributeCancelCurrentMove ]]()
TributeChooseMechanic = nil --/esoui/InternalIngame/Tribute/TributeMechanicSelector.lua:76:9 | [[ TributeChooseMechanic ]](self.mechanicIndex)
TributeConcede = nil --/esoui/InternalIngame/Tribute/Tribute.lua:503:21 | [[ TributeConcede ]]()
TributeConfirmTargetSelection = nil --/esoui/InternalIngame/Tribute/TributeTargetViewer_Shared.lua:42:17 | [[ TributeConfirmTargetSelection ]]()
TributeExitResponse = nil --/esoui/InternalIngame/Tribute/Tribute.lua:522:13 | [[ TributeExitResponse ]](ACCEPT)
TrySaveCharacterListOrder = nil --/esoui/Pregame/StateManager/Keyboard/PregameStates_Keyboard.lua:36:13 | [[ TrySaveCharacterListOrder ]]()
UninstallModListing = nil --/esoui/PregameAndIngame/AddOns/ModBrowserData.lua:209:9 | [[ UninstallModListing ]](self.listingIndex, deleteSavedVariables)
UnlockGamepads = nil --/esoui/Pregame/AccountLogin/Gamepad/PregameInitialScreen_Gamepad.lua:181:9 | [[ UnlockGamepads ]]()
UpdateAllInstalledMods = nil --/esoui/PregameAndIngame/AddOns/Gamepad/ModBrowser_Gamepad.lua:1006:13 | [[ UpdateAllInstalledMods ]]()
UpdateMarketAnnouncement = nil --/esoui/InternalIngame/MarketAnnouncement/MarketAnnouncement_Shared.lua:144:9 | [[ UpdateMarketAnnouncement ]]()
UseDiggingActiveSkillOnSelectedCell = nil --/esoui/InternalIngame/AntiquityDigging/AntiquityDigging.lua:240:17 | [[ UseDiggingActiveSkillOnSelectedCell ]](selectedSkill)
VoiceChatChannelJoin = nil --/esoui/Ingame/VoiceChat/Console/ZO_VoiceChat_Manager.lua:526:5 | [[ VoiceChatChannelJoin ]](channel.channelName)
VoiceChatChannelLeave = nil --/esoui/Ingame/VoiceChat/Console/ZO_VoiceChat_Manager.lua:560:5 | [[ VoiceChatChannelLeave ]](channel.channelName)
VoiceChatChannelTransmit = nil --/esoui/Ingame/VoiceChat/Console/ZO_VoiceChat_Manager.lua:543:5 | [[ VoiceChatChannelTransmit ]](channel.channelName)
VoiceChatGetChannelInfo = nil --/esoui/AppAndIngame/VoiceChatHUD/Console/ZO_VoiceChatHUD.lua:95:51 | local channelType, guildId, guildRoomNumber = [[ VoiceChatGetChannelInfo ]](channelName)
VoiceChatGetChannels = nil --/esoui/Ingame/VoiceChat/Console/ZO_VoiceChat_Manager.lua:278:13 | [[ VoiceChatGetChannels ]]()
VoiceChatGetMutedPlayerDisplayName = nil --/esoui/Ingame/VoiceChat/Console/ZO_VoiceChat_Manager.lua:568:29 | local displayName = [[ VoiceChatGetMutedPlayerDisplayName ]](i)
VoiceChatGetNumberMutedPlayers = nil --/esoui/Ingame/VoiceChat/Console/ZO_VoiceChat_Manager.lua:566:27 | local numMutedUsers = [[ VoiceChatGetNumberMutedPlayers ]]()
VoiceChatGetTransmitChannelType = nil --/esoui/Ingame/VoiceChat/Console/ZO_VoiceChat_Manager.lua:295:37 | local transmitChannelType = [[ VoiceChatGetTransmitChannelType ]]()
VoiceChatRequestChannelUsers = nil --/esoui/Ingame/VoiceChat/Console/ZO_VoiceChat_Manager.lua:261:17 | [[ VoiceChatRequestChannelUsers ]](channel.channelName)
WillConcedeCausePenalty = nil --/esoui/InternalIngame/Tribute/Keyboard/TributeDialogs_Keyboard.lua:47:16 | if [[ WillConcedeCausePenalty ]]() then
WriteToInterfaceLog = nil --/esoui/Libraries/Globals/DebugUtils.lua:244:9 | [[ WriteToInterfaceLog ]](string.format("Lua mem profile '%s' result: %.3f kb", tag, deltaKB))

-- 10. Global XML defined controls/fonts --
AbilityIconTooltip = nil --/esoui/Ingame/EndlessDungeon/Keyboard/EndlessDungeonBuffSelector_Keyboard.lua:76:23 | InitializeTooltip([[ AbilityIconTooltip ]], self.control, RIGHT, -5, 0, LEFT)
AbilityTooltip = nil --/esoui/Ingame/Skills/ActionBarAssignmentManager.lua:428:12 | return [[ AbilityTooltip ]]
AchievementTooltip = nil --/esoui/Ingame/Achievements/Keyboard/Achievements.lua:1065:27 | InitializeTooltip([[ AchievementTooltip ]], self.control, BOTTOM, 0, -5, TOP)
AntiquityTooltip = nil --/esoui/Ingame/Antiquities/Keyboard/AntiquityJournal_Keyboard.lua:242:31 | InitializeTooltip([[ AntiquityTooltip ]], self.control, TOPLEFT, 0, 5, BOTTOMLEFT)
ChampionGamepadStarTooltip = nil --/esoui/Ingame/Champion/Champion.lua:174:31 | self.gamepadStarTooltip = [[ ChampionGamepadStarTooltip ]]
ChampionSkillTooltip = nil --/esoui/Ingame/Champion/ChampionStar.lua:360:36 | self:InitializeKeyboardTooltip([[ ChampionSkillTooltip ]])
ComparativeAbilityTooltip1 = nil --/esoui/Ingame/Crafting/Keyboard/ScribingLayout_Keyboard.lua:479:27 | InitializeTooltip([[ ComparativeAbilityTooltip1 ]], AbilityTooltip, TOPRIGHT, -5, 0, TOPLEFT)
ComparativeTooltip1 = nil --/esoui/Ingame/Inventory/InventorySlot.lua:2691:53 | ZO_PlayShowAnimationOnComparisonTooltip([[ ComparativeTooltip1 ]])
ComparativeTooltip2 = nil --/esoui/Ingame/Inventory/InventorySlot.lua:2692:53 | ZO_PlayShowAnimationOnComparisonTooltip([[ ComparativeTooltip2 ]])
GameStartup_GamepadMiddlePane = nil --/esoui/Pregame/AccountLogin/Gamepad/GameStartup_Gamepad.lua:205:58 | self.announcementFragment = ZO_FadeSceneFragment:New([[ GameStartup_GamepadMiddlePane ]])
GameStartup_Gamepad_ServerAlert = nil --/esoui/Pregame/AccountLogin/Gamepad/GameStartup_Gamepad.lua:206:57 | self.serverAlertFragment = ZO_FadeSceneFragment:New([[ GameStartup_Gamepad_ServerAlert ]])
GameTooltip = nil --/esoui/Ingame/Stats/Keyboard/ZO_StatEntry_Keyboard.lua:180:23 | InitializeTooltip([[ GameTooltip ]], control, control.mouseOverAnchor, control.mouseOverOffsetX)
GroupFinderGroupListingTooltip = nil --/esoui/Ingame/GroupFinder/Keyboard/GroupFinder_ApplicationList_Keyboard.lua:22:27 | InitializeTooltip([[ GroupFinderGroupListingTooltip ]], self.myListingControl, RIGHT, -15, 0, LEFT)
HelpOverlayModal = nil --/esoui/Ingame/Scenes/Keyboard/KeyboardIngameFragmentGroups.lua:33:62 | local helpModalUnderlayFragment = ZO_SimpleSceneFragment:New([[ HelpOverlayModal ]])
InformationTooltip = nil --/esoui/Common/ZO_UIErrors/ErrorFrame.lua:565:23 | InitializeTooltip([[ InformationTooltip ]], control, LEFT, 0, 0, RIGHT)
ItemTooltip = nil --/esoui/Ingame/Inventory/InventorySlot.lua:2256:26 | return true, [[ ItemTooltip ]]
KeepUpgradeTooltip = nil --/esoui/Ingame/Map/Keyboard/WorldMapKeepUpgrade_Keyboard.lua:31:23 | InitializeTooltip([[ KeepUpgradeTooltip ]], control, TOPLEFT, 5, 0)
NarrowTooltip = nil --/esoui/PublicAllIngames/Tribute/TributeCard.lua:1200:25 | local control = [[ NarrowTooltip ]]
PopupTooltip = nil --/esoui/Ingame/Scenes/IngameSceneManager.lua:603:8 | if [[ PopupTooltip ]] and not PopupTooltip:IsControlHidden() then
ServiceTooltip = nil --/esoui/Pregame/CharacterSelect/Keyboard/ZO_CharacterSelect_Keyboard.lua:731:20 | self.tooltip = [[ ServiceTooltip ]]
SkillTooltip = nil --/esoui/Ingame/Skills/ActionBarAssignmentManager.lua:284:12 | return [[ SkillTooltip ]]
SmallKeyMarkupInformationTooltip = nil --/esoui/Ingame/PromotionalEvents/Keyboard/PromotionalEvents_Keyboard.lua:151:27 | InitializeTooltip([[ SmallKeyMarkupInformationTooltip ]])
