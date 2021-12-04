package db

import (
	"io/ioutil"
	"math/rand"
	"os"
	"testing"

	"github.com/google/logger"
	_ "github.com/mattn/go-sqlite3"
)

func TestGetJobsStatsByDays(t *testing.T) {
	logger.Init("LoggerExample", true, false, ioutil.Discard)
	InitDB("./test.db")
	cstr := "CREATE TABLE IF NOT EXISTS jobs ("
	cstr += "check_date TEXT NOT NULL UNIQUE,"
	cstr += "n_jobs_total INTEGER NOT NULL,"
	cstr += "n_jobs_devs INTEGER NOT NULL)"
	E(cstr)

	jobsList := GetJobsByDay()
	if len(jobsList) != 0 {
		t.Error("returned non empty list for empty db")
	}

	dates := []string{}
	tots := []int{}
	devs := []int{}
	for i := 0; i < 10; i++ {
		idate := "2020-10-" + i2s(1+rand.Intn(30))
		itot := 100 + rand.Intn(500)
		idev := itot - rand.Intn(300)
		cstr := "INSERT OR IGNORE INTO jobs (check_date, n_jobs_total, n_jobs_devs) "
		cstr += "VALUES ('" + idate + "'," + i2s(itot) + "," + i2s(idev) + ")"
		E(cstr)
		dates = append(dates, idate)
		tots = append(tots, itot)
		devs = append(devs, idev)
	}

	jobsList = GetJobsByDay()
	if len(jobsList) != len(dates) {
		t.Error("returned list of the wrong length")
	}

	for i1 := range jobsList {
		for i2 := range dates {
			if dates[i2] == jobsList[i1].Date {
				if (tots[i2] != jobsList[i1].Total) || (devs[i2] != jobsList[i1].Dev) {
					t.Error("returned wrong pair result")
				}
			}
		}
	}

	db.Close()
	_ = os.Remove("./test.db")
}
