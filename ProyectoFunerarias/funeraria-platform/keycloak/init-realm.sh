#!/bin/bash
# Script para inicializar el Realm en Keycloak para el proyecto Funerarias

KEYCLOAK_URL="http://localhost:8080"
ADMIN_USER="admin"
ADMIN_PASS="admin"
REALM_NAME="funeraria-realm"
CLIENT_ID="funeraria-client"

echo "Esperando a que Keycloak inicie..."
until curl -s $KEYCLOAK_URL/health/ready | grep -q 'UP'; do
  echo "Keycloak no está listo todavía..."
  sleep 5
done
echo "Keycloak está listo."

echo "1. Obteniendo token de administrador..."
ADMIN_TOKEN=$(curl -s -X POST "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$ADMIN_USER" \
  -d "password=$ADMIN_PASS" \
  -d 'grant_type=password' \
  -d 'client_id=admin-cli' | jq -r '.access_token')

if [ "$ADMIN_TOKEN" == "null" ] || [ -z "$ADMIN_TOKEN" ]; then
    echo "Error obteniendo token. Verifica que jq esté instalado y que las credenciales sean correctas."
    exit 1
fi

echo "2. Creando Realm '$REALM_NAME'..."
curl -s -X POST "$KEYCLOAK_URL/admin/realms" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"realm\": \"$REALM_NAME\",
    \"enabled\": true
  }"

echo "3. Creando Cliente '$CLIENT_ID'..."
curl -s -X POST "$KEYCLOAK_URL/admin/realms/$REALM_NAME/clients" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"clientId\": \"$CLIENT_ID\",
    \"enabled\": true,
    \"publicClient\": false,
    \"directAccessGrantsEnabled\": true,
    \"secret\": \"\"
  }"

echo "4. Creando Roles 'admin' y 'operario'..."
curl -s -X POST "$KEYCLOAK_URL/admin/realms/$REALM_NAME/roles" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "admin"}'

curl -s -X POST "$KEYCLOAK_URL/admin/realms/$REALM_NAME/roles" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "operario"}'

echo "Configuración de Keycloak completada exitosamente."
