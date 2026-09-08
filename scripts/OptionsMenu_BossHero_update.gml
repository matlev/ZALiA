/// OptionsMenu_BossHero_update()
var _confirm=a_button_pressed || start_button_pressed;
if (!timer && (Backout_requested || (BossHero_row==13 && _confirm)))
{
    OptionsMenu_BossHero_save();
    menu_state=menu_state_BOSS_TEST;
    timer=DURATION1;
    aud_play_sound(BACK_SOUND1);
    exit;
}
if (!timer2 && (select_button_pressed || Input.pressedV))
{
    BossHero_row=(BossHero_row+sign_(select_button_pressed || Input.Down_pressed)+14) mod 14;
    timer2=DURATION2;
    aud_play_sound(CURSOR_SOUND1);
    exit;
}
if (timer) exit;
var _field=-1;
if (BossHero_row==0 || BossHero_row==12)
{
    var _count=14;
    if (BossHero_row==12) _count=2;
    if (!timer2 && Input.pressedH)
    {
        if (BossHero_row==0)
            BossHero_item=(BossHero_item+sign_(Input.Right_pressed)+_count) mod _count;
        else BossHero_skill=1-BossHero_skill;
        timer2=DURATION2;
        aud_play_sound(CURSOR_SOUND1);
        exit;
    }
    if (_confirm)
    {
        if (BossHero_row==0) _field=BossHero_item;
        else _field=25+BossHero_skill;
    }
}
else if (BossHero_row<12 && (_confirm || Input.pressedH))
    _field=13+BossHero_row;
if (_field<0) exit;
var _dir=1;
if (!_confirm && Input.Left_pressed) _dir=-1;
var _min=BossHero_dg[#2,_field], _max=BossHero_dg[#3,_field];
BossHero_dg[#1,_field]=_min+(BossHero_dg[#1,_field]-_min+_dir+_max-_min+1) mod (_max-_min+1);
BossHero_dirty=true;
timer=DURATION1;
aud_play_sound(CONFIRM_SOUND1);
