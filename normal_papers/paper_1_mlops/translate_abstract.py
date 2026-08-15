import re

def translate_abstract(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    english_abstract = r"""Scaling hyperparameter optimization (HPO) for computer vision models across heterogeneous GPU clusters introduces critical industry bottlenecks in state isolation and task routing. Current methods like Ray Tune and Kubeflow introduce significant containerization overhead, while native distributed Optuna lacks hardware isolation. We present NeuralForge, a distributed MLOps framework bridging this gap with an Invoker-Executor pattern that distributes Optuna trials across GPU worker nodes using Celery. By decoupling execution into ephemeral Docker containers, NeuralForge prevents OOM-driven host failures. Empirical experiments on a 3-node GPU cluster demonstrate median task dispatch latency of 0.8ms ($p < 0.001$, Wilcoxon test), moderate fault tolerance, and a 40\% reduction in idle GPU time (95\% CI [38.5, 41.2]). NeuralForge achieves an optimal HPO best mAP of 0.82 on COCO \cite{lin2014microsoft} with YOLOv8 \cite{jocher2023yolov8} (95\% CI [0.81, 0.83]) in 45 trials, outperforming equivalent Ray Tune and Kubeflow baselines. Scalability to 30 nodes is strictly a theoretical projection via M/M/c queueing models, not an empirical result."""

    spanish_abstract = r"""Escalar la optimización de hiperparámetros (HPO) para modelos de visión artificial en clústeres heterogéneos de GPU introduce cuellos de botella industriales críticos en el aislamiento de estado y enrutamiento de tareas. Los métodos actuales como Ray Tune y Kubeflow introducen una sobrecarga significativa de contenedorización, mientras que Optuna distribuido nativo carece de aislamiento de hardware. Presentamos NeuralForge, un marco de trabajo MLOps distribuido que cierra esta brecha con un patrón Invoker-Executor que distribuye ensayos de Optuna a través de nodos trabajadores de GPU utilizando Celery. Al desacoplar la ejecución en contenedores Docker efímeros, NeuralForge previene los fallos de host causados por falta de memoria (OOM). Los experimentos empíricos en un clúster de GPU de 3 nodos demuestran una latencia mediana de despacho de tareas de 0.8ms ($p < 0.001$, test de Wilcoxon), tolerancia a fallos moderada, y una reducción del 40\% en el tiempo de inactividad de GPU (IC del 95\% [38.5, 41.2]). NeuralForge alcanza un mAP óptimo de HPO de 0.82 en COCO \cite{lin2014microsoft} con YOLOv8 \cite{jocher2023yolov8} (IC del 95\% [0.81, 0.83]) en 45 ensayos, superando a las líneas base equivalentes de Ray Tune y Kubeflow. La escalabilidad a 30 nodos es estrictamente una proyección teórica mediante modelos de colas M/M/c, no un resultado empírico."""

    content = content.replace(english_abstract, spanish_abstract)
    
    with open(filepath, 'w') as f:
        f.write(content)

translate_abstract('/home/william.rodriguez/Documents/w_libraries/train_service2/wyoloservice2_paper/normal_papers/paper_1_mlops/es/main.tex')
