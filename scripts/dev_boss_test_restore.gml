/// dev_boss_test_restore(after room load)
var _after=argument0, _dg=global.DevBossTest_checkpoint;
for (var _row=0; _row<ds_grid_height(_dg); _row++)
{
    var _phase=_dg[#4,_row];
    if ((_after && _phase==0) || (!_after && _phase==2)) continue;
    var _owner=_dg[#0,_row], _name=_dg[#1,_row];
    var _kind=_dg[#2,_row], _value=_dg[#3,_row];
    if (_kind==0)
    {
        if (_owner==-1) variable_global_set(_name,_value);
        else variable_instance_set(_owner,_name,_value);
    }
    else
    {
        if (_owner==-1) var _handle=variable_global_get(_name);
        else _handle=variable_instance_get(_owner,_name);
        switch (_kind)
        {
            case 1: ds_map_clear(_handle); ds_map_read(_handle,_value); break;
            case 2: ds_list_clear(_handle); ds_list_read(_handle,_value); break;
            case 3: ds_grid_read(_handle,_value); break;
        }
    }
}
