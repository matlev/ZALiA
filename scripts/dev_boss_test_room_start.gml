/// dev_boss_test_room_start() -- before normal g_Room_Start
if (!dev_boss_test_active()) exit;
if (global.DevBossTest_stage==4)
{
    dev_boss_test_restore(false);
    global.DevBossTest_stage=5;
    exit;
}
if (global.DevBossTest_stage!=1) exit;
global.DevBossTest_stage=2;
f.quest_num=global.DevBossTest_quest;
f.reen=global.DevBossTest_exit;
ds_map_clear(f.dm_quests);
ds_map_clear(f.dm_rando);
ds_map_clear(f.dm_rando_dungeon_tileset);
ds_map_clear(global.dm_save_file_settings);
global.SceneRando_enabled=false;
global.EnemyRando_enabled=false;
global.RandoDungeonTilesets_enabled=false;
global.RandoHints_enabled=false;
global.QuestTimer_state=0;
g.CuccoSpell2_Active=false;
g.CuccoSpell2_Acquired=true;
g.CuccoSpell2_Option=true;
f.Cucco_skills=f.CuccoSkill_THRUST_D|f.CuccoSkill_THRUST_U|f.CuccoSkill_BREAK1|f.CuccoSkill_PROJ1|f.CuccoSkill_PROJ2;
g.dev_invState=0;
g.DevDash_state=0;
g.use_StabToCheat=false;
g.game_end_state=0;
g.spells_active=0;
g.spell_selected=SPL_PRTC;
g.spell_ready=0;
ds_list_copy(g.dl_HP,g.dl_HP_DEFAULT);
f.crystals=0;
f.level_atk=STAT_LEVEL_MAX;
f.level_mag=STAT_LEVEL_MAX;
f.level_lif=STAT_LEVEL_MAX;
f.cont_pieces_hp="";
f.cont_pieces_mp="";
for (var _c=1; _c<=f.CONT_MAX_HP; _c++)
    for (var _p=1; _p<=f.CONT_PIECE_PER_HP; _p++)
        f.cont_pieces_hp+=hex_str(_c)+hex_str(_p);
for (_c=1; _c<=f.CONT_MAX_MP; _c++)
    for (_p=1; _p<=f.CONT_PIECE_PER_MP; _p++)
        f.cont_pieces_mp+=hex_str(_c)+hex_str(_p);
// The item menu's registered bits include quest collectibles (and SUMMON).
f.items=ITM_CAND|ITM_GLOV|ITM_RAFT|ITM_BOOT|ITM_FLUT|ITM_CROS|ITM_HAMM|ITM_BRAC
    |ITM_FRY1|ITM_MASK|ITM_BOOK|ITM_MEAT|ITM_SHLD|ITM_RING|ITM_NKLC|ITM_SWRD
    |ITM_NOTE|ITM_MIRR|ITM_TRPH|ITM_MEDI|ITM_CHLD|ITM_BTL1|ITM_SKEY|ITM_MAP1
    |ITM_MAP2|ITM_TBLT|ITM_MEL1|ITM_FTHR;
f.spells=SPL_PRTC|SPL_JUMP|SPL_LIFE|SPL_FARY|SPL_FIRE|SPL_RFLC|SPL_SPEL|SPL_THUN|SPL_SUMM;
f.skills=SKILL_THD|SKILL_THU|SKILL_BNC|SKILL_CST|SKILL_AFR;
f.hp=get_stat_max(STR_Heart);
f.mp=get_stat_max(STR_Magic);
f.xp=0;
f.xpNext=XP_MAX;
f.xpPending=0;
f.xpDrain=0;
f.dm_quests[?STR_Bottle+"01"+STR_State]=1;
dev_boss_test_hero_apply();
show_debug_message("BOSS TEST: Q"+string(f.quest_num)+" "+global.DevBossTest_spawn);
