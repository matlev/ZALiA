/// dev_boss_test_return(reason)
if (!dev_boss_test_active()) return false;
if (global.DevBossTest_stage>=4) return true;
show_debug_message("BOSS TEST: return requested - "+argument0);
global.DevBossTest_stage=4;
// Leave test state intact for its own Room End cleanup. Restore at Room Start.
room_goto_(global.DevBossTest_room,global.DevBossTest_view_w,global.DevBossTest_view_h);
return true;
