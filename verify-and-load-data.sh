#!/bin/bash
# Script para verificar y cargar datos en la base de datos UPTC
# Ejecutar en el servidor: bash verify-and-load-data.sh

echo "🔍 Verificando estado de la base de datos UPTC..."
echo "================================================"

# Verificar si el contenedor de la base de datos está corriendo
if ! docker ps | grep -q "uptc_database"; then
    echo "❌ El contenedor uptc_database no está corriendo"
    exit 1
fi

echo "✅ Contenedor de base de datos está activo"

# Verificar si la tabla existe y tiene datos
echo ""
echo "📊 Verificando tabla consumption_records..."
RECORD_COUNT=$(docker exec uptc_database psql -U uptc_user -d uptc_energy -t -c "SELECT COUNT(*) FROM consumption_records;" 2>/dev/null | xargs)

if [ -z "$RECORD_COUNT" ] || [ "$RECORD_COUNT" = "0" ]; then
    echo "⚠️  La tabla está vacía o no existe"
    echo ""
    echo "🔄 Cargando datos desde CSV..."
    echo "   Esto puede tomar 5-10 minutos..."
    
    # Copiar el CSV al contenedor si no está
    if ! docker exec uptc_database test -f /tmp/consumos_uptc.csv; then
        echo "   Copiando archivo CSV al contenedor..."
        docker cp ./consumos_uptc_hackday/consumos_uptc.csv uptc_database:/tmp/consumos_uptc.csv
    fi
    
    # Ejecutar script de carga
    docker exec -i uptc_database psql -U uptc_user -d uptc_energy < ./backend/init_data.sql
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Datos cargados exitosamente"
        
        # Verificar conteo final
        FINAL_COUNT=$(docker exec uptc_database psql -U uptc_user -d uptc_energy -t -c "SELECT COUNT(*) FROM consumption_records;" 2>/dev/null | xargs)
        echo "📊 Total de registros cargados: $FINAL_COUNT"
    else
        echo ""
        echo "❌ Error al cargar los datos"
        exit 1
    fi
else
    echo "✅ La tabla tiene $RECORD_COUNT registros"
fi

echo ""
echo "================================================"
echo "📋 Resumen por sede:"
docker exec uptc_database psql -U uptc_user -d uptc_energy -c "
SELECT 
    sede,
    COUNT(*) as registros,
    MIN(timestamp) as fecha_inicio,
    MAX(timestamp) as fecha_fin
FROM consumption_records 
GROUP BY sede 
ORDER BY sede;
" 2>/dev/null

echo ""
echo "✅ Verificación completada!"
