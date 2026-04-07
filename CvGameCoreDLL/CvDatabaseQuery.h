#pragma once

#include "CvGameCoreDLL.h"

#ifndef CV_SQLITEQUERY_H
#define CV_SQLITEQUERY_H

class SQLiteStatement;

class CvDatabaseQuery : private boost::noncopyable
{
public:
	CvDatabaseQuery();
	explicit CvDatabaseQuery(const char* tableName);
	~CvDatabaseQuery() {};

	CvDatabaseQuery& createTable(const char* tableName);
	CvDatabaseQuery& createTableIfNotExists(const char* tableName);
	CvDatabaseQuery& column(const char* name, const char* type);
	CvDatabaseQuery& notNull();
	CvDatabaseQuery& unique();
	CvDatabaseQuery& primaryKey();
	CvDatabaseQuery& autoIncrement();
	CvDatabaseQuery& defaultValue(const char* value);

	CvDatabaseQuery& references(const char* table, const char* column);
	CvDatabaseQuery& foreignKey(const char* columns, const char* refTable, const char* refColumns);
	CvDatabaseQuery& onDelete(const char* action);
	CvDatabaseQuery& onUpdate(const char* action);

	CvDatabaseQuery& endTable();

	CvDatabaseQuery& dropTable(const char* tableName);
	CvDatabaseQuery& dropTableIfExists(const char* tableName);
	CvDatabaseQuery& alterTable(const char* tableName);
	CvDatabaseQuery& addColumn(const char* name, const char* type);

	CvDatabaseQuery& select(const char* columns);
	CvDatabaseQuery& selectDistinct(const char* columns);
	CvDatabaseQuery& from(const char* table);
	
	CvDatabaseQuery& join(const char* table, const char* onCondition);
	CvDatabaseQuery& leftJoin(const char* table, const char* onCondition);
	CvDatabaseQuery& innerJoin(const char* table, const char* onCondition);
	
	CvDatabaseQuery& where(const char* column, const char* op, const char* paramName);
	CvDatabaseQuery& andWhere(const char* column, const char* op, const char* paramName);
	CvDatabaseQuery& orWhere(const char* column, const char* op, const char* paramName);
	
	CvDatabaseQuery& whereEquals(const char* column, const char* paramName);
	CvDatabaseQuery& whereNotEquals(const char* column, const char* paramName);
	CvDatabaseQuery& whereLessThan(const char* column, const char* paramName);
	CvDatabaseQuery& whereLessThanOrEqual(const char* column, const char* paramName);
	CvDatabaseQuery& whereGreaterThan(const char* column, const char* paramName);
	CvDatabaseQuery& whereGreaterThanOrEqual(const char* column, const char* paramName);
	CvDatabaseQuery& whereLike(const char* column, const char* paramName);
	CvDatabaseQuery& whereNotNull(const char* column);
	CvDatabaseQuery& whereNull(const char* column);
	
	CvDatabaseQuery& whereRaw(const char* condition);
	CvDatabaseQuery& andWhereRaw(const char* condition);
	CvDatabaseQuery& orWhereRaw(const char* condition);
	
	CvDatabaseQuery& groupBy(const char* columns);
	CvDatabaseQuery& having(const char* condition);
	CvDatabaseQuery& orderBy(const char* column, bool ascending = true);
	CvDatabaseQuery& limit(int count);
	CvDatabaseQuery& offset(int count);
	
	CvDatabaseQuery& update(const char* table);
	CvDatabaseQuery& set(const char* column, const char* paramName);
	CvDatabaseQuery& addSet(const char* column, const char* paramName);
	
	CvDatabaseQuery& insertInto(const char* table);
	CvDatabaseQuery& columns(const char* columnList);
	CvDatabaseQuery& values(const char* paramList);
	
	CvDatabaseQuery& deleteFrom(const char* table);
	
	CvDatabaseQuery& clear();
	const CvString& getSQLString() const;
	
	SQLiteStatement toStatement() const;
	void applyTo(SQLiteStatement& stmt) const;

private:
	CvString m_sql;
	bool m_hasWhere;
	bool m_hasSet;
	bool m_hasColumns;
	bool m_hasCreateColumns;
	static std::string intToString(int value);
};
#endif // CV_SQLITEQUERY_H
