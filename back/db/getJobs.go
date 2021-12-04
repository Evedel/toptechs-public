package db

import "github.com/google/logger"

// JobStatsEntry structure
type JobStatsEntry struct {
	Date  string
	Total int
	Dev   int
}

// GetJobsByDay returns list of total and dev jobs by days
func GetJobsByDay() (jobs []JobStatsEntry) {
	qstr := "SELECT * FROM jobs "
	qstr += "WHERE check_date > date('now', '-30 day')"
	rows := Q(qstr)
	defer rows.Close()

	jobs = nil
	var err error
	if rows != nil {
		jobs = []JobStatsEntry{}
		for rows.Next() {
			var date string
			var total int
			var dev int
			err = rows.Scan(&date, &total, &dev)
			if err != nil {
				logger.Errorln(err)
				return nil
			}
			jobs = append(jobs, JobStatsEntry{date, total, dev})
		}
	}
	return
}

// GetJobsByMonth returns list of total and dev jobs by month
func GetJobsByMonth() (jobs []JobStatsEntry) {
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

	res := []JobStatsEntry{}
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
		qstr := "SELECT SUM(n_jobs_total),SUM(n_jobs_devs) FROM jobs "
		qstr += "WHERE check_date LIKE '" + date + "-%'"
		cursor, _ := db.Query(qstr)
		defer cursor.Close()
		for cursor.Next() {
			var ntot int
			var ndev int
			cursor.Scan(&ntot, &ndev)
			res = append(res, JobStatsEntry{date, ntot, ndev})
		}
	}
	return res
}

// GetJobsByYear returns list of total and dev jobs by month
func GetJobsByYear() (jobs []JobStatsEntry) {
	qstrDate := "SELECT date('now')"
	rowsDate := Q(qstrDate)
	defer rowsDate.Close()
	var date string
	var yearLast int
	if rowsDate.Next() {
		_ = rowsDate.Scan(&date)
		yearLast = s2i(date[:4])
	}

	res := []JobStatsEntry{}
	for i := 10; i > -1; i-- {
		qstr := "SELECT SUM(n_jobs_total),SUM(n_jobs_devs) FROM jobs "
		qstr += "WHERE check_date LIKE '" + i2s(yearLast-i) + "-%'"
		cursor, _ := db.Query(qstr)
		defer cursor.Close()
		for cursor.Next() {
			var ntot int
			var ndev int
			cursor.Scan(&ntot, &ndev)
			res = append(res, JobStatsEntry{i2s(yearLast - i), ntot, ndev})
		}
	}
	return res
}
