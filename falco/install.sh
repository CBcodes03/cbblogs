helm repo add falcosecurity https://falcosecurity.github.io/charts
helm repo update

helm upgrade --install falco-operator \
  falcosecurity/falco-operator \
  --namespace falco-operator \
  --create-namespace

kubectl get pods -n falco-operator