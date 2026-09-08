/// OptionsMenu_BossHero_load() -- OptionsMenu context, before test/checkpoint restore
// Columns: save key, value, minimum, maximum, label/type, item or spell bit.
ds_grid_resize(BossHero_dg,6,27);
var _keys=ds_list_create();
ds_list_add(_keys,STR_CANDLE,STR_FLUTE,STR_MEAT,STR_SHIELD,STR_RING,
    STR_PENDANT,STR_SWORD,STR_FEATHER,STR_NOTE,STR_MAP1,STR_MAP2,
    STR_1UP,STR_HEART,STR_MAGIC);
for (var _i=0; _i<14; _i++)
{
    var _key=_keys[|_i];
    BossHero_dg[#0,_i]=_key;
    BossHero_dg[#2,_i]=0;
    BossHero_dg[#3,_i]=1;
    BossHero_dg[#4,_i]=_key;
    BossHero_dg[#5,_i]=val(g.dm_ITEM[?_key+STR_Bit]);
}
ds_list_destroy(_keys);
BossHero_dg[#3,11]=3+(BossTest_quest==1);
BossHero_dg[#2,12]=1;
BossHero_dg[#3,12]=f.CONT_MAX_HP;
BossHero_dg[#2,13]=1;
BossHero_dg[#3,13]=f.CONT_MAX_MP;
for (_i=14; _i<27; _i++)
{
    BossHero_dg[#2,_i]=0;
    BossHero_dg[#3,_i]=1;
    BossHero_dg[#5,_i]=0;
}
BossHero_dg[#4,14]="ATTACK LEVEL";
BossHero_dg[#4,15]="MAGIC LEVEL";
BossHero_dg[#4,16]="LIFE LEVEL";
for (_i=14; _i<17; _i++)
{
    BossHero_dg[#2,_i]=1;
    BossHero_dg[#3,_i]=STAT_LEVEL_MAX;
}
BossHero_dg[#4,17]="PROTECT"; BossHero_dg[#5,17]=SPL_PRTC;
BossHero_dg[#4,18]="JUMP";    BossHero_dg[#5,18]=SPL_JUMP;
BossHero_dg[#4,19]="HEAL";    BossHero_dg[#5,19]=SPL_LIFE;
BossHero_dg[#4,20]="FAIRY";   BossHero_dg[#5,20]=SPL_FARY;
BossHero_dg[#4,21]="FIRE";    BossHero_dg[#5,21]=SPL_FIRE;
BossHero_dg[#4,22]="REFLECT"; BossHero_dg[#5,22]=SPL_RFLC;
BossHero_dg[#4,23]="ENIGMA";  BossHero_dg[#5,23]=SPL_SPEL;
BossHero_dg[#4,24]="THUNDER"; BossHero_dg[#5,24]=SPL_THUN;
BossHero_dg[#4,25]="DOWN STAB"; BossHero_dg[#5,25]=SKILL_THD;
BossHero_dg[#4,26]="UP STAB";   BossHero_dg[#5,26]=SKILL_THU;
for (_i=14; _i<27; _i++) BossHero_dg[#0,_i]=BossHero_dg[#4,_i];
var _saved=get_saved_value(f.file_num,"_DevBossTest_HeroStats_v1","");
var _dm=ds_map_create();
if (is_string(_saved) && string_length(_saved)>0)
{
    var _decoded=json_decode(_saved);
    if (_decoded!=-1)
    {
        ds_map_copy(_dm,_decoded);
        ds_map_destroy(_decoded);
    }
}
for (_i=0; _i<27; _i++)
{
    var _max=BossHero_dg[#3,_i];
    var _value=val(_dm[?BossHero_dg[#0,_i]],_max);
    if (!is_real(_value)) _value=_max;
    BossHero_dg[#1,_i]=clamp(floor(_value),BossHero_dg[#2,_i],_max);
}
ds_map_destroy(_dm);
BossHero_dirty=false;
