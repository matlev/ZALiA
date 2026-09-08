/// dev_boss_test_spawn_xy() -- after set_pc_spawn_xy
if (!dev_boss_test_active()) exit;
if (global.DevBossTest_stage==5)
{
    global.pc.spawn_xl=global.DevBossTest_x-global.pc.ww_;
    global.pc.spawn_yt=global.DevBossTest_y-global.pc.hh_;
}
else if (global.DevBossTest_stage==2)
{
    // Preserve the ordinary entry position for fights whose intro moves Link.
    if (is_ancestor(global.DevBossTest_object,Ganon)
    || global.DevBossTest_object==ShadowLonk01) exit;
    var _dk=global.DevBossTest_spawn;
    var _x=val(g.dm_spawn[?_dk+STR_Arena+"_x"],g.rm_w_);
    var _y=val(g.dm_spawn[?_dk+"_y"]);
    // Center the arena's vertical page, rather than an entrance at its edge.
    _y=(_y div PAGE_H)*PAGE_H+(PAGE_H>>1);
    _y=clamp(_y,cam_yt_min()+viewH_(),cam_yb_max()-viewH_());
    global.pc.spawn_xl=_x-global.pc.ww_;
    global.pc.spawn_yt=_y-global.pc.hh_;
}
