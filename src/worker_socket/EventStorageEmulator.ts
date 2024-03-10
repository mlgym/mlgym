// (async function () {
//     try {
//         const run_config = await fetch(process.env.PUBLIC_URL + "/event_storage/2024-02-14--22-15-46/run_config.yml");
//         export await run_config.text();
//     } catch (error) {
//         console.error(error)
//     }
// })();


export { default as model_card } from '../event_storage/2024-02-14--22-15-46/1/model_card.json';
// export { default as event_storage } from '../event_storage/2024-02-14--22-15-46/event_storage.log';

export const experiment_config = Array.from({ length: 15 }, (_, i) => require(`../event_storage/2024-02-14--22-15-46/${i}/experiment_config.json`));

