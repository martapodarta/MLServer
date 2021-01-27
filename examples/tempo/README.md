# Running a Tempo pipeline in MLServer

This example walks you through how to create and serialise a [Tempo pipeline](https://github.com/SeldonIO/tempo), which can then be served through MLServer.
This pipeline can contain custom Python arbitrary code.

## Creating the pipeline

The first step will be to create our Tempo pipeline.


```python
import numpy as np
import os

from tempo.serve.metadata import (
    ModelFramework,
    MetadataTensorParameters,
    MetadataTensor,
)
from tempo.serve.model import Model
from tempo.serve.pipeline import Pipeline
from tempo.serve.utils import pipeline
from tempo.seldon.docker import SeldonDockerRuntime

MODELS_PATH = os.path.join(os.getcwd(), 'models')

docker_runtime = SeldonDockerRuntime()
model_outputs = [
    MetadataTensor(
        name="output-0",
        datatype="FP32",
        shape=[2, 3],
        parameters=MetadataTensorParameters(ext_datatype=np.ndarray),
    )
]

sklearn_iris_path = os.path.join(MODELS_PATH, 'sklearn-iris')
sklearn_model = Model(
    name="test-iris-sklearn",
    runtime=docker_runtime,
    framework=ModelFramework.SKLearn,
    uri="gs://seldon-models/sklearn/iris",
    local_folder=sklearn_iris_path,
    outputs=model_outputs
)

xgboost_iris_path = os.path.join(MODELS_PATH, 'xgboost-iris')
xgboost_model = Model(
    name="test-iris-xgboost",
    runtime=docker_runtime,
    framework=ModelFramework.XGBoost,
    uri="gs://seldon-models/xgboost/iris",
    local_folder=xgboost_iris_path,
    outputs=model_outputs
)

@pipeline(name="inference-pipeline", models=[sklearn_model, xgboost_model])
def inference_pipeline(payload: np.ndarray) -> np.ndarray:
    res1 = sklearn_model(payload)
    if res1[0][0] > 0.7:
        return res1
    else:
        return xgboost_model(payload)

```

This pipeline can then be serialised using `cloudpickle`.


```python
inference_pipeline.save("inference-pipeline.pickle")
```

## Serving the pipeline

Once we have our pipeline created and serialised, we can then create a `model-settings.json` file.
This configuration file will hold the configuration specific to our MLOps pipeline.


```python
%%writefile ./model-settings.json
{
    "name": "tempo-pipeline",
    "implementation": "mlserver_tempo.TempoModel",
    "parameters": {
        "uri": "./inference-pipeline.pickle"
    }
}
```

### Start serving our model

Now that we have our config in-place, we can start the server by running `mlserver start .`. This needs to either be ran from the same directory where our config files are or pointing to the folder where they are.

```shell
mlserver start .
```

Since this command will start the server and block the terminal, waiting for requests, this will need to be ran in the background on a separate terminal.

### Deploy our pipeline components

Additionally, we will also need to deploy our pipeline components.
That is, the SKLearn and XGBoost models.
We can do that as:


```python
inference_pipeline.deploy()
```

### Send test inference request

We now have our model being served by `mlserver`.
To make sure that everything is working as expected, let's send a request.

For that, we can use the Python types that `mlserver` provides out of box, or we can build our request manually.


```python
import requests

x_0 = np.array([[0.1, 3.1, 1.5, 0.2]])
inference_request = {
    "inputs": [
        {
          "name": "predict",
          "shape": x_0.shape,
          "datatype": "FP32",
          "data": x_0.tolist()
        }
    ]
}

endpoint = "http://localhost:8080/v2/models/mlops-pipeline/infer"
response = requests.post(endpoint, json=inference_request)

response.json()
```


```python

```