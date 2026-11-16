# HPDC-400 Dijital İkiz (FreeCAD)

400 t soğuk kamaralı yatay döküm makinesi. Toggle kapamalı, 5 noktalı çift mafsal. Parametrik ve ürün ağacına bağlı FreeCAD modeli.

## Birden fazla bilgisayar
Kurulum ve günlük akış: [docs/COKLU_PC_KURULUM.md](docs/COKLU_PC_KURULUM.md). FreeCAD'de açmak: Makro → `HPDC400_yukle.FCMacro`.

## Hızlı başlangıç (PC, VS Code terminali)
1. FreeCAD 1.0+ kur. `git clone https://github.com/neka-nat/freecad-mcp` yap ve `addon/FreeCADMCP` klasörünü `%APPDATA%\FreeCAD\Mod\` içine kopyala. FreeCAD'i yeniden başlat, "MCP Addon" tezgâhında **Start RPC Server**'a bas.
2. `uv` kur (uvx için). Bu klasörde `claude` çalıştır, ardından `/mcp` ile `freecad` bağlantısını gör.
3. Komut ver: **"CLAUDE.md döngüsüyle faz 2'yi geliştir"** (veya istediğin faz/parça).

Köprü olmadan: `FreeCADCmd assembly/assemble.py` çalıştır. Çıktılar `out/hpdc400.FCStd` (grup ağaçlı) ve `out/hpdc400.step`.
FreeCAD'siz test: `pip install cadquery-ocp matplotlib` kur, sonra `python3 checks/check.py` ve `python3 checks/render.py` çalıştır.

## Yapı
- `params/bom.json`: ürün ağacı, fazlar, koordinat sistemi
- `params/params.json`: ölçüler, lokal orijinler, montaj konumları, izinli temaslar (sahibi: olcu-mimari / Fable)
- `parts/*.py`: her parça için `build(d, G, g)` (sahibi: parca-cizer / Sonnet)
- `lib/geo.py`: FreeCAD Part ve OCP için ortak geometri API'si
- `assembly/assemble.py`: çizer, yerleştirir, FCStd ve STEP yazar
- `checks/check.py`: kalite kapısı (GECERSIZ_GEOMETRI, ADET_UYUSMAZ, BBOX_SAPMA, CAKISMA, GOMULME, ZEMIN_ALTI)
- `checks/render.py`: FreeCAD'siz önizleme PNG'leri
- `.claude/agents/`: ekip tanımları (Fable / Sonnet / Haiku), `CLAUDE.md`: orkestrasyon döngüsü
