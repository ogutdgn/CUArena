# VERIFY — pipeline'ı adım adım kendin doğrula (ensure-parity dalı)

> Bu dal SADECE ölçüm makinesini içerir: motorlar + problar + cevap anahtarları.
> Üretilmiş sonuç/rapor YOK — her şeyi kendin koşturup üreteceksin; amaç tam da bu:
> "gerçekten ölçebiliyor mu?" sorusunu kendi gözünle cevaplamak.
>
> Hazırlık (bir kez): `npm install` (gerekirse) → `npm run build`. Word kapalı olsun.
> Her adımın çıktısı `parity/results/` altına yazılır (bu dalda boş başlar — senin ürettiklerin).

## Sıra önerisi ve her adımda neye bakacağın

### 0) Önce hakemi test et — differ'ın güven kapısı
```
python parity/engines/review_differ.py
```
- **Beklenen:** "ALL PASS — differ trustworthy". Tuzaklı çiftleri kendisi üretir ve
  yakalamak zorundadır. Bu geçmeden 1. eksenin hiçbir sonucuna güvenme.

### 1) OOXML — dosya içeriği paritesi
```
python parity/engines/run.py --capture          # iki tarafı da yakalar (Word açılıp kapanır) + diff
```
- Rapor: `parity/results/LEDGER.md`
- **Nokta-doğrulama:** "gap" denen bir görevin `wc-<id>.docx` ve `rw-<id>.docx` dosyalarını
  7-zip ile aç, `word/document.xml`'e bak — ledger'ın "missing" dediği düğüm gerçekten yok mu?
  Bir de "semantic-pass" denen bir çifti karşılaştır — gerçekten aynı mı? (yanlış-yeşil avı)

### 2) STRUCTURE — şerit yapısı + menü içi
```
python parity/engines/structure_verify.py --capture --report-only
```
- Rapor: `parity/results/STRUCTURE_LEDGER.md`
- **Nokta-doğrulama:** "MISSING" listesinden 2 kontrol seç → `npm start` ile klonu aç,
  o sekmeye bak: düğme gerçekten yok mu? Bir de "matched" birini Word'de aç, adı birebir mi?

### 2b) STATE — gri/aktif durumu
```
powershell -File parity/oracle/capture_enabled_states.ps1 -List parity/oracle/_idmso_list.txt -Out parity/oracle/_enabled_states.tsv
python parity/engines/state_verify.py --capture --report-only
```
- Rapor: `parity/results/STATE_LEDGER.md`
- **Nokta-doğrulama:** bir "MISMATCH" satırı seç → klonu aç, o bağlamı kur (ör. tablo dışı),
  düğme gerçekten yanlış durumda mı? Aynısını gerçek Word'de de gör.

### 3) SCORECARD — canlı tıklama
```
python parity/engines/scorecard_verify.py --deep --report-only     # derin mod ~15-30 dk
```
- Rapor: `parity/results/SCORECARD_LEDGER.md`
- **Nokta-doğrulama:** "DEAD" denen kontrole klonda kendin tıkla — gerçekten ölü mü?
  "pass" denen bir dropdown'ı da aç — menü gerçekten dolu mu?

### 4) DIALOG — diyalog alanları
```
python parity/engines/dialog_verify.py --capture-clone --report-only
```
- Rapor: `parity/results/DIALOG_LEDGER.md` (Word tarafı `parity/oracle/dialogs/*.json`
  olarak hazır — gerçek Word'den yakalanmış cevap anahtarları)
- **Nokta-doğrulama:** "missing" denen bir alanı klonun diyaloğunda ara — yok mu?
  Word'de aynı diyaloğu aç (ör. Ctrl+D) — alan orada mı?

### 5) VISUAL — yan yana görsel
```
python parity/engines/visual_verify.py --capture    # Word + klon ekran görüntüleri + birleşik PNG
python parity/engines/visual_verify.py --status
```
- Çıktılar: `C:/tmp/wc-visual/compare-*.png` — **kendi gözünle bak.**
- Hakem verdisi kaydetmek istersen önce altın tuzakları doğru sınıfla
  (`--record g-identical pass ...` / `--record g-different fail ...` → `--golden-ok`),
  yoksa sistem verdini REDDEDER (güven kapısı — bilerek böyle).

### 6) BEHAVIOR — davranış kartları
```
python parity/engines/behavior_verify.py --capture --report-only
```
- Rapor: `parity/results/BEHAVIOR_LEDGER.md`
- **Nokta-doğrulama:** "FAIL" denen adımı klonda elle tekrarla — gerçekten öyle mi?
  "PENDING(❓)" = Word kaydı bekleyen beklenti; tahmin edilmediği için boş — doğru davranış bu.

### 7) KARNE — hepsi bir arada
```
python parity/tools/gen_feature_registry.py     # 111 özelliği komutlara eşler (2. adımdan sonra)
python parity/engines/feature_ledger.py --report-only
```
- Rapor: `parity/results/FEATURE_LEDGER.md` — 111 özellik × eksen kolonları.
- **Kontrol:** kolonlar 1-6'da kendi ürettiğin ledger'larla tutarlı mı? "—" (ölçülmedi)
  hiçbir yerde "pass" gibi görünmüyor mu?

## Değerlendirme ilkesi

Her eksen için karar iki sorudur:
1. **Yanlış alarm var mı?** ("eksik/ölü" dediği şey aslında sağlam mı?)
2. **Yanlış-yeşil var mı?** ("pass" dediği şey aslında bozuk mu?) ← tehlikeli olan bu.

Bir eksen bu iki soruda temiz çıkıyorsa o eksen GÜVENİLİR. Çıkmıyorsa bozuk olan ölçüm
mekanizmasıdır (prob mu yanlış okuyor, eşleştirici mi şaşırıyor) — bulguyu not et, birlikte
o mekanizmayı düzeltiriz.
