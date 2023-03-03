interface DedicatedWorkerInterface {
    worker: Worker
    onMessageCtxNFunc: Function
}

class DedicatedWorker implements DedicatedWorkerInterface{
    
    worker: Worker
    onMessageCtxNFunc: Function

    constructor(onMessageCtxNFunc: Function) {
        if(window.Worker) {
            this.worker = new Worker(new URL('./worker_utils.tsx', import.meta.url));
            this.worker.onmessage = (e: MessageEvent) => {
                this.onMessageCtxNFunc.apply(this.onMessageCtxNFunc, [e.data])
            }
            this.onMessageCtxNFunc = onMessageCtxNFunc;
        }
        else {
            throw new Error('WebWorker not supported by browser. Please use an updated browser.');
        }
    }

    postMessage(data={}) {
        this.worker.postMessage(data);
    }
}

export default DedicatedWorker;