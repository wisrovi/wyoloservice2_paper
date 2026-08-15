import os

def fix_bib(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Remove fabricated ones
    content = content.replace(
"""@inproceedings{grank2022,
  title={G-RANK: Topology-Aware GPU Scheduling},
  author={Smith, J. and Doe, A.},
  booktitle={Proceedings of the IEEE International Parallel and Distributed Processing Symposium},
  year={2022}
}""",
"""@inproceedings{amaral2017topology,
  title={Topology-aware GPU scheduling for learning workloads in cloud environments},
  author={Amaral, Marcelo and Polo, Jorda and Carrera, David and Mohomed, Iqbal and Unuvar, Merve and Steinder, Malgorzata},
  booktitle={SC'17},
  year={2017}
}"""
    )
    
    content = content.replace(
"""@article{tdwr2023,
  title={Dynamic Workload Redistribution for GPU Clusters},
  author={Johnson, M. and Lee, K.},
  journal={IEEE Transactions on Cloud Computing},
  year={2023}
}""",
"""@inproceedings{weng2022mlaas,
  title={MLaaS in the Wild: Workload Analysis and Scheduling in Large-Scale Heterogeneous GPU Clusters},
  author={Weng, Qizhen and others},
  booktitle={NSDI},
  year={2022}
}"""
    )
    
    # Kubeflow real reference
    content = content.replace(
"""@inproceedings{burns2016borg,
  title={Borg, Omega, and Kubernetes},
  author={Burns, Brendan and others},
  booktitle={ACM Queue},
  year={2016}
}""",
"""@misc{bisong2019kubeflow,
  title={Kubeflow and Kubeflow Pipelines},
  author={Bisong, Ekaba},
  howpublished={Building Machine Learning and Deep Learning Models on Google Cloud Platform},
  year={2019}
}"""
    )
    
    # Add COCO and YOLOv8
    if "lin2014microsoft" not in content:
        content += """\n@inproceedings{lin2014microsoft,
  title={Microsoft COCO: Common Objects in Context},
  author={Lin, Tsung-Yi and others},
  booktitle={ECCV},
  year={2014}
}\n"""

    if "jocher2023yolov8" not in content:
        content += """\n@misc{jocher2023yolov8,
  title={YOLOv8},
  author={Jocher, Glenn and Chaurasia, Ayush and Qiu, Jing},
  howpublished={\\url{https://github.com/ultralytics/ultralytics}},
  year={2023}
}\n"""
        
    with open(filepath, 'w') as f:
        f.write(content)

fix_bib('/home/william.rodriguez/Documents/w_libraries/train_service2/wyoloservice2_paper/normal_papers/paper_1_mlops/en/references.bib')
fix_bib('/home/william.rodriguez/Documents/w_libraries/train_service2/wyoloservice2_paper/normal_papers/paper_1_mlops/es/references.bib')
