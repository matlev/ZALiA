/// OptionsMenu_BossTest_update()
var _count=ds_grid_height(BossTest_dg);
var _confirm=a_button_pressed || start_button_pressed;
if (!timer && (Backout_requested || (BossTest_cursor==_count+2 && _confirm)))
{
    menu_state=menu_state_DEV_TOOLS;
    timer=DURATION1;
    aud_play_sound(BACK_SOUND1);
    exit;
}
if (!timer2 && (select_button_pressed || Input.pressedV))
{
    BossTest_cursor=(BossTest_cursor+sign_(select_button_pressed || Input.Down_pressed)+_count+3) mod (_count+3);
    timer2=DURATION2;
    aud_play_sound(CURSOR_SOUND1);
    exit;
}
if (timer) exit;
if (BossTest_cursor==0 && _confirm)
{
    OptionsMenu_BossHero_load();
    BossHero_row=0;
    BossHero_item=0;
    BossHero_skill=0;
    menu_state=menu_state_BOSS_HERO;
    timer=DURATION1;
    aud_play_sound(CONFIRM_SOUND1);
}
else if (BossTest_cursor==1 && (_confirm || Input.pressedH))
{
    BossTest_quest=3-BossTest_quest;
    dev_boss_test_catalog(BossTest_quest);
    timer=DURATION1;
    aud_play_sound(CONFIRM_SOUND1);
}
else if (BossTest_cursor>1 && BossTest_cursor<=_count+1 && _confirm)
{
    aud_play_sound(CONFIRM_SOUND1);
    dev_boss_test_start(BossTest_cursor-2);
}
