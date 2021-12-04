package db

import (
	"io/ioutil"
	"testing"

	"github.com/google/logger"
)

func TestGetAssociationsByDays(t *testing.T) {
	InitDB("../hottesttechs.db")
	PrefetchTechs()
	logger.Init("LoggerExample", true, false, ioutil.Discard)

	res1 := GetAssociationsByDays(2, "2020-07-11")
	if res1.List != nil {
		t.Error("expected empty list")
	}

	res2 := GetAssociationsByDays(2, "2020-10-28")
	// str := "AssociationResponse{"
	// str += "\"" + res2.Date + "\","
	// str += "[]AssociationEntry{"
	// for i, s := range res2.List {
	// 	str += "AssociationEntry{" + i2s(s.Rank) + ",\"" + s.Name + "\"," + i2s(s.Amount) + "}"
	// 	if i != len(res2.List)-1 {
	// 		str += ","
	// 	} else {
	// 		str += "}}"
	// 	}
	// }
	// logger.Infoln(str)
	want := AssociationResponse{"2020-10-28", []AssociationEntry{AssociationEntry{1, "Golang", 9}, AssociationEntry{2, "Azure", 6}, AssociationEntry{3, "Google Cloud Platform", 5}, AssociationEntry{4, "Monitoring", 4}, AssociationEntry{5, "Linux", 4}, AssociationEntry{6, "DevOps", 4}, AssociationEntry{7, "JavaScript", 4}, AssociationEntry{8, "Networking", 3}, AssociationEntry{9, "REST", 3}, AssociationEntry{10, "AWS S3", 3}, AssociationEntry{11, "Docker", 3}, AssociationEntry{12, "VMWare", 2}, AssociationEntry{13, "NoSQL", 2}, AssociationEntry{14, "AWS Lambda", 2}, AssociationEntry{15, "CI/CD", 2}, AssociationEntry{16, "Mocha", 2}, AssociationEntry{17, "HTML", 2}, AssociationEntry{18, "Terraform", 2}, AssociationEntry{19, "Kubernetes", 2}, AssociationEntry{20, "Ansible", 2}, AssociationEntry{21, "Chef", 2}, AssociationEntry{22, "CSS", 2}, AssociationEntry{23, "Microsoft Windows Server", 2}, AssociationEntry{24, "ReactJS", 2}, AssociationEntry{25, "SQL", 2}, AssociationEntry{26, "Tomcat", 1}, AssociationEntry{27, "Kibana", 1}, AssociationEntry{28, "git", 1}, AssociationEntry{29, "API Gateway", 1}, AssociationEntry{30, "Data Science", 1}, AssociationEntry{31, "Teradata", 1}, AssociationEntry{32, "Containerisation", 1}, AssociationEntry{33, "Firewall", 1}, AssociationEntry{34, "GitLab", 1}, AssociationEntry{35, "High Availability", 1}, AssociationEntry{36, "BitBucket", 1}, AssociationEntry{37, "Jest", 1}, AssociationEntry{38, "Jasmine", 1}, AssociationEntry{39, "TCP/IP", 1}, AssociationEntry{40, "Typescript", 1}, AssociationEntry{41, "Cloudformation", 1}, AssociationEntry{42, "Puppet", 1}, AssociationEntry{43, "PHP", 1}, AssociationEntry{44, "MySQL", 1}, AssociationEntry{45, "Apache", 1}, AssociationEntry{46, "GraphQL", 1}, AssociationEntry{47, "AngularJS", 1}, AssociationEntry{48, ".NET", 1}, AssociationEntry{49, "Ruby", 1}, AssociationEntry{50, "Cassandra", 1}, AssociationEntry{51, "Azure ML", 1}, AssociationEntry{52, "Data Mining", 1}, AssociationEntry{53, "Machine Learning", 1}, AssociationEntry{54, "Hadoop", 1}, AssociationEntry{55, "Data Engineering", 1}, AssociationEntry{56, "Java", 1}, AssociationEntry{57, "Kotlin", 1}, AssociationEntry{58, "PostgreSQL", 1}, AssociationEntry{59, "NodeJS", 1}, AssociationEntry{60, "ActiveDirectory", 1}, AssociationEntry{61, "Jenkins", 1}, AssociationEntry{62, "Aurora", 1}, AssociationEntry{63, "Bash", 1}, AssociationEntry{64, "R", 1}, AssociationEntry{65, "Python", 1}}}
	if res2.Date != want.Date {
		t.Error("returned dates are different")
	}
	for i := range res2.List {
		if res2.List[i] != want.List[i] {
			t.Error("returned values are different")
		}
	}
}

// qstr  = "SELECT t1, t2, SUM(amount) FROM ("
// qstr += "SELECT tech_id AS t1, linked_tech_id AS t2, amount "
// qstr += f"FROM groups WHERE tech_id={tid} "
// qstr += "UNION ALL "
// qstr += "SELECT linked_tech_id AS t1, tech_id AS t2, amount "
// qstr += f"FROM groups WHERE linked_tech_id={tid} ) subquery1 "
// qstr += "GROUP BY t2 ORDER BY SUM(amount) DESC "
