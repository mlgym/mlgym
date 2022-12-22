type DedicatedWorkerClassInterface = {
    worker: any // I don't know what type should come here. Ask someone regarding this...
    userCallbacks: {
        onMessageCtxNFunc: Function | null
    }
}

class DedicatedWorkerClass implements DedicatedWorkerClassInterface{
    
    worker: any // I don't know what type should come here. Ask someone regarding this...
    userCallbacks: {
        onMessageCtxNFunc: Function | null
    }

    constructor(onMessageCtxNFunc = null) {
        if(window.Worker) {
            this.worker = new Worker(new URL('./worker.tsx', import.meta.url));
            this.worker.onmessage = (e: any) => {
                this.onMessage(e);
            }
            this.userCallbacks = {
                onMessageCtxNFunc
            }
        }
        else {
            throw new Error('WebWorker not supported by browser. Please use an updated browser.');
        }
    }

    postMessage(data = {}, transferData = []) {
        this.worker.postMessage(data, transferData)
    }

    onMessage(e:any) {
        if (this.userCallbacks !== null) {
            this.userCallbacks.onMessageCtxNFunc && 
            this.userCallbacks.onMessageCtxNFunc.apply(this.userCallbacks.onMessageCtxNFunc, [e.data])
        }
    }
}

export default DedicatedWorkerClass;