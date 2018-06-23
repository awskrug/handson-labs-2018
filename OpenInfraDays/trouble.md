# install
```bash
kubectl apply -f https://raw.githubusercontent.com/nalbam/kubernetes/master/sample/sample-node-ing.yml
kubectl apply -f https://raw.githubusercontent.com/nalbam/kubernetes/master/sample/sample-web-ing.yml

kubectl apply -f https://raw.githubusercontent.com/nalbam/kubernetes/master/addons/dashboard-v1.8.3.yml
kubectl apply -f https://raw.githubusercontent.com/nalbam/kubernetes/master/addons/heapster-v1.7.0.yml

kubectl create serviceaccount admin -n kube-system
kubectl create clusterrolebinding cluster-admin:kube-system:admin --clusterrole=cluster-admin --serviceaccount=kube-system:admin

kubectl describe secret $(kubectl get secret -n kube-system | grep admin-token | awk '{print $1}') -n kube-system
```

# uninstall cluster
```bash
kops delete cluster --name=awskrug.k8s.local --yes
rm -rf ~/.jx ~/.helm ~/.kube
```

# uninstall jx
```bash
jx uninstall
helm reset --force
rm -rf ~/.jx ~/.helm
```

# start pipeline
```bash
jx start pipeline -f demo
```
