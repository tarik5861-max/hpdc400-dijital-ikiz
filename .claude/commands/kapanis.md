---
description: Oturumu kapat — kontroller, DURUM/KARARLAR güncelle, commit + push
---
Bu bir oturum kapanışı. Sırayla yap:
1. `statik_kontrol` ve gerekiyorsa `hareket_kontrolu` (mengene + `kalip_yuksekligi_taramasi`) → YEŞİL değilse commit etme, sorunu DURUM.md'ye yaz ve kullanıcıya bildir.
2. `docs/DURUM.md`'yi baştan yeniden yaz (ekleme değil): Şu an / Açık noktalar / Sıradaki adım, en fazla ~60 satır.
3. Bu oturumda alınan kararları `docs/KARARLAR.md` tablosunun en üstüne ekle (tarih, karar, neden).
4. Kademe durumu değiştiyse `docs/YOL_HARITASI.md` tablosunu güncelle. Konuşulan ama yapılmayan fikirleri `docs/fikirler.md`'ye tek satır ekle.
5. `git add -A && git commit -m "<ne yapıldı>; check <hata sayısı>"` ve `git push`.
6. Kullanıcıya 3 satır: ne yapıldı, kontrol sonucu, sıradaki adım. Ek not: $ARGUMENTS
