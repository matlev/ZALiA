/// OptionsMenu_Draw_BossHero(y)
// Same item sprites/palettes and draw_pc_skin poses as the randomizer.
var _top=argument0, _left=TextArea1_xl, _right=TextArea2_xr;
var _line=min(12,max(8,(MenuWindow_yb-_top-100) div 11));
var _step=(_right-_left-8)/14;
for (var _i=0; _i<14; _i++)
{
    var _type=BossHero_dg[#4,_i];
    var _spr=val(g.dm_ITEM[?_type+STR_Sprite],spr_Torch_1a);
    var _pi=global.PI_MOB_ORG;
    if (_i==11) _pi=global.PI_PC1;
    if (_i==12) {_spr=spr_Item_Heart_container_1d; _pi=global.PI_MOB_RED;}
    if (_i==13) _spr=spr_Item_Magic_container_1d;
    if (!BossHero_dg[#1,_i]) _pi=PI_DARK1;
    var _x=_left+4+_step*(_i+0.5), _y=_top+15;
    draw_sprite_(_spr,0,_x,_y,_pi);
    if (_i>=11)
        draw_text_(_x-3,_top-2,string(BossHero_dg[#1,_i]),FONT2,PI_MENU1);
    if (BossHero_row==0 && BossHero_item==_i)
        draw_sprite_(spr_arrow_6_up,0,_x,_top+31,PI_MENU1);
}
var _y0=_top+39;
for (_i=14; _i<25; _i++)
{
    _y=_y0+(_i-14)*_line;
    _pi=PI_MENU2;
    if (BossHero_row==_i-13) _pi=PI_MENU1;
    draw_text_(_left,_y,BossHero_dg[#4,_i],FONT2,_pi);
    var _text=string(BossHero_dg[#1,_i]);
    if (_i>=17)
    {
        _text="ON";
        if (!BossHero_dg[#1,_i]) _text="OFF";
    }
    draw_text_(_right-string_length(_text)*sprite_get_width(FONT2),_y,_text,FONT2,_pi);
    if (BossHero_row==_i-13)
        draw_sprite_(Cursor_SPRITE,0,Cursor_xl+(Cursor_W>>1),_y+4,PI_MENU1);
}
_y=_y0+11*_line+18;
for (_i=0; _i<2; _i++)
{
    _x=_left+12+_i*36;
    _pi=PI_DARK1;
    if (BossHero_dg[#1,25+_i]) _pi=global.PI_PC1;
    var _behavior=global.pc.behavior_STAB_DOWN;
    if (_i) _behavior=global.pc.behavior_STAB_UP;
    draw_pc_skin(_x,_y,1,1,_behavior,false,-1,-1,_pi);
    if (BossHero_row==12 && BossHero_skill==_i)
        draw_sprite_(spr_arrow_6_up,0,_x,_y+20,PI_MENU1);
}
_y+=31;
_pi=PI_MENU2;
if (BossHero_row==13) _pi=PI_MENU1;
draw_text_(_left,_y,"BACK",FONT2,_pi);
if (BossHero_row==13)
    draw_sprite_(Cursor_SPRITE,0,Cursor_xl+(Cursor_W>>1),_y+4,PI_MENU1);
// Numeric icons cycle (including MAX -> 1) with confirm; arrows select icons.
if (_y+20<MenuWindow_yb)
    draw_text_(_left,_y+12,"ARROWS: SELECT/ADJUST  A: CHANGE",FONT2,PI_MENU2);
