/// room_goto_(room, *width, *height)

// Leaving the arena (including pits/warps) cancels the test. The return
// itself has already changed stage to 4 and uses the ordinary room loader.
if (dev_boss_test_active() && (global.DevBossTest_stage==2 || global.DevBossTest_stage==3))
{
    dev_boss_test_return("arena exit");
    exit;
}


var                                  _view_w = g.VIEW_W;
if (argument_count>1 && argument[1]) _view_w = clamp(argument[1], 1<<8,4<<8);

var                                  _view_h = g.VIEW_H;
if (argument_count>2 && argument[2]) _view_h = clamp(argument[2], 1<<8,4<<8);

show_debug_message("room_goto_(). "+room_get_name(argument[0]));
room_set_view_(argument[0], _view_w,_view_h);
room_goto(     argument[0]);




