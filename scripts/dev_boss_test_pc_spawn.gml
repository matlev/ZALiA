/// dev_boss_test_pc_spawn() -- AFTER normal PC_spawn, PC context
if (!dev_boss_test_active()) exit;
if (global.DevBossTest_stage==5)
{
    // Spawn callbacks can mark exploration/progression. Put the original data
    // back a second time, but NEVER reset spawn permissions after actors exist.
    dev_boss_test_restore(true);
    is_fairy=pc_is_fairy();
    is_cucco=pc_is_cucco();
    PC_update_1a();
    set_xy(id,global.DevBossTest_x,global.DevBossTest_y);
    set_camera_xy(global.DevBossTest_view_x,global.DevBossTest_view_y);
    g.EnterRoom_control_timer=0;
    g.pc_lock=0;
    state=state_NORMAL;
    updateCSPoints();
    PC_update_hitboxes_1a();
    ds_grid_destroy(global.DevBossTest_checkpoint);
    global.DevBossTest_checkpoint=-1;
    global.DevBossTest_stage=0;
    show_debug_message("BOSS TEST: original Link and progression restored; room reloaded.");
    exit;
}
if (global.DevBossTest_stage!=2) exit;
var _intro=is_ancestor(global.DevBossTest_object,Ganon)
    || global.DevBossTest_object==ShadowLonk01;
Disguise_enabled=false;
is_dead=false;
if (!_intro) g.EnterRoom_control_timer=0;
g.pc_lock=0;
g.spells_active=0;
g.StatRestore_timer_hp=0;
g.StatRestore_timer_mp=0;
g.boss_stun_timer=0;
set_xy(id,spawn_xl+ww_,spawn_yt+hh_);
if (!_intro)
{
    set_camera_xy(x-viewW_(),y-viewH_());
    g.view_dir_x=1;
}
var _dk=global.DevBossTest_spawn;
var _obj=global.DevBossTest_object;
var _ver=val(g.dm_spawn[?_dk+STR_Version],1);
// Automatic spawns are filtered; construct this exact registered version once.
g.dm_spawn[?_dk+STR_Spawn_Permission]=1;
global.DevBossTest_allow_spawn=true;
var _boss=GameObject_create(val(g.dm_spawn[?_dk+"_x"]),
    val(g.dm_spawn[?_dk+"_y"]),_obj,_ver,_dk);
global.DevBossTest_allow_spawn=false;
if (!instance_exists(_boss))
{
    dev_boss_test_return("selected boss could not spawn");
    exit;
}
global.DevBossTest_stage=3;
global.DevBossTest_boss=_boss;
with (_boss)
{
    switch (object_index)
    {
        case Ganon1:
            // Satisfy the normal summoning trigger, then let its full intro run.
            ds_list_add(g.dl_spell_history,SPL_SUMM);
            break;
        case Ganon2:
        case Ganon3:
        case ShadowLonk01:
            // Their existing intro / scene controller owns battle setup.
            break;
        default:
            Boss_update_start();
            break;
    }

}
updateCSPoints();
PC_update_hitboxes_1a();
