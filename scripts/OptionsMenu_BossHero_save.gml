/// OptionsMenu_BossHero_save() -- persist preferences, never live progress
if (dev_boss_test_active() || !BossHero_dirty) exit;
var _dm=ds_map_create();
for (var _i=0; _i<27; _i++)
    _dm[?BossHero_dg[#0,_i]]=BossHero_dg[#1,_i];
set_saved_value(f.file_num,"_DevBossTest_HeroStats_v1",json_encode(_dm));
ds_map_destroy(_dm);
// Options was checkpointed before editing preferences. Keep its encoded-file
// cache current so return cannot resurrect the old preference in memory.
var _checkpoint=global.DevBossTest_checkpoint;
if (ds_exists(_checkpoint,ds_type_grid))
{
    for (_i=0; _i<ds_grid_height(_checkpoint); _i++)
    {
        if (_checkpoint[#0,_i]==-1 && _checkpoint[#1,_i]=="dm_save_file_data")
            _checkpoint[#3,_i]=ds_map_write(global.dm_save_file_data);
    }
}
BossHero_dirty=false;
