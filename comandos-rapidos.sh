#!/bin/bash
# Script para subir rápidamente a GitHub

echo "🚀 Iniciando deploy del Sistema YOLO..."

# Verificar si Git está instalado
if ! command -v git &> /dev/null
then
    echo "❌ Git no está instalado. Descárgalo de: https://git-scm.com"
    exit
fi

# Inicializar Git si no existe
if [ ! -d .git ]; then
    echo "📦 Inicializando repositorio Git..."
    git init
fi

# Agregar todos los archivos
echo "📝 Agregando archivos..."
git add .

# Commit
echo "💾 Creando commit..."
read -p "Mensaje del commit (Enter para 'Deploy Sistema YOLO'): " mensaje
mensaje=${mensaje:-"Deploy Sistema YOLO"}
git commit -m "$mensaje"

# Configurar remoto si no existe
if ! git remote | grep -q origin; then
    echo "🔗 Configurando repositorio remoto..."
    read -p "URL de tu repositorio GitHub (ej: https://github.com/usuario/repo.git): " repo_url
    git remote add origin "$repo_url"
fi

# Push
echo "⬆️ Subiendo a GitHub..."
git branch -M main
git push -u origin main

echo "✅ ¡Código subido exitosamente!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Ve a https://render.com"
echo "2. Crea un nuevo Web Service"
echo "3. Conecta tu repositorio de GitHub"
echo "4. ¡Deploy automático en 5-7 minutos!"
echo ""
echo "🌐 Tu app estará en: https://tu-servicio.onrender.com"