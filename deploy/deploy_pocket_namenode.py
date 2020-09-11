from os import path
import time

import yaml

from kubernetes import client, config


def main():
    config.load_kube_config()

#    with open(path.join(path.dirname(__file__), "pocket-namenode-service.yaml")) as f:
#        service = yaml.load(f)
#        k8s_beta = client.CoreV1Api()
#        resp = k8s_beta.create_namespaced_service(
#            body=service, namespace="default")
#        print("Service created. status='%s'" % str(resp.status))
#
#    time.sleep(10)

    with open(path.join(path.dirname(__file__), "pocket-namenode-deployment.yaml")) as f:
        # use safe load to disable warnings
        # https://github.com/yaml/pyyaml/wiki/PyYAML-yaml.load(input)-Deprecation
        dep = yaml.safe_load(f)
        k8s_beta = client.AppsV1Api()
        resp = k8s_beta.create_namespaced_deployment(
            body=dep, namespace="default")
        print("Deployment created. status='%s'" % str(resp.status))


if __name__ == '__main__':
    main()
