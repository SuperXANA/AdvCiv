#pragma once

#ifndef CV_SQLITESCHEMA_H
#define CV_SQLITESCHEMA_H

// ============================================================================
// 1. MASTER SCHEMA DEFINITION
// ============================================================================
// Define ALL tables here. This is the single source of truth.
// Format: SQL_TABLE(TableName, PREFIX, ColumnList)
// ColumnList uses COL(PREFIX, EnumName, SQLName, SQLType)

#define SQL_DATABASE_SCHEMA \
	SQL_TABLE(Player, PLAYER, \
		COL(PLAYER, PlayerID,   "player_id",   INTEGER) \
		COL(PLAYER, PlayerType, "player_type", INTEGER) \
		COL(PLAYER, IsAlive,    "is_alive",    INTEGER) \
		COL(PLAYER, PlayerName, "player_name", TEXT)    \
		COL(PLAYER, Score,      "score",       REAL)    \
	) \
	SQL_TABLE(WarPlans, WAR_PLANS, \
		COL(WAR_PLANS, PlanID,    "plan_id",    INTEGER) \
		COL(WAR_PLANS, PlayerID,  "player_id",  INTEGER) \
		COL(WAR_PLANS, PlanType,  "plan_type",  TEXT)    \
		COL(WAR_PLANS, StartTurn, "start_turn", INTEGER) \
	) \
	SQL_TABLE(LeaderStats, LEADER_STATS, \
		COL(LEADER_STATS, LeaderID, "leader_id", INTEGER) \
		COL(LEADER_STATS, Rating,   "rating",    REAL)   \
	)

// ============================================================================
// 2. TABLE NAMES ENUM (Auto-generated)
// ============================================================================
enum TableTypes
{
	NO_TABLE = -1,
	#define SQL_TABLE(Name, PREFIX, ColumnList) TABLE_##PREFIX,
	SQL_DATABASE_SCHEMA
	#undef SQL_TABLE
	NUM_TABLE_TYPES
};

// ============================================================================
// 3. PER-TABLE COLUMN ENUMS (Auto-generated)
// ============================================================================
// Note: We use the Prefix from SQL_TABLE to create the enum name, 
// and the COL Prefix to create the enum values
#define SQL_TABLE(Name, PREFIX, ColumnList) \
	enum Name##ColumnTypes \
	{ \
		NO_PREFIX##COLUMN = -1,
		#define COL(PREFIX, enumName, sqlName, sqlType) PREFIX##COLUMN_##enumName,
		ColumnList \
		#undef COL \
		NUM_PREFIX##COLUMN_TYPES \
	};
SQL_DATABASE_SCHEMA
#undef SQL_TABLE

// ============================================================================
// 4. SQL TYPE MAPPING
// ============================================================================
#define SQL_INTEGER	"INTEGER"
#define SQL_BOOL	"INTEGER"
#define SQL_TEXT	"TEXT"
#define SQL_STRING	"TEXT"
#define SQL_FLOAT	"REAL"
#define SQL_DOUBLE	"REAL"

// ============================================================================
// 5. METADATA LOOKUP FUNCTIONS
// ============================================================================
// Get table name from enum
inline const char* GetTableName(TableTypes sqlTable)
{
	switch(sqlTable)
	{
		#define SQL_TABLE(Name, PREFIX, ColumnList) case TABLE_##PREFIX: return #Name;
		SQL_DATABASE_SCHEMA
		#undef SQL_TABLE
		default: return "";
	}
}
// Column name lookup (overloaded by enum type)
#define SQL_TABLE(Name, PREFIX, ColumnList) \
	inline const char* GetColumnName(Name##ColumnTypes sqlColumn) { \
		switch(sqlColumn) { \
			#define COL(PREFIX, enumName, sqlName, sqlType) \
				case PREFIX##COLUMN_##enumName: return sqlName;
			ColumnList \
			#undef COL \
			default: return ""; \
		} \
	} \
	inline const char* GetColumnType(Name##ColumnTypes sqlColumn) { \
		switch(sqlColumn) { \
			#define COL(PREFIX, enumName, sqlName, sqlType) \
				case PREFIX##COLUMN_##enumName: return SQL_##sqlType;
			ColumnList \
			#undef COL \
			default: return ""; \
		} \
	} \
	inline const char* GetParamName(Name##ColumnTypes sqlColumn) { \
		switch(sqlColumn) { \
			#define COL(PREFIX, enumName, sqlName, sqlType) \
				case PREFIX##COLUMN_##enumName: return ":" sqlName;
			ColumnList \
			#undef COL \
			default: return ""; \
		} \
	}
SQL_DATABASE_SCHEMA
#undef SQL_TABLE
#undef SQL_DATABASE_SCHEMA

#endif // CV_SQLITESCHEMA_H