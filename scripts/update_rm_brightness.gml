/// update_rm_brightness()


var _BRIGHTNESS_PREV = g.rm_brightness;


var _SCENE_IS_RANDO = global.SceneRando_enabled && g.rm_name!=val(f.dm_rando[?dk_SceneRando+STR_Scene+STR_Randomized+g.rm_name], g.rm_name);
// Test entry skips approach torches, sometimes outside the locked arena.
// Do not apply this while the original room is being restored (stages 4/5).
var _BOSS_TEST_LIT = false;
if (dev_boss_test_active())
    _BOSS_TEST_LIT = global.DevBossTest_stage==2 || global.DevBossTest_stage==3;
if (_BOSS_TEST_LIT || pal_rm_dark_idx<0
||  (_SCENE_IS_RANDO && global.SceneRando_scene_brightness_control==1) ) // global.SceneRando_scene_brightness_control: 1: All dark scenes during scene rando are max brightness. 2: Use dark scene setting of vanilla scene
{
    set_rm_brightness(g.RM_BRIGHTNESS_MAX);
}
else if(!g.EnterRoom_SpawnGO_timer)
{
    set_rm_brightness(0);
    
    if (f.items&ITM_CAND) set_rm_brightness(g.rm_brightness+1);
    
    if (g.rm_brightness<g.RM_BRIGHTNESS_MAX)
    {
        with(GameObject)
        {
            if(!state 
            || !brightness )
            {
                continue;//with(GameObject)
            }
            
            set_rm_brightness(g.rm_brightness+brightness);
            if (g.rm_brightness>=g.RM_BRIGHTNESS_MAX) break;//with(GameObject)
        }
    }
}


if (g.rm_brightness!=_BRIGHTNESS_PREV)
{
    tile_hidden_update_2a(); // updates all tg(tile graphic) ids
    
    if (g.rm_brightness<g.RM_BRIGHTNESS_MAX)
    {
        update_Pallete_1b(); // update dark pal
    }
}




