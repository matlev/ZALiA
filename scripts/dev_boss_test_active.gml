/// dev_boss_test_active()
// Also safe before OptionsMenu_Create (save preferences are loaded at startup).
if (!variable_global_exists("DevBossTest_stage")) return false;
return global.DevBossTest_stage != 0;
