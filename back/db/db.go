package db

import (
	"database/sql"
	"os"
	"strconv"

	"github.com/google/logger"
	// sql driver
	_ "github.com/mattn/go-sqlite3"
)

var db *sql.DB
var isInit = false

var cacheTechs = map[int]string{}
var cacheTechsRev = map[string]int{}
var cacheTechsTop = map[int]int{}
var cacheTechsTopSorted = []int{}
var isTechsReady = false

// InitDB return db pointer
func InitDB(path string) *sql.DB {
	dbr, err := sql.Open("sqlite3", path)
	db = dbr
	if err != nil {
		logger.Errorln(err)
		os.Exit(1)
	}
	isInit = true
	return dbr
}

// Q returns result of query or nil
func Q(cmd string) *sql.Rows {
	if !isInit {
		logger.Errorln("db is not initialised")
		return nil
	}

	cursor, err := db.Query(cmd)
	if err != nil {
		logger.Errorln(err)
		cursor = nil
	}
	return cursor
}

// E executes the command on db
func E(cmd string) sql.Result {
	if !isInit {
		logger.Errorln("db is not initialised")
		return nil
	}

	result, err := db.Exec(cmd)
	if err != nil {
		logger.Errorln(err)
		result = nil
	}
	return result
}

func i2s(n int) string {
	return strconv.Itoa(n)
}
func s2i(s string) int {
	i, _ := strconv.Atoi(s)
	return i
}

// PrefetchTechs loads the list of all techs and store it in memory
func PrefetchTechs() {
	if !isInit {
		logger.Errorln("db is not initialised")
	}

	rows := Q("SELECT * FROM techs")
	defer rows.Close()
	for rows.Next() {
		var id int
		var name string
		err := rows.Scan(&id, &name)
		if err != nil {
			logger.Errorln(err)
		}
		cacheTechs[id] = name
		cacheTechsRev[name] = id
	}

	qstr := "SELECT tech_id,SUM(amount) FROM vacancies GROUP BY tech_id ORDER BY SUM(amount) DESC"
	rows2 := Q(qstr)
	defer rows2.Close()
	for rows2.Next() {
		var id int
		var amount int
		rows2.Scan(&id, &amount)
		cacheTechsTop[id] = amount
		cacheTechsTopSorted = append(cacheTechsTopSorted, id)
	}

	for id := range cacheTechs {
		if _, ok := cacheTechsTop[id]; !ok {
			cacheTechsTop[id] = 0
			cacheTechsTopSorted = append(cacheTechsTopSorted, id)
		}
	}

	isTechsReady = true
}

// GetIDFromVacancyName returns -1 for error and tech_id otherwise
func GetIDFromVacancyName(name string) int {
	if !isTechsReady {
		logger.Errorln("Tech cache is not ready. Call db.PrefetchTechs() before this function.")
		return -1
	} else {
		if val, ok := cacheTechsRev[name]; ok {
			return val
		} else {
			return -1
		}
	}
}
