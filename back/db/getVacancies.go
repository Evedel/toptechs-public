package db

import "github.com/google/logger"

// TechEntry structure
type TechEntry struct {
	Rank   int
	Name   string
	Amount int
}

// TechGraphEntry structure
type TechGraphEntry struct {
	Date   string
	Amount int
}

// GetAllTechs returns list of all techs
func GetAllTechs() (list []TechEntry) {
	if !isTechsReady {
		logger.Errorln("Tech cache is not ready. Call db.PrefetchTechs() before this function.")
		return nil
	}
	rank := 0
	for _, id := range cacheTechsTopSorted {
		rank++
		amount := cacheTechsTop[id]
		name := cacheTechs[id]
		list = append(list, TechEntry{rank, name, amount})
	}
	return
}

// GetVacanciesVSDaysForTech returns list of vacancies vs days for a specified tech
func GetVacanciesVSDaysForTech(techID int) []TechGraphEntry {
	qstr := "SELECT check_date,amount FROM vacancies "
	qstr += "WHERE check_date > date('now', '-30 day') AND tech_id=" + i2s(techID)
	cursor, _ := db.Query(qstr)
	defer cursor.Close()

	res := []TechGraphEntry{}
	for cursor.Next() {
		var date string
		var amount int
		cursor.Scan(&date, &amount)
		res = append(res, TechGraphEntry{date, amount})
	}
	return res
}

// GetVacanciesVSMonthForTech returns list of vacancies vs days for a specified tech
func GetVacanciesVSMonthForTech(techID int) []TechGraphEntry {
	qstrDate := "SELECT date('now')"
	rowsDate := Q(qstrDate)
	defer rowsDate.Close()
	var date string
	var yearLast int
	var mnthLast int
	if rowsDate.Next() {
		_ = rowsDate.Scan(&date)
		yearLast = s2i(date[:4])
		mnthLast = s2i(date[5:7])
	}

	res := []TechGraphEntry{}
	for i := 12; i > -1; i-- {
		year := 0
		mnth := 0
		if mnthLast-i < 1 {
			year = yearLast - 1
			mnth = 12 - (i - mnthLast)
		} else {
			year = yearLast
			mnth = mnthLast - i
		}
		if mnth < 10 {
			date = i2s(year) + "-0" + i2s(mnth)
		} else {
			date = i2s(year) + "-" + i2s(mnth)
		}
		qstr := "SELECT SUM(amount) FROM vacancies "
		qstr += "WHERE check_date LIKE '" + date + "-%' AND tech_id=" + i2s(techID)
		cursor, _ := db.Query(qstr)
		defer cursor.Close()
		for cursor.Next() {
			var amount int
			cursor.Scan(&amount)
			res = append(res, TechGraphEntry{date, amount})
		}
	}
	return res
}

// GetVacanciesVSYearForTech returns list of vacancies vs days for a specified tech
func GetVacanciesVSYearForTech(techID int) []TechGraphEntry {
	qstrDate := "SELECT date('now')"
	rowsDate := Q(qstrDate)
	defer rowsDate.Close()
	var date string
	var yearLast int
	if rowsDate.Next() {
		_ = rowsDate.Scan(&date)
		yearLast = s2i(date[:4])
	}

	res := []TechGraphEntry{}
	for i := 10; i > -1; i-- {
		qstr := "SELECT SUM(amount) FROM vacancies "
		qstr += "WHERE check_date LIKE '" + i2s(yearLast-i) + "-%' AND tech_id=" + i2s(techID)
		cursor, _ := db.Query(qstr)
		defer cursor.Close()
		for cursor.Next() {
			var amount int
			cursor.Scan(&amount)
			res = append(res, TechGraphEntry{i2s(yearLast - i), amount})
		}
	}
	return res
}
