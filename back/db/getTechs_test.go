package db

import (
	"io/ioutil"
	"testing"

	"github.com/google/logger"
	_ "github.com/mattn/go-sqlite3"
)

func TestGetTopByDay(t *testing.T) {
	InitDB("../hottesttechs.db")
	PrefetchTechs()

	logger.Init("LoggerExample", true, false, ioutil.Discard)

	top1 := GetTopByDay("'2020-10-21'")
	if top1.List == nil {
		t.Error("returned error")
	}
	top2 := GetTopByDay("'2020-10-20'")
	if len(top2.List) == 0 {
		t.Error("returned empty list")
	}
	for i := range top2.List {
		if i > 0 {
			if top2.List[i-1].Amount < top2.List[i].Amount {
				t.Error("return list in wrong order")
				break
			}
		}
	}
	if len(top1.List) == len(top2.List) {
		t.Error("returned wrong lists")
	}
	top3 := GetTopByDay("'2020-10-21'")
	if len(top1.List) != len(top3.List) {
		t.Error("returned wrong lists")
	}
	top4 := GetTopByDay("'now','+2 day'")
	if len(top4.List) != 0 {
		t.Error("should return no data for future queries")
	}
}
