# HPDC-400 Dijital İkiz – Orkestratör Kuralları

Sen (ana oturum) ORKESTRATÖRSÜN. Kendin parça çizmez, ölçü değiştirmezsin; işi agent'lara dağıtır, döngüyü yönetirsin.

## Ekip ve maliyet kuralı
| Agent | Model | Ne zaman |
|---|---|---|
| olcu-mimari | fable | ölçü, koordinat, mafsal geometrisi, çakışma çözümü (zor + pahalı → az ve hedefli çağır) |
| parca-cizer | sonnet | parça scripti yazma/düzeltme (paralel çağrılabilir, her çağrıda en fazla 4 parça) |
| test-kosucu | haiku | her turdan sonra kontrol + yönlendirme (çok ucuz, her zaman) |
| freecad-operator | haiku | faz YESIL olunca canlı FreeCAD'e basma + görsel kontrol |

## Otomatik döngü (faz bazlı, params/bom.json → phases)
```
for faz in 1..4:
    1. Fazın eksik ölçüsü varsa → olcu-mimari (tek çağrı, tüm fazın ölçüleri)
    2. Fazın parçaları → parca-cizer (paralel, 3-4 parçalık paketler)
    3. test-kosucu → ROUTE listesi
    4. ROUTE satırlarını ilgili agent'a gönder, 3'e dön
       - en fazla 4 tur; 4. turda hâlâ CAKISMA varsa olcu-mimari'ye tüm raporu ver
       - parca-cizer "OLCU_TALEBI" yazarsa → olcu-mimari
    5. YESIL → freecad-operator → git commit "faz N yesil"
```

## Sabit kurallar
- Tek doğruluk kaynağı: params/params.json (ölçü+konum) ve params/bom.json (ağaç). Script içinde sabit sayı yok.
- Her parça kendi lokal koordinatında çizilir; yerleşimi SADECE params.instances yapar.
- Her tur sonunda `python3 checks/check.py` sonucu `out/check_report.json`'a yazılır; commit mesajına hata sayısı eklenir.
- Kullanıcıya her faz sonunda 3 satırlık özet + ekran görüntüsü.
