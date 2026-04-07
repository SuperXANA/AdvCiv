#include "CvDatabaseQuery.h"
#include "SQLiteStatement.h"

CvDatabaseQuery::CvDatabaseQuery() 
	: m_hasWhere(false), m_hasSet(false), m_hasColumns(false), m_hasCreateColumns(false) 
{}

CvDatabaseQuery::CvDatabaseQuery(const char* tableName)
	: m_hasWhere(false), m_hasSet(false), m_hasColumns(false), m_hasCreateColumns(false) 
{
	m_sql = CvString::format("SELECT * FROM ");
	m_sql += CvString::format(tableName);
}

CvDatabaseQuery& CvDatabaseQuery::createTable(const char* tableName)
{
	m_sql = CvString::format("CREATE TABLE ");
	m_sql += CvString::format(tableName);
	m_sql += CvString::format(" (");
	m_hasWhere = false;
	m_hasSet = false;
	m_hasColumns = false;
	m_hasCreateColumns = false;
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::createTableIfNotExists(const char* tableName)
{
	m_sql = CvString::format("CREATE TABLE IF NOT EXISTS ");
	m_sql += CvString::format(tableName);
	m_sql += CvString::format(" (");
	m_hasWhere = false;
	m_hasSet = false;
	m_hasColumns = false;
	m_hasCreateColumns = false;
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::column(const char* name, const char* type)
{
	if (m_hasCreateColumn)
	{
		m_sql += CvString::format(", ");
	}
	m_sql += CvString::format(name);
	m_sql += CvString::format(" ");
	m_sql += CvString::format(type);
	m_hasCreateColumns = true;
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::notNull()
{
	m_sql += CvString::format(" NOT NULL");
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::unique()
{
	m_sql += CvString::format(" UNIQUE");
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::primaryKey()
{
	m_sql += CvString::format(" PRIMARY KEY");
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::autoIncrement()
{
	m_sql += CvString::format(" AUTOINCREMENT");
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::defaultValue(const char* value)
{
	m_sql += CvString::format(" DEFAULT ");
	m_sql += CvString::format(value);
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::references(const char* table, const char* column)
{
	m_sql += CvString::format(" REFERENCES ");
	m_sql += CvString::format(table);
	m_sql += CvString::format("(");
	m_sql += CvString::format(column);
	m_sql += CvString::format(")");
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::foreignKey(const char* columns, const char* refTable, const char* refColumns)
{
	if (m_hasCreateColumn)
	{
		m_sql += CvString::format(", ");
	}
	m_sql += CvString::format("FOREIGN KEY (");
	m_sql += CvString::format(columns);
	m_sql += CvString::format(") REFERENCES ");
	m_sql += CvString::format(refTable);
	m_sql += CvString::format("(");
	m_sql += CvString::format(refColumns);
	m_sql += CvString::format(")");
	m_hasCreateColumns = true;
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::onDelete(const char* action)
{
	m_sql += CvString::format(" ON DELETE ");
	m_sql += CvString::format(action);
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::onUpdate(const char* action)
{
	m_sql += CvString::format(" ON UPDATE ");
	m_sql += CvString::format(action);
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::endTable()
{
	m_sql += CvString::format(")");
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::dropTable(const char* tableName)
{
	m_sql = CvString::format("DROP TABLE ");
	m_sql += CvString::format(tableName);
	m_hasWhere = false;
	m_hasSet = false;
	m_hasColumns = false;
	m_hasCreateColumns = false;
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::dropTableIfExists(const char* tableName)
{
	m_sql = CvString::format("DROP TABLE IF EXISTS ");
	m_sql += CvString::format(tableName);
	m_hasWhere = false;
	m_hasSet = false;
	m_hasColumns = false;
	m_hasCreateColumns = false;
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::alterTable(const char* tableName)
{
	m_sql = CvString::format("ALTER TABLE ");
	m_sql += CvString::format(tableName);
	m_hasWhere = false;
	m_hasSet = false;
	m_hasColumns = false;
	m_hasCreateColumns = false;
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::addColumn(const char* name, const char* type)
{
	m_sql += CvString::format(" ADD COLUMN ");
	m_sql += CvString::format(name);
	m_sql += CvString::format(" ");
	m_sql += CvString::format(type);
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::select(const char* columns)
{
	m_sql = CvString::format("SELECT ");
	m_sql += CvString::format(columns);
	m_hasWhere = false;
	m_hasSet = false;
	m_hasColumns = false;
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::selectDistinct(const char* columns)
{
	m_sql = CvString::format("SELECT DISTINCT ");
	m_sql += CvString::format(columns);
	m_hasWhere = false;
	m_hasSet = false;
	m_hasColumns = false;
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::from(const char* table)
{
	m_sql += CvString::format(" FROM ");
	m_sql += CvString::format(table);
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::join(const char* table, const char* onCondition)
{
	m_sql += CvString::format(" JOIN ");
	m_sql += CvString::format(table);
	m_sql += CvString::format(" ON ");
	m_sql += CvString::format(onCondition);
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::leftJoin(const char* table, const char* onCondition)
{
	m_sql += CvString::format(" LEFT JOIN ");
	m_sql += CvString::format(table);
	m_sql += CvString::format(" ON ");
	m_sql += CvString::format(onCondition);
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::innerJoin(const char* table, const char* onCondition)
{
	m_sql += CvString::format(" INNER JOIN ");
	m_sql += CvString::format(table);
	m_sql += CvString::format(" ON ");
	m_sql += CvString::format(onCondition);
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::where(const char* column, const char* op, const char* paramName)
{
	m_sql += CvString::format(" WHERE ");
	m_sql += CvString::format(column);
	m_sql += CvString::format(" ");
	m_sql += CvString::format(op);
	m_sql += CvString::format(" ");
	m_sql += CvString::format(paramName);
	m_hasWhere = true;
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::andWhere(const char* column, const char* op, const char* paramName)
{
	if (!m_hasWhere)
	{
		return where(column, op, paramName);
	}
	m_sql += CvString::format(" AND ");
	m_sql += CvString::format(column);
	m_sql += CvString::format(" ");
	m_sql += CvString::format(op);
	m_sql += CvString::format(" ");
	m_sql += CvString::format(paramName);
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::orWhere(const char* column, const char* op, const char* paramName)
{
	if (!m_hasWhere)
	{
		return where(column, op, paramName);
	}
	m_sql += CvString::format(" OR ");
	m_sql += CvString::format(column);
	m_sql += CvString::format(" ");
	m_sql += CvString::format(op);
	m_sql += CvString::format(" ");
	m_sql += CvString::format(paramName);
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::whereEquals(const char* column, const char* paramName)
{
	return where(column, "=", paramName);
}

CvDatabaseQuery& CvDatabaseQuery::whereNotEquals(const char* column, const char* paramName)
{
	return where(column, "!=", paramName);
}

CvDatabaseQuery& CvDatabaseQuery::whereLessThan(const char* column, const char* paramName)
{
	return where(column, "<", paramName);
}

CvDatabaseQuery& CvDatabaseQuery::whereLessThanOrEqual(const char* column, const char* paramName)
{
	return where(column, "<=", paramName);
}

CvDatabaseQuery& CvDatabaseQuery::whereGreaterThan(const char* column, const char* paramName)
{
	return where(column, ">", paramName);
}

CvDatabaseQuery& CvDatabaseQuery::whereGreaterThanOrEqual(const char* column, const char* paramName)
{
	return where(column, ">=", paramName);
}

CvDatabaseQuery& CvDatabaseQuery::whereLike(const char* column, const char* paramName)
{
	return where(column, "LIKE", paramName);
}

CvDatabaseQuery& CvDatabaseQuery::whereNull(const char* column)
{
	m_sql += CvString::format(" WHERE ");
	m_sql += CvString::format(column);
	m_sql += CvString::format(" IS NULL");
	m_hasWhere = true;
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::whereNotNull(const char* column)
{
	m_sql += CvString::format(" WHERE ");
	m_sql += CvString::format(column);
	m_sql += CvString::format(" IS NOT NULL");
	m_hasWhere = true;
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::whereRaw(const char* condition)
{
	m_sql += CvString::format(" WHERE ");
	m_sql += CvString::format(condition);
	m_hasWhere = true;
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::andWhereRaw(const char* condition)
{
	if (!m_hasWhere)
		return whereRaw(condition);
	m_sql += CvString::format(" AND ");
	m_sql += CvString::format(condition);
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::orWhereRaw(const char* condition)
{
	if (!m_hasWhere)
		return whereRaw(condition);
	m_sql += CvString::format(" OR ");
	m_sql += CvString::format(condition);
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::groupBy(const char* columns)
{
	m_sql += CvString::format(" GROUP BY ");
	m_sql += CvString::format(columns);
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::having(const char* condition)
{
	m_sql += CvString::format(" HAVING ");
	m_sql += CvString::format(condition);
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::orderBy(const char* column, bool ascending)
{
	m_sql += CvString::format(" ORDER BY ");
	m_sql += CvString::format(column);
	if (ascending)
		m_sql += CvString::format(" ASC");
	else
		m_sql += CvString::format(" DESC");
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::limit(int count)
{
	m_sql += CvString::format(" LIMIT ");
	m_sql += CvString::format(intToString(count).c_str());
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::offset(int count)
{
	m_sql += CvString::format(" OFFSET ");
	m_sql += CvString::format(intToString(count).c_str());
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::update(const char* table)
{
	m_sql = CvString::format("UPDATE ");
	m_sql += CvString::format(table);
	m_hasWhere = false;
	m_hasSet = false;
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::set(const char* column, const char* paramName)
{
	m_sql += CvString::format(" SET ");
	m_sql += CvString::format(column);
	m_sql += CvString::format(" = ");
	m_sql += CvString::format(paramName);
	m_hasSet = true;
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::addSet(const char* column, const char* paramName)
{
	if (!m_hasSet)
		return set(column, paramName);
	m_sql += CvString::format(", ");
	m_sql += CvString::format(column);
	m_sql += CvString::format(" = ");
	m_sql += CvString::format(paramName);
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::insertInto(const char* table)
{
	m_sql = CvString::format("INSERT INTO ");
	m_sql += CvString::format(table);
	m_hasWhere = false;
	m_hasSet = false;
	m_hasColumns = false;
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::columns(const char* columnList)
{
	m_sql += CvString::format(" (");
	m_sql += CvString::format(columnList);
	m_sql += CvString::format(")");
	m_hasColumns = true;
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::values(const char* paramList)
{
	m_sql += CvString::format(" VALUES (");
	m_sql += CvString::format(paramList);
	m_sql += CvString::format(")");
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::deleteFrom(const char* table)
{
	m_sql = CvString::format("DELETE FROM ");
	m_sql += CvString::format(table);
	m_hasWhere = false;
	m_hasSet = false;
	return *this;
}

CvDatabaseQuery& CvDatabaseQuery::clear()
{
	m_sql.clear();
	m_hasWhere = false;
	m_hasSet = false;
	m_hasColumns = false;
	return *this;
}

const CvString& CvDatabaseQuery::getSQLString() const
{
    return m_sql;
}

SQLiteStatement CvDatabaseQuery::toStatement() const
{
    return SQLiteStatement(m_sql);
}

void CvDatabaseQuery::applyTo(SQLiteStatement& stmt) const
{
    stmt.prepare(m_sql);
}

static std::string CvDatabaseQuery::intToString(int value)
{
	std::ostringstream kStream;
	kStream << value;
    return kStream.str();
}