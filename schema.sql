CREATE TABLE bot_quiz (
	quiz_question TEXT NOT NULL, 
	quiz_answer TEXT NOT NULL
); -- Quizzes --

CREATE INDEX bot_quiz_index ON bot_quiz (
	quiz_question
); -- Quiz Index

CREATE TABLE users (
	uid BIGINT NOT NULL, 
	money FLOAT DEFAULT 0.0, 
	points INTEGER DEFAULT 0, 
	level INTEGER DEFAULT 0.0,
	state INTEGER DEFAULT 0, 
	item_list TEXT[] DEFAULT '{}', 
	epoch_hourly BIGINT DEFAULT 0, 
	epoch_daily BIGINT DEFAULT 0, 
	epoch_weekly BIGINT DEFAULT 0, 
	mm_state BIGINT DEFAULT 0
); -- Users

CREATE INDEX users_index ON users (
	uid, 
	state, 
	level
); -- Users Index

CREATE TABLE user_guild (
	gid BIGINT NOT NULL, 
	uid BIGINT NOT NULL, 
	user_guild_level INTEGER DEFAULT 0, 
	msg_count BIGINT DEFAULT 0, 
	warnings TEXT[] DEFAULT '{}'
); -- User Guild

CREATE INDEX user_guild_index ON user_guild (
	uid, 
	gid, 
	warnings
); -- User Guild Index

CREATE TABLE user_modmail (
	uid BIGINT NOT NULL, 
	gid BIGINT NOT NULL, 
	count BIGINT DEFAULT 0, 
	mm_logs TEXT[]
); -- Mod Mail

CREATE INDEX user_modmail_index ON user_modmail (
	uid, 
	gid
); -- Mod Mail Index

CREATE TABLE guild (
	gid BIGINT NOT NULL, 
	guild_level INTEGER DEFAULT 0, 
	guild_money FLOAT DEFAULT 0.0, 
	guild_points INTEGER DEFAULT 0, 
	guild_perks TEXT[] DEFAULT '{}'
); -- Guild

CREATE INDEX guild_index ON guild (
        gid, 
        guild_perks, 
        guild_level
); -- Guild Index


CREATE TABLE guild_config (
	gid BIGINT NOT NULL,
	prefix TEXT,
	vanity TEXT,
	private BOOLEAN DEFAULT FALSE,
	guild_economy_rate INTEGER DEFAULT 2,
	verify_channel BIGINT,
	verify_message TEXT DEFAULT '{user} has successfully verifed into {server}',
        lvl_channel BIGINT,
        welcome_channel BIGINT,
        auto_roles BIGINT[] DEFAULT '{}',
        mute_role BIGINT,
        welcome_message TEXT DEFAULT '{user} has joined {server}',
        mod_log BIGINT, 
        join_log BIGINT, 
	rolelog BIGINT, 
	userlog BIGINT,
	verify_mode INTEGER DEFAULT 0, -- 0 = normal, 1 = captcha, 2...
	staffapp_channel BIGINT,
	modmail_typeproxy BOOLEAN DEFAULT TRUE,
	modmail_welcome_message TEXT,
	modmail_category BIGINT
); -- Guild Configuration

CREATE INDEX guild_config_index ON guild_config (
	gid,
	prefix
); -- Guild Configuration Index

CREATE TABLE guild_staff_app (
	gid BIGINT NOT NULL, 
	qid TEXT NOT NULL, 
	question TEXT DEFAULT '', 
	qcheck TEXT
); -- Guild Staff Application

CREATE INDEX IF NOT EXISTS guild_staff_app_index ON guild_staff_app (
	gid, qid
) -- Guild Staff Application Schemea

--       # API Tokens
--    await db.execute('CREATE TABLE IF NOT EXISTS webtokens (uid TEXT NOT NULL, token TEXT, perms INTEGER)')

