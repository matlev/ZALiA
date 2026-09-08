/// dev_boss_test_catalog(quest) -- OptionsMenu context
// Use loaded registration data, including SceneData01.txt, not a second scene table.
ds_grid_resize(BossTest_dg,5,0);
var _quest=argument0;
var _objects=ds_list_create();
// data_go_prop1 registers each object's resource index here. Discover Boss
// descendants from that registry; new boss types need no selector allowlist.
var _suffix=STR_Object+STR_Idx;
var _suffix_len=string_length(_suffix);
var _key=ds_map_find_first(g.dm_go_prop);
repeat (ds_map_size(g.dm_go_prop))
{
    if (is_string(_key))
    {
        if (string_copy(_key,string_length(_key)-_suffix_len+1,_suffix_len)==_suffix)
        {
            var _registered=g.dm_go_prop[?_key];
            if (object_exists(_registered))
            {
                if (is_ancestor(_registered,Boss) && _registered!=Rebonack01B)
                    ds_list_add(_objects,_registered);
                // Rebonack's rider is spawned by the mounted phase, not a test.
            }
        }
    }
    _key=ds_map_find_next(g.dm_go_prop,_key);
}
// Resource order is stable and independent of DS-map traversal order.
ds_list_sort(_objects,true);
for (var _o=0; _o<ds_list_size(_objects); _o++)
{
    var _obj=_objects[|_o], _name=object_get_name(_obj);
    if (_quest==1 && is_ancestor(_obj,Ganon)) continue;
    var _count=val(g.dm_spawn[?_name+STR_Count]);
    for (var _s=1; _s<=_count; _s++)
    {
        var _dk=g.dm_spawn[?_name+hex_str(_s)+STR_Spawn+STR_Datakey];
        if (!is_string(_dk)) continue;
        var _qualified=g.dm_spawn[?_dk+STR_Qualified+STR_Quest+STR_Nums];
        if (is_string(_qualified) && !string_pos(hex_str(_quest),_qualified)) continue;
        // Ganon3 also has a transit/cutscene spawn. Only Phase00 is the fight.
        var _transit=false;
        if (_obj==Ganon3)
        {
            for (var _d=1; _d<=$F; _d++)
            {
                var _data=g.dm_spawn[?_dk+STR_Data+hex_str(_d)];
                if (is_string(_data) && string_pos(STR_Phase,_data))
                    _transit=(_data!=STR_Phase+"00");
            }
        }
        if (_transit) continue;
        var _scene=g.dm_spawn[?_dk+STR_Rm+STR_Name];
        var _exit=g.dm_rm[?_scene+STR_Exit+"01"+STR_Name];
        var _dungeon=g.dm_dungeon[?STR_Dungeon+hex_str(get_dungeon_num(_scene))+STR_Name];
        if (is_string(_dungeon))
        {
            var _preferred=g.dm_rm[?_dungeon+STR_Boss+STR_Scene+STR_Entrance+STR_Exit];
            if (is_string(_preferred))
                if (get_exit_rm_name(_preferred)==_scene) _exit=_preferred;
        }
        // Ganon1 registers its floor-hole exit first. Enter from the left,
        // as in normal play, rather than spawning at the bottom of the pit.
        if (_obj==Ganon1)
        {
            var _exit_count=val(g.dm_rm[?_scene+STR_Exit+STR_Count]);
            for (var _e=1; _e<=_exit_count; _e++)
            {
                var _candidate=g.dm_rm[?_scene+STR_Exit+hex_str(_e)+STR_Name];
                if (is_string(_candidate))
                {
                    if (val(g.dm_rm[?_candidate+STR_Num])&g.EXIT_DIR_LEFT)
                    {
                        _exit=_candidate;
                        break;
                    }
                }
            }
        }
        if (!is_string(_exit)) continue;
        var _label=string_upper(val(g.dm_go_prop[?_name+dk_FullName],_name));
        switch (_obj)
        {
            // Display exceptions only; this is not a list of supported types.
            case Rebonack01A: _label="REBONACK"; break;
            case ShadowLonk01: _label="SHADOW LINK"; break;
            case Ganon1: _label="GANON P1 - FLOOR"; break;
            case Ganon2: _label="GANON P2"; break;
            case Ganon3: _label="GANON P3"; break;
        }
        var _ver=val(g.dm_spawn[?_dk+STR_Version],1);
        if (_obj==Carock01 && _ver==2) _label="CAROCK - PENDANT CAVE";
        else if (_obj==Rebonack01A && _ver==2) _label="REBONACK - DARK KNIGHT";
        else if (!is_ancestor(_obj,Ganon))
            _label+=" - PALACE "+string(get_dungeon_num(_scene));
        var _r=ds_grid_height(BossTest_dg);
        ds_grid_resize(BossTest_dg,5,_r+1);
        BossTest_dg[#0,_r]=_label;
        BossTest_dg[#1,_r]=_dk;
        BossTest_dg[#2,_r]=_scene;
        BossTest_dg[#3,_r]=_exit;
        BossTest_dg[#4,_r]=_obj;
    }
}
ds_list_destroy(_objects);
