"use strict";

const App = {
  data() {
    return {
      top_techs: [],
      chartTechs: null,
      chartJobs: null,
      techsData: {
        labels: [],
        techs: [],
        datasets: [],
        colors: [],
        bgcolors: [],
      },
      chartsLabelsNumber: 8,
      manualSelection: false,
      server_addr: "http://localhost",
      isChartTechsReady: true,
      all_techs: [],
      ch_jobs_dataTotal: [],
      ch_jobs_dataDevs: [],
      ch_jobs_dataLabels: [],
      currentTab: 'day',
      allTabs: ['day', 'month', 'year'],
      currentDate: '',
      styleinlistbuttonselected: 'style-in-list-button-selected',
      associationsCloudTechName: '',
      associationsCloudElements: [],
      isTopUpdated: false,
    };
  },
  mounted() {
    this.initialise()
  },
  created() {
    this.refreshScrollableArea = setInterval(() => {
        const { offsetWidth, offsetHeight } = document.getElementById('app');
        if ((this.appHeight != offsetHeight) || (this.appWidth != offsetWidth)) {
          if (this.associationsCloudTechName != '') {
            this.createTechAssociationCloud(this.associationsCloudTechName)
          }
        }
        this.appWidth = offsetWidth;
        this.appHeight = offsetHeight;
        if (this.appWidth < 1000) {
          this.chartsLabelsNumber = 5
        }
        if (this.appWidth < 500) {
          this.chartsLabelsNumber = 2.5
        }
    }, 1000);
  },
  methods: {
    initialise() {
      const { offsetWidth, offsetHeight } = document.getElementById('app');
      if (offsetWidth < 1000) {
        this.chartsLabelsNumber = 5
      }
      if (offsetWidth < 500) {
        this.chartsLabelsNumber = 2.5
      }

      this.isTopUpdated = false
      this.fillTop()
      const timer = async () => {
        while (!this.isTopUpdated) {
          await new Promise(r => setTimeout(r, 100));
        }
        this.fillVacancies(this.top_techs.slice(0,3).map(x => x.Name))
        this.associationsCloudTechName = this.top_techs[0].Name
      }
      timer()
      axios.get(this.server_addr+'/api/v1/techs')
        .then(response => {
          this.all_techs = response.data
        })
      this.fillJobs()
    },
    fillTop() {
      var q = this.server_addr+'/api/v1/top/'+this.currentTab
      axios.get(q)
        .then(response => {
          this.top_techs = response.data.List
          this.currentDate = response.data.Date
          this.isTopUpdated = true
        })
    },
    fillVacancies(techsList) {
      const graphDrawer = async () => {
        for (var i = 0; i < techsList.length; i++) {
          
          this.addDataTechByDays(techsList[i])
          while (!this.isChartTechsReady) {
            await new Promise(r => setTimeout(r, 100));
          }
        }
        this.createTechAssociationCloud(this.associationsCloudTechName)
      }
      graphDrawer()
    },
    fillJobs() {
      axios.get(this.server_addr+'/api/v1/jobs/'+this.currentTab)
        .then(response => {
          response.data.forEach(element => {
            this.ch_jobs_dataLabels.push(element.Date)
            this.ch_jobs_dataTotal.push(element.Total)
            this.ch_jobs_dataDevs.push(element.Dev)
          });
          this.createNewChartJobs()
        })
    },
    switchTabTo(value) {
      this.currentTab = value
      var selectedTechs
      if (this.manualSelection) {
        selectedTechs = [...this.techsData.techs]
      }
      this.clearChartTechs()
      this.clearChartJobs()
      if (this.manualSelection) {
        
        this.fillVacancies(selectedTechs)
        this.fillTop()
        this.fillJobs()
      } else {
        
        this.initialise()
      }
    },
    clickClearChartTechs() {
      this.manualSelection = false
      this.clearChartTechs()
    },
    clickTechName(tech) {
      this.manualSelection = true
      this.addDataTechByDays(tech)
      if (this.techsData.techs.includes(tech)) return
      this.createTechAssociationCloud(tech)
    },
    updateChartTechsData(newTech, newLabels, newDataset) {
      if (this.techsData.techs.length == 0) {
        this.techsData.techs.push(newTech)
        this.techsData.labels = [...newLabels]
        this.techsData.datasets.push(newDataset)
        var r = Math.random()*255
        var g = Math.random()*255
        var b = Math.random()*255
        this.techsData.colors.push('rgba('+r+', '+g+', '+b+', 1)')
        this.techsData.bgcolors.push('rgba('+r+', '+g+', '+b+', 0.05)')
        // this.techsData.bgcolors.push('rgba(255,255,255,0)')
      } else {
        if (this.techsData.techs.includes(newTech)) {
          var i = this.techsData.techs.indexOf(newTech)
          this.techsData.techs.splice(i,1)
          this.techsData.datasets.splice(i,1)
          this.techsData.colors.splice(i,1)
          this.techsData.bgcolors.splice(i,1)
          return
        }
        this.techsData.techs.push(newTech)
        var r = Math.random()*255
        var g = Math.random()*255
        var b = Math.random()*255
        this.techsData.colors.push('rgba('+r+', '+g+', '+b+', 1)')
        this.techsData.bgcolors.push('rgba('+r+', '+g+', '+b+', 0.05)')
        // this.techsData.bgcolors.push('rgba(255,255,255,0)')
        var oldLabels = [...this.techsData.labels]
        var iOld=0
        var iNew=0
        this.techsData.labels = []
        while ((iOld < oldLabels.length) && (iNew < newLabels.length)) {
          if (oldLabels[iOld] < newLabels[iNew]) {
            this.techsData.labels.push(oldLabels[iOld])
            iOld++
          } else if (oldLabels[iOld] > newLabels[iNew]) {
            this.techsData.labels.push(newLabels[iNew])
            iNew++
          } else {
            this.techsData.labels.push(oldLabels[iOld])
            iOld++
            iNew++
          }
        }
        while (iNew < newLabels.length) {
          this.techsData.labels.push(newLabels[iNew])
          iNew++
        }
        while (iOld < oldLabels.length) {
          this.techsData.labels.push(oldLabels[iOld])
          iOld++
        }
        for (var i=0; i<this.techsData.datasets.length;i++) {
          var oldDataSet = [...this.techsData.datasets[i]]
          this.techsData.datasets[i] = []
          var iOld = 0
          for (var j=0; j<this.techsData.labels.length; j++) {
            if (this.techsData.labels[j] == oldLabels[iOld]) {
              this.techsData.datasets[i].push(oldDataSet[iOld])
              iOld++
            } else {
              this.techsData.datasets[i].push(0)
            }
          }
        }
        this.techsData.datasets.push([])
        i = this.techsData.datasets.length-1
        iNew = 0
        for (var j=0; j<this.techsData.labels.length; j++) {
          if (this.techsData.labels[j] == newLabels[iNew]) {
            this.techsData.datasets[i].push(newDataset[iNew])
            iNew++
          } else {
            this.techsData.datasets[i].push(0)
          }
        }
      }
    },
    addDataTechByDays(tech) {
      if (!this.isChartTechsReady) return
      this.isChartTechsReady = false
      var q = this.server_addr
      q += '/api/v1/vacancies/'+this.currentTab
      q += '\?tech\='+encodeURIComponent(tech)
      axios.get(q)
        .then(response => {
          var dates = []
          var amounts = []
          response.data.forEach(element => {
            dates.push(element.Date)
            amounts.push(element.Amount)
          })
          this.updateChartTechsData(tech, dates, amounts.map(x=>+x))
          if (this.chartTechs == null) {
            this.createNewChartTechs()
          } else {
            this.redrawChartTechsLines()
          }
        })
    },
    createNewChartTechs() {
      var ctx = document.getElementById('chart-canvas-techs').getContext('2d');
      this.chartTechs = new Chart(ctx, {
        type: 'line',
        data: {
          labels: this.techsData.labels,
          datasets: [{
            label: this.techsData.techs[0],
            data: this.techsData.datasets[0],
            borderColor: this.techsData.colors[0],
            backgroundColor: this.techsData.bgcolors[0],
            pointHoverBorderColor: this.techsData.colors[0],
            pointHoverBackgroundColor: this.techsData.bgcolors[0],
          }]
        },
        options: {
          title: {
            display: true,
            text: 'Number of vacancies per '+this.currentTab+', where techs were mentioned'
          },
          animation: {
            duration: 0,
            onComplete: () => {
              this.isChartTechsReady = true
            },
          },
          legend: {
            position: "bottom",
            labels: {
              boxWidth: 12,
              boxHeight: 10,
            }
          },
          responsive:true,
          maintainAspectRatio: false,
          scales: {
            xAxes: [{
              ticks: {
                  autoSkip: true,
                  maxTicksLimit: this.chartsLabelsNumber,
                  maxRotation: 0,
                  minRotation: 0,
              }
            }],
            yAxes: [{
              display: true,
              position: 'left',
              ticks: {
                beginAtZero: true,
              }
            },{
              display: true,
              position: 'right',
              ticks: {
                beginAtZero: true,
              }
            }]
          },
          tooltips: {
            callbacks: {
              labelColor: function (tooltipItem, chartInstace) {
                return {
                  borderColor : chartInstace.data.datasets[tooltipItem.datasetIndex].borderColor,
                  backgroundColor : chartInstace.data.datasets[tooltipItem.datasetIndex].backgroundColor,
                };
              }
            }
          }
        }
      });
    },
    createNewChartJobs() {
      var ctx = document.getElementById('chart-canvas-jobs').getContext('2d');
      this.chartJobs = new Chart(ctx, {
        type: 'line',
        data: {
          labels: this.ch_jobs_dataLabels,
          datasets: [{
            label: "Total Jobs",
            data: this.ch_jobs_dataTotal,
            borderColor: 'rgba(140,151,171,255)',
            backgroundColor: 'rgba(140,151,171,0.1)',
          },{
            label: "IT Jobs",
            data: this.ch_jobs_dataDevs,
            borderColor: 'rgba(0,46,82,255)',
            backgroundColor: 'rgba(0,46,82,0.1)',
          }]
        },
        options: {
          title: {
            display: true,
            text: 'Number of job postings per '+this.currentTab
          },
          animation: {
            duration: 0,
            onComplete: () => {
              this.isChartTechsReady = true
            },
          },
          legend: {
            position: "top",
            labels: {
              boxWidth: 12,
              boxHeight: 10,
            }
          },
          responsive:true,
          maintainAspectRatio: false,
          scales: {
            xAxes: [{
              ticks: {
                  autoSkip: true,
                  maxTicksLimit: this.chartsLabelsNumber,
                  maxRotation: 0,
                  minRotation: 0,
              }
            }],
            yAxes: [{
              position: 'left',
              display: true,
              ticks: {
                min: 0,
                callback: function(value, index, values) {
                  return Number(value.toString());
                },
              },
              afterBuildTicks: function(pckBarChart) {
                var defaulMax = pckBarChart.ticks[0]
                var maxD = 0
                pckBarChart.chart.config.data.datasets[1].data.forEach(e => {
                  if (e > maxD) { maxD = e }
                })
                pckBarChart.ticks = [];
                pckBarChart.ticks.push(0);
                pckBarChart.ticks.push(maxD);
                pckBarChart.ticks.push(defaulMax);
              }
            }]
          }
        }
      });
    },
    createTechAssociationCloud(tech) {
      this.associationsCloudTechName = tech

      var q = this.server_addr
      q += '/api/v1/associations/'+this.currentTab
      q += '\?tech\='+encodeURIComponent(tech)
      axios.get(q)
        .then(response => {
          var arr = []
          var maxAmount = 1
          if (response.data.List != null) {
            response.data.List.forEach(e => {
              if (e.Amount > maxAmount) { maxAmount = e.Amount}
            })
            var scale = 22.0/Math.sqrt(maxAmount)

            response.data.List.forEach(e => {
              var size = Math.sqrt(e.Amount)*scale
              var minSize = 10
              if (size < minSize) { size = minSize }
              var name = e.Name
              var parts = name.split(' ')
              if (parts.length > 1) {
                name = ''
                const syllableRegex = /[^aeiouy]*[aeiouy]+(?:[^aeiouy]*$|[^aeiouy](?=[^aeiouy]))?/gi;
                function syllabify(words) {
                    return words.match(syllableRegex);
                }
                parts.forEach( part => {
                  if (part.length > 5) {
                    var syllables = syllabify(part)
                    if ((syllables != null) && (syllables.length > 1)) {
                      name += syllables[0] + syllables[1][0] + "."
                    } else {
                      name += part + " "
                    }
                  } else {
                    name += part + " "
                  }
                })
              }
              arr.push([name+" ["+this.amountToHuman(e.Amount)+"]", size])
            })
          }
          WordCloud(document.getElementById('word-cloud'),
          {
            list: arr,
            shrinkToFit: false,
            drawOutOfBound: false,
            minRotation: 0,
            maxRotation: 0,
            fontFamily: 'Roboto',
            fontWeight: 200,
            clearCanvas: true,
            color: 'black',
            shape: 'square',
          });
        })
    },
    redrawChartTechsLines() {
      var currentNumberOfGraphs = this.chartTechs.data.datasets.length
      var desiredNumberOfGraphs = this.techsData.techs.length

      while (currentNumberOfGraphs != desiredNumberOfGraphs) {
        if (currentNumberOfGraphs < desiredNumberOfGraphs) {
          this.chartTechs.data.datasets.push({
            borderColor: this.techsData.colors[desiredNumberOfGraphs-1],
            backgroundColor: this.techsData.bgcolors[desiredNumberOfGraphs-1],
            label: this.techsData.techs[desiredNumberOfGraphs-1],
            data: this.techsData.datasets[desiredNumberOfGraphs-1],
            pointHoverBorderColor: this.techsData.colors[desiredNumberOfGraphs-1],
            pointHoverBackgroundColor: this.techsData.bgcolors[desiredNumberOfGraphs-1],
          })
        } else {
          for (var i=0; i<currentNumberOfGraphs; i++) {
            if (this.chartTechs.data.datasets[i].label != this.techsData.techs[i]) {
              this.chartTechs.data.datasets.splice(i, 1);
              break
            }
          }
        }
        currentNumberOfGraphs = this.chartTechs.data.datasets.length
        desiredNumberOfGraphs = this.techsData.techs.length  
      }

      if (this.chartTechs.data.labels.length != this.techsData.labels.length) {
        for (var i=0; i<currentNumberOfGraphs; i++) {
          this.chartTechs.data.datasets[i].data = [...this.techsData.datasets[i]]
        }
        this.chartTechs.data.labels = [...this.techsData.labels]
      }
      this.chartTechs.update()
      this.chartTechs.config.options.scales.yAxes[1].ticks.max = this.chartTechs.scales["y-axis-0"].max
      this.chartTechs.config.options.title.text = 'Number of vacancies per '+this.currentTab+', where techs were mentioned'
      this.chartTechs.update()
      
    },
    clearChartTechs() {
      if (this.chartTechs != null) {
        this.techsData.techs = []
        this.techsData.datasets = []
        this.techsData.colors = []
        this.techsData.bgcolors = []
        this.redrawChartTechsLines()
      }
    },
    clearChartJobs() {
      this.ch_jobs_dataLabels = []
      this.ch_jobs_dataTotal = []
      this.ch_jobs_dataDevs = []
      this.chartJobs.destroy()
    },
    selectedColorStyleTabs(thisTab) {
      if (this.currentTab == thisTab) {
         return {
          border: '2px solid #000',
          background: '#eee',
         };
      } else {
        return {
          border: '1px solid rgba(0,0,0,0.4)',
        }
      }
    },
    selectedColorStyleTech(tech) {
      var indx = this.techsData.techs.indexOf(tech)
      if (indx == -1) {
        return {
          border: '1px solid rgba(0,0,0,0.4)',
        }
      } else {
        var strnumbs = this.techsData.colors[indx]
          .replace(/ /g, '')
          .replace(')', '')
          .replace('rgba(', '')
          .split(',')
        var total = 0;
        for(var i = 0; i < strnumbs.length-1; i++) {
            total += parseFloat(strnumbs[i]);
        }
        var avg = total / strnumbs.length-1;
        // var textColor = avg < 127 ? 'white' : 'black'
        var textColor = 'black'
        return {
          backgroundColor: this.techsData.bgcolors[indx],
          border: '2px solid '+this.techsData.colors[indx],
          color: textColor
        }
      }
    },
    amountToHuman(amount) {
      if (amount < 1000) {
        return amount
      } else if (amount < 10000) {
        return (amount/1000).toFixed(1)+"K"
      } else if (amount < 99000) {
        return (amount/1000).toFixed(0)+"K"
      } else {
        return (amount/1000/1000).toFixed(1)+"M"
      }
    }
  },
};

const app = Vue.createApp(App)

app.mount('#app');
