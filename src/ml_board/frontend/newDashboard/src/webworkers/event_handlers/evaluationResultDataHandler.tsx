type evalResultCustomData = {
    grid_search_id: string,
    event_type: string,
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
        }
    },
    colors_mapped_to_exp_id: {
        [key: number]: string
    }
}

type evalResultSocketData = {
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

const handleEvaluationResultData = (event_type: string, evalResultCustomData: evalResultCustomData, evalResultSocketData: evalResultSocketData) => {
    let exp = undefined;
    if(evalResultCustomData.grid_search_id !== null) {
        exp = evalResultCustomData.experiments;
    }
    else {
        evalResultCustomData.grid_search_id = evalResultSocketData.grid_search_id;
        evalResultCustomData.event_type = event_type
        exp = {}
    }

    if(evalResultCustomData.colors_mapped_to_exp_id[evalResultSocketData.experiment_id] === undefined) {
        let random_color = getRandomColor();
        evalResultCustomData.colors_mapped_to_exp_id[evalResultSocketData.experiment_id] = random_color;
    }

    for(let i=0; i<evalResultSocketData.loss_scores.length; i++)
    {
        let d = evalResultSocketData.loss_scores[i]
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
        if(exp[d.split + "_" + d.loss].ids_to_track_and_find_exp_id.includes(evalResultSocketData.experiment_id)){
            prevIndex = exp[d.split + "_" + d.loss].ids_to_track_and_find_exp_id.indexOf(evalResultSocketData.experiment_id)
        }
        else {
            exp[d.split + "_" + d.loss].ids_to_track_and_find_exp_id.push(evalResultSocketData.experiment_id);
        }

        if(!exp[d.split + "_" + d.loss].data.labels.includes(evalResultSocketData.epoch)) {
            exp[d.split + "_" + d.loss].data.labels.push(evalResultSocketData.epoch);
        }

        if(prevIndex!==null) {
            exp[d.split + "_" + d.loss].data.datasets[prevIndex].data = [...exp[d.split + "_" + d.loss].data.datasets[prevIndex].data, d.score]
        }
        else {
            exp[d.split + "_" + d.loss].data.datasets.push({
                exp_id: evalResultSocketData.experiment_id,
                label: "experiment_"+evalResultSocketData.experiment_id.toString(),
                data: [d.score],
                fill: false,
                backgroundColor: evalResultCustomData.colors_mapped_to_exp_id[evalResultSocketData.experiment_id],
                borderColor: evalResultCustomData.colors_mapped_to_exp_id[evalResultSocketData.experiment_id]
            });
        }
        exp[d.split + "_" + d.loss].data.datasets.sort((a,b) => (a.exp_id > b.exp_id) ? 1 : -1)
        exp[d.split + "_" + d.loss].ids_to_track_and_find_exp_id.sort((a,b) => (a > b) ? 1 : -1)
    }

    for(let i=0; i<evalResultSocketData.metric_scores.length; i++)
    {
        let d = evalResultSocketData.metric_scores[i]
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
        if(exp[d.split + "_" + d.metric].ids_to_track_and_find_exp_id.includes(evalResultSocketData.experiment_id)){
            prevIndex = exp[d.split + "_" + d.metric].ids_to_track_and_find_exp_id.indexOf(evalResultSocketData.experiment_id)
        }
        else {
            exp[d.split + "_" + d.metric].ids_to_track_and_find_exp_id.push(evalResultSocketData.experiment_id);
        }

        if(!exp[d.split + "_" + d.metric].data.labels.includes(evalResultSocketData.epoch)) {
            exp[d.split + "_" + d.metric].data.labels.push(evalResultSocketData.epoch);
        }

        if(prevIndex!==null) {
            exp[d.split + "_" + d.metric].data.datasets[prevIndex].data = [...exp[d.split + "_" + d.metric].data.datasets[prevIndex].data, d.score]
        }
        else {
            exp[d.split + "_" + d.metric].data.datasets.push({
                exp_id: evalResultSocketData.experiment_id,
                label: "experiment_"+evalResultSocketData.experiment_id.toString(),
                data: [d.score],
                fill: false,
                backgroundColor: evalResultCustomData.colors_mapped_to_exp_id[evalResultSocketData.experiment_id],
                borderColor: evalResultCustomData.colors_mapped_to_exp_id[evalResultSocketData.experiment_id]
            });
        }

        exp[d.split + "_" + d.metric].data.datasets.sort((a,b) => (a.exp_id > b.exp_id) ? 1 : -1)
        exp[d.split + "_" + d.metric].ids_to_track_and_find_exp_id.sort((a,b) => (a > b) ? 1 : -1)
    }
    
    evalResultCustomData.experiments = exp;
    // console.log("In Handle Exp evalResultCustomData = ",evalResultCustomData);
    
    return evalResultCustomData;
    
}

// TODO: const handleExperimentStatusDataForDashboard() [like above method]

function getRandomColor() {
    let letters = '0123456789ABCDEF'.split('');
    let color = '#';
    for (let i = 0; i < 6; i++ ) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

export {
    handleEvaluationResultData,
    type evalResultCustomData,
    type evalResultSocketData
    // TODO: export handleExperimentStatusDataForDashboard
} 