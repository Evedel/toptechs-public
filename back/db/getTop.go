package db

import (
	"github.com/google/logger"
)

// TopResponse structure
type TopResponse struct {
	Date string
	List []TechEntry
}

// GetTopByDay returns list of vacancies for a specified day
func GetTopByDay(day string) (top TopResponse) {
	qstrDate := "SELECT date(" + day + ")"
	rowsDate := Q(qstrDate)
	defer rowsDate.Close()
	var topDate string
	if rowsDate.Next() {
		_ = rowsDate.Scan(&topDate)
	}
	top.List = nil
	top.Date = topDate

	rows := Q("SELECT * FROM vacancies WHERE check_date = DATE(" + day + ") ORDER BY amount DESC")
	defer rows.Close()
	rank := 1
	var err error
	if rows != nil {
		top.List = []TechEntry{}
		for rows.Next() {
			var id int
			var tid int
			var date string
			var amount int
			err = rows.Scan(&id, &tid, &date, &amount)
			if err != nil {
				logger.Errorln(err)
				top.List = nil
				return
			}
			if !isTechsReady {
				logger.Errorln("Tech cache is not ready. Call db.PrefetchTechs() before this function.")
				top.List = nil
				return
			}
			top.List = append(top.List, TechEntry{rank, cacheTechs[tid], amount})
			rank++
		}
	}
	return
}

// GetTopByMonth returns list of vacancies for a month
func GetTopByMonth() (top TopResponse) {
	top.List = nil
	qstrDate := "SELECT date('now')"
	rowsDate := Q(qstrDate)
	defer rowsDate.Close()
	var date string
	if rowsDate.Next() {
		_ = rowsDate.Scan(&date)
		year := s2i(date[:4])
		mnth := s2i(date[5:7])
		if mnth == 1 {
			year--
			mnth = 12
		} else {
			mnth--
		}
		if mnth < 10 {
			date = i2s(year) + "-0" + i2s(mnth)
		} else {
			date = i2s(year) + "-" + i2s(mnth)
		}
	}
	top.Date = date
	qstr := "SELECT tech_id,SUM(amount) FROM vacancies "
	qstr += "WHERE check_date LIKE '" + date + "-%' GROUP BY tech_id ORDER BY SUM(amount) DESC"
	rows := Q(qstr)
	defer rows.Close()
	rank := 1
	var err error
	if rows != nil {
		top.List = []TechEntry{}
		for rows.Next() {
			var tid int
			var amount int
			err = rows.Scan(&tid, &amount)
			if err != nil {
				logger.Errorln(err)
				top.List = nil
				return
			}
			if !isTechsReady {
				logger.Errorln("Tech cache is not ready. Call db.PrefetchTechs() before this function.")
				top.List = nil
				return
			}
			top.List = append(top.List, TechEntry{rank, cacheTechs[tid], amount})
			rank++
		}
	}
	return
}

// GetTopByYear returns top of vacancies for this year
func GetTopByYear() (top TopResponse) {
	top.List = nil
	qstrDate := "SELECT date('now')"
	rowsDate := Q(qstrDate)
	defer rowsDate.Close()
	var date string
	year := 0
	if rowsDate.Next() {
		_ = rowsDate.Scan(&date)
		year = s2i(date[:4])
		mnth := s2i(date[5:7])
		day := s2i(date[8:9])
		if (mnth == 1) && (day == 1) {
			year--
		}
	}
	top.Date = i2s(year)
	qstr := "SELECT tech_id,SUM(amount) FROM vacancies "
	qstr += "WHERE check_date LIKE '" + i2s(year) + "-%' GROUP BY tech_id ORDER BY SUM(amount) DESC"
	rows := Q(qstr)
	defer rows.Close()
	rank := 1
	var err error
	if rows != nil {
		top.List = []TechEntry{}
		for rows.Next() {
			var tid int
			var amount int
			err = rows.Scan(&tid, &amount)
			if err != nil {
				logger.Errorln(err)
				top.List = nil
				return
			}
			if !isTechsReady {
				logger.Errorln("Tech cache is not ready. Call db.PrefetchTechs() before this function.")
				top.List = nil
				return
			}
			top.List = append(top.List, TechEntry{rank, cacheTechs[tid], amount})
			rank++
		}
	}
	return
}
