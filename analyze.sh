#!/bin/bash

echo "=== Ejecutando Ruff ==="

echo ""
echo "=== Generando reporte JSON de Ruff ==="
ruff check . --output-format=json > ruff-report.json

echo ""
echo "=== Ejecutando análisis de SonarQube ==="
sonar-scanner-7.3.0.5189-windows-x64/bin/sonar-scanner.bat

echo ""
echo "=== Análisis completado ==="
echo "Ver resultados en: http://localhost:9000/dashboard?id=practica2-calidadsoft"