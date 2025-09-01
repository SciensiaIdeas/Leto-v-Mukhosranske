#!/usr/bin/env bash
set -euo pipefail

PKG=leto-v-mukhosranske
VER=1.1.0
ARCH=amd64
ROOT="${PKG}_${VER}_${ARCH}"

DIST_DIR="$(pwd)/dist/main"

# Очистка и структура пакета
rm -rf "$ROOT"
mkdir -p "$ROOT/DEBIAN"
mkdir -p "$ROOT/opt/$PKG"
mkdir -p "$ROOT/usr/bin"
mkdir -p "$ROOT/usr/share/applications"
mkdir -p "$ROOT/usr/share/icons/hicolor/128x128/apps"

# 1) Копируем содержимое игры
#   - ВАЖНО: нужен бинарь Leto-v-Mukhosranske и вся папка _internal
install -Dm0755 "$DIST_DIR/Leto-v-Mukhosranske" "$ROOT/opt/$PKG/Leto-v-Mukhosranske"
cp -a "$DIST_DIR/_internal" "$ROOT/opt/$PKG/"

# 2) Лаунчер /usr/bin
cat > "$ROOT/usr/bin/$PKG" << 'EOF'
#!/usr/bin/env bash
set -euo pipefail
APP_DIR="/opt/leto-v-mukhosranske"
cd "$APP_DIR"
exec "./Leto-v-Mukhosranske" "$@"
EOF
chmod 0755 "$ROOT/usr/bin/$PKG"

# 3) .desktop (категория Игры)
cat > "$ROOT/usr/share/applications/$PKG.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Лето в Мухосранске
Comment=Небольшая игра про Мухосранск, сделанная из снятых видео, с многолинейным сюжетом
Exec=$PKG
Icon=$PKG
Terminal=false
Categories=Game;
StartupWMClass=Leto-v-Mukhosranske
EOF

# 4) Иконка (положи свой PNG 128x128 в файл icon.png в текущей папке)
if [[ -f logo.png ]]; then
  install -m 0644 logo.png "$ROOT/usr/share/icons/hicolor/128x128/apps/$PKG.png"
else
  echo "Внимание: logo.png не найден — иконка не будет установлена."
fi

# 5) DEBIAN/control
cat > "$ROOT/DEBIAN/control" << EOF
Package: $PKG
Version: $VER
Section: games
Priority: optional
Architecture: $ARCH
Depends: libc6, zlib1g
Maintainer: SciensiaIdeas
Description: The satirical interactive film with multiple endings
EOF

# 6) Права
find "$ROOT" -type d -exec chmod 0755 {} +
find "$ROOT/DEBIAN" -type f -exec chmod 0644 {} +
chmod 0755 "$ROOT/usr/bin/$PKG" "$ROOT/opt/$PKG/Leto-v-Mukhosranske"

# 7) Сборка .deb
dpkg-deb --build --root-owner-group "$ROOT"
echo "Built: ${ROOT}.deb"