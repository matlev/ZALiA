/// dev_boss_test_checkpoint()
// Called BEFORE opening Options, while Link and the save still describe play.
// Reload the original room on return; don't retain references to its actors.
if (!DEV || dev_boss_test_active()) exit;
if (ds_exists(global.DevBossTest_checkpoint,ds_type_grid))
    ds_grid_destroy(global.DevBossTest_checkpoint);
global.DevBossTest_checkpoint=ds_grid_create(5,0);
global.DevBossTest_room=room;
global.DevBossTest_view_w=viewW();
global.DevBossTest_view_h=viewH();
global.DevBossTest_view_x=viewXL();
global.DevBossTest_view_y=viewYT();
global.DevBossTest_x=global.pc.x;
global.DevBossTest_y=global.pc.y;
global.DevBossTest_reen=f.reen;

dev_boss_test_capture_fields(f.id,
    "file_num save_name saveCreated quest_num game_completed_count death_count level_atk level_mag level_lif cont_pieces_hp cont_pieces_mp hp mp items spells skills Cucco_skills crystals lives xp xpPending xpNext xpDrain key_count kakusu_count fastTravel cont_run_dngn_num cont_run_town_num reen reen_new_run",0,1);
dev_boss_test_capture_fields(f.id,
    "dm_jars dm_1up_doll dm_PBags dm_keys dm_openedLocks dm_kakusu dm_explored dm_quests dm_challenges dm_rando_full dm_rando dm_rando_dungeon_tileset",1,1);
dev_boss_test_capture_fields(f.id,"dg_xp_next",3,1);
dev_boss_test_capture_fields(g.id,"dm_room_history dm_exit_leave_history dm_RandoHintsRecorder",1,1);
dev_boss_test_capture_fields(g.id,"dl_spell_history dl_HP",2,1);
dev_boss_test_capture_fields(g.id,
    "kill_count1 kill_count2 spell_selected spell_ready spells_active CuccoSpell2_Active CuccoSpell2_Acquired CuccoSpell2_Option dev_invState DevDash_state use_StabToCheat StatRestore_timer_hp StatRestore_timer_mp StatRestore_timer_lives StatRestore_timer_xp boss_stun_timer counter1 game_end_state",0,1);
dev_boss_test_capture_fields(-1,
    "QuestTimer_time QuestTimer_state QuestTimer_text SceneRando_enabled EnemyRando_enabled RandoDungeonTilesets_enabled RandoHints_enabled randomized",0,1);
dev_boss_test_capture_fields(-1,"dm_save_file dm_save_file_data dm_save_file_settings",1,1);
dev_boss_test_capture_fields(global.pc,
    "xScale hspd vspd hspd_sub vspd_sub hspd_dir vspd_dir ogr Disguise_enabled Cucco_damage_taken Cucco_damaged_count RescueDropOff_rc",0,2);
// Room entry also updates persistent overworld tiles and cached dungeon maps.
dev_boss_test_capture_fields(global.OVERWORLD,"pcrc pcrc_map last_pcrc",0,1);
dev_boss_test_capture_fields(global.OVERWORLD,"dm",1,1);
dev_boss_test_capture_fields(global.OVERWORLD,"dg_tsrc dg_solid dg_anarkhya_tsrc dg_anarkhya_tsrc_detail",3,1);
dev_boss_test_capture_fields(g.PAUSE_MENU,"dg_dngn_map dg_dngn_map_1 dg_dngn_map_2 dg_dngn_map_3 dg_dngn_map_4 dg_dngn_map_5 dg_dngn_map_6 dg_dngn_map_7 dg_dngn_map_8",3,1);
show_debug_message("BOSS TEST: captured Link and progression before Options opened.");
