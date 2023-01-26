type DedicatedWorkerInterface = {
    worker: any // I don't know what type should come here. Ask someone regarding this...
    onMessageCtxNFunc: Function
}

class DedicatedWorker implements DedicatedWorkerInterface{
    
    worker: any // I don't know what type should come here. Ask someone regarding this...
    onMessageCtxNFunc: Function

    constructor(onMessageCtxNFunc: Function) {
        if(window.Worker) {
            this.worker = new Worker(new URL('./worker_utils.tsx', import.meta.url));
            this.worker.onmessage = (e: any) => {
                console.log("onMessage ==> ",e.data)
                this.onMessageCtxNFunc.apply(this.onMessageCtxNFunc, [e.data])
            }
            this.onMessageCtxNFunc = onMessageCtxNFunc
        }
        else {
            throw new Error('WebWorker not supported by browser. Please use an updated browser.');
        }
    }

    postMessage(data = {}, transferData = []) {
        this.worker.postMessage(data, transferData)
    }
}

export default DedicatedWorker;