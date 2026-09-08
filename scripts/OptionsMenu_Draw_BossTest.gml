/// OptionsMenu_Draw_BossTest(y)
var _y=argument0+4, _h=sprite_get_height(FONT2), _line=_h+4;
var _count=ds_grid_height(BossTest_dg);
// Reserve two lines for encounter identity and the escape reminder.
var _rows=max(1,((MenuWindow_yb-_y) div _line)-3);
var _first=max(0,BossTest_cursor-_rows+1);
for (var _i=_first; _i<min(_first+_rows,_count+3); _i++)
{
    var _text="BACK";
    if (_i==0) _text="HERO STATS";
    else if (_i==1) _text="QUEST "+string(BossTest_quest)+"  < CHANGE >";
    else if (_i<=_count+1) _text=BossTest_dg[#0,_i-2];
    var _pi=PI_MENU2;
    if (_i==BossTest_cursor) _pi=PI_MENU1;
    draw_text_(TextArea1_xl,_y,_text,FONT2,_pi);
    if (_i==BossTest_cursor)
        draw_sprite_(Cursor_SPRITE,0,Cursor_xl+(Cursor_W>>1),_y+(_h>>1),PI_MENU1);
    _y+=_line;
}
_y+=4;
if (BossTest_cursor>1 && BossTest_cursor<=_count+1)
{
    var _dk=BossTest_dg[#1,BossTest_cursor-2];
    var _text=string_upper(BossTest_dg[#2,BossTest_cursor-2])+"  V"+string(val(g.dm_spawn[?_dk+STR_Version],1));
    draw_text_(TextArea1_xl,_y,_text,FONT2,PI_MENU2);
}
draw_text_(TextArea1_xl,_y+_line,"ESC / OPTIONS: END TEST",FONT2,PI_MENU2);
