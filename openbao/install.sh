helm repo add openbao https://openbao.github.io/openbao-helm
helm repo update

helm upgrade --install openbao \
  openbao/openbao \
  --namespace openbao \
  --create-namespace \
  --set server.dev.enabled=true