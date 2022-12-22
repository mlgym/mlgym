type reduxData = {
    grid_search_id: string,
    experiments: {
        [key: string]: {
            data: {
                labels: Array<number>,
                datasets: Array<{
                    exp_id: number,
                    label: string,
                    data: Array<number>,
                    fill: Boolean,
                    backgroundColor: string,
                    borderColor: string 
                }>
            },
            options: {
                plugins: {
                    title: {
                        display: Boolean,
                        text: string,
                        color: string,
                        font: {
                            weight: string,
                            size: string
                        }
                    }
                }
            },
            ids_to_track_and_find_exp_id: Array<number>
        };
    },
    colors_mapped_to_exp_id: {
        [key: number]: string
    }
}

type data = {
    epoch: number,
    grid_search_id: string, 
    experiment_id: number,
    metric_scores: Array<{
        metric: string, 
        split: string,
        score: number
    }>,
    loss_scores: Array<{
        loss: string, 
        split: string,
        score: number
    }>
}

const handleExperimentStatusData = (data: data, reduxData: reduxData) => {
    let exp = undefined;
    if(reduxData.grid_search_id !== null) {
        exp = reduxData.experiments;
    }
    else {
        reduxData.grid_search_id = data.grid_search_id;
        exp = {}
    }

    if(reduxData.colors_mapped_to_exp_id[data.experiment_id] === undefined) {
        let random_color = getRandomColor();
        reduxData.colors_mapped_to_exp_id[data.experiment_id] = random_color;
    }

    for(let i=0; i<data.loss_scores.length; i++)
    {
        let d = data.loss_scores[i]
        if(exp[d.split + "_" + d.loss] === undefined) {
            exp[d.split + "_" + d.loss] = {
                data: {
                    labels: [],
                    datasets: []
                },
                options: {
                    plugins: {
                        title: {
                            display: true,
                            text: (d.split + " " + d.loss.split("_").join(" ")).toLowerCase(),
                            color: 'black',
                            font: {
                                weight: 'bold',
                                size: '20px'
                            }
                        }
                    }
                },
                ids_to_track_and_find_exp_id: []
            }
        }

        let prevIndex = null;
        if(exp[d.split + "_" + d.loss].ids_to_track_and_find_exp_id.includes(data.experiment_id)){
            prevIndex = exp[d.split + "_" + d.loss].ids_to_track_and_find_exp_id.indexOf(data.experiment_id)
        }
        else {
            exp[d.split + "_" + d.loss].ids_to_track_and_find_exp_id.push(data.experiment_id);
        }

        if(!exp[d.split + "_" + d.loss].data.labels.includes(data.epoch)) {
            exp[d.split + "_" + d.loss].data.labels.push(data.epoch);
        }

        if(prevIndex!==null) {
            exp[d.split + "_" + d.loss].data.datasets[prevIndex].data = [...exp[d.split + "_" + d.loss].data.datasets[prevIndex].data, d.score]
        }
        else {
            exp[d.split + "_" + d.loss].data.datasets.push({
                exp_id: data.experiment_id,
                label: "experiment_"+data.experiment_id.toString(),
                data: [d.score],
                fill: false,
                backgroundColor: reduxData.colors_mapped_to_exp_id[data.experiment_id],
                borderColor: reduxData.colors_mapped_to_exp_id[data.experiment_id]
            });
        }
        exp[d.split + "_" + d.loss].data.datasets.sort((a,b) => (a.exp_id > b.exp_id) ? 1 : -1)
        exp[d.split + "_" + d.loss].ids_to_track_and_find_exp_id.sort((a,b) => (a > b) ? 1 : -1)
    }

    for(let i=0; i<data.metric_scores.length; i++)
    {
        let d = data.metric_scores[i]
        if(exp[d.split + "_" + d.metric] === undefined) {
            exp[d.split + "_" + d.metric] = {
                data: {
                    labels: [],
                    datasets: []
                },
                options: {
                    plugins: {
                        title: {
                            display: true,
                            text: (d.split + " " + d.metric.split("_").join(" ")).toLowerCase(),
                            color: 'black',
                            font: {
                                weight: 'bold',
                                size: '20px'
                            }
                        }
                    }
                },
                ids_to_track_and_find_exp_id: []
            }
        }

        let prevIndex = null;
        if(exp[d.split + "_" + d.metric].ids_to_track_and_find_exp_id.includes(data.experiment_id)){
            prevIndex = exp[d.split + "_" + d.metric].ids_to_track_and_find_exp_id.indexOf(data.experiment_id)
        }
        else {
            exp[d.split + "_" + d.metric].ids_to_track_and_find_exp_id.push(data.experiment_id);
        }

        if(!exp[d.split + "_" + d.metric].data.labels.includes(data.epoch)) {
            exp[d.split + "_" + d.metric].data.labels.push(data.epoch);
        }

        if(prevIndex!==null) {
            exp[d.split + "_" + d.metric].data.datasets[prevIndex].data = [...exp[d.split + "_" + d.metric].data.datasets[prevIndex].data, d.score]
        }
        else {
            exp[d.split + "_" + d.metric].data.datasets.push({
                exp_id: data.experiment_id,
                label: "experiment_"+data.experiment_id.toString(),
                data: [d.score],
                fill: false,
                backgroundColor: reduxData.colors_mapped_to_exp_id[data.experiment_id],
                borderColor: reduxData.colors_mapped_to_exp_id[data.experiment_id]
            });
        }

        exp[d.split + "_" + d.metric].data.datasets.sort((a,b) => (a.exp_id > b.exp_id) ? 1 : -1)
        exp[d.split + "_" + d.metric].ids_to_track_and_find_exp_id.sort((a,b) => (a > b) ? 1 : -1)
    }
    
    reduxData.experiments = exp;
    // console.log("In Handle Exp reduxData = ",reduxData);
    
    return reduxData;
    
}

function getRandomColor() {
    var letters = '0123456789ABCDEF'.split('');
    var color = '#';
    for (var i = 0; i < 6; i++ ) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

export default handleExperimentStatusData;