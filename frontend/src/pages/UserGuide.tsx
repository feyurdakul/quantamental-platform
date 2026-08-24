import React from 'react';
import { 
  BookOpen, 
  HelpCircle, 
  Calculator, 
  Layers, 
  CheckCircle2, 
  TrendingUp, 
  ShieldCheck, 
  Zap, 
  DollarSign, 
  BarChart3, 
  Compass, 
  Info,
  PieChart,
  LayoutDashboard,
  Settings
} from 'lucide-react';

export const UserGuide: React.FC = () => {
  return (
    <div className="space-y-6 max-w-5xl">
      
      {/* 1. Üst Başlık Banner */}
      <div className="bg-dark-800 border border-slate-800/80 p-6 rounded-md flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-blue-400" />
            <h2 className="text-xl font-bold text-white font-mono">NASIL KULLANILIR & SKORLAMA METODOLOJİSİ</h2>
          </div>
          <p className="text-xs text-slate-400 font-sans mt-1 leading-relaxed">
            Quantamental Platform; temel bilanço analizini, teknik momentum göstergelerini ve iflas riski modellerini 10.0'luk objektif bir kantitatif bileşik skorda birleştiren kurumsal bir karar destek terminalidir.
          </p>
        </div>
        <span className="px-3 py-1 rounded bg-blue-600/10 border border-blue-500/30 text-blue-400 font-mono text-xs font-semibold whitespace-nowrap">
          v1.0.0 REHBERİ
        </span>
      </div>

      {/* 2. 5 KATEGORİ PUAN DAĞILIMI VE HESAPLAMA MATEMATİĞİ (Kullanıcı İsteği) */}
      <div className="bg-dark-800 border border-slate-800/80 p-6 rounded-md space-y-5">
        <div className="flex items-center gap-2 pb-3 border-b border-slate-800/80">
          <Calculator className="w-4 h-4 text-emerald-400" />
          <h3 className="font-bold text-sm font-mono uppercase tracking-wider text-slate-100">
            5 Kategori Puan Dağılımı ve 10'luk Skorlama Mantığı
          </h3>
        </div>

        <p className="text-xs text-slate-300 leading-relaxed font-sans">
          Bu 5 kategori puanı, <code className="text-blue-400 font-mono">sistem_mimari.md Bölüm 8</code> spesifikasyonunda tanımlanan <strong>objektif finansal ve teknik kriterlere</strong> göre <strong>1.00 ile 10.00 arasında</strong> hesaplanır.
        </p>

        {/* 5 Kategori Kartları */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
          
          {/* 1. Değerleme */}
          <div className="bg-dark-900 border border-slate-800 p-4 rounded space-y-2 font-mono">
            <div className="flex justify-between items-center">
              <span className="font-bold text-xs text-white flex items-center gap-1.5">
                🏷️ 1. Değerleme Metrikleri
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 font-bold">%25 AĞIRLIK</span>
            </div>
            <p className="text-[11px] text-slate-400 font-sans">
              Şirketin hisse fiyatının ürettiği kâra ve defter değerine (özkaynağına) göre ne kadar ucuz olduğunu ölçer:
            </p>
            <ul className="text-xs text-slate-300 space-y-1 pl-1 list-disc list-inside">
              <li><strong>F/K Oranı:</strong> F/K &lt; 8.0x ise ➔ <span className="text-emerald-400 font-bold">10.0 Puan</span> (Hisse çok ucuz).</li>
              <li><strong>PD/DD Oranı:</strong> PD/DD &lt; 1.5x ise ➔ <span className="text-emerald-400 font-bold">10.0 Puan</span> (Defter değerine yakın).</li>
            </ul>
            <p className="text-[10px] text-slate-400 pt-1 border-t border-slate-800">
              * Sonuç: Her iki çarpan da çok cazip olduğunda kategori <strong>10.00 tam puan</strong> üretir.
            </p>
          </div>

          {/* 2. Kalite & Kârlılık */}
          <div className="bg-dark-900 border border-slate-800 p-4 rounded space-y-2 font-mono">
            <div className="flex justify-between items-center">
              <span className="font-bold text-xs text-white flex items-center gap-1.5">
                💎 2. Kalite & Kârlılık
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-teal-500/10 text-teal-400 font-bold">%20 AĞIRLIK</span>
            </div>
            <p className="text-[11px] text-slate-400 font-sans">
              Şirketin sahip olduğu özsermayeyi ve varlıkları ne kadar verimli kâra dönüştürdüğünü ölçer:
            </p>
            <ul className="text-xs text-slate-300 space-y-1 pl-1 list-disc list-inside">
              <li><strong>ROE (Özsermaye Kârlılığı):</strong> %5 - %15 aralığındaysa ➔ <span className="text-amber-400 font-bold">6.0 Puan</span>.</li>
              <li><strong>Faaliyet Kâr Marjı:</strong> Marjlar daralmış veya %5'in altındaysa ➔ <span className="text-rose-400 font-bold">4.0 - 2.0 Puan</span>.</li>
            </ul>
            <p className="text-[10px] text-slate-400 pt-1 border-t border-slate-800">
              * Sonuç: Alt metriklerin ağırlıklı ortalaması örneğin <strong>4.67 puan</strong> üretir.
            </p>
          </div>

          {/* 3. Finansal Dayanıklılık */}
          <div className="bg-dark-900 border border-slate-800 p-4 rounded space-y-2 font-mono">
            <div className="flex justify-between items-center">
              <span className="font-bold text-xs text-white flex items-center gap-1.5">
                🛡️ 3. Finansal Dayanıklılık
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold">%20 AĞIRLIK</span>
            </div>
            <p className="text-[11px] text-slate-400 font-sans">
              Şirketin kısa vadeli borç ödeme gücünü ve iflas/likidite riskini denetler:
            </p>
            <ul className="text-xs text-slate-300 space-y-1 pl-1 list-disc list-inside">
              <li><strong>Cari Oran:</strong> 1.0x - 1.5x arasında dengeliyse ➔ <span className="text-emerald-400 font-bold">6.0 - 8.0 Puan</span>.</li>
              <li><strong>Net Borç / Özsermaye:</strong> Borç yönetilebilir düzeyde ➔ <span className="text-emerald-400 font-bold">6.0 Puan</span>.</li>
            </ul>
            <p className="text-[10px] text-slate-400 pt-1 border-t border-slate-800">
              * Brüt Borç Guard koruması devrededir; aşırı borçta puan otomatik sınırlandırılır.
            </p>
          </div>

          {/* 4. Büyüme */}
          <div className="bg-dark-900 border border-slate-800 p-4 rounded space-y-2 font-mono">
            <div className="flex justify-between items-center">
              <span className="font-bold text-xs text-white flex items-center gap-1.5">
                🚀 4. Büyüme & Trend
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 font-bold">%15 AĞIRLIK</span>
            </div>
            <p className="text-[11px] text-slate-400 font-sans">
              Şirketin hasılatının (satışlarının) ve net kârının yıllık artış hızını ölçer:
            </p>
            <ul className="text-xs text-slate-300 space-y-1 pl-1 list-disc list-inside">
              <li><strong>Yıllık Gelir Büyümesi:</strong> Enflasyonun üzerinde %30'dan fazla ise ➔ <span className="text-purple-400 font-bold">10.0 Puan</span>.</li>
              <li><strong>Baz Etkisi Kontrolü:</strong> Önceki dönem negatifse yanıltıcı büyüme filtrelenir.</li>
            </ul>
            <p className="text-[10px] text-slate-400 pt-1 border-t border-slate-800">
              * Sonuç: Hızlı büyüyen gruptaki şirketler <strong>10.00 tam puan</strong> alır.
            </p>
          </div>

          {/* 5. Teknik Görünüm */}
          <div className="bg-dark-900 border border-slate-800 p-4 rounded space-y-2 font-mono md:col-span-2">
            <div className="flex justify-between items-center">
              <span className="font-bold text-xs text-white flex items-center gap-1.5">
                📈 5. Teknik Görünüm & Momentum
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 font-bold">%20 AĞIRLIK</span>
            </div>
            <p className="text-[11px] text-slate-400 font-sans">
              Piyasadaki anlık alım/satım momentumunu, hareketli ortalamaları ve trend rejimini ölçer:
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-slate-300">
              <div className="bg-dark-800 p-2 rounded">
                <strong>Trend Rejimi:</strong> Fiyat &gt; SMA200 ve SMA50 &gt; SMA200 ise ➔ <span className="text-emerald-400 font-bold">Altın Kesişim / Pozitif Trend (10.0 Puan)</span>.
              </div>
              <div className="bg-dark-800 p-2 rounded">
                <strong>RSI (14):</strong> 45–65 arasında sağlıklı yükseliş bandındaysa ➔ <span className="text-emerald-400 font-bold">10.0 Puan</span>.
              </div>
            </div>
          </div>

        </div>

        {/* Nihai Formül Hesabı Kutusu */}
        <div className="bg-dark-950 p-4 rounded border border-blue-500/30 space-y-3 font-mono">
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-blue-400" />
            <h4 className="text-xs font-bold text-white uppercase tracking-wider">
              🧮 Nihai Bileşik Skorun Hesaplanması Örneği:
            </h4>
          </div>

          <p className="text-xs text-slate-300 font-sans">
            Tüm kategori puanları kendi ağırlıklarıyla çarpılarak toplanır:
          </p>

          <div className="bg-dark-900 p-3 rounded text-xs text-blue-300 border border-slate-800 space-y-1">
            <p className="text-slate-400">Bileşik Skor = (Değerleme × 0.25) + (Kalite × 0.20) + (Dayanıklılık × 0.20) + (Büyüme × 0.15) + (Teknik × 0.20)</p>
            <p className="text-slate-400">Bileşik Skor = (10.00 × 0.25) + (4.67 × 0.20) + (6.00 × 0.20) + (10.00 × 0.15) + (10.00 × 0.20)</p>
            <p className="text-white font-bold pt-1">
              Bileşik Skor = 2.50 + 0.93 + 1.20 + 1.50 + 2.00 = <span className="text-emerald-400 text-sm font-black">8.13 / 10.00</span> ➔ <span className="px-2 py-0.5 rounded bg-teal-500/20 text-teal-400 font-bold">BUY SİNYALİ 🟩</span>
            </p>
          </div>

          <p className="text-[11px] text-slate-400 font-sans">
            * <em>Hiçbir skor rastgele veya tahminle oluşturulmaz; her biri şirketin resmi finansal tablosundaki satırlar ile borsadaki canlı fiyatların matematiksel fonksiyonudur.</em>
          </p>
        </div>

      </div>

      {/* 3. SİNYAL EŞİKLERİ TABLOSU */}
      <div className="bg-dark-800 border border-slate-800/80 p-5 rounded-md space-y-3 font-mono text-xs">
        <h3 className="font-bold text-xs uppercase tracking-wider text-slate-200 flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          Sinyal Karar Matrisi & Güven Aralıkları
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-slate-800 text-slate-500 text-[10px]">
                <th className="pb-2">SKOR ARALIĞI</th>
                <th className="pb-2">SİNYAL</th>
                <th className="pb-2">GÜVEN</th>
                <th className="pb-2">TAVSİYE EDİLEN KARAR DESTEĞİ</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              <tr>
                <td className="py-2 font-bold text-emerald-400">≥ 8.40 / 10.0</td>
                <td className="py-2"><span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">STRONG BUY</span></td>
                <td className="py-2 text-emerald-400">HIGH</td>
                <td className="py-2 text-slate-300 font-sans">Güçlü kârlılık, ucuz değerleme ve pozitif trendde. Model portföy adayı.</td>
              </tr>
              <tr>
                <td className="py-2 font-bold text-teal-400">7.20 – 8.39 / 10.0</td>
                <td className="py-2"><span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-teal-500/20 text-teal-400 border border-teal-500/40">BUY</span></td>
                <td className="py-2 text-teal-400">HIGH / MED</td>
                <td className="py-2 text-slate-300 font-sans">Pozitif temel ve teknik yapı. Kademeli alım için uygun.</td>
              </tr>
              <tr>
                <td className="py-2 font-bold text-amber-400">5.20 – 7.19 / 10.0</td>
                <td className="py-2"><span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/40">HOLD</span></td>
                <td className="py-2 text-slate-400">MED / LOW</td>
                <td className="py-2 text-slate-300 font-sans">Dengeli profil. Mevcut pozisyonlar korunabilir, yeni giriş için katalizör beklenir.</td>
              </tr>
              <tr>
                <td className="py-2 font-bold text-rose-400">3.60 – 5.19 / 10.0</td>
                <td className="py-2"><span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-rose-500/20 text-rose-300 border border-rose-500/40">SELL</span></td>
                <td className="py-2 text-rose-400">HIGH / MED</td>
                <td className="py-2 text-slate-300 font-sans">Bozulan marjlar, yüksek borçluluk veya negatif teknik trend.</td>
              </tr>
              <tr>
                <td className="py-2 font-bold text-rose-500">&lt; 3.60 / 10.0</td>
                <td className="py-2"><span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-rose-600/20 text-rose-400 border border-rose-600/40">STRONG SELL</span></td>
                <td className="py-2 text-rose-500">HIGH</td>
                <td className="py-2 text-slate-300 font-sans">Yüksek finansal distres veya aşırı şişmiş değerleme. Portföyden çıkarılmalı.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* 4. SİSTEMİN NASIL KULLANILACAĞI (5 Sayfa Rehberi) */}
      <div className="bg-dark-800 border border-slate-800/80 p-6 rounded-md space-y-4">
        <div className="flex items-center gap-2 pb-3 border-b border-slate-800/80">
          <Compass className="w-4 h-4 text-blue-400" />
          <h3 className="font-bold text-sm font-mono uppercase tracking-wider text-slate-100">
            Terminal Sayfalarının Kullanım Rehberi
          </h3>
        </div>

        <div className="space-y-3 font-sans text-xs">
          
          <div className="bg-dark-900 p-3.5 rounded border border-slate-800">
            <h4 className="font-bold font-mono text-white flex items-center gap-2">
              <LayoutDashboard className="w-3.5 h-3.5 text-blue-400" /> 1. Terminal Özeti (Dashboard)
            </h4>
            <p className="text-slate-300 mt-1">
              Piyasa genel görünümünü ve iki liderlik tablosunu (<strong>En Güçlü Potansiyel Liderleri</strong> ve <strong>En Riskli & Aşırı Değerliler</strong>) tek bakışta izleyin. Varlık sınıfı butonlarına basarak BIST, ABD, ETF veya Kripto bazında filtreleyebilirsiniz.
            </p>
          </div>

          <div className="bg-dark-900 p-3.5 rounded border border-slate-800">
            <h4 className="font-bold font-mono text-white flex items-center gap-2">
              <Layers className="w-3.5 h-3.5 text-blue-400" /> 2. Varlık Evreni (Quant Screener)
            </h4>
            <p className="text-slate-300 mt-1">
              673 varlığı sektör, isim veya sembolle arayabilir; 10'luk bileşik skora veya sembole göre sıralayabilirsiniz. Herhangi bir satırdaki <strong>360° İncele</strong> butonuna basarak derinlemesine analiz sayfasına geçebilirsiniz.
            </p>
          </div>

          <div className="bg-dark-900 p-3.5 rounded border border-slate-800">
            <h4 className="font-bold font-mono text-white flex items-center gap-2">
              <BarChart3 className="w-3.5 h-3.5 text-blue-400" /> 3. 360° Varlık Detayı
            </h4>
            <p className="text-slate-300 mt-1">
              10 metrik grubunun (Fiyat, RSI, Değerleme, Kalite, Büyüme, Borçluluk, Altman Z-Score ve Piotroski F-Score) dökümünü inceleyin. BIST hisselerinde sağ üstteki <strong>USD (TMS-29 Arındırılmış)</strong> butonuna basarak enflasyondan arındırılmış USD tablolara geçiş yapabilirsiniz. Beğendiğiniz hisseyi <strong>Portföye Ekle</strong> butonuyla model portföyünüze ekleyebilirsiniz.
            </p>
          </div>

          <div className="bg-dark-900 p-3.5 rounded border border-slate-800">
            <h4 className="font-bold font-mono text-white flex items-center gap-2">
              <PieChart className="w-3.5 h-3.5 text-blue-400" /> 4. Model Portföyü & Risk Dağılımı
            </h4>
            <p className="text-slate-300 mt-1">
              Açık pozisyonlarınızın toplam portföy değerini, alış maliyetini, realize edilmemiş net kâr/zararını ve sektör çeşitlendirmesini takip edin. Konsantrasyon kuralı uyarınca tek bir sektörün %30'u geçmemesi risk kontrolü açısından tavsiye edilir.
            </p>
          </div>

          <div className="bg-dark-900 p-3.5 rounded border border-slate-800">
            <h4 className="font-bold font-mono text-white flex items-center gap-2">
              <Settings className="w-3.5 h-3.5 text-blue-400" /> 5. Ayarlar & Sistem Yönetimi
            </h4>
            <p className="text-slate-300 mt-1">
              <strong>TAM TARAMAYI BAŞLAT</strong> butonuna basarak arka planda tüm 7 veri sağlayıcıdan güncel fiyat ve tabloları çekip skorları baştan hesaplatabilirsiniz. <strong>EKRANI GÜNCELLE</strong> butonu ise salt okunur olarak son veritabanı kayıtlarını ekrana yeniden yükler.
            </p>
          </div>

        </div>
      </div>

    </div>
  );
};
