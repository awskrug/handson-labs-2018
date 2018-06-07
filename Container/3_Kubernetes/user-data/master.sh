#!/bin/bash
# Copyright 2016 The Kubernetes Authors All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -o errexit
set -o nounset
set -o pipefail

NODEUP_URL=https://kubeupv2.s3.amazonaws.com/kops/1.9.0/linux/amd64/nodeup
NODEUP_HASH=54ecae66a2b4e1409b36fc00b550f2501afedbfc








function ensure-install-dir() {
  INSTALL_DIR="/var/cache/kubernetes-install"
  # On ContainerOS, we install to /var/lib/toolbox install (because of noexec)
  if [[ -d /var/lib/toolbox ]]; then
    INSTALL_DIR="/var/lib/toolbox/kubernetes-install"
  fi
  mkdir -p ${INSTALL_DIR}
  cd ${INSTALL_DIR}
}

# Retry a download until we get it. Takes a hash and a set of URLs.
#
# $1 is the sha1 of the URL. Can be "" if the sha1 is unknown.
# $2+ are the URLs to download.
download-or-bust() {
  local -r hash="$1"
  shift 1

  urls=( $* )
  while true; do
    for url in "${urls[@]}"; do
      local file="${url##*/}"
      rm -f "${file}"

      if [[ $(which curl) ]]; then
        if ! curl -f --ipv4 -Lo "${file}" --connect-timeout 20 --retry 6 --retry-delay 10 "${url}"; then
          echo "== Failed to curl ${url}. Retrying. =="
          break
        fi
      elif [[ $(which wget ) ]]; then
        if ! wget --inet4-only -O "${file}" --connect-timeout=20 --tries=6 --wait=10 "${url}"; then
          echo "== Failed to wget ${url}. Retrying. =="
          break
        fi
      else
        echo "== Could not find curl or wget. Retrying. =="
        break
      fi

      if [[ -n "${hash}" ]] && ! validate-hash "${file}" "${hash}"; then
        echo "== Hash validation of ${url} failed. Retrying. =="
      else
        if [[ -n "${hash}" ]]; then
          echo "== Downloaded ${url} (SHA1 = ${hash}) =="
        else
          echo "== Downloaded ${url} =="
        fi
        return
      fi
    done

    echo "All downloads failed; sleeping before retrying"
    sleep 60
  done
}

validate-hash() {
  local -r file="$1"
  local -r expected="$2"
  local actual

  actual=$(sha1sum ${file} | awk '{ print $1 }') || true
  if [[ "${actual}" != "${expected}" ]]; then
    echo "== ${file} corrupted, sha1 ${actual} doesn't match expected ${expected} =="
    return 1
  fi
}

function split-commas() {
  echo $1 | tr "," "\n"
}

function try-download-release() {
  # TODO(zmerlynn): Now we REALLY have no excuse not to do the reboot
  # optimization.

  local -r nodeup_urls=( $(split-commas "${NODEUP_URL}") )
  local -r nodeup_filename="${nodeup_urls[0]##*/}"
  if [[ -n "${NODEUP_HASH:-}" ]]; then
    local -r nodeup_hash="${NODEUP_HASH}"
  else
  # TODO: Remove?
    echo "Downloading sha1 (not found in env)"
    download-or-bust "" "${nodeup_urls[@]/%/.sha1}"
    local -r nodeup_hash=$(cat "${nodeup_filename}.sha1")
  fi

  echo "Downloading nodeup (${nodeup_urls[@]})"
  download-or-bust "${nodeup_hash}" "${nodeup_urls[@]}"

  chmod +x nodeup
}

function download-release() {
  # In case of failure checking integrity of release, retry.
  until try-download-release; do
    sleep 15
    echo "Couldn't download release. Retrying..."
  done

  echo "Running nodeup"
  # We can't run in the foreground because of https://github.com/docker/docker/issues/23793
  ( cd ${INSTALL_DIR}; ./nodeup --install-systemd-unit --conf=${INSTALL_DIR}/kube_env.yaml --v=8  )
}

####################################################################################

/bin/systemd-machine-id-setup || echo "failed to set up ensure machine-id configured"

echo "== nodeup node config starting =="
ensure-install-dir

cat > cluster_spec.yaml << '__EOF_CLUSTER_SPEC'
cloudConfig: null
docker:
  bridge: ""
  insecureRegistry: 100.64.0.0/10
  ipMasq: false
  ipTables: false
  logDriver: json-file
  logLevel: warn
  logOpt:
  - max-size=10m
  - max-file=5
  storage: overlay,aufs
  version: 17.03.2
encryptionConfig: null
etcdClusters:
  events:
    image: gcr.io/google_containers/etcd:2.2.1
    version: 2.2.1
  main:
    image: gcr.io/google_containers/etcd:2.2.1
    version: 2.2.1
kubeAPIServer:
  address: 127.0.0.1
  admissionControl:
  - Initializers
  - NamespaceLifecycle
  - LimitRanger
  - ServiceAccount
  - PersistentVolumeLabel
  - DefaultStorageClass
  - DefaultTolerationSeconds
  - MutatingAdmissionWebhook
  - ValidatingAdmissionWebhook
  - NodeRestriction
  - ResourceQuota
  allowPrivileged: true
  anonymousAuth: false
  apiServerCount: 1
  authorizationMode: RBAC
  cloudProvider: aws
  etcdQuorumRead: false
  etcdServers:
  - http://127.0.0.1:4001
  etcdServersOverrides:
  - /events#http://127.0.0.1:4002
  image: gcr.io/google_containers/kube-apiserver:v1.9.3
  insecurePort: 8080
  kubeletPreferredAddressTypes:
  - InternalIP
  - Hostname
  - ExternalIP
  logLevel: 2
  requestheaderAllowedNames:
  - aggregator
  requestheaderExtraHeaderPrefixes:
  - X-Remote-Extra-
  requestheaderGroupHeaders:
  - X-Remote-Group
  requestheaderUsernameHeaders:
  - X-Remote-User
  securePort: 443
  serviceClusterIPRange: 100.64.0.0/13
  storageBackend: etcd2
kubeControllerManager:
  allocateNodeCIDRs: true
  attachDetachReconcileSyncPeriod: 1m0s
  cloudProvider: aws
  clusterCIDR: 100.96.0.0/11
  clusterName: nalbam-seoul.k8s.local
  configureCloudRoutes: false
  image: gcr.io/google_containers/kube-controller-manager:v1.9.3
  leaderElection:
    leaderElect: true
  logLevel: 2
  useServiceAccountCredentials: true
kubeProxy:
  clusterCIDR: 100.96.0.0/11
  cpuRequest: 100m
  hostnameOverride: '@aws'
  image: gcr.io/google_containers/kube-proxy:v1.9.3
  logLevel: 2
kubeScheduler:
  image: gcr.io/google_containers/kube-scheduler:v1.9.3
  leaderElection:
    leaderElect: true
  logLevel: 2
kubelet:
  allowPrivileged: true
  cgroupRoot: /
  cloudProvider: aws
  clusterDNS: 100.64.0.10
  clusterDomain: cluster.local
  enableDebuggingHandlers: true
  evictionHard: memory.available<100Mi,nodefs.available<10%,nodefs.inodesFree<5%,imagefs.available<10%,imagefs.inodesFree<5%
  featureGates:
    ExperimentalCriticalPodAnnotation: "true"
  hostnameOverride: '@aws'
  kubeconfigPath: /var/lib/kubelet/kubeconfig
  logLevel: 2
  networkPluginName: cni
  nonMasqueradeCIDR: 100.64.0.0/10
  podInfraContainerImage: gcr.io/google_containers/pause-amd64:3.0
  podManifestPath: /etc/kubernetes/manifests
masterKubelet:
  allowPrivileged: true
  cgroupRoot: /
  cloudProvider: aws
  clusterDNS: 100.64.0.10
  clusterDomain: cluster.local
  enableDebuggingHandlers: true
  evictionHard: memory.available<100Mi,nodefs.available<10%,nodefs.inodesFree<5%,imagefs.available<10%,imagefs.inodesFree<5%
  featureGates:
    ExperimentalCriticalPodAnnotation: "true"
  hostnameOverride: '@aws'
  kubeconfigPath: /var/lib/kubelet/kubeconfig
  logLevel: 2
  networkPluginName: cni
  nonMasqueradeCIDR: 100.64.0.0/10
  podInfraContainerImage: gcr.io/google_containers/pause-amd64:3.0
  podManifestPath: /etc/kubernetes/manifests
  registerSchedulable: false

__EOF_CLUSTER_SPEC

cat > ig_spec.yaml << '__EOF_IG_SPEC'
kubelet: null
nodeLabels:
  kops.k8s.io/instancegroup: master-ap-northeast-2a
suspendProcesses: null
taints: null

__EOF_IG_SPEC

cat > kube_env.yaml << '__EOF_KUBE_ENV'
Assets:
- ef979a00ba2f7bf4ee5023e82f94ced2d94c1726@https://storage.googleapis.com/kubernetes-release/release/v1.9.3/bin/linux/amd64/kubelet
- a27d808eb011dbeea876fe5326349ed167a7ed28@https://storage.googleapis.com/kubernetes-release/release/v1.9.3/bin/linux/amd64/kubectl
- d595d3ded6499a64e8dac02466e2f5f2ce257c9f@https://storage.googleapis.com/kubernetes-release/network-plugins/cni-plugins-amd64-v0.6.0.tgz
- c6f310214f687b6c2f32e81c2a49235182950be3@https://kubeupv2.s3.amazonaws.com/kops/1.9.0/linux/amd64/utils.tar.gz
ClusterName: nalbam-seoul.k8s.local
ConfigBase: s3://kops-state-store-nalbam-seoul/nalbam-seoul.k8s.local
InstanceGroupName: master-ap-northeast-2a
Tags:
- _automatic_upgrades
- _aws
- _kubernetes_master
- _networking_cni
channels:
- s3://kops-state-store-nalbam-seoul/nalbam-seoul.k8s.local/addons/bootstrap-channel.yaml
protokubeImage:
  hash: 4bbfcc6df1c1c0953bd0532113a74b7ae21e0ded
  name: protokube:1.9.0
  source: https://kubeupv2.s3.amazonaws.com/kops/1.9.0/images/protokube.tar.gz

__EOF_KUBE_ENV

download-release
echo "== nodeup node config done =="
