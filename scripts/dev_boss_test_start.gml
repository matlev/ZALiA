/// dev_boss_test_start(row) -- OptionsMenu context
if (!DEV || dev_boss_test_active()) return false;
if (!ds_exists(global.DevBossTest_checkpoint,ds_type_grid)) return false;
OptionsMenu_BossHero_load();
var _r=argument0;
global.DevBossTest_spawn=BossTest_dg[#1,_r];
global.DevBossTest_scene=BossTest_dg[#2,_r];
global.DevBossTest_exit=BossTest_dg[#3,_r];
global.DevBossTest_object=BossTest_dg[#4,_r];
global.DevBossTest_quest=BossTest_quest;
global.DevBossTest_allow_spawn=false;
global.DevBossTest_stage=1; // Original room still owns its state until Room End.
sub_state=sub_state_IDLE_CLOSED;
g.gui_state=g.gui_state_NONE;
// Read canonical dimensions without letting the currently loaded randomizer
// replace the selected scene before its state has been checkpointed.
var _file=g.dm_rm[?global.DevBossTest_scene+dk_FileName+STR_Quest+hex_str(BossTest_quest)];
// Match g_Room_Start: quest 2 uses quest 1 tiles unless an override exists.
if (is_undefined(_file))
    _file=g.dm_rm[?global.DevBossTest_scene+dk_FileName+STR_Quest+"01"];
var _w=val(global.dm_scene_wh[?_file+STR_Width]);
var _h=val(global.dm_scene_wh[?_file+STR_Height]);
// This script runs on OptionsMenu; the configurable action-room alias belongs to g.
room_goto_(g.rmA_ACTION,_w,_h);
return true;
