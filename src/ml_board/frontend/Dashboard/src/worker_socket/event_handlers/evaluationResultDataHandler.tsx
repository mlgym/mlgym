// export interface evalResultCustomData {
//     grid_search_id: string | null, //TODO: move it to the statusSlice?
//     experiments: {
//         [key: string]: {
//             data: {
//                 labels: Array<number>, // the X-axis
//                 datasets: Array<{ // the experiments
//                     exp_id: number, // exp_id
//                     label: string, // exp_name
//                     data: Array<number>, // exp_values, same size as labels (X-axis)
//                     fill: Boolean,
//                     backgroundColor: string,
//                     borderColor: string,
//                     tension: number // to give smoothness to the line curves
//                 }>
//             },
//             // TODO: this is not needed here as it is the same for every graph except the Title!
//             options: {
//                 animation: {
//                     duration: number,
//                     easing: string
//                 }
//                 radius: number, // radius of the label tag
//                 hoverRadius: number, // on hover:: change of data point radius size
//                 hitRadius: number, // radius of mouse to show the label values when mouse is near a datapoint
//                 responsive: Boolean,
//                 maintainAspectRatio: Boolean,
//                 plugins: {
//                     title: {
//                         display: Boolean,
//                         text: string,
//                         color: string,
//                         font: {
//                             weight: string,
//                             size: string
//                         }
//                     },
//                     legend: {
//                         display: true,
//                         labels: {
//                             usePointStyle: boolean,
//                             pointStyle: string
//                         }
//                     }
//                 }
//             },
//             ids_to_track_and_find_exp_id: Array<number>
//         }
//     },
//     colors_mapped_to_exp_id: {
//         [key: number]: string
//     }
// }

// export interface EvaluationResultPayload {
//     epoch: number,
//     grid_search_id: string,
//     experiment_id: number,
//     metric_scores: Array<Score>,
//     loss_scores: Array<Score>
// }

// interface Score {
//     metric?: string,
//     loss?: string,
//     split: string,
//     score: number
// }

// export default function handleEvaluationResultData(evalResultCustomData: evalResultCustomData, evalResultSocketData: EvaluationResultPayload) {
//     // exp holds all experiments 
//     // if grid_search_id isn't null point to or copy the experiments else {}
//     let exp = undefined;
//     if (evalResultCustomData.grid_search_id !== null) {
//         exp = evalResultCustomData.experiments;
//     } else {
//         // TODO: Don't set the grid_search_id here!
//         evalResultCustomData.grid_search_id = evalResultSocketData.grid_search_id;
//         exp = {}
//     }

//     // if the incoming experiment doesn't have a color set a new random color for it
//     if (evalResultCustomData.colors_mapped_to_exp_id[evalResultSocketData.experiment_id] === undefined) {
//         evalResultCustomData.colors_mapped_to_exp_id[evalResultSocketData.experiment_id] = getRandomColor();
//     }

//     LooP(evalResultSocketData.loss_scores, (score: Score) => score.loss as string, exp, evalResultCustomData, evalResultSocketData);

//     LooP(evalResultSocketData.metric_scores, (score: Score) => score.metric as string, exp, evalResultCustomData, evalResultSocketData);

//     // copy the final object back into the experiments
//     evalResultCustomData.experiments = exp;
//     // console.log("In Handle Exp evalResultCustomData = ",evalResultCustomData);

//     return evalResultCustomData;
// }

// function LooP(scores: Array<Score>, get_metric_or_loss: (score: Score) => string, exp:any, evalResultCustomData: evalResultCustomData, evalResultSocketData: EvaluationResultPayload) {
//     // loop over the array of scores
//     for (let i = 0; i < scores.length; i++) {
//         // score element
//         const score = scores[i];
//         const metric_or_loss = get_metric_or_loss(score);
//         // if Graph of this score isn't already there 
//         if (exp[score.split + "_" + metric_or_loss] === undefined) {
//             exp[score.split + "_" + metric_or_loss] = {
//                 // create new empty graph
//                 data: {
//                     labels: [],
//                     datasets: []
//                 },
//                 // with fixed options
//                 // TODO: REMOVE options from here!
//                 options: {
//                     animation: {
//                         duration: 300,
//                         easing: 'linear'
//                     },
//                     radius: 3,
//                     hoverRadius: 12,
//                     hitRadius: 20,
//                     responsive: true,
//                     maintainAspectRatio: false,
//                     plugins: {
//                         title: {
//                             display: true,
//                             // except here 
//                             text: (score.split + " " + metric_or_loss.split("_").join(" ")).toLowerCase(),
//                             color: 'black',
//                             font: {
//                                 weight: 'bold',
//                                 size: '20px'
//                             }
//                         },
//                         legend: {
//                             display: true,
//                             labels: {
//                                 usePointStyle: true,
//                                 pointStyle: 'circle'
//                             }
//                         }
//                     }
//                 },
//                 ids_to_track_and_find_exp_id: []
//             }
//         }

//         let prevIndex = null;
//         // IF a Graph for this score already exists get the index of experiment_id in it ELSE add it
//         if (exp[score.split + "_" + metric_or_loss].ids_to_track_and_find_exp_id.includes(evalResultSocketData.experiment_id)) {
//             prevIndex = exp[score.split + "_" + metric_or_loss].ids_to_track_and_find_exp_id.indexOf(evalResultSocketData.experiment_id)
//         }
//         else {
//             exp[score.split + "_" + metric_or_loss].ids_to_track_and_find_exp_id.push(evalResultSocketData.experiment_id);
//         }

//         // if this epoch isn't yet in this Graph score add it
//         if (!exp[score.split + "_" + metric_or_loss].data.labels.includes(evalResultSocketData.epoch)) {
//             exp[score.split + "_" + metric_or_loss].data.labels.push(evalResultSocketData.epoch);
//         }

//         // add the new score point to the Graph if it exits
//         if (prevIndex !== null) {
//             exp[score.split + "_" + metric_or_loss].data.datasets[prevIndex].data = [...exp[score.split + "_" + metric_or_loss].data.datasets[prevIndex].data, score.score]
//         }
//         else {
//             // ELSE 
//             exp[score.split + "_" + metric_or_loss].data.datasets.push({
//                 exp_id: evalResultSocketData.experiment_id,
//                 label: "experiment_" + evalResultSocketData.experiment_id.toString(),
//                 data: [score.score],
//                 fill: false,
//                 backgroundColor: evalResultCustomData.colors_mapped_to_exp_id[evalResultSocketData.experiment_id],
//                 borderColor: evalResultCustomData.colors_mapped_to_exp_id[evalResultSocketData.experiment_id],
//                 tension: 0
//             });
//         }
//         exp[score.split + "_" + metric_or_loss].data.datasets.sort((a: { exp_id: number }, b: { exp_id: number }) => (a.exp_id > b.exp_id) ? 1 : -1)
//         exp[score.split + "_" + metric_or_loss].ids_to_track_and_find_exp_id.sort((a: number, b: number) => (a > b) ? 1 : -1)
//     }
// }

export { };

// // TODO: should be moved to the statusSlice maybe ?
// function getRandomColor() {
//     let letters = '0123456789ABCDEF'.split('');
//     let color = '#';
//     for (let i = 0; i < 6; i++) {
//         color += letters[Math.floor(Math.random() * 16)];
//     }
//     return color;
// }

