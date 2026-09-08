/// dev_boss_test_hero_apply() -- g context, after the default full test build
var _dg=OptionsMenu.BossHero_dg;
for (var _i=0; _i<11; _i++)
{
    var _bit=_dg[#5,_i];
    if (!_dg[#1,_i]) f.items &= ~_bit;
}
f.level_atk=_dg[#1,14];
f.level_mag=_dg[#1,15];
f.level_lif=_dg[#1,16];
f.cont_pieces_hp="";
f.cont_pieces_mp="";
for (var _c=1; _c<=_dg[#1,12]; _c++)
    for (var _p=1; _p<=f.CONT_PIECE_PER_HP; _p++)
        f.cont_pieces_hp+=hex_str(_c)+hex_str(_p);
for (_c=1; _c<=_dg[#1,13]; _c++)
    for (_p=1; _p<=f.CONT_PIECE_PER_MP; _p++)
        f.cont_pieces_mp+=hex_str(_c)+hex_str(_p);
for (_i=17; _i<27; _i++)
{
    if (_dg[#1,_i]) continue;
    if (_i<25) f.spells &= ~_dg[#5,_i];
    else f.skills &= ~_dg[#5,_i];
}
// The randomizer's doll setting is acquired permanent dolls, not spare lives.
var _dolls=clamp(_dg[#1,11],0,val(f.dm_1up_doll[?STR_Count])-(f.quest_num==2));
for (_i=1; _i<=val(f.dm_1up_doll[?STR_Count]); _i++)
{
    var _item=f.dm_1up_doll[?hex_str(_i)+STR_Item+STR_ID];
    if (!is_undefined(_item)) f.dm_1up_doll[?_item+STR_Acquired]=(_i<=_dolls);
}
// Leave spare lives unchanged: death returns immediately from a test.
f.hp=get_stat_max(STR_Heart);
f.mp=get_stat_max(STR_Magic);
// SUMMON stays available; never leave an unavailable spell selected.
g.spell_selected=SPL_SUMM;
for (_i=17; _i<25; _i++)
{
    if (_dg[#1,_i]) {g.spell_selected=_dg[#5,_i]; break;}
}
