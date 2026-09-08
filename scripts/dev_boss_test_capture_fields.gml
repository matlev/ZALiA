/// dev_boss_test_capture_fields(owner, names, kind, restore phase)
// Private checkpoint helper. owner=-1 means global. kind: 0 scalar, 1 map,
// 2 list, 3 grid. phase: 0 before room load, 1 both, 2 after PC_spawn.
// Explicit fields avoid confusing a numeric stat with a DS handle in GMS 1.4.
var _owner=argument0, _names=argument1+" ", _kind=argument2, _phase=argument3;
var _dg=global.DevBossTest_checkpoint;
while (string_length(_names)>0)
{
    var _pos=string_pos(" ",_names);
    var _name=string_copy(_names,1,_pos-1);
    _names=string_delete(_names,1,_pos);
    if (_name=="") continue;
    if (_owner==-1)
    {
        if (!variable_global_exists(_name)) continue;
        var _value=variable_global_get(_name);
    }
    else
    {
        if (!variable_instance_exists(_owner,_name)) continue;
        _value=variable_instance_get(_owner,_name);
    }
    if (is_undefined(_value)) continue;
    switch (_kind)
    {
        case 1: _value=ds_map_write(_value); break;
        case 2: _value=ds_list_write(_value); break;
        case 3: _value=ds_grid_write(_value); break;
    }
    var _row=ds_grid_height(_dg);
    ds_grid_resize(_dg,5,_row+1);
    _dg[#0,_row]=_owner;
    _dg[#1,_row]=_name;
    _dg[#2,_row]=_kind;
    _dg[#3,_row]=_value;
    _dg[#4,_row]=_phase;
}
