/// Boss_update_5()

if (state!=state_NORMAL && dev_boss_test_defeated(id)) exit;


// BC5D & B1F6 & A3DB
if (state!=state_NORMAL)
{
    state         = state_NORMAL;
    pending_death = true;
    timer         = $FF;
    stun_timer    = EXPLODE_DELAY1; // $7F
}




