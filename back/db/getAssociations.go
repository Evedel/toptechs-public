package db

import "fmt"

// AssociationResponse structure
type AssociationResponse struct {
	Date string
	List []AssociationEntry
}

// AssociationEntry structure
type AssociationEntry struct {
	Rank   int
	Name   string
	Amount int
}

// GetAssociationsByDays return connectivity info for tech for day
func GetAssociationsByDays(tid int, day string) (result AssociationResponse) {
	qstrDate := "SELECT date('" + day + "')"
	rowsDate := Q(qstrDate)
	defer rowsDate.Close()
	var date string
	if rowsDate.Next() {
		_ = rowsDate.Scan(&date)
	}
	result.List = nil
	result.Date = date

	qstr := "SELECT t1, t2, SUM(amount) FROM ("
	qstr += "SELECT tech_id AS t1, linked_tech_id AS t2, amount "
	qstr += fmt.Sprintf("FROM groups WHERE tech_id=%d ", tid)
	qstr += fmt.Sprintf("AND check_date=DATE('%s') ", day)
	qstr += "UNION ALL "
	qstr += "SELECT linked_tech_id AS t1, tech_id AS t2, amount "
	qstr += fmt.Sprintf("FROM groups WHERE linked_tech_id=%d ", tid)
	qstr += fmt.Sprintf("AND check_date=DATE('%s') ", day)
	qstr += ") subquery1 "
	qstr += "GROUP BY t2 ORDER BY SUM(amount) DESC "
	rows := Q(qstr)
	defer rows.Close()

	result.List = []AssociationEntry{}
	rank := 1
	for rows.Next() {
		t1 := 0
		t2 := 0
		am := 0
		rows.Scan(&t1, &t2, &am)
		result.List = append(result.List, AssociationEntry{rank, cacheTechs[t2], am})
		rank++
	}
	if len(result.List) == 0 {
		result.List = nil
	}
	return
}

// GetAssociationsByMonth return connectivity info for tech for the last month
func GetAssociationsByMonth(tid int, day string) (result AssociationResponse) {
	qstrDate := "SELECT date('" + day + "')"
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
	result.List = nil
	result.Date = date
	qstr := "SELECT t1, t2, SUM(amount) FROM ("
	qstr += "SELECT tech_id AS t1, linked_tech_id AS t2, amount "
	qstr += fmt.Sprintf("FROM groups WHERE tech_id=%d ", tid)
	qstr += "AND check_date LIKE '" + date + "-%' "
	qstr += "UNION ALL "
	qstr += "SELECT linked_tech_id AS t1, tech_id AS t2, amount "
	qstr += fmt.Sprintf("FROM groups WHERE linked_tech_id=%d ", tid)
	qstr += "AND check_date LIKE '" + date + "-%' "
	qstr += ") subquery1 "
	qstr += "GROUP BY t2 ORDER BY SUM(amount) DESC "
	rows := Q(qstr)
	defer rows.Close()

	result.List = []AssociationEntry{}
	rank := 1
	for rows.Next() {
		t1 := 0
		t2 := 0
		am := 0
		rows.Scan(&t1, &t2, &am)
		result.List = append(result.List, AssociationEntry{rank, cacheTechs[t2], am})
		rank++
	}
	if len(result.List) == 0 {
		result.List = nil
	}
	return
}

// GetAssociationsByYear return connectivity info for tech for the last month
func GetAssociationsByYear(tid int, day string) (result AssociationResponse) {
	qstrDate := "SELECT date('" + day + "')"
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
		date = i2s(year)
	}
	result.List = nil
	result.Date = date

	qstr := "SELECT t1, t2, SUM(amount) FROM ("
	qstr += "SELECT tech_id AS t1, linked_tech_id AS t2, amount "
	qstr += fmt.Sprintf("FROM groups WHERE tech_id=%d ", tid)
	qstr += "AND check_date LIKE '" + date + "-%' "
	qstr += "UNION ALL "
	qstr += "SELECT linked_tech_id AS t1, tech_id AS t2, amount "
	qstr += fmt.Sprintf("FROM groups WHERE linked_tech_id=%d ", tid)
	qstr += "AND check_date LIKE '" + date + "-%' "
	qstr += ") subquery1 "
	qstr += "GROUP BY t2 ORDER BY SUM(amount) DESC "
	rows := Q(qstr)
	defer rows.Close()

	result.List = []AssociationEntry{}
	rank := 1
	for rows.Next() {
		t1 := 0
		t2 := 0
		am := 0
		rows.Scan(&t1, &t2, &am)
		result.List = append(result.List, AssociationEntry{rank, cacheTechs[t2], am})
		rank++
	}
	if len(result.List) == 0 {
		result.List = nil
	}
	return
}
