package main

import (
	"database/sql"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"os"

	"github.com/Evedel/HottestTechs/db"

	"github.com/gin-gonic/gin"
	"github.com/google/logger"
	_ "github.com/mattn/go-sqlite3"
)

// DB is the main db connection
var DB *sql.DB

const loggerPath = "/var/log/api/state.log"
const ginPath = "/var/log/api/access.log"
const dbPath = "./hottesttechs.db"

func main() {
	isDev := false

	if isDev {
		logger.Init("LoggerExample", true, false, ioutil.Discard)
	} else {
		lf1, _ := os.Open(loggerPath)
		defer lf1.Close()
		defer logger.Init("Logger", false, true, lf1).Close()
	}

	logger.SetFlags(log.Llongfile)
	logger.SetFlags(log.LstdFlags)

	DB = db.InitDB(dbPath)
	db.PrefetchTechs()

	if !isDev {
		gin.DisableConsoleColor()
		lf2, _ := os.Create(ginPath)
		gin.DefaultWriter = io.MultiWriter(lf2)
	}
	router := gin.Default()

	router.GET("/techs", handlerGetAllTechs)

	router.GET("/vacancies/day", handlerGetVacancies)
	router.GET("/vacancies/month", handlerGetVacanciesMonth)
	router.GET("/vacancies/year", handlerGetVacanciesYear)

	router.GET("/top/day", handlerGetTopByDay)
	router.GET("/top/month", handlerGetTopByMonth)
	router.GET("/top/year", handlerGetTopByYear)

	router.GET("/jobs/day", handlerGetJobsByDay)
	router.GET("/jobs/month", handlerGetJobsByMonth)
	router.GET("/jobs/year", handlerGetJobsByYear)

	router.GET("/associations/day", handlerGetAssociationsByDay)
	router.GET("/associations/month", handlerGetAssociationsByMonth)
	router.GET("/associations/year", handlerGetAssociationsByYear)

	router.Run(":8090")
}

func handlerGetJobsByDay(c *gin.Context) {
	list := db.GetJobsByDay()
	if list == nil {
		c.String(http.StatusInternalServerError, "there was an error")
		return
	}
	c.JSON(http.StatusOK, list)
}

func handlerGetJobsByMonth(c *gin.Context) {
	list := db.GetJobsByMonth()
	if list == nil {
		c.String(http.StatusInternalServerError, "there was an error")
		return
	}
	c.JSON(http.StatusOK, list)
}

func handlerGetJobsByYear(c *gin.Context) {
	list := db.GetJobsByYear()
	if list == nil {
		c.String(http.StatusInternalServerError, "there was an error")
		return
	}
	c.JSON(http.StatusOK, list)
}

func handlerGetTopByDay(c *gin.Context) {
	top := db.GetTopByDay("'now'")
	if top.List == nil {
		c.String(http.StatusInternalServerError, "there was an error")
		return
	}
	var days = []string{"1", "2", "3"}
	i := 0
	for (len(top.List) == 0) && (i < len(days)) {
		top = db.GetTopByDay("'now', '-" + days[i] + " day'")
		i++
	}
	c.JSON(http.StatusOK, top)
}

func handlerGetTopByMonth(c *gin.Context) {
	top := db.GetTopByMonth()
	if top.List == nil {
		c.String(http.StatusInternalServerError, "there was an error")
		return
	}
	c.JSON(http.StatusOK, top)
}

func handlerGetTopByYear(c *gin.Context) {
	top := db.GetTopByYear()
	if top.List == nil {
		c.String(http.StatusInternalServerError, "there was an error")
		return
	}
	c.JSON(http.StatusOK, top)
}

func handlerGetAllTechs(c *gin.Context) {
	list := db.GetAllTechs()
	if list == nil {
		c.String(http.StatusInternalServerError, "there was an error")
		return
	}
	c.JSON(http.StatusOK, list)
}

func handlerGetVacancies(c *gin.Context) {
	id := db.GetIDFromVacancyName(c.Query("tech"))
	if id < 0 {
		c.String(http.StatusNotFound, "there is no such tech"+c.Query("tech"))
	} else {
		res := db.GetVacanciesVSDaysForTech(id)
		c.JSON(http.StatusOK, res)
	}
}

func handlerGetVacanciesMonth(c *gin.Context) {
	id := db.GetIDFromVacancyName(c.Query("tech"))
	if id < 0 {
		c.String(http.StatusNotFound, "there is no such tech"+c.Query("tech"))
	} else {
		res := db.GetVacanciesVSMonthForTech(id)
		c.JSON(http.StatusOK, res)
	}
}

func handlerGetVacanciesYear(c *gin.Context) {
	id := db.GetIDFromVacancyName(c.Query("tech"))
	if id < 0 {
		c.String(http.StatusNotFound, "there is no such tech"+c.Query("tech"))
	} else {
		res := db.GetVacanciesVSYearForTech(id)
		c.JSON(http.StatusOK, res)
	}
}

func handlerGetAssociationsByDay(c *gin.Context) {
	id := db.GetIDFromVacancyName(c.Query("tech"))
	if id < 0 {
		c.String(http.StatusNotFound, "there is no such tech"+c.Query("tech"))
	} else {
		res := db.GetAssociationsByDays(id, "now")
		var days = []string{"1", "2", "3"}
		if res.List == nil {
			i := 0
			for (len(res.List) == 0) && (i < len(days)) {
				res = db.GetAssociationsByDays(id, "now', '-"+days[i]+" day")
				i++
			}
		}
		c.JSON(http.StatusOK, res)
	}
}

func handlerGetAssociationsByMonth(c *gin.Context) {
	id := db.GetIDFromVacancyName(c.Query("tech"))
	if id < 0 {
		c.String(http.StatusNotFound, "there is no such tech"+c.Query("tech"))
	} else {
		res := db.GetAssociationsByMonth(id, "now")
		c.JSON(http.StatusOK, res)
	}
}

func handlerGetAssociationsByYear(c *gin.Context) {
	id := db.GetIDFromVacancyName(c.Query("tech"))
	if id < 0 {
		c.String(http.StatusNotFound, "there is no such tech"+c.Query("tech"))
	} else {
		res := db.GetAssociationsByYear(id, "now")
		c.JSON(http.StatusOK, res)
	}
}
