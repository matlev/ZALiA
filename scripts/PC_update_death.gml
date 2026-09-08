/// PC_update_death()

if (dev_boss_test_active() && global.pc.is_dead)
    return dev_boss_test_return("Link died");


// C2D5: JSR D385, C2E9: JSR D385, D3CC
if (global.pc.is_dead 
&& !global.pc.stun_timer )
{
    global.BackgroundColor_at_death = background_colour;
    global.pc.is_dead = 0;
    global.pc.state   = global.pc.state_DEAD;
    
    audio_stop_sound(Audio.mus_rm_inst);
    aud_play_sound(get_audio_theme_track(STR_PC+STR_Death));
    
    room_goto_(rmB_Death);
    return true;
}


return false;




