#!/usr/bin/env bash
set -euo pipefail

# Ruta raíz del proyecto (carpeta donde está este script)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

POX_DIR="${PROJECT_ROOT}/pox"
POX_ENTRY="${POX_DIR}/pox.py"
RULES_FILE="${PROJECT_ROOT}/config/reglas_firewall.json"

CONTROLLER_IP="${1:-127.0.0.1}"
CONTROLLER_PORT="${2:-6633}"
FIREWALL_RULES="${3:-${RULES_FILE}}"
TARGET_SWITCH="${4:-}"

echo "Iniciando POX (firewall L2) en ${CONTROLLER_IP}:${CONTROLLER_PORT}..."
echo "Archivo de reglas: ${FIREWALL_RULES}"
[ -n "${TARGET_SWITCH}" ] && echo "Switch objetivo para firewall: ${TARGET_SWITCH}"


if [[ "${FIREWALL_RULES}" != /* ]]; then
    FIREWALL_RULES="${PROJECT_ROOT}/${FIREWALL_RULES#./}"
fi


pushd "${POX_DIR}" >/dev/null

if [ -n "${TARGET_SWITCH}" ]; then
    python3 "${POX_ENTRY}" openflow.of_01 --port="${CONTROLLER_PORT}" firewall \
        --reglas="${FIREWALL_RULES}" --switch_objetivo="${TARGET_SWITCH}" &
else
    python3 "${POX_ENTRY}" openflow.of_01 --port="${CONTROLLER_PORT}" firewall \
        --reglas="${FIREWALL_RULES}" &
fi

POX_PID=$!
popd >/dev/null

cleanup() {
    if kill -0 "${POX_PID}" >/dev/null 2>&1; then
        echo "Finalizando POX (PID ${POX_PID})..."
        kill "${POX_PID}"
    fi
}
trap cleanup EXIT

echo "POX en marcha. Lanza Mininet en otra terminal apuntando a ${CONTROLLER_IP}:${CONTROLLER_PORT}."
echo "Presiona Ctrl+C para detener POX."

wait "${POX_PID}"
