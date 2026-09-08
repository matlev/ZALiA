/// dev_boss_test_defeated(boss instance)
// RebonackA losing its mounted HP is a phase change, not completion. Its
// RebonackB rider carries the same spawn key and ends the entire encounter.
if (!dev_boss_test_active()) return false;
if (global.DevBossTest_stage!=3) return false;
var _boss=argument0;
if (!instance_exists(_boss)) return false;
if (_boss.object_index==Rebonack01A) return false;
if (!is_ancestor(_boss.object_index,Boss)) return false;
if (_boss.dk_spawn!=global.DevBossTest_spawn) return false;
return dev_boss_test_return("boss encounter completed");
